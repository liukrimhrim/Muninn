"""Application Workflows: coordinate one user intention across the domain modules.

Each command is one Library transaction with one receipt. Model calls never run inside
a transaction: a command saves the inputs and a pending ``operation`` first, the call
happens outside, and a second command validates and accepts (or refuses) the result.
Domain decisions stay with their owners; this module only orders them.
"""

from __future__ import annotations

import contextlib
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, ValidationError

from muninn import content, evidence, measurement, practice
from muninn.library import (
    JSON,
    KIND_OWNER,
    ModelRequest,
    Record,
    Store,
    activate,
    active_store,
    digest,
    export_library,
    new_id,
    restore_library,
)
from muninn.library import Conflict as Conflict  # noqa: PLC0414 - re-exported for Web Interaction

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from muninn.library import Clock, Tx

OWNER = "workflows"
RELEASE = "muninn-0.1.0"


# --- the provider seam -----------------------------------------------------------


class ProviderError(Exception):
    """A model call that produced no usable output."""

    def __init__(
        self,
        kind: Literal["timeout", "unavailable", "refused", "malformed"],
        detail: str,
        raw: str | None = None,
    ) -> None:
        """Classify the failure; ``raw`` keeps any malformed response text."""
        super().__init__(f"{kind}: {detail}")
        self.kind = kind
        self.detail = detail
        self.raw = raw


@dataclass(frozen=True)
class ProviderResult:
    """A schema-valid model output, its raw text and the model that produced it."""

    output: BaseModel
    raw: str
    model: str


class Provider(Protocol):
    """Sends one prepared request to the configured model."""

    model: str
    parameters: JSON

    def complete(self, request: ModelRequest) -> ProviderResult:
        """Return a schema-valid output or raise ``ProviderError``."""
        ...


OUTPUTS: dict[str, type[BaseModel]] = {
    content.DRAFT_PROTOCOL["name"]: content.DraftOutline,
    content.TEACH_PROTOCOL["name"]: content.TeachingDraft,
    content.VARIANT_PROTOCOL["name"]: content.VariantDraft,
    evidence.ASSESS_PROTOCOL["name"]: evidence.AssessmentOutput,
    evidence.REASSESS_PROTOCOL["name"]: evidence.AssessmentOutput,
}
AUTHORING_FOR_CONCERN = ("teaching_intervention", "exercise_variant")


# --- operation records -------------------------------------------------------------


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OperationP(_Strict):
    """A saved model-assisted operation and what became of its output."""

    purpose: Literal["draft_material", "assess_answer"]
    intent: Literal["initial_outline", "exercise_variant", "teaching_intervention"] | None
    inputs: list[content.RefP]
    input_snapshot: dict[str, Any]
    model: evidence.AssessorP
    status: Literal["pending", "running", "succeeded", "failed", "interrupted"]
    outputs: list[content.RefP]
    raw_response: str | None
    error: str | None
    request_group: str
    try_index: int
    acceptance: Literal["pending", "accepted", "rejected", "stale", "cancelled"]
    acceptance_reason: str | None
    answered_by: str | None = None


class TransitionP(_Strict):
    """Links the revisions one intentional semantic change wrote (compatibility section 3)."""

    scope: list[content.RefP]
    category: Literal["curriculum", "assessment", "policy"]
    before: list[content.RefP]
    after: list[content.RefP]
    actor: str
    reason: str


PAYLOADS: dict[str, type[BaseModel]] = {"operation": OperationP, "transition": TransitionP}


def validate_records(records: list[Record]) -> list[str]:
    """Check every Workflows-owned record against its payload contract."""
    errors: list[str] = []
    for r in records:
        if KIND_OWNER[r.kind] != OWNER:
            continue
        model = PAYLOADS.get(r.kind)
        if model is None:
            errors.append(f"{r.kind} records are not supported by this release")
            continue
        try:
            model.model_validate(r.payload)
        except ValidationError as e:
            errors.append(f"{r.kind} {r.id} r{r.revision}: {e.errors()[0]['msg']}")
    return errors


def _transition(
    tx: Tx,
    *,
    category: Literal["curriculum", "assessment"],
    scope: list[JSON],
    actor: str,
    reason: str,
) -> JSON:
    """Record the semantic change this command made: each revised record, before and after."""
    after = [r for r in tx.written if r["kind"] not in ("operation", "transition")]
    first: dict[tuple[str, str], int] = {}
    for r in after:
        first.setdefault((r["kind"], r["id"]), r["revision"])
    before = [
        content.RefP(kind=kind, id=id_, revision=revision - 1)
        for (kind, id_), revision in first.items()
        if revision > 1
    ]
    payload = TransitionP(
        scope=[content.RefP(**r) for r in scope],
        category=category,
        before=before,
        after=[content.RefP(**r) for r in after],
        actor=actor,
        reason=reason,
    )
    return tx.put("transition", payload.model_dump(), by=OWNER)


VALIDATORS = (
    content.validate_records,
    evidence.validate_records,
    practice.validate_records,
    measurement.validate_records,
    validate_records,
)


def validate_library(records: list[Record]) -> list[str]:
    """Run every owner's validator over an archive's records (fixed wiring)."""
    return [error for validator in VALIDATORS for error in validator(records)]


def _saved_request(snapshot: JSON, *, refusal: str | None = None) -> ModelRequest:
    """Rebuild the exact saved request, optionally telling the model why it was refused."""
    user = snapshot["user"]
    if refusal is not None:
        user += (
            f"\n<previous_output_refused>\nYour previous output was refused: {refusal}\n"
            "Produce a corrected output that passes these checks.\n</previous_output_refused>"
        )
    return ModelRequest(
        protocol=snapshot["protocol"],
        system=snapshot["system"],
        user=user,
        output=OUTPUTS[snapshot["protocol"]["name"]],
    )


def _group_accepted(tx: Tx, group: str) -> bool:
    return any(
        r.payload["request_group"] == group and r.payload["acceptance"] == "accepted"
        for r in tx.current("operation", by=OWNER)
    )


class _NeedsReview(Exception):  # noqa: N818 - a domain outcome, not a programming error
    """A checked outline proposes reusing or contradicting existing claims."""


REVIEW_PROPOSALS = "waiting for your review of how it relates to claims you already have"
REVIEW_CORRECTION = "waiting for your decision on the reviewed judgment"


def _reviews(snapshot: JSON) -> bool:
    """Tell whether an operation's saved request reviews a judgment (``reassess-answer``)."""
    return bool(snapshot["protocol"]["name"] == evidence.REASSESS_PROTOCOL["name"])


def _waiting_review(tx: Tx, operation_id: str) -> tuple[Record, OperationP]:
    """Return a finished review still waiting for the learner's decision."""
    record = tx.require("operation", operation_id, by=OWNER)
    op = OperationP.model_validate(record.payload)
    if not _reviews(op.input_snapshot) or (op.status, op.acceptance) != ("succeeded", "pending"):
        msg = "this review is not waiting for a decision"
        raise ValueError(msg)
    return record, op


def _decide(tx: Tx, record: Record, op: OperationP, **update: Any) -> JSON:  # noqa: ANN401
    """Record the learner's decision on an operation's waiting output."""
    decided = op.model_copy(update=update)
    return tx.put("operation", decided.model_dump(), by=OWNER, id=record.id, base=record.revision)


def _change_content(tx: Tx, changed: JSON, *, scope: list[JSON], reason: str) -> JSON:
    """Select the replaced goal revisions in enrollments and record the transition."""
    practice.replace_goals(tx, curricula=changed["curricula"], replaced=changed["replaced"])
    return _transition(tx, category="curriculum", scope=scope, actor="learner", reason=reason)


class _Preview(Exception):  # noqa: N818 - control flow for a rolled-back dry run
    """Carries a correction preview out of its rolled-back savepoint."""


