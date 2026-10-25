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
    evidence.ASSESS_PROTOCOL["name"]: evidence.AssessmentOutput,
}


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


def validate_records(records: list[Record]) -> list[str]:
    """Check every Workflows-owned record against its payload contract."""
    errors: list[str] = []
    for r in records:
        if KIND_OWNER[r.kind] != OWNER:
            continue
        if r.kind != "operation":
            errors.append(f"{r.kind} records are not supported by this release")
            continue
        try:
            OperationP.model_validate(r.payload)
        except ValidationError as e:
            errors.append(f"operation {r.id} r{r.revision}: {e.errors()[0]['msg']}")
    return errors


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
            return {
                "operation": tx.put(
                    "operation",
                    op.model_copy(
                        update={"status": "succeeded", "raw_response": raw, **update}
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
        if op.purpose == "draft_material":
            source = op.inputs[0]
            latest = content.current_definition(tx, "source", source.id)
            return latest is not None and latest["ref"]["revision"] == source.revision
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
        if op.purpose == "draft_material":
            draft = content.DraftOutline.model_validate(result.output.model_dump())
            source = op.inputs[0].model_dump()
            errors = content.check_draft(draft, content.definition(tx, source)["text"])
            if errors:
                raise ValueError("; ".join(errors))
            accepted = content.accept_draft(
                tx,
                source=source,
                draft=draft,
                authoring=operation,
                purpose_given=bool(op.input_snapshot["context"].get("purpose_given")),
            )
            enrollment = practice.enroll(
                tx, curriculum=accepted["curriculum"], goal_order=accepted["targets"]
            )
            return [accepted["curriculum"], enrollment, *accepted["exercises"]]
        out = evidence.AssessmentOutput.model_validate(result.output.model_dump())
        attempt = op.inputs[0].model_dump()
        accepted = evidence.accept_assessment(
            tx, attempt=attempt, out=out, assessor=assessor, raw_response=result.raw
        )
        practice.reconcile(
            tx, attempt=attempt, assessment=accepted["assessment"], results=accepted["labels"]
        )
        return [accepted["assessment"]]

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
            request = content.draft_request(source_title=title, source_text=text, purpose=purpose)
            op = self._new_operation(
                tx,
                purpose="draft_material",
                intent="initial_outline",
                inputs=[source],
                request=request,
                context={"purpose_given": bool(purpose)},
            )
            return {"source": source, "operation": op}

        inputs = {"title": title, "text": text, "purpose": purpose}
        return self.store.run(request_id, "add_material", inputs, fn).result

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

    # --- practice ------------------------------------------------------------------

    def start_session(self, request_id: str, *, curriculum_id: str) -> JSON:
        """Open a session in a curriculum's enrollment."""

        def fn(tx: Tx) -> JSON:
            enrollment = practice.enrollment_for(tx, curriculum_id)
            if enrollment is None:
                msg = "this curriculum has no enrollment yet"
                raise LookupError(msg)
            return {"session": practice.start_session(tx, enrollment_id=enrollment["ref"]["id"])}

        return self.store.run(request_id, "start_session", {"curriculum": curriculum_id}, fn).result

    def next_exercise(self, request_id: str, *, session_id: str) -> JSON:
        """Resume the session's open draft, or deliver the next exercise as a new draft."""

        def fn(tx: Tx) -> JSON:
            reserved = practice.open_offer(tx, session_id)
            if reserved is not None:
                return {"attempt": reserved["attempt"], "offer": reserved["ref"], "resumed": True}
            exercise = practice.choose_exercise(tx, session_id=session_id)
            if exercise is None:
                return {"attempt": None, "offer": None, "resumed": False}
            session = practice.session_view(tx, session_id)
            attempt = evidence.start_attempt(tx, session=session["ref"], exercise=exercise["ref"])
            offer = practice.deliver(tx, session_id=session_id, exercise=exercise, attempt=attempt)
            return {"attempt": attempt, "offer": offer, "resumed": False}

        return self.store.run(request_id, "next_exercise", {"session": session_id}, fn).result

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
        """Record that the learner was shown feedback and the reference answer."""
        return self.store.run(
            request_id,
            "view_feedback",
            {"attempt": attempt_id},
            lambda tx: {"exposure": evidence.record_feedback_view(tx, attempt_id=attempt_id)},
        ).result

    def end_session(self, request_id: str, *, session_id: str, base: int, reason: str) -> JSON:
        """End a session; an unfinished draft stays resumable."""
        return self.store.run(
            request_id,
            "end_session",
            {"session": session_id, "base": base, "reason": reason},
            lambda tx: {
                "session": practice.end_session(
                    tx, session_id=session_id, base=base, stop_reason=reason
                )
            },
        ).result

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
        if (s := practice.schedule_view(tx, t["id"])) is not None and s["due_at"] is not None
    ]
    return min(dues) if dues else None


def home_view(tx: Tx) -> JSON:
    """List curricula with their state, and material still being drafted."""
    accepted_groups = {o["request_group"] for o in _operations(tx) if o["acceptance"] == "accepted"}
    latest_by_group: dict[str, JSON] = {}
    for o in _operations(tx):
        if o["purpose"] == "draft_material" and o["request_group"] not in accepted_groups:
            latest_by_group[o["request_group"]] = o
    drafting = [
        {"source": content.definition(tx, o["inputs"][0])["title"], "operation": _op_state(o)}
        for o in latest_by_group.values()
    ]
    items: list[JSON] = []
    for c in content.curricula(tx):
        enrollment = practice.enrollment_for(tx, c["ref"]["id"])
        goals: list[JSON] = enrollment["goal_order"] if enrollment else []
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
            }
        )
    return {
        "curricula": items,
        "drafting": drafting,
        "effort": measurement.ledger(measurement.all_spans(tx)),
    }