def _phase_id(operation_id: str, phase: str) -> str:
    """Return the deterministic request ID of a server-initiated command."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"muninn:{operation_id}:{phase}"))


class App:
    """The application interface: typed commands and page views over one store."""

    def __init__(
        self, store: Store, provider: Provider, *, activation_id: str | None = None
    ) -> None:
        """Wire the store and the model provider; ``activation_id`` names this process."""
        self.store = store
        self.provider = provider
        self.activation_id = activation_id or new_id()

    @property
    def library_id(self) -> str:
        """Return the active library's identity."""
        return self.store.library_id

    def read[T](self, view: Callable[..., T], *args: Any) -> T:  # noqa: ANN401
        """Run a page view against one consistent snapshot (no writes, no model calls)."""
        return self.store.read(lambda tx: view(tx, *args))

    # --- startup ----------------------------------------------------------------

    def recover(self) -> None:
        """Mark operations cut off by a restart as interrupted and close stale timers."""

        def fn(tx: Tx) -> JSON:
            for r in tx.current("operation", by=OWNER):
                if r.payload["status"] in ("pending", "running"):
                    op = OperationP.model_validate(r.payload)
                    tx.put(
                        "operation",
                        op.model_copy(
                            update={
                                "status": "interrupted",
                                "error": "the app stopped before it finished",
                            }
                        ).model_dump(),
                        by=OWNER,
                        id=r.id,
                        base=r.revision,
                    )
            measurement.interrupt_other_activations(tx, activation_id=self.activation_id)
            return {}

        self.store.run(
            _phase_id(self.activation_id, "recover"),
            "recover",
            {"activation": self.activation_id},
            fn,
        )

    # --- operations -------------------------------------------------------------

    def _new_operation(  # noqa: PLR0913 - one keyword per operation field
        self,
        tx: Tx,
        *,
        purpose: Literal["draft_material", "assess_answer"],
        intent: Literal["initial_outline", "exercise_variant", "teaching_intervention"] | None,
        inputs: list[JSON],
        request: ModelRequest,
        context: JSON,
        group: str | None = None,
        try_index: int = 1,
    ) -> JSON:
        op = OperationP(
            purpose=purpose,
            intent=intent,
            inputs=[content.RefP(**r) for r in inputs],
            input_snapshot={
                "protocol": request.protocol,
                "system": request.system,
                "user": request.user,
                "context": context,
            },
            model=evidence.AssessorP(
                kind="model",
                name=self.provider.model,
                version=self.provider.model,
                protocol_version=request.protocol["version"],
                parameters=self.provider.parameters,
            ),
            status="pending",
            outputs=[],
            raw_response=None,
            error=None,
            request_group=group or new_id(),
            try_index=try_index,
            acceptance="pending",
            acceptance_reason=None,
        )
        return tx.put("operation", op.model_dump(), by=OWNER)

    def operation(self, operation_id: str) -> JSON:
        """Return an operation's current state."""
        record = self.store.read(lambda tx: tx.get("operation", operation_id, by=OWNER))
        if record is None:
            msg = f"no operation {operation_id}"
            raise LookupError(msg)
        return record.view

    def run_operation(self, operation_id: str) -> JSON:
        """Make the saved model request and accept or refuse its result.

        Safe to call twice: only a pending operation starts. A refused first output gets
        one targeted retry; a timeout waits for an explicit retry.
        """
        current = self.operation(operation_id)
        if current["status"] != "pending":
            return current

        def start(tx: Tx) -> JSON:
            record = tx.get("operation", operation_id, by=OWNER)
            if record is None or record.payload["status"] != "pending":
                msg = "operation is no longer pending"
                raise Conflict(msg)
            op = OperationP.model_validate(record.payload)
            return {
                "operation": tx.put(
                    "operation",
                    op.model_copy(update={"status": "running"}).model_dump(),
                    by=OWNER,
                    id=operation_id,
                    base=record.revision,
                )
            }

        try:
            self.store.run(
                _phase_id(operation_id, "start"),
                "start_operation",
                {"operation": operation_id},
                start,
            )
        except Conflict:
            return self.operation(operation_id)
        request = _saved_request(current["input_snapshot"])
        try:
            result = self.provider.complete(request)
        except ProviderError as e:
            if e.kind == "malformed":
                return self._finish(operation_id, None, e.raw, f"malformed output: {e.detail}")
            self._fail(operation_id, str(e))
            return self.operation(operation_id)
        except Exception as e:  # noqa: BLE001 - any failure must leave a retryable operation
            self._fail(operation_id, f"unexpected: {e}")
            return self.operation(operation_id)
        return self._finish(operation_id, result, result.raw, None)

    def _fail(self, operation_id: str, error: str) -> None:
        def fn(tx: Tx) -> JSON:
            record = tx.get("operation", operation_id, by=OWNER)
            assert record is not None  # noqa: S101 - started above
            op = OperationP.model_validate(record.payload)
            return {
                "operation": tx.put(
                    "operation",
                    op.model_copy(update={"status": "failed", "error": error}).model_dump(),
                    by=OWNER,
                    id=operation_id,
                    base=record.revision,
                )
            }

        self.store.run(
            _phase_id(operation_id, "finish"), "fail_operation", {"operation": operation_id}, fn
        )

    def _finish(
        self, operation_id: str, result: ProviderResult | None, raw: str | None, refused: str | None
    ) -> JSON:
        retry: list[str] = []

        def fn(tx: Tx) -> JSON:
            record = tx.get("operation", operation_id, by=OWNER)
            if record is None or record.payload["status"] != "running":
                msg = "operation is no longer running; its output is not accepted"
                raise Conflict(msg)
            op = OperationP.model_validate(record.payload)
            update = self._outcome(tx, record, op, result, refused)
            if update["acceptance"] == "rejected" and op.try_index == 1:
                retry.append(self._retry_with_reasons(tx, op, update["acceptance_reason"])["id"])
            answered = {"answered_by": result.model} if result else {}
            return {
                "operation": tx.put(
                    "operation",
                    op.model_copy(
                        update={"status": "succeeded", "raw_response": raw, **answered, **update}
                    ).model_dump(),
                    by=OWNER,
                    id=operation_id,
                    base=record.revision,
                )
            }

        with contextlib.suppress(Conflict):  # a late result for an interrupted operation
            self.store.run(
                _phase_id(operation_id, "finish"),
                "finish_operation",
                {"operation": operation_id},
                fn,
            )
        for next_id in retry:
            self.run_operation(next_id)
        return self.operation(operation_id)

    def _outcome(
        self,
        tx: Tx,
        record: Record,
        op: OperationP,
        result: ProviderResult | None,
        refused: str | None,
    ) -> JSON:
        """Decide what becomes of an output; a refused acceptance writes nothing."""
        if refused is not None or result is None:
            return {"acceptance": "rejected", "acceptance_reason": refused or "no output"}
        if not self._inputs_current(tx, op):
            return {"acceptance": "stale", "acceptance_reason": "its inputs changed while it ran"}
        try:
            with tx.savepoint():
                outputs = self._accept(tx, record.ref, op, result)
        except _NeedsReview as e:
            return {"acceptance": "pending", "acceptance_reason": str(e) or REVIEW_PROPOSALS}
        except ValueError as e:
            return {"acceptance": "rejected", "acceptance_reason": str(e)}
        return {"acceptance": "accepted", "outputs": [content.RefP(**o) for o in outputs]}

    def _retry_with_reasons(self, tx: Tx, op: OperationP, reason: str) -> JSON:
        return self._new_operation(
            tx,
            purpose=op.purpose,
            intent=op.intent,
            inputs=[i.model_dump() for i in op.inputs],
            request=_saved_request(op.input_snapshot, refusal=reason),
            context=op.input_snapshot["context"],
            group=op.request_group,
            try_index=2,
        )

    def _inputs_current(self, tx: Tx, op: OperationP) -> bool:
        if _group_accepted(tx, op.request_group):
            return False  # another try already produced the accepted result
        if op.intent in AUTHORING_FOR_CONCERN:
            concern = practice.concern_view(tx, op.inputs[0].id)
            return bool(concern["ref"]["revision"] == op.inputs[0].revision)
        if op.purpose == "draft_material":
            source = op.inputs[0]
            latest = content.current_definition(tx, "source", source.id)
            return latest is not None and latest["ref"]["revision"] == source.revision
        if _reviews(op.input_snapshot):  # the judgment it reviews must still be current
            current = evidence.assessment_for(tx, op.input_snapshot["context"]["attempt"]["id"])
            return current is not None and current["ref"] == op.inputs[0].model_dump()
        attempt = op.inputs[0]
        latest = evidence.attempt_view(tx, attempt_id=attempt.id)
        offer = practice.offer_for(tx, attempt.id)
        return (
            latest["ref"]["revision"] == attempt.revision
            and offer is not None
            and offer["state"] == "submitted"
        )

    def _accept(
        self, tx: Tx, operation: JSON, op: OperationP, result: ProviderResult
    ) -> list[JSON]:
        assessor = op.model.model_copy(
            update={"name": result.model, "version": result.model}
        ).model_dump()
        if op.intent == "teaching_intervention":
            return [self._accept_teaching(tx, operation, op, result)]
        if op.intent == "exercise_variant":
            return [_accept_variant(tx, operation, op, result)]
        if op.purpose == "draft_material":
            draft = content.DraftOutline.model_validate(result.output.model_dump())
            source = op.inputs[0].model_dump()
            listed = op.input_snapshot["context"].get("existing", {})
            errors = content.check_draft(draft, content.definition(tx, source)["text"], listed)
            if errors:
                raise ValueError("; ".join(errors))
            if content.needs_review(draft):
                raise _NeedsReview
            return _accept_outline(tx, operation, op, draft, {})
        out = evidence.AssessmentOutput.model_validate(result.output.model_dump())
        if _reviews(op.input_snapshot):  # checked now, applied only when the learner accepts
            errors = evidence.check_reassessment(tx, op.inputs[0].model_dump(), out)
            if errors:
                raise ValueError("; ".join(errors))
            raise _NeedsReview(REVIEW_CORRECTION)
        attempt = op.inputs[0].model_dump()
        accepted = evidence.accept_assessment(
            tx, attempt=attempt, out=out, assessor=assessor, raw_response=result.raw
        )
        question = None
        if out.question and practice.wants_question(
            tx, attempt=attempt, out=out, results=accepted["labels"]
        ):
            exercise = content.definition(tx, evidence.attempt_view(tx, attempt)["exercise"])
            question = content.accept_question(
                tx,
                prompt=out.question.prompt,
                criteria=evidence.question_criteria(exercise, out.question),
                reference_response=out.question.reference_response,
                expected_seconds=out.question.expected_seconds,
                basis=exercise["ref"],
                authoring=operation,
                protocol=evidence.ASSESS_PROTOCOL,
            )
        practice.reconcile(
            tx,
            attempt=attempt,
            assessment=accepted["assessment"],
            results=accepted["labels"],
            out=out,
            question=question,
        )
        return [accepted["assessment"], *([question] if question else [])]

    def _accept_teaching(
        self, tx: Tx, operation: JSON, op: OperationP, result: ProviderResult
    ) -> JSON:
        ctx = op.input_snapshot["context"]
        return content.accept_teaching(
            tx,
            draft=content.TeachingDraft.model_validate(result.output.model_dump()),
            prior=ctx["prior"],
            concern=ctx["concern"],
            scope=ctx["scope"],
            source=ctx["source"],
            supporting_claims=ctx["supporting_claims"],
            authoring=operation,
        )

    def retry_operation(self, request_id: str, operation_id: str) -> JSON:
        """Explicitly retry a failed, interrupted or refused operation in its request group."""

        def fn(tx: Tx) -> JSON:
            op = OperationP.model_validate(tx.require("operation", operation_id, by=OWNER).payload)
            if op.status not in ("failed", "interrupted") and op.acceptance != "rejected":
                msg = "only a failed, interrupted or refused operation can be retried"
                raise ValueError(msg)
            if _group_accepted(tx, op.request_group):
                msg = "this request was already accepted; there is nothing to retry"
                raise ValueError(msg)
            new = self._new_operation(
                tx,
                purpose=op.purpose,
                intent=op.intent,
                inputs=[i.model_dump() for i in op.inputs],
                request=_saved_request(op.input_snapshot),
                context=op.input_snapshot["context"],
                group=op.request_group,
                try_index=op.try_index,
            )
            return {"operation": new}

        return self.store.run(request_id, "retry_operation", {"operation": operation_id}, fn).result

    # --- material and outline ------------------------------------------------------

    def add_material(self, request_id: str, *, title: str, text: str, purpose: str | None) -> JSON:
        """Save new text and a pending drafting operation; call ``run_operation`` next."""
        if not text.strip() or not title.strip():
            msg = "material needs a title and some text"
            raise ValueError(msg)

        def fn(tx: Tx) -> JSON:
            source = content.add_source(tx, title=title, text=text, origin=None)
            existing = content.existing_claims(tx)
            request = content.draft_request(
                source_title=title, source_text=text, purpose=purpose, existing=existing
            )
            op = self._new_operation(
                tx,
                purpose="draft_material",
                intent="initial_outline",
                inputs=[source],
                request=request,
                context={
                    "purpose_given": bool(purpose),
                    "existing": {key: claim["ref"] for key, claim in existing.items()},
                },
            )
            return {"source": source, "operation": op}

        inputs = {"title": title, "text": text, "purpose": purpose}
        return self.store.run(request_id, "add_material", inputs, fn).result

    def accept_material(
        self, request_id: str, *, operation_id: str, decisions: dict[str, str]
    ) -> JSON:
        """Accept a reviewed outline with the learner's reuse decisions."""

        def fn(tx: Tx) -> JSON:
            record = tx.require("operation", operation_id, by=OWNER)
            op = OperationP.model_validate(record.payload)
            waiting = (op.intent, op.status, op.acceptance) == (
                "initial_outline",
                "succeeded",
                "pending",
            )
            if not waiting:
                msg = "this outline is not waiting for a review"
                raise ValueError(msg)
            if not self._inputs_current(tx, op):
                msg = "its source changed after it was drafted"
                raise Conflict(msg)
            draft = content.DraftOutline.model_validate_json(op.raw_response or "")
            outputs = _accept_outline(tx, record.ref, op, draft, decisions)
            _decide(
                tx,
                record,
                op,
                acceptance="accepted",
                acceptance_reason="reviewed by the learner",
                outputs=[content.RefP(**o) for o in outputs],
            )
            return {"curriculum": outputs[0], "operation": record.ref}

        inputs = {"operation": operation_id, "decisions": decisions}
        return self.store.run(request_id, "accept_material", inputs, fn).result

    def edit_outline(  # noqa: PLR0913 - one keyword per edited field
        self,
        request_id: str,
        *,
        curriculum_id: str,
        base: int,
        title: str,
        purpose: str,
        sections: list[JSON],
    ) -> JSON:
        """Revise the outline's organization (titles, purpose, order)."""

        def fn(tx: Tx) -> JSON:
            revised = content.edit_outline(
                tx,
                curriculum_id=curriculum_id,
                base=base,
                title=title,
                purpose=purpose,
                sections=sections,
            )
            return {"curriculum": revised}

        inputs = {
            "curriculum_id": curriculum_id,
            "base": base,
            "title": title,
            "purpose": purpose,
            "sections": sections,
        }
        return self.store.run(request_id, "edit_outline", inputs, fn).result

    def revise_target(  # noqa: PLR0913 - one keyword per edited field
        self,
        request_id: str,
        *,
        target_id: str,
        base: int,
        action: str,
        mode: str,
        conditions: list[str],
        requirements: list[JSON],
        reason: str,
    ) -> JSON:
        """Change a goal after practice: a new revision, selected wherever the old one was."""

        def fn(tx: Tx) -> JSON:
            changed = content.revise_target(
                tx,
                target_id=target_id,
                base=base,
                action=action,
                mode=mode,
                conditions=conditions,
                requirements=requirements,
                reason=reason,
            )
            transition = _change_content(tx, changed, scope=[changed["target"]], reason=reason)
            return {
                "target": changed["target"],
                "mapping": changed["mapping"],
                "transition": transition,
            }

        inputs = {
            "target": target_id,
            "base": base,
            "action": action,
            "mode": mode,
            "conditions": conditions,
            "requirements": requirements,
            "reason": reason,
        }
        return self.store.run(request_id, "revise_target", inputs, fn).result

    def flag_material(self, request_id: str, *, knowledge_id: str, base: int, reason: str) -> JSON:
        """Flag a claim as wrong: what rests on it is held, everything else continues."""
        return self.store.run(
            request_id,
            "flag_material",
            {"knowledge": knowledge_id, "base": base, "reason": reason},
            lambda tx: {
                "knowledge": content.flag_knowledge(
                    tx, knowledge_id=knowledge_id, base=base, reason=reason
                )
            },
        ).result

    def revise_material(  # noqa: PLR0913 - one keyword per edited field
        self,
        request_id: str,
        *,
        knowledge_id: str,
        base: int,
        statement: str,
        scope: str,
        reason: str,
    ) -> JSON:
        """Keep a flagged claim as it is, or correct it (a meaning change for its goals)."""

        def fn(tx: Tx) -> JSON:
            changed = content.revise_knowledge(
                tx,
                knowledge_id=knowledge_id,
                base=base,
                statement=statement,
                scope=scope,
                reason=reason,
            )
            transition = _change_content(tx, changed, scope=[changed["knowledge"]], reason=reason)
            return {"knowledge": changed["knowledge"], "transition": transition}

        inputs = {
            "knowledge": knowledge_id,
            "base": base,
            "statement": statement,
            "scope": scope,
            "reason": reason,
        }
        return self.store.run(request_id, "revise_material", inputs, fn).result

    def rebind_exercise(self, request_id: str, *, exercise_id: str, base: int) -> JSON:
        """Confirm that a held exercise still checks the edited goals it covers."""
        return self.store.run(
            request_id,
            "rebind_exercise",
            {"exercise": exercise_id, "base": base},
            lambda tx: {
                "exercise": content.rebind_exercise(tx, exercise_id=exercise_id, base=base)
            },
        ).result

    # --- corrections of judgments -----------------------------------------------------

    def dispute_judgment(self, request_id: str, *, attempt_id: str, reason: str) -> JSON:
        """Ask for a review of an accepted judgment ("this judgment is wrong").

        A self-report is a claim to check: it saves a reassessment of the original
        answer; nothing changes until the learner accepts the reviewed judgment.
        """
        if not reason.strip():
            msg = "say why the judgment looks wrong"
            raise ValueError(msg)

        def fn(tx: Tx) -> JSON:
            attempt = evidence.attempt_view(tx, attempt_id=attempt_id)
            if not evidence.disputable(attempt):
                raise ValueError(evidence.NOT_DISPUTABLE)
            graded = evidence.assessment_for(tx, attempt_id)
            if graded is None:
                msg = "this answer has no judgment yet"
                raise ValueError(msg)
            live = [
                o
                for o in _operations(tx)
                if o["inputs"]
                and o["inputs"][0]["id"] == graded["ref"]["id"]
                and o["acceptance"] == "pending"
            ]
            if live:
                msg = "this judgment is already being reviewed"
                raise ValueError(msg)
            op = self._new_operation(
                tx,
                purpose="assess_answer",
                intent=None,
                inputs=[graded["ref"]],
                request=evidence.reassessment_request(tx, graded["ref"], reason.strip()),
                context={"reason": reason.strip(), "attempt": attempt["ref"]},
            )
            return {"operation": op}

        inputs = {"attempt": attempt_id, "reason": reason}
        return self.store.run(request_id, "dispute_judgment", inputs, fn).result

    def _reviewed(self, tx: Tx, operation_id: str) -> tuple[Record, OperationP]:
        """Return a waiting review whose judgment is still the current one."""
        record, op = _waiting_review(tx, operation_id)
        if not self._inputs_current(tx, op):
            msg = "the judgment changed after this review started"
            raise Conflict(msg)
        return record, op

    def _apply_correction(self, tx: Tx, record: Record, op: OperationP) -> JSON:
        """Accept a reviewed judgment: one revision, rebuilt evidence, replayed needs."""
        out = evidence.AssessmentOutput.model_validate_json(op.raw_response or "")
        reason = op.input_snapshot["context"]["reason"]
        attempt = op.input_snapshot["context"]["attempt"]
        answered = op.answered_by or op.model.name  # the model that actually answered
        corrected = evidence.revise_assessment(
            tx,
            assessment=op.inputs[0].model_dump(),
            out=out,
            assessor=op.model.model_copy(
                update={"name": answered, "version": answered}
            ).model_dump(),
            raw_response=op.raw_response or "",
            reason=reason,
        )
        practice.reconcile_correction(
            tx,
            attempt=attempt,
            assessment=corrected["assessment"],
            results=corrected["labels"],
            out=out,
        )
        transition = _transition(
            tx,
            category="assessment",
            scope=[attempt, corrected["assessment"]],
            actor=f"learner request, reviewed by {op.model.name}",
            reason=reason,
        )
        _decide(
            tx,
            record,
            op,
            acceptance="accepted",
            acceptance_reason="accepted by the learner",
            outputs=[content.RefP(**corrected["assessment"])],
        )
        return {"assessment": corrected["assessment"], "transition": transition}

    def accept_correction(
        self, request_id: str, *, operation_id: str, preview: str | None = None
    ) -> JSON:
        """Accept the reviewed judgment and recompute what depends on it, atomically.

        ``preview`` is the digest the preview showed; when given, the accepted effect must
        be exactly that one, or nothing is written and the preview must be looked at again.
        """

        def fn(tx: Tx) -> JSON:
            record, op = self._reviewed(tx, operation_id)
            applied = self._apply_correction(tx, record, op)
            after = _correction_state(tx, op.input_snapshot["context"]["attempt"])
            if preview is not None and digest(after) != preview:
                msg = "the effect of this correction changed since its preview; look at it again"
                raise Conflict(msg)
            return applied

        inputs = {"operation": operation_id, "preview": preview}
        return self.store.run(request_id, "accept_correction", inputs, fn).result

    def keep_judgment(self, request_id: str, *, operation_id: str) -> JSON:
        """Keep the original judgment; the review stays on record and changes nothing."""

        def fn(tx: Tx) -> JSON:
            record, op = _waiting_review(tx, operation_id)
            kept = _decide(
                tx,
                record,
                op,
                acceptance="cancelled",
                acceptance_reason="kept the original judgment",
            )
            return {"operation": _op_state(tx.at(kept, by=OWNER).view)}

        return self.store.run(request_id, "keep_judgment", {"operation": operation_id}, fn).result

    def correction_preview(self, operation_id: str) -> JSON:
        """Show exactly what accepting a reviewed judgment would change, writing nothing.

        ponytail: a dry run of the real correction inside a rolled-back savepoint, so the
        preview cannot drift from the effect; it takes the write lock for that moment.
        """

        def fn(tx: Tx) -> JSON:
            record, op = self._reviewed(tx, operation_id)
            attempt = op.input_snapshot["context"]["attempt"]
            before = _correction_state(tx, attempt)

            def apply_then_roll_back() -> None:
                self._apply_correction(tx, record, op)
                raise _Preview(_correction_state(tx, attempt))

            try:
                with tx.savepoint():
                    apply_then_roll_back()
            except _Preview as preview:
                return {"before": before, "after": preview.args[0]}
            msg = "the dry run did not finish"  # pragma: no cover - apply always raises
            raise AssertionError(msg)

        states = self.store.run(new_id(), "preview_correction", {"operation": operation_id}, fn)
        after = states.result["after"]
        return {**_compare(states.result["before"], after), "digest": digest(after)}

    # --- practice ------------------------------------------------------------------

    def start_session(
        self,
        request_id: str,
        *,
        curriculum_id: str | None = None,
        curriculum_ids: list[str] | None = None,
        budget_seconds: int | None = None,
    ) -> JSON:
        """Open a session over one or more curricula, in that order, with an optional budget."""
        chosen = curriculum_ids or ([curriculum_id] if curriculum_id else [])

        def fn(tx: Tx) -> JSON:
            enrollments: list[str] = []
            for cid in chosen:
                enrollment = practice.enrollment_for(tx, cid)
                if enrollment is None:
                    msg = "this curriculum has no enrollment yet"
                    raise LookupError(msg)
                enrollments.append(enrollment["ref"]["id"])
            session = practice.start_session(
                tx, enrollment_ids=enrollments, budget_seconds=budget_seconds
            )
            return {"session": session}

        inputs = {"curricula": chosen, "budget": budget_seconds}
        return self.store.run(request_id, "start_session", inputs, fn).result

    def change_budget(
        self, request_id: str, *, session_id: str, base: int, budget_seconds: int | None
    ) -> JSON:
        """Change how long this session may run; the time already spent stays as it was."""
        return self.store.run(
            request_id,
            "change_budget",
            {"session": session_id, "base": base, "budget": budget_seconds},
            lambda tx: {
                "session": practice.change_budget(
                    tx, session_id=session_id, base=base, budget_seconds=budget_seconds
                )
            },
        ).result

    def next_exercise(
        self,
        request_id: str,
        *,
        session_id: str,
        exercise_id: str | None = None,
        new_material: bool = False,
    ) -> JSON:
        """Take the session's next step: resume, ask, teach, verify, or a new exercise.

        Teaching and fresh variants are authored before delivery: when none is ready,
        this saves a pending authoring operation (``operation``) for ``run_operation``.
        ``exercise_id`` or ``new_material`` is the learner's own choice (an override).
        """

        def fn(tx: Tx) -> JSON:
            step = practice.next_step(
                tx,
                session_id,
                elapsed_ms=measurement.session_elapsed_ms(tx, session_id),
                exercise_id=exercise_id,
                new_material=new_material,
            )
            nothing: JSON = {"attempt": None, "offer": None, "resumed": False}
            kind = step["kind"]
            if kind == "resume":
                attempt = evidence.attempt_view(tx, step["offer"]["attempt"])
                return {
                    **nothing,
                    "kind": _attempt_kind(attempt),
                    "attempt": step["offer"]["attempt"],
                    "offer": step["offer"]["ref"],
                    "resumed": True,
                }
            if kind in ("none", "stopped", "pending", "study", "budget_spent", "nothing_fits"):
                left = [
                    {**x, "action": content.definition(tx, x["target"])["action"]}
                    for x in step.get("left", [])
                ]
                return {**nothing, **step, "left": left}
            if kind in ("teach", "verify"):
                serve = self._teach if kind == "teach" else self._verify
                return {
                    **nothing,
                    "concern": step["concern"],
                    **serve(tx, session_id, step["concern"]),
                }
            session = practice.session_view(tx, session_id)
            exercise = step["exercise"]
            if kind == "ask":
                return {**nothing, **_ask(tx, session, exercise, step["concern"])}
            attempt = evidence.start_attempt(tx, session=session["ref"], exercise=exercise["ref"])
            offer = practice.deliver(
                tx,
                session_id=session_id,
                exercise=exercise,
                attempt=attempt,
                reason=step["reason"],
                selection=step["selection"],
            )
            delivered = practice.offer_for(tx, attempt["id"])
            assert delivered is not None  # noqa: S101 - just reserved
            measurement.assign_endpoints(tx, offer=delivered, exercise=exercise)
            return {**nothing, "kind": "exercise", "attempt": attempt, "offer": offer}

        inputs = {"session": session_id, "exercise": exercise_id, "new": new_material}
        return self.store.run(request_id, "next_exercise", inputs, fn).result

    def _teach(self, tx: Tx, session_id: str, concern: JSON) -> JSON:
        """Deliver accepted teaching for this concern revision, or author it first."""
        for taught in content.teachings(tx):
            if taught["concern"] != concern["ref"]:
                continue
            study = next(
                (s for s in evidence.studies(tx) if s["teaching"]["id"] == taught["ref"]["id"]),
                None,
            )
            if study is None:
                session = practice.session_view(tx, session_id)["ref"]
                return {
                    "kind": "study",
                    "study": evidence.start_study(
                        tx, session=session, teaching=taught, concern=concern["ref"]
                    ),
                }
            return {"kind": "study", "study": study["ref"]}
        return self._authoring(tx, "teaching_intervention", concern, _teaching_packet)

    def _authoring(
        self,
        tx: Tx,
        intent: Literal["teaching_intervention", "exercise_variant"],
        concern: JSON,
        packet: Callable[[Tx, JSON], tuple[ModelRequest, JSON]],
    ) -> JSON:
        """Report the authoring request for this exact concern revision, saving it if new.

        After two refused tries (or a failure) it is not ready; only an explicit retry
        or a changed concern makes a new request.
        """
        ops = [
            o for o in _operations(tx) if o["intent"] == intent and o["inputs"][0] == concern["ref"]
        ]
        if ops:
            latest = ops[-1]
            live = latest["status"] in ("pending", "running")
            return {"kind": "preparing" if live else "not_ready", "operation": _op_state(latest)}
        request, context = packet(tx, concern)
        saved = self._new_operation(
            tx,
            purpose="draft_material",
            intent=intent,
            inputs=[concern["ref"]],
            request=request,
            context=context,
        )
        return {"kind": "preparing", "operation": _op_state(tx.at(saved, by=OWNER).view)}

    def complete_study(
        self, request_id: str, *, study_id: str, base: int, client_at: str | None
    ) -> JSON:
        """Record that the learner worked through the teaching; repair moves to a fresh check."""

        def fn(tx: Tx) -> JSON:
            before = evidence.study_view(tx, study_id)
            if before["status"] == "completed":
                return {"study": before["ref"]}
            done = evidence.complete_study(
                tx, study_id=study_id, base=base, raw_client_at=client_at
            )
            if before["concern"]:
                practice.after_study(tx, study=evidence.study_view(tx, study_id))
            return {"study": done}

        inputs = {"study": study_id, "base": base}
        return self.store.run(request_id, "complete_study", inputs, fn).result

    def pause_concern(self, request_id: str, *, concern_id: str, base: int) -> JSON:
        """Pause a concern at the learner's request; its evidence and counts are kept."""
        return self.store.run(
            request_id,
            "pause_concern",
            {"concern": concern_id, "base": base},
            lambda tx: {"concern": practice.pause_concern(tx, concern_id=concern_id, base=base)},
        ).result

    def _verify(self, tx: Tx, session_id: str, concern: JSON) -> JSON:
        """Deliver the accepted fresh variant bound to this repair cycle, or author it."""
        accepted = [
            o
            for o in _operations(tx)
            if o["intent"] == "exercise_variant"
            and o["inputs"][0] == concern["ref"]
            and o["acceptance"] == "accepted"
        ]
        if not accepted:
            return self._authoring(tx, "exercise_variant", concern, _variant_packet)
        exercise = content.definition(tx, accepted[-1]["outputs"][0])
        cycle = concern["cycles"][-1]
        session = practice.session_view(tx, session_id)
        attempt = evidence.start_attempt(
            tx,
            session=session["ref"],
            exercise=exercise["ref"],
            purpose="verification",
            concern=concern["ref"],
            follows=concern["origin"],
            verification_of={
                "concern": concern["ref"],
                "cycle_id": cycle["id"],
                "studies": cycle["studies"],
                "scope": concern["scope"],
            },
        )
        offer = practice.deliver(
            tx,
            session_id=session_id,
            exercise=exercise,
            attempt=attempt,
            role="extra",
            reason="a fresh check of the repaired part after completed teaching",
            policy=practice.REPAIR_POLICY,
        )
        return {"kind": "verification", "attempt": attempt, "offer": offer}

    def save_draft(self, request_id: str, *, attempt_id: str, base: int, response: str) -> JSON:
        """Save the learner's unfinished answer."""
        return self.store.run(
            request_id,
            "save_draft",
            {"attempt": attempt_id, "base": base, "response": response},
            lambda tx: {
                "attempt": evidence.save_draft(
                    tx, attempt_id=attempt_id, base=base, response=response
                )
            },
        ).result

    def reveal_hint(self, request_id: str, *, attempt_id: str, hint_id: str) -> JSON:
        """Send a hint for display; it counts as help once the display is acknowledged."""

        def fn(tx: Tx) -> JSON:
            exposure, hint = evidence.reveal_hint(tx, attempt_id=attempt_id, hint_id=hint_id)
            return {"exposure": exposure, "hint": hint}

        return self.store.run(
            request_id, "reveal_hint", {"attempt": attempt_id, "hint": hint_id}, fn
        ).result

    def acknowledge_hint(
        self, request_id: str, *, attempt_id: str, base: int, hint_id: str, client_at: str | None
    ) -> JSON:
        """Record that the hint was displayed during this answer."""
        return self.store.run(
            request_id,
            "acknowledge_hint",
            {"attempt": attempt_id, "base": base, "hint": hint_id},
            lambda tx: {
                "attempt": evidence.acknowledge_hint(
                    tx, attempt_id=attempt_id, base=base, hint_id=hint_id, raw_client_at=client_at
                )
            },
        ).result

    def submit_answer(
        self, request_id: str, *, attempt_id: str, base: int, response: str, client_at: str | None
    ) -> JSON:
        """Save the answer, the submitted offer and a pending assessment in one command."""

        def fn(tx: Tx) -> JSON:
            attempt = evidence.submit(
                tx, attempt_id=attempt_id, base=base, response=response, raw_client_at=client_at
            )
            practice.mark_submitted(tx, attempt_id=attempt_id)
            op = self._new_operation(
                tx,
                purpose="assess_answer",
                intent=None,
                inputs=[attempt],
                request=evidence.assessment_request_for(tx, attempt),
                context={},
            )
            return {"attempt": attempt, "operation": op}

        inputs = {"attempt": attempt_id, "base": base, "response": response}
        return self.store.run(request_id, "submit_answer", inputs, fn).result

    def view_feedback(self, request_id: str, *, attempt_id: str) -> JSON:
        """Record that the learner was shown feedback and the reference answer.

        Seeing the answer defers the next offer of a later check for its goals.
        """

        def fn(tx: Tx) -> JSON:
            exposure = evidence.record_feedback_view(tx, attempt_id=attempt_id)
            _exposed(tx, exposure)
            return {"exposure": exposure}

        return self.store.run(request_id, "view_feedback", {"attempt": attempt_id}, fn).result

    def read_material(self, request_id: str, *, targets: list[JSON], what: str) -> JSON:
        """Record that answer-bearing material (claims or source text) was opened."""

        def fn(tx: Tx) -> JSON:
            exposure = evidence.record_material_view(tx, targets=targets, what=what)
            _exposed(tx, exposure)
            return {"exposure": exposure}

        inputs = {"targets": targets, "what": what}
        return self.store.run(request_id, "read_material", inputs, fn).result

    def rate_recall(self, request_id: str, *, attempt_id: str, target: JSON, choice: str) -> JSON:
        """Save the learner's recall rating of an owned answer; FSRS dates the next review."""

        def fn(tx: Tx) -> JSON:
            assessment = evidence.assessment_for(tx, attempt_id)
            if assessment is None:
                msg = "this answer cannot be rated: it is not graded yet"
                raise ValueError(msg)
            offer = practice.review_binding(
                tx,
                attempt_id=attempt_id,
                target=target,
                choice=choice,
                under_review=_under_review(tx, assessment),
            )
            attempt = evidence.attempt_view(tx, attempt_id=attempt_id)["ref"]
            saved = evidence.record_review(
                tx,
                attempt=attempt,
                target=target,
                offer=offer["ref"],
                assessment=assessment["ref"],
                choice=choice,
            )
            practice.recompute_schedule(tx, target, basis=[saved])
            return {"review": saved}

        inputs = {"attempt": attempt_id, "target": target, "choice": choice}
        return self.store.run(request_id, "rate_recall", inputs, fn).result

    def confirm_closed(self, request_id: str, *, targets: list[JSON]) -> JSON:
        """Start later checks of these goals from now: earlier views are confirmed closed."""

        def fn(tx: Tx) -> JSON:
            checkpoint = evidence.confirm_closed(tx, targets=targets)
            if checkpoint is not None:
                for target in targets:
                    practice.recompute_schedule(tx, target, basis=[checkpoint])
            return {"checkpoint": checkpoint}

        return self.store.run(request_id, "confirm_closed", {"targets": targets}, fn).result

    def close_view(self, request_id: str, *, exposure_id: str) -> JSON:
        """Record that an answer-bearing view was closed; its wait starts from now."""

        def fn(tx: Tx) -> JSON:
            closed = evidence.close_exposure(tx, exposure_id=exposure_id)
            if closed is not None:
                _exposed(tx, closed)
            return {"exposure": closed}

        return self.store.run(request_id, "close_view", {"exposure": exposure_id}, fn).result

    def end_session(self, request_id: str, *, session_id: str, base: int, reason: str) -> JSON:
        """End a session, saving what it left unserved; an unfinished draft stays resumable."""

        def fn(tx: Tx) -> JSON:
            elapsed = measurement.session_elapsed_ms(tx, session_id)
            return {
                "session": practice.end_session(
                    tx, session_id=session_id, base=base, stop_reason=reason, elapsed_ms=elapsed
                )
            }

        inputs = {"session": session_id, "base": base, "reason": reason}
        return self.store.run(request_id, "end_session", inputs, fn).result

    # --- measurement -----------------------------------------------------------------

    def open_timer(self, request_id: str, *, document_run_id: str, takeover: bool) -> JSON:
        """Grant this browser tab the timer (``Conflict`` if another tab holds it)."""
        return self.store.run(
            request_id,
            "open_timer",
            {"document": document_run_id, "takeover": takeover},
            lambda tx: {
                "run": measurement.open_run(
                    tx,
                    activation_id=self.activation_id,
                    document_run_id=document_run_id,
                    takeover=takeover,
                )
            },
        ).result

    def record_spans(self, request_id: str, *, spans: list[JSON]) -> JSON:
        """Accept a batch of browser spans; spans already saved are skipped."""

        def fn(tx: Tx) -> JSON:
            refs: list[JSON] = []
            rejected: list[str] = []
            for s in spans:
                saved = measurement.record_span(tx, activation_id=self.activation_id, span=s)
                if saved is None:
                    rejected.append(s["id"])
                else:
                    refs.append(saved)
            holds = all(
                measurement.holds_timer(tx, run_id=s["run_id"], activation_id=self.activation_id)
                for s in spans
                if s["id"] not in rejected
            )
            return {"spans": refs, "rejected": rejected, "holds_timer": holds}

        return self.store.run(request_id, "record_spans", {"spans": spans}, fn).result

    def start_tracking(self, request_id: str, *, curriculum_id: str) -> JSON:
        """Freeze a tracking plan over this curriculum's admitted goals (one command)."""

        def fn(tx: Tx) -> JSON:
            curriculum, enrollment = _tracked(tx, curriculum_id)
            return {
                "cohort": measurement.start_tracking(
                    tx, curriculum=curriculum["ref"], enrollment=enrollment
                )
            }

        return self.store.run(
            request_id, "start_tracking", {"curriculum": curriculum_id}, fn
        ).result

    def stop_tracking(self, request_id: str, *, cohort_id: str, base: int, reason: str) -> JSON:
        """Stop a tracking plan; its frozen endpoints stay, later ones become missing."""
        return self.store.run(
            request_id,
            "stop_tracking",
            {"cohort": cohort_id, "base": base, "reason": reason},
            lambda tx: {
                "cohort": measurement.stop_tracking(
                    tx, cohort_id=cohort_id, base=base, reason=reason
                )
            },
        ).result

    def session_feedback(
        self,
        request_id: str,
        *,
        session_id: str,
        effort: str | None,
        usefulness: str | None,
        note: str | None,
    ) -> JSON:
        """Save optional end-of-session ratings."""

        def fn(tx: Tx) -> JSON:
            session = practice.session_view(tx, session_id)["ref"]
            return {
                "feedback": measurement.save_feedback(
                    tx, session=session, effort=effort, usefulness=usefulness, note=note
                )
            }

        inputs = {"session": session_id, "effort": effort, "usefulness": usefulness, "note": note}
        return self.store.run(request_id, "session_feedback", inputs, fn).result

    # --- export and restore ------------------------------------------------------------

    def export(self) -> JSON:
        """Export the whole library as one portable archive."""
        return export_library(self.store, writer_release=RELEASE)

    @staticmethod
    def restore(path: Path, text: str, *, clock: Clock) -> Store:
        """Restore an archive into a new store file, validating every record first."""
        return restore_library(path, text, clock=clock, validate=validate_library)


# --- practice: parts of the commands above -----------------------------------------------


def _exposed(tx: Tx, exposure: JSON) -> None:
    """Let Practice re-derive the next offer of every goal an exposure revision names."""
    for target in evidence.exposure_view(tx, exposure)["targets"]:
        practice.recompute_schedule(tx, target, basis=[exposure])


# --- corrections: parts of the commands above -------------------------------------------


def _correction_state(tx: Tx, attempt: JSON) -> JSON:
    """Capture what a corrected judgment can change: criteria, targets, concerns."""
    view = evidence.attempt_view(tx, attempt)
    exercise = content.definition(tx, view["exercise"])
    graded = evidence.assessment_for(tx, attempt["id"])
    assert graded is not None  # noqa: S101 - only judged answers are reviewed
    results = {r["criterion_id"]: r for r in graded["results"]}
    misread = evidence.misread_criteria(graded)
    return {
        "explanation": graded["explanation"],
        "criteria": [
            {
                "id": c["id"],
                "requirement": c["requirement"],
                "outcome": results[c["id"]]["outcome"],
                "reason": results[c["id"]]["reason"],
                "misread": c["id"] in misread,
            }
            for c in exercise["criteria"]
        ],
        "targets": [
            {
                "ref": t,
                "action": content.definition(tx, t)["action"],
                "label": evidence.target_evidence(tx, t)["label"],
                "schedule": (
                    {k: s[k] for k in ("need", "due_at", "hold_reason")}
                    if (s := practice.schedule_view(tx, t))
                    else None
                ),
            }
            for t in exercise["targets"]
        ],
        "concerns": {
            c["ref"]["id"]: c
            for c in (practice.concern_view(tx, r) for r in practice.concern_ids_for(tx, attempt))
        },
    }