def _target_view(tx: Tx, target: JSON, enrollment: JSON | None) -> JSON:
    definition = content.definition(tx, target)
    knowledge = {k["id"]: content.definition(tx, k) for k in definition["content"]}
    entry = next(
        (e for e in (enrollment or {}).get("practice", []) if e["target"]["id"] == target["id"]),
        None,
    )
    schedule = practice.schedule_view(tx, target["id"])
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
        "knowledge": [
            {
                "form": k["form"],
                "statement": k["statement"],
                "scope": k["scope"],
                "quotes": [p["quote"] for p in k["sources"]],
            }
            for k in knowledge.values()
        ],
        "state": entry["state"] if entry else "not selected",
        "evidence": {"label": result["label"], "reasons": result["reasons"]},
        "schedule": {"need": schedule["need"], "due_at": schedule["due_at"]} if schedule else None,
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


def outline_view(tx: Tx, curriculum_id: str) -> JSON:
    """Return the outline with each goal's state, latest evidence, due check and effort."""
    curriculum = content.current_definition(tx, "curriculum", curriculum_id)
    if curriculum is None:
        msg = f"no curriculum {curriculum_id}"
        raise LookupError(msg)
    enrollment = practice.enrollment_for(tx, curriculum_id)
    goals = [t for s in curriculum["sections"] for t in s["targets"]]
    exercises = content.exercises_for(tx, goals)
    covered = {t["id"] for e in exercises for t in e["targets"]}
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
                "target_ids": [t["id"] for t in e["targets"]],
                "review": e["design_review"]["disposition"],
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
    reserved = practice.open_offer(tx, session_id)
    attempts = _session_attempts(tx, session_id)
    current = (
        evidence.attempt_view(tx, attempt_id=reserved["attempt"]["id"])
        if reserved
        else (attempts[-1] if attempts else None)
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
        view["attempt"] = {
            "ref": current["ref"],
            "status": current["status"],
            "response": current["response"],
            "prompt": exercise["prompt"],
            "hints": [
                {"id": h["id"], "text": h["text"] if h["id"] in revealed else None}
                for h in exercise["hints"]
            ],
            "assessment": _assessing(tx, current["ref"]["id"]),
            "feedback_ready": evidence.assessment_for(tx, current["ref"]["id"]) is not None,
        }
    return view


def feedback_view(tx: Tx, attempt_id: str) -> JSON:
    """Return the answer, the judgment of each criterion with its quotes, and labels."""
    attempt = evidence.attempt_view(tx, attempt_id=attempt_id)
    exercise = content.definition(tx, attempt["exercise"])
    assessment = evidence.assessment_for(tx, attempt_id)
    results = {r["criterion_id"]: r for r in assessment["results"]} if assessment else {}
    help_by_criterion = evidence.criterion_help(tx, attempt)
    return {
        "attempt": {
            "ref": attempt["ref"],
            "response": attempt["response"],
            "status": attempt["status"],
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
    }


def summary_view(tx: Tx, session_id: str) -> JSON:
    """Summarize a session: what was shown, with what help, what remains, and time."""
    session = practice.session_view(tx, session_id)
    targets: dict[str, JSON] = {}
    pending = 0
    for attempt in _session_attempts(tx, session_id):
        exercise = content.definition(tx, attempt["exercise"])
        graded = evidence.assessment_for(tx, attempt["ref"]["id"]) is not None
        if attempt["status"] == "submitted" and not graded:
            pending += 1
        for t in exercise["targets"]:
            result = (
                evidence.target_evidence(tx, t, attempt_id=attempt["ref"]["id"])
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
    return {
        "session": session,
        "headline": "Practiced today; later recall not checked yet.",
        "targets": list(targets.values()),
        "pending_assessments": pending,
        "next_check": _due(tx, [t["ref"] for t in targets.values()]),
        "effort": measurement.ledger(
            measurement.spans_for(tx, session_ids={session_id}, context_ids=set())
        ),
        "elapsed_ms": elapsed_ms,
    }