def _compare(before: JSON, after: JSON) -> JSON:
    """Pair each criterion, target and concern before and after a correction."""
    criteria = [
        {"id": b["id"], "requirement": b["requirement"], "before": b, "after": a}
        for b, a in zip(before["criteria"], after["criteria"], strict=True)
    ]
    targets = [
        {"ref": b["ref"], "action": b["action"], "before": b, "after": a}
        for b, a in zip(before["targets"], after["targets"], strict=True)
    ]
    concerns = [
        {"before": before["concerns"].get(cid), "after": c}
        for cid, c in after["concerns"].items()
        if before["concerns"].get(cid, {}).get("status") != c["status"]
        or before["concerns"].get(cid, {}).get("route") != c["route"]
        or before["concerns"].get(cid, {}).get("scope") != c["scope"]
    ]
    changed = any(c["before"] != c["after"] for c in criteria + targets) or bool(concerns)
    return {
        "explanation": after["explanation"],
        "criteria": criteria,
        "targets": targets,
        "concerns": concerns,
        "changes": changed,
    }


# --- material: parts of the commands above ---------------------------------------------


def _listed_claims(tx: Tx, op: OperationP) -> dict[str, JSON]:
    """Return each existing claim the drafting packet listed, as it stands now."""
    return content.listed_claims(tx, op.input_snapshot["context"].get("existing", {}))


def _accept_outline(
    tx: Tx, operation: JSON, op: OperationP, draft: content.DraftOutline, decisions: dict[str, str]
) -> list[JSON]:
    accepted = content.accept_draft(
        tx,
        source=op.inputs[0].model_dump(),
        draft=draft,
        authoring=operation,
        purpose_given=bool(op.input_snapshot["context"].get("purpose_given")),
        existing=_listed_claims(tx, op),
        decisions=decisions,
    )
    enrollment = practice.enroll(
        tx, curriculum=accepted["curriculum"], goal_order=accepted["targets"]
    )
    return [accepted["curriculum"], enrollment, *accepted["exercises"]]


# --- diagnosis and repair: parts of the commands above ------------------------------


def _ask(tx: Tx, session: JSON, exercise: JSON, concern: JSON) -> JSON:
    """Deliver a concern's clarification question as an extra, focused draft."""
    attempt = evidence.start_attempt(
        tx,
        session=session["ref"],
        exercise=exercise["ref"],
        purpose="clarification",
        concern=concern["ref"],
        follows=concern["origin"],
    )
    offer = practice.deliver(
        tx,
        session_id=session["ref"]["id"],
        exercise=exercise,
        attempt=attempt,
        role="extra",
        reason="a clarification question whose answer changes the help",
        policy=practice.REPAIR_POLICY,
    )
    return {"kind": "clarification", "attempt": attempt, "offer": offer}


def _concern_evidence(tx: Tx, concern: JSON) -> list[str]:
    """List the learner's own answers behind a concern, criterion by criterion."""
    lines: list[str] = []
    for basis in concern["basis"]:
        assessment = evidence.assessment_view(tx, basis)
        attempt = evidence.attempt_view(tx, assessment["attempt"])
        exercise = content.definition(tx, attempt["exercise"])
        requirement = {c["id"]: c["requirement"] for c in exercise["criteria"]}
        lines += [f"Task: {exercise['prompt']}", f"Answer: {attempt['response']}"]
        lines += [
            f"- {requirement[r['criterion_id']]}: {r['outcome'].replace('_', ' ')}. {r['reason']}"
            for r in assessment["results"]
        ]
    return lines


def _teaching_packet(tx: Tx, concern: JSON) -> tuple[ModelRequest, JSON]:
    """Gather the bounded teaching packet for a concern (lifecycle section 3)."""
    targets: list[JSON] = []
    claims: list[JSON] = []
    source: JSON | None = None
    for s in concern["scope"]:
        target = content.definition(tx, s["target"])
        knowledge = [content.definition(tx, k) for k in target["content"]]
        claims += target["content"]
        # ponytail: one source per curriculum today; gather several when reuse links sources.
        source = source or knowledge[0]["sources"][0]["source"]
        targets.append(
            {
                "action": target["action"],
                "mode": target["mode"],
                "requirements": [
                    r["statement"]
                    for r in target["evidence_requirements"]
                    if r["id"] in s["requirement_ids"]
                ],
                "knowledge": [k["statement"] for k in knowledge],
            }
        )
    assert source is not None  # noqa: S101 - accepted knowledge always quotes a source
    hypotheses = {h["key"]: f"{h['cause']} (help: {h['practice']})" for h in concern["hypotheses"]}
    failed = {
        s["id"] for c in concern["cycles"] if c["outcome"] == "unsuccessful" for s in c["studies"]
    }
    studied = {s["teaching"]["id"]: s["ref"]["id"] for s in evidence.studies(tx)}
    prior = [
        {
            "approach": t["approach"],
            "content": t["content"],
            "unsuccessful": studied.get(t["ref"]["id"]) in failed,
        }
        for t in content.teachings(tx)
        if t["concern"] and t["concern"]["id"] == concern["ref"]["id"]
    ]
    text = content.definition(tx, source)
    request = content.teaching_request(
        source_title=text["title"],
        source_text=text["text"],
        targets=targets,
        evidence=_concern_evidence(tx, concern),
        focus=hypotheses[concern["focus"]] if concern["help"] == "supported" else None,
        alternatives=list(hypotheses.values()) if concern["help"] == "uncertain" else [],
        prior=prior,
    )
    context = {
        "concern": concern["ref"],
        "scope": concern["scope"],
        "source": source,
        "supporting_claims": claims,
        "prior": [p for p in prior if p["unsuccessful"]],
    }
    return request, context


def _variant_packet(tx: Tx, concern: JSON) -> tuple[ModelRequest, JSON]:
    """Gather what the variant request needs: the earlier task and the teaching given."""
    basis = evidence.attempt_view(tx, concern["origin"])["exercise"]
    studies = {s["ref"]["id"]: s["content"] for s in evidence.studies(tx)}
    request = content.variant_request(
        tx,
        basis=basis,
        scope=concern["scope"],
        teaching=[studies[s["id"]] for s in concern["cycles"][-1]["studies"]],
    )
    return request, {"concern": concern["ref"], "basis": basis}


def _accept_variant(tx: Tx, operation: JSON, op: OperationP, result: ProviderResult) -> JSON:
    return content.accept_variant(
        tx,
        draft=content.VariantDraft.model_validate(result.output.model_dump()),
        basis=op.input_snapshot["context"]["basis"],
        authoring=operation,
    )


def _attempt_kind(attempt: JSON) -> str:
    return {"clarification": "clarification", "verification": "verification"}.get(
        attempt["purpose"], "exercise"
    )


# --- the selected provider: Anthropic --------------------------------------------------


class AnthropicProvider:
    """Claude via the Anthropic API, with schema-constrained output.

    Credentials come from the environment (``ANTHROPIC_API_KEY`` or an ``ant`` login).
    Server-side refusal fallback is on; the model that actually answered is recorded.
    """

    def __init__(
        self, model: str = "claude-opus-5-5", *, effort: str = "high", timeout_s: float = 300
    ) -> None:
        """Configure the model, effort and per-request timeout."""
        import anthropic  # noqa: PLC0415 - only the live provider needs the SDK loaded

        self._anthropic = anthropic
        # no automatic retries: a timeout waits for the learner's explicit retry
        self.client = anthropic.Anthropic(timeout=timeout_s, max_retries=0)
        self.model = model
        self.parameters: JSON = {"effort": effort, "max_tokens": 16000, "fallbacks": "default"}

    def complete(self, request: ModelRequest) -> ProviderResult:
        """Send the request and return its validated structured output."""
        errors = self._anthropic
        try:
            response = self.client.beta.messages.parse(
                model=self.model,
                max_tokens=self.parameters["max_tokens"],
                system=request.system,
                messages=[{"role": "user", "content": request.user}],
                output_format=request.output,
                output_config={"effort": self.parameters["effort"]},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
        except errors.APITimeoutError as e:
            raise ProviderError(kind="timeout", detail=str(e)) from e
        except (errors.APIConnectionError, errors.RateLimitError) as e:
            raise ProviderError(kind="unavailable", detail=str(e)) from e
        except errors.APIStatusError as e:
            raise ProviderError(kind="unavailable", detail=f"{e.status_code}: {e.message}") from e
        except ValidationError as e:
            raise ProviderError(kind="malformed", detail=str(e)) from e
        raw = "".join(getattr(b, "text", "") for b in response.content)
        if response.stop_reason == "refusal":
            raise ProviderError(kind="refused", detail="the model declined this request", raw=raw)
        if response.stop_reason == "max_tokens":
            raise ProviderError(
                kind="malformed", detail="the output was cut off at the token limit", raw=raw
            )
        if response.parsed_output is None:
            raise ProviderError(kind="malformed", detail="no structured output", raw=raw)
        return ProviderResult(output=response.parsed_output, raw=raw, model=response.model)


# --- opening the active store -----------------------------------------------------------


def open_app(data_dir: Path, provider: Provider, *, clock: Clock) -> App:
    """Open the active store (creating one on first use) and recover unfinished work."""
    data_dir.mkdir(parents=True, exist_ok=True)
    path = active_store(data_dir)
    if path is None:
        path = data_dir / f"library-{new_id()}.sqlite"
        Store.open(path, clock=clock).close()
        activate(data_dir, path)
    app = App(Store.open(path, clock=clock), provider)
    app.recover()
    return app


def restore_into(app: App, data_dir: Path, text: str, *, clock: Clock) -> None:
    """Restore an archive into a new store, make it active and switch the app to it."""
    path = data_dir / f"library-{new_id()}.sqlite"
    restored = App.restore(path, text, clock=clock)
    activate(data_dir, path)
    previous = app.store
    app.store = restored
    app.activation_id = new_id()  # a restored store grants no old timer authority
    previous.close()
    app.recover()


# --- page views (reads only: no records, no model calls) ----------------------------------


def _operations(tx: Tx) -> list[JSON]:
    return [r.view for r in tx.current("operation", by=OWNER)]


def _op_state(op: JSON) -> JSON:
    return {
        "id": op["ref"]["id"],
        "status": op["status"],
        "acceptance": op["acceptance"],
        "reason": op["acceptance_reason"] or op["error"],
        "try_index": op["try_index"],
    }


def _assessing(tx: Tx, attempt_id: str) -> JSON | None:
    ops = [
        o
        for o in _operations(tx)
        if o["purpose"] == "assess_answer" and o["inputs"][0]["id"] == attempt_id
    ]
    return _op_state(ops[-1]) if ops else None


def _due(tx: Tx, targets: list[JSON]) -> str | None:
    dues = [
        s["due_at"]
        for t in targets
        if (s := practice.schedule_view(tx, t)) is not None and s["due_at"] is not None
    ]
    return min(dues) if dues else None


def proposals_view(tx: Tx, operation_id: str) -> JSON:
    """Show how a drafted outline's claims relate to claims already in the library."""
    record = tx.require("operation", operation_id, by=OWNER)
    op = OperationP.model_validate(record.payload)
    draft = content.DraftOutline.model_validate_json(op.raw_response or "")
    existing = _listed_claims(tx, op)
    return {
        "operation": _op_state(record.view),
        "title": draft.title,
        "source": content.definition(tx, op.inputs[0].model_dump())["title"],
        "claims": [
            {
                "key": k.key,
                "statement": k.statement,
                "scope": k.scope,
                "quotes": k.quotes,
                "proposals": [
                    {
                        "relation": p.relation,
                        "why": p.why,
                        "existing": _claim_view(tx, existing[p.key]),
                    }
                    for p in k.existing
                ],
                "choices": content.reuse_choices(k.existing, existing),
            }
            for k in draft.knowledge
            if k.existing
        ],
    }


def home_view(tx: Tx) -> JSON:
    """List curricula with their state and due work, and material still being drafted."""
    accepted_groups = {o["request_group"] for o in _operations(tx) if o["acceptance"] == "accepted"}
    latest_by_group: dict[str, JSON] = {}
    for o in _operations(tx):
        if o["intent"] == "initial_outline" and o["request_group"] not in accepted_groups:
            latest_by_group[o["request_group"]] = o
    drafting = [
        {"source": content.definition(tx, o["inputs"][0])["title"], "operation": _op_state(o)}
        for o in latest_by_group.values()
    ]
    items: list[JSON] = []
    for c in content.curricula(tx):
        enrollment = practice.enrollment_for(tx, c["ref"]["id"])
        goals: list[JSON] = enrollment["goal_order"] if enrollment else []
        due = _due_work(tx, enrollment)
        items.append(
            {
                "id": c["ref"]["id"],
                "title": c["title"],
                "purpose": c["purpose"],
                "goals": len(goals),
                "started": sum(
                    1 for e in (enrollment or {}).get("practice", []) if e["state"] != "unstarted"
                ),
                "next_check": _due(tx, goals),
                **due,
            }
        )
    return {
        "curricula": items,
        "drafting": drafting,
        "due": {
            "checks": sum(i["due_now"] for i in items),
            "repairs": sum(i["repairs"] for i in items),
            "blocked": sum(i["blocked"] for i in items),
            "curricula": [i["id"] for i in items if i["due_now"] or i["repairs"] or i["blocked"]],
            "oldest": min((i["oldest"] for i in items if i["oldest"]), default=None),
        },
        "now": tx.now,
        "effort": measurement.ledger(measurement.all_spans(tx)),
    }


def _due_work(tx: Tx, enrollment: JSON | None) -> JSON:
    """Count what is ready in one enrollment now (shown when the app opens)."""
    if enrollment is None:
        return {"due_now": 0, "repairs": 0, "blocked": 0, "oldest": None}
    preview = practice.proposal(tx, [enrollment["ref"]], None)
    return {
        "due_now": preview["ready"],
        "repairs": preview["repairs"],
        "blocked": len(preview["blocked"]),
        "oldest": preview["oldest"],
    }


def _reason(hold: content.Hold | None) -> str | None:
    return hold.reason if hold else None


def _claim_view(tx: Tx, claim: JSON) -> JSON:
    """Show a claim as it stands now (its current revision, flag included)."""
    current = content.current_definition(tx, "knowledge", claim["ref"]["id"]) or claim
    return {
        "ref": current["ref"],
        "form": current["form"],
        "statement": current["statement"],
        "scope": current["scope"],
        "quotes": [p["quote"] for p in current["sources"]],
        "status": current["status"],
        "dispute": current.get("dispute"),
    }


def _target_view(tx: Tx, target: JSON, enrollment: JSON | None) -> JSON:
    definition = content.definition(tx, target)
    knowledge = {k["id"]: content.definition(tx, k) for k in definition["content"]}
    entry = next(
        (e for e in (enrollment or {}).get("practice", []) if e["target"] == target),
        None,
    )
    schedule = practice.schedule_view(tx, target)
    result = evidence.target_evidence(tx, target)
    return {
        "ref": target,
        "action": definition["action"],
        "mode": definition["mode"],
        "conditions": definition["conditions"],
        "requirements": [
            {"id": r["id"], "statement": r["statement"]}
            for r in definition["evidence_requirements"]
        ],
        "knowledge": [_claim_view(tx, k) for k in knowledge.values()],
        "hold": _reason(content.target_hold(tx, target)),
        "state": entry["state"] if entry else "not selected",
        "evidence": {"label": result["label"], "reasons": result["reasons"]},
        "schedule": {
            "type": schedule["type"],
            "need": schedule["need"],
            "hold_reason": schedule["hold_reason"],
            "due_at": schedule["due_at"],
            "next_offer": {k: schedule["next_offer"][k] for k in ("at", "reason")}
            if schedule.get("next_offer")
            else None,
        }
        if schedule
        else None,
    }


def _curriculum_effort(tx: Tx, curriculum: JSON, enrollment: JSON | None) -> JSON:
    """Ask Measurement for a curriculum's effort, naming its preparation records."""
    authoring = {
        o["ref"]["id"]
        for o in _operations(tx)
        if o["purpose"] == "draft_material" and o["inputs"][0]["id"] == curriculum["source"]["id"]
    }
    return measurement.curriculum_effort(
        tx,
        enrollment_id=enrollment["ref"]["id"] if enrollment else None,
        preparation_ids={curriculum["ref"]["id"], curriculum["source"]["id"], *authoring},
    )


def _tracked(tx: Tx, curriculum_id: str) -> tuple[JSON, JSON]:
    curriculum = content.current_definition(tx, "curriculum", curriculum_id)
    enrollment = practice.enrollment_for(tx, curriculum_id)
    if curriculum is None or enrollment is None:
        msg = f"no curriculum {curriculum_id}"
        raise LookupError(msg)
    return curriculum, enrollment


def tracking_preview_view(tx: Tx, curriculum_id: str) -> JSON:
    """Preview a tracking plan: its goals, baselines, windows and known checks."""
    curriculum, enrollment = _tracked(tx, curriculum_id)
    preview = measurement.tracking_preview(tx, curriculum=curriculum["ref"], enrollment=enrollment)
    for group in ("population", "outside"):
        for row in preview[group]:
            row["action"] = content.definition(tx, row["target"])["action"]
    plans = measurement.cohorts(tx, enrollment["ref"]["id"])
    return {
        **preview,
        "title": curriculum["title"],
        "plans": [
            {"id": p["ref"]["id"], "lifecycle": p["lifecycle"], "frozen_at": p["frozen_at"]}
            for p in plans
        ],
    }


def tracking_view(tx: Tx, cohort_id: str) -> JSON:
    """Report a tracking plan as of now, with each goal's action."""
    report = measurement.tracking_report(tx, cohort_id)
    actions = {
        m["target"]["id"]: content.definition(tx, m["target"])["action"]
        for m in report["population"]
    }
    enrollment = practice.enrollment_for(tx, report["curriculum"]["id"])
    tracked = {m["target"]["id"] for m in report["population"]} | {
        o["target"]["id"] for o in report["outside"]
    }
    return {
        **report,
        "actions": actions,
        "added": [
            {"target": t, "action": content.definition(tx, t)["action"]}
            for t in (enrollment or {}).get("goal_order", [])
            if t["id"] not in tracked
        ],
    }


def later_checks_view(tx: Tx, curriculum_id: str) -> JSON:
    """Show every later check of a curriculum's goals, the counts, and whether it is caught up."""
    curriculum, enrollment = _tracked(tx, curriculum_id)
    rows: list[JSON] = [
        {
            "ref": t,
            "action": content.definition(tx, t)["action"],
            "type": s["type"] if (s := practice.schedule_view(tx, t)) else None,
            "checks": practice.later_checks(tx, t),
        }
        for t in enrollment["goal_order"]
    ]
    return {
        "curriculum": {"ref": curriculum["ref"], "title": curriculum["title"]},
        "targets": rows,
        "counts": measurement.later_check_counts([c for r in rows for c in r["checks"]], tx.now),
        "caught_up": {
            **(caught := practice.caught_up(tx, enrollment)),
            "pending": [
                {**p, "action": content.definition(tx, p["target"])["action"]}
                for p in caught["pending"]
            ],
        },
    }


def choices_view(tx: Tx, session_id: str) -> JSON:
    """List what the learner may choose to practise instead (a recorded override)."""
    session = practice.session_view(tx, session_id)
    checks, _upcoming = practice.pending(tx, session["enrollments"], tx.now)
    needs = {(p.target["id"], p.target["revision"]): p for p in checks}
    goals = [
        e["target"]
        for ref_ in session["enrollments"]
        for e in practice.enrollment_view(tx, ref_["id"])["practice"]
    ]
    rows = [
        {
            "exercise": e["ref"],
            "prompt": e["prompt"],
            "seconds": practice.full_cost(e),
            "targets": [_choice_target(tx, t, needs) for t in e["targets"]],
        }
        for e in content.exercises_for(tx, goals)
    ]
    return {"session": session, "exercises": rows}


def _choice_target(tx: Tx, target: JSON, needs: dict[tuple[str, int], Any]) -> JSON:
    p = needs.get((target["id"], target["revision"]))
    return {
        "action": content.definition(tx, target)["action"],
        "need": p.need if p else None,
        "blocked": p.blocked if p else None,
        "role": practice.role_now(tx, target),
    }


def session_proposal_view(tx: Tx, curriculum_ids: list[str], budget_seconds: int | None) -> JSON:
    """Preview a session over these curricula and budget before starting it."""
    enrollments = [
        e["ref"] for cid in curriculum_ids if (e := practice.enrollment_for(tx, cid)) is not None
    ]
    if not enrollments:
        msg = "none of these curricula has an enrollment yet"
        raise LookupError(msg)
    return practice.proposal(tx, enrollments, budget_seconds)


def outline_view(tx: Tx, curriculum_id: str) -> JSON:
    """Return the outline with each goal's state, latest evidence, due check and effort."""
    curriculum = content.current_definition(tx, "curriculum", curriculum_id)
    if curriculum is None:
        msg = f"no curriculum {curriculum_id}"
        raise LookupError(msg)
    enrollment = practice.enrollment_for(tx, curriculum_id)
    goals = [t for s in curriculum["sections"] for t in s["targets"]]
    exercises = content.practice_exercises(tx, {t["id"] for t in goals})
    holds = {e["ref"]["id"]: content.exercise_hold(tx, e) for e in exercises}
    covered = {t["id"] for e in exercises if holds[e["ref"]["id"]] is None for t in e["targets"]}
    targets = [_target_view(tx, t, enrollment) for t in goals]
    labels = [t["evidence"]["label"] for t in targets]
    return {
        "curriculum": {
            "ref": curriculum["ref"],
            "title": curriculum["title"],
            "purpose": curriculum["purpose"],
            "purpose_basis": curriculum["purpose_basis"],
            "doubts": curriculum["doubts"],
            "omitted": curriculum["omitted"],
            "sections": [
                {"id": s["id"], "title": s["title"], "target_ids": [t["id"] for t in s["targets"]]}
                for s in curriculum["sections"]
            ],
        },
        "source": {
            "title": (src := content.definition(tx, curriculum["source"]))["title"],
            "text": src["text"],
        },
        "targets": targets,
        "exercises": [
            {
                "id": e["ref"]["id"],
                "prompt": e["prompt"],
                "ref": e["ref"],
                "target_ids": [t["id"] for t in e["targets"]],
                "review": e["design_review"]["disposition"],
                "reviewer": e["design_review"]["actor"],
                "hold": _reason(holds[e["ref"]["id"]]),
                "rebindable": (hold := holds[e["ref"]["id"]]) is not None and hold.kind == "stale",
            }
            for e in exercises
        ],
        "without_exercise": [t["id"] for t in goals if t["id"] not in covered],
        "counts": {
            "selected": len(goals),
            "unstarted": sum(1 for t in targets if t["state"] == "unstarted"),
            "active": sum(1 for t in targets if t["state"] == "active"),
            "independent": labels.count("independent"),
            "helped": labels.count("helped"),
            "errors": labels.count("error"),
            "unresolved": labels.count("unresolved"),
            "untested": labels.count("untested"),
        },
        "next_check": _due(tx, goals),
        "effort": _curriculum_effort(tx, curriculum, enrollment),
        "enrollment": enrollment["ref"] if enrollment else None,
    }


def _session_attempts(tx: Tx, session_id: str) -> list[JSON]:
    return [a for a in evidence.attempts(tx) if a["session"]["id"] == session_id]


def practice_view(tx: Tx, session_id: str) -> JSON:
    """Return the session's current exercise, draft, help and assessment state."""
    session = practice.session_view(tx, session_id)
    shown = practice.open_offer(tx, session_id) or practice.waiting_offer(tx, session_id)
    attempts = _session_attempts(tx, session_id)
    submitted = [a for a in attempts if a["status"] == "submitted"]
    current = (
        evidence.attempt_view(tx, attempt_id=shown["attempt"]["id"])
        if shown
        else (submitted[-1] if submitted else None)  # a released draft is not resumed here
    )
    view: JSON = {"session": session, "attempt": None}
    if current is not None:
        exercise = content.definition(tx, current["exercise"])
        revealed = {
            h["id"]
            for h in exercise["hints"]
            for e in evidence.exposures_for(tx, current["ref"]["id"])
            if e["details"].get("hint_id") == h["id"]
        }
        offer = practice.offer_for(tx, current["ref"]["id"])
        view["attempt"] = {
            "ref": current["ref"],
            "purpose": current["purpose"],
            "status": current["status"],
            "response": current["response"],
            "prompt": exercise["prompt"],
            "hints": [
                {"id": h["id"], "text": h["text"] if h["id"] in revealed else None}
                for h in exercise["hints"]
            ],
            "assessment": _assessing(tx, current["ref"]["id"]),
            "feedback_ready": evidence.assessment_for(tx, current["ref"]["id"]) is not None,
            "counts_as_practice": bool(shown and practice.revoked(tx, shown["ref"]["id"])),
            "roles": [
                {"action": content.definition(tx, slot["target"])["action"], "role": slot["role"]}
                for slot in _offer_slots(offer)
            ],
        }
    return view


def _offer_slots(offer: JSON | None) -> list[JSON]:
    return list(offer["slots"]) if offer else []


def feedback_view(tx: Tx, attempt_id: str) -> JSON:
    """Return the answer, the judgment of each criterion with its quotes, and labels."""
    attempt = evidence.attempt_view(tx, attempt_id=attempt_id)
    exercise = content.definition(tx, attempt["exercise"])
    assessment = evidence.assessment_for(tx, attempt_id)
    results = {r["criterion_id"]: r for r in assessment["results"]} if assessment else {}
    help_by_criterion = evidence.criterion_help(tx, attempt)
    misread: set[str] = evidence.misread_criteria(assessment) if assessment else set()
    return {
        "attempt": {
            "ref": attempt["ref"],
            "response": attempt["response"],
            "status": attempt["status"],
            "purpose": attempt["purpose"],
        },
        "session": attempt["session"],
        "prompt": exercise["prompt"],
        "criteria": [
            {
                "id": c["id"],
                "requirement": c["requirement"],
                "outcome": results[c["id"]]["outcome"] if c["id"] in results else None,
                "quotes": [q["quote"] for q in results[c["id"]]["response_quotes"]]
                if c["id"] in results
                else [],
                "reason": results[c["id"]]["reason"] if c["id"] in results else None,
                "help": help_by_criterion.get(c["id"]),
                "misread": c["id"] in misread,
            }
            for c in exercise["criteria"]
        ],
        "explanation": assessment["explanation"] if assessment else None,
        "assessor": assessment["assessor"] if assessment else None,
        "reference_response": exercise["reference_response"],
        "targets": [
            {
                "action": content.definition(tx, t)["action"],
                **evidence.target_evidence(tx, t),
            }
            for t in exercise["targets"]
        ],
        "assessment": _assessing(tx, attempt_id),
        "concern": practice.concern_for(tx, assessment["ref"]["id"]) if assessment else None,
        "disputable": assessment is not None and evidence.disputable(attempt),
        "revision_reason": assessment["revision_reason"] if assessment else None,
        "earlier_judgments": [
            _judgment(j, exercise) for j in evidence.assessment_history(tx, attempt_id)[:-1]
        ],
        "review": _review(tx, assessment),
        "ratings": _ratings(tx, attempt, exercise),
    }


def _ratings(tx: Tx, attempt: JSON, exercise: JSON) -> list[JSON]:
    """Return the recall ratings this answer can take, per goal (none for extra practice)."""
    found: list[JSON] = []
    for target in exercise["targets"]:
        choices, _why = practice.rating_choices(
            tx,
            attempt["ref"]["id"],
            target,
            under_review=_under_review(tx, evidence.assessment_for(tx, attempt["ref"]["id"])),
        )
        if choices:
            review = evidence.review_for(tx, attempt["ref"]["id"], target)
            found.append(
                {
                    "target": target,
                    "action": content.definition(tx, target)["action"],
                    "choices": choices,
                    "choice": review["choice"] if review else None,
                }
            )
    return found


def _judgment(judgment: JSON, exercise: JSON) -> JSON:
    """Show one revision of a judgment, criterion by criterion."""
    requirement = {c["id"]: c["requirement"] for c in exercise["criteria"]}
    return {
        "ref": judgment["ref"],
        "assessor": judgment["assessor"]["name"],
        "results": [
            {
                "criterion_id": r["criterion_id"],
                "requirement": requirement[r["criterion_id"]],
                "outcome": r["outcome"],
                "reason": r["reason"],
            }
            for r in judgment["results"]
        ],
        "interpretation": judgment["interpretation"],
        "explanation": judgment["explanation"],
        "revision_reason": judgment["revision_reason"],
    }


def _under_review(tx: Tx, assessment: JSON | None) -> bool:
    """Tell whether a review of this judgment is running or waiting for a decision."""
    review = _review(tx, assessment)
    return review is not None and review["acceptance"] == "pending"


def _review(tx: Tx, assessment: JSON | None) -> JSON | None:
    """Return the latest review of a judgment ("this judgment is wrong"), if any."""
    if assessment is None:
        return None
    reviews = [
        o
        for o in _operations(tx)
        if _reviews(o["input_snapshot"]) and o["inputs"][0]["id"] == assessment["ref"]["id"]
    ]
    return _op_state(reviews[-1]) if reviews else None


def target_history_view(tx: Tx, target_id: str) -> JSON:
    """Show every revision of a goal with its own evidence, judgments and schedule decisions.

    Old definitions stay readable: each revision keeps the answers given under it, every
    revision of their judgments (corrections included) and the reasons for its due dates.
    """
    revisions = content.revisions(tx, "target", target_id)
    current = revisions[-1]["ref"]
    return {
        "target_id": target_id,
        "revisions": [_revision_history(tx, r, current) for r in revisions],
    }


def _revision_history(tx: Tx, revision: JSON, current: JSON) -> JSON:
    target = revision["ref"]
    mapping = content.mapping_to(tx, target)
    answers: list[JSON] = []
    for event in evidence.chronology(tx, target):
        if event["kind"] != "answer":
            continue
        attempt = evidence.attempt_view(tx, event["attempt"])
        exercise = content.definition(tx, attempt["exercise"])
        history = evidence.assessment_history(tx, attempt["ref"]["id"])
        answers.append(
            {
                "attempt": attempt["ref"],
                "purpose": attempt["purpose"],
                "prompt": exercise["prompt"],
                "response": attempt["response"],
                "submitted_at": attempt["submitted_at"],
                "label": event["label"],
                "judgments": [
                    {**_judgment(j, exercise), "current": n == len(history) - 1}
                    for n, j in enumerate(history)
                ],
                "review": _review(tx, history[-1] if history else None),
                "disputable": bool(history) and evidence.disputable(attempt),
            }
        )
    return {
        "ref": target,
        "current": target == current,
        "action": revision["action"],
        "mode": revision["mode"],
        "conditions": revision["conditions"],
        "requirements": [
            {"id": r["id"], "statement": r["statement"]} for r in revision["evidence_requirements"]
        ],
        "mapping": {"relation": mapping["relation"], "reason": mapping["reason"]}
        if mapping
        else None,
        "hold": _reason(content.target_hold(tx, target)),
        "evidence": {
            k: v for k, v in evidence.target_evidence(tx, target).items() if k != "observations"
        },
        "answers": answers,
        "schedule": [
            {
                "revision": h["ref"]["revision"],
                "need": h["need"],
                "due_at": h["due_at"],
                "reason": h["reason"],
                "obligation": {k: h["obligation"][k] for k in ("kind", "status")},
                "hold_reason": h["hold_reason"],
                "resolution_rule": h["resolution_rule"]["name"]
                if h.get("resolution_rule")
                else None,
                "check_effects": [e["disposition"] for e in h.get("check_effects", [])],
            }
            for h in practice.schedule_history(tx, target)
        ],
    }


def study_page_view(tx: Tx, study_id: str) -> JSON:
    """Return delivered teaching with its approach and what it is about."""
    study = evidence.study_view(tx, study_id)
    teaching = content.definition(tx, study["teaching"])
    concern = practice.concern_at(tx, teaching["concern"]) if teaching["concern"] else None
    return {
        "ref": study["ref"],
        "session": study["session"],
        "status": study["status"],
        "content": study["content"],
        "approach": teaching["approach"],
        "derivation": teaching["derivation"],
        "quotes": [p["quote"] for p in teaching["sources"]],
        "targets": [content.definition(tx, t)["action"] for t in study["targets"]],
        "uncertain": bool(concern and concern["help"] == "uncertain"),
    }


def summary_view(tx: Tx, session_id: str) -> JSON:
    """Summarize a session: what was shown, with what help, what remains, and time."""
    session = practice.session_view(tx, session_id)
    targets: dict[str, JSON] = {}
    pending = 0
    attempts = _session_attempts(tx, session_id)
    session_attempts = {a["ref"]["id"] for a in attempts}
    for attempt in attempts:
        exercise = content.definition(tx, attempt["exercise"])
        graded = evidence.assessment_for(tx, attempt["ref"]["id"]) is not None
        if attempt["status"] == "submitted" and not graded:
            pending += 1
        for t in exercise["targets"]:
            result = (
                evidence.target_evidence(tx, t, attempt_ids=session_attempts)
                if graded
                else evidence.pending_evidence()
            )
            targets[t["id"]] = {
                "ref": t,
                "action": content.definition(tx, t)["action"],
                "label": result["label"],
                "reasons": result["reasons"],
                "attempt": attempt["ref"]["id"],
            }
    elapsed_ms = measurement.elapsed_ms(session["started_at"], session["ended_at"] or tx.now)
    assessed = [g for a in attempts if (g := evidence.assessment_for(tx, a["ref"]["id"]))]
    concerns = {
        c["ref"]["id"]: c for g in assessed if (c := practice.concern_for(tx, g["ref"]["id"]))
    }
    help_given = [
        {
            "approach": content.definition(tx, s["teaching"])["approach"],
            "status": s["status"],
            "targets": [content.definition(tx, t)["action"] for t in s["targets"]],
        }
        for s in evidence.studies(tx)
        if s["session"]["id"] == session_id
    ]
    unmet = (
        session["unmet"]
        if session["status"] == "ended"
        else practice.unserved_view(tx, session_id, measurement.session_elapsed_ms(tx, session_id))
    )
    return {
        "session": session,
        "unmet": [{**u, "action": content.definition(tx, u["target"])["action"]} for u in unmet],
        "headline": "Practiced today; later recall not checked yet.",
        "targets": list(targets.values()),
        "help": help_given,
        "clarifications": sum(
            len(content.definition(tx, a["exercise"])["criteria"])
            for a in attempts
            if a["purpose"] == "clarification"
        ),
        "clarification_limit": practice.DIAGNOSTIC_LIMIT,
        "concerns": list(concerns.values()),
        "pending_assessments": pending,
        "next_check": _due(tx, [t["ref"] for t in targets.values()]),
        "effort": measurement.ledger(
            measurement.spans_for(tx, session_ids={session_id}, context_ids=set())
        ),
        "elapsed_ms": elapsed_ms,
    }
