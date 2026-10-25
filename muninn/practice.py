"""Practice: what learning work is needed and how to continue it.

Owns enrollment (goal admission), sessions, offers, selection, concerns and schedules.
Slice 1 schedules capability checks with the simple interval policy: the first later
check 24 hours after a full demonstration. FSRS recall scheduling arrives later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict

from muninn import content, evidence
from muninn.library import JSON, Record, exact_key, new_id, parse_utc, utc, validate_payloads

if TYPE_CHECKING:
    from muninn.library import Tx

OWNER = "practice"

FIRST_CHECK = timedelta(hours=24)
POLICY: JSON = {
    "name": "capability-interval",
    "version": 1,
    "parameters": {"first_check_hours": 24, "qualification_claim": evidence.QUALIFICATION},
}
SELECTION_POLICY: JSON = {
    "name": "first-unanswered-in-outline-order",
    "version": 1,
    "parameters": {},
}
DIAGNOSTIC_LIMIT = 3
UNSUCCESSFUL_CYCLE_LIMIT = 2
REPAIR_POLICY: JSON = {
    "name": "bounded-repair",
    "version": 1,
    "parameters": {
        "diagnostic_prompts_per_session": DIAGNOSTIC_LIMIT,
        "diagnostic_prompts_per_concern": DIAGNOSTIC_LIMIT,
        "unsuccessful_cycles_before_stop": UNSUCCESSFUL_CYCLE_LIMIT,
    },
}
STILL_UNCERTAIN = "still uncertain after clarification"
OUT_OF_QUESTIONS = "still uncertain: the question allowance is used up"

Need = Literal["initial", "independent_check", "repair", "clarify", "held"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


Ref = content.RefP


class PracticeEntryP(_Strict):
    """Admission state of one selected goal."""

    target: Ref
    state: Literal["unstarted", "active", "paused"]
    admitted_at: str | None
    basis: list[Ref]


class EnrollmentP(_Strict):
    """The learner's selected goals in one curriculum."""

    curriculum: Ref
    goal_order: list[Ref]
    status: Literal["active", "paused", "archived"]
    checkpoints: list[dict[str, Any]]
    practice: list[PracticeEntryP]


class SessionP(_Strict):
    """One sitting of practice."""

    enrollments: list[Ref]
    budget_seconds: int | None
    started_at: str
    ended_at: str | None
    status: Literal["open", "ended"]
    stop_reason: str | None
    next_action: str | None
    time_evidence: list[evidence.TimeEvidenceP]


class ObligationP(_Strict):
    """A check the schedule owes the target."""

    id: str
    kind: Literal["initial", "later"]
    origin: list[Ref]
    status: Literal["open", "consumed", "replaced", "invalidated"]
    successor_id: str | None


class CheckEffectP(_Strict):
    """What a correction decided for one offer's slot of this target (lifecycle section 4)."""

    offer: Ref
    disposition: Literal["preserved", "reanchored", "no_advance", "pending", "held"]
    revokes_reservation: bool
    basis: list[Ref]
    reason: str


class ScheduleP(_Strict):
    """One target's current learning need and due check."""

    target: Ref
    type: Literal["capability", "recall"]
    policy: content.AlgorithmP
    state_format: str
    engine_state: dict[str, Any]
    due_at: str | None
    need: Need
    basis: list[Ref]
    previous: Ref | None
    reason: str
    obligation: ObligationP
    consumed_by: Ref | None
    hold_reason: str | None
    resolution_rule: content.AlgorithmP | None = None
    check_effects: list[CheckEffectP] = []


class SlotP(_Strict):
    """One target an offer claims."""

    target: Ref
    obligation_id: str
    schedule_at_offer: Ref
    role: Literal["owner", "extra"]


class OfferP(_Strict):
    """A delivered exercise and the obligations it serves."""

    attempt: Ref
    session: Ref
    slots: list[SlotP]
    state: Literal["reserved", "submitted", "settled", "released"]
    reserved_at: str
    released_at: str | None
    reason: str | None


class SelectionP(_Strict):
    """Why an exercise was chosen."""

    session: Ref
    exercise: Ref
    policy: content.AlgorithmP
    reason: str


class ConcernScopeP(_Strict):
    """Which requirements a concern is about."""

    target: Ref
    requirement_ids: list[str]


class HypothesisP(_Strict):
    """One competing explanation the evidence still allows."""

    key: str
    cause: str
    practice: str


class BranchP(_Strict):
    """What one kind of answer to the pending question will change."""

    outcome: Literal["demonstrated", "error", "inconclusive"]
    next: Literal["resolve", "teach", "still_uncertain"]
    hypothesis_key: str | None
    why: str


class QuestionP(_Strict):
    """The clarification question a concern is waiting on, with branches fixed before asking."""

    exercise: Ref
    branches: list[BranchP]


class CycleP(_Strict):
    """One repair cycle: completed teaching, then one fresh check of the same scope."""

    id: str
    studies: list[Ref]
    verification: Ref | None
    outcome: Literal["pending", "recovered", "unsuccessful", "assisted", "incomplete"]


class ConcernP(_Strict):
    """A continuing, evidence-linked reason to provide help."""

    origin: Ref
    scope: list[ConcernScopeP]
    previous_concern: Ref | None
    status: Literal["open", "paused", "resolved", "superseded"]
    route: Literal[
        "diagnosis", "repair", "verification", "later_check", "assessment_review", "content_review"
    ]
    basis: list[Ref]
    resolution_reason: str | None
    kind: Literal["error", "uncertainty"] = "error"
    hypotheses: list[HypothesisP] = []
    focus: str | None = None
    question: QuestionP | None = None
    cycles: list[CycleP] = []


PAYLOADS: dict[str, type[BaseModel]] = {
    "enrollment": EnrollmentP,
    "session": SessionP,
    "schedule": ScheduleP,
    "practice_offer": OfferP,
    "selection": SelectionP,
    "concern": ConcernP,
}


def validate_records(records: list[Record]) -> list[str]:
    """Check every Practice-owned record against its payload contract."""
    return validate_payloads(records, OWNER, PAYLOADS)


# --- goals and sessions --------------------------------------------------------------


def enroll(tx: Tx, *, curriculum: JSON, goal_order: list[JSON]) -> JSON:
    """Select a curriculum's goals; nothing is admitted or scheduled yet."""
    payload = EnrollmentP(
        curriculum=Ref(**curriculum),
        goal_order=[Ref(**t) for t in goal_order],
        status="active",
        checkpoints=[],
        practice=[
            PracticeEntryP(target=Ref(**t), state="unstarted", admitted_at=None, basis=[])
            for t in goal_order
        ],
    )
    return tx.put("enrollment", payload.model_dump(), by=OWNER)


def enrollment_for(tx: Tx, curriculum_id: str) -> JSON | None:
    """Return the enrollment in a curriculum, if the learner has one."""
    for r in tx.current("enrollment", by=OWNER):
        if r.payload["curriculum"]["id"] == curriculum_id:
            return r.view
    return None


def start_session(tx: Tx, *, enrollment_id: str) -> JSON:
    """Open a practice session for one enrollment."""
    enrollment = tx.get("enrollment", enrollment_id, by=OWNER)
    if enrollment is None:
        msg = f"no enrollment {enrollment_id}"
        raise LookupError(msg)
    payload = SessionP(
        enrollments=[Ref(**enrollment.ref)],
        budget_seconds=None,
        started_at=tx.now,
        ended_at=None,
        status="open",
        stop_reason=None,
        next_action=None,
        time_evidence=[
            evidence.TimeEvidenceP(
                field="started_at",
                precision="exact",
                earliest_at=tx.now,
                latest_at=tx.now,
                basis="qualified_clock",
                raw_client_at=None,
                explanation="store time when the session opened",
            )
        ],
    )
    return tx.put("session", payload.model_dump(), by=OWNER)


def end_session(tx: Tx, *, session_id: str, base: int, stop_reason: str) -> JSON:
    """Close a session; an unfinished draft stays resumable, never a failure."""
    record = tx.require("session", session_id, by=OWNER)
    session = SessionP.model_validate(record.payload)
    ended = session.model_copy(
        update={"status": "ended", "ended_at": tx.now, "stop_reason": stop_reason}
    )
    return tx.put("session", ended.model_dump(), by=OWNER, id=session_id, base=base)


def session_view(tx: Tx, session_id: str) -> JSON:
    """Return a session's current revision."""
    record = tx.require("session", session_id, by=OWNER)
    return record.view


def sessions(tx: Tx) -> list[JSON]:
    """Return every session's current revision, oldest first."""
    return [r.view for r in tx.current("session", by=OWNER)]


# --- offers -------------------------------------------------------------------------


def open_offer(tx: Tx, session_id: str) -> JSON | None:
    """Return the unsubmitted draft offered in this enrollment, from any session.

    A draft stays bound to the session it was offered in; a later session resumes
    it rather than offering the same obligation again.
    """
    return _enrollment_offer(tx, session_id, "reserved")


def waiting_offer(tx: Tx, session_id: str) -> JSON | None:
    """Return a submitted answer in this enrollment still waiting for its assessment."""
    return _enrollment_offer(tx, session_id, "submitted")


def _enrollment_offer(tx: Tx, session_id: str, state: str) -> JSON | None:
    enrollment_id = session_view(tx, session_id)["enrollments"][0]["id"]
    sessions = {
        r.id
        for r in tx.current("session", by=OWNER)
        if r.payload["enrollments"][0]["id"] == enrollment_id
    }
    for r in tx.current("practice_offer", by=OWNER):
        if r.payload["session"]["id"] in sessions and r.payload["state"] == state:
            if state == "reserved" and _held_draft(tx, r.payload["attempt"]):
                continue  # the draft is kept; it resumes if its material is settled again
            return r.view
    return None


def _held_draft(tx: Tx, attempt: JSON) -> bool:
    exercise = content.definition(tx, evidence.attempt_view(tx, attempt)["exercise"])
    return content.exercise_hold(tx, exercise) is not None


def revoked(tx: Tx, offer_id: str) -> bool:
    """Tell whether a correction ended this offer's reservation (its answer is practice)."""
    offer = tx.require("practice_offer", offer_id, by=OWNER)
    return any(
        e["offer"]["id"] == offer_id and e["revokes_reservation"]
        for slot in offer.payload["slots"]
        for h in schedule_history(tx, slot["target"])
        for e in h.get("check_effects", [])
    )


def offer_for(tx: Tx, attempt_id: str) -> JSON | None:
    """Return the offer that delivered an attempt."""
    for r in tx.current("practice_offer", by=OWNER):
        if r.payload["attempt"]["id"] == attempt_id:
            return r.view
    return None


def choose_exercise(tx: Tx, *, session_id: str) -> JSON | None:
    """Choose the next exercise: the first unanswered one in the current outline order."""
    session = session_view(tx, session_id)
    enrollment = tx.require("enrollment", session["enrollments"][0]["id"], by=OWNER)
    curriculum = content.current_definition(
        tx, "curriculum", enrollment.payload["curriculum"]["id"]
    )
    order = [t["id"] for s in curriculum["sections"] for t in s["targets"]] if curriculum else []
    answered = {
        exact_key(a["exercise"]) for a in evidence.attempts(tx) if a["status"] == "submitted"
    }
    candidates = [
        e
        for e in content.exercises_for(tx, enrollment.payload["goal_order"])
        if exact_key(e["ref"]) not in answered  # a rebound revision checks a new contract
    ]
    position = {target_id: n for n, target_id in enumerate(order)}
    candidates.sort(key=lambda e: min(position.get(t["id"], len(order)) for t in e["targets"]))
    return candidates[0] if candidates else None


def _schedule(tx: Tx, target: JSON) -> Record | None:
    """Return the schedule of one exact goal revision (each contract has its own)."""
    for r in tx.current("schedule", by=OWNER):
        if exact_key(r.payload["target"]) == exact_key(target):
            return r
    return None


def deliver(  # noqa: PLR0913 - one keyword per delivery decision
    tx: Tx,
    *,
    session_id: str,
    exercise: JSON,
    attempt: JSON,
    role: Literal["owner", "extra"] = "owner",
    reason: str = "first exercise in outline order without a submitted answer",
    policy: JSON = SELECTION_POLICY,
) -> JSON:
    """Admit the exercise's targets and reserve the offer for its draft.

    Admission happens only now, for the covered targets; each gets an open initial
    obligation with no due date. Admission gives no credit. A focused clarification
    or verification is ``extra``: it never consumes or moves a scheduled check.
    """
    session = session_view(tx, session_id)
    record = tx.get("enrollment", session["enrollments"][0]["id"], by=OWNER)
    if record is None:
        msg = "the session has no enrollment"
        raise LookupError(msg)
    targets = exercise["targets"]
    covered = {exact_key(t) for t in targets}
    enrollment = EnrollmentP.model_validate(record.payload)
    entries = [
        e.model_copy(
            update={"state": "active", "admitted_at": tx.now, "basis": [Ref(**exercise["ref"])]}
        )
        if exact_key(e.target.model_dump()) in covered and e.state == "unstarted"
        else e
        for e in enrollment.practice
    ]
    if entries != enrollment.practice:
        tx.put(
            "enrollment",
            enrollment.model_copy(update={"practice": entries}).model_dump(),
            by=OWNER,
            id=record.id,
            base=record.revision,
        )
    slots: list[SlotP] = []
    for target in targets:
        existing = _schedule(tx, target)
        if existing is None:
            schedule = ScheduleP(
                target=Ref(**target),
                type="capability",
                policy=content.AlgorithmP(**POLICY),
                state_format="none",
                engine_state={},
                due_at=None,
                need="initial",
                basis=[Ref(**exercise["ref"])],
                previous=None,
                reason="admitted for practice",
                obligation=ObligationP(
                    id=new_id(),
                    kind="initial",
                    origin=[Ref(**exercise["ref"])],
                    status="open",
                    successor_id=None,
                ),
                consumed_by=None,
                hold_reason=None,
            )
            at_offer = tx.put("schedule", schedule.model_dump(), by=OWNER)
            obligation_id = schedule.obligation.id
        else:
            at_offer = existing.ref
            obligation_id = existing.payload["obligation"]["id"]
        slots.append(
            SlotP(
                target=Ref(**target),
                obligation_id=obligation_id,
                schedule_at_offer=Ref(**at_offer),
                role=role,
            )
        )
    offer = tx.put(
        "practice_offer",
        OfferP(
            attempt=Ref(**attempt),
            session=Ref(**session["ref"]),
            slots=slots,
            state="reserved",
            reserved_at=tx.now,
            released_at=None,
            reason=None,
        ).model_dump(),
        by=OWNER,
    )
    tx.put(
        "selection",
        SelectionP(
            session=Ref(**session["ref"]),
            exercise=Ref(**exercise["ref"]),
            policy=content.AlgorithmP(**policy),
            reason=reason,
        ).model_dump(),
        by=OWNER,
    )
    return offer


def _set_offer_state(tx: Tx, attempt_id: str, state: Literal["submitted", "settled"]) -> None:
    offer = offer_for(tx, attempt_id)
    if offer is None:
        msg = f"no offer delivered attempt {attempt_id}"
        raise LookupError(msg)
    payload = OfferP.model_validate({k: v for k, v in offer.items() if k != "ref"})
    tx.put(
        "practice_offer",
        payload.model_copy(update={"state": state}).model_dump(),
        by=OWNER,
        id=offer["ref"]["id"],
        base=offer["ref"]["revision"],
    )


def mark_submitted(tx: Tx, *, attempt_id: str) -> None:
    """Record that the offered draft was submitted."""
    _set_offer_state(tx, attempt_id, "submitted")


# --- content changes (compatibility-design.md section 6) ----------------------------------

GOAL_CHANGED = "the goal changed; the work done on its earlier version is kept"


def replace_goals(tx: Tx, *, curricula: list[list[JSON]], replaced: list[list[JSON]]) -> None:
    """Select replaced goal revisions in each affected enrollment as unstarted goals.

    The old revision keeps its schedule and evidence. Concerns drop a replaced revision
    from their scope (superseded when nothing is left), and drafts offered for it are
    released; the drafts themselves stay saved.
    """
    swap = {exact_key(old): Ref(**new) for old, new in replaced}
    moved = {old["id"]: Ref(**new) for old, new in curricula}
    for record in tx.current("enrollment", by=OWNER):
        curriculum = moved.get(record.payload["curriculum"]["id"])
        if curriculum is None:
            continue
        enrollment = EnrollmentP.model_validate(record.payload)
        revised = enrollment.model_copy(
            update={
                "curriculum": curriculum,
                "goal_order": [
                    swap.get(exact_key(t.model_dump()), t) for t in enrollment.goal_order
                ],
                "practice": [
                    PracticeEntryP(target=new, state="unstarted", admitted_at=None, basis=[])
                    if (new := swap.get(exact_key(e.target.model_dump())))
                    else e
                    for e in enrollment.practice
                ],
            }
        )
        tx.put("enrollment", revised.model_dump(), by=OWNER, id=record.id, base=record.revision)
    for record in tx.current("concern", by=OWNER):
        concern = ConcernP.model_validate(record.payload)
        kept = [s for s in concern.scope if exact_key(s.target.model_dump()) not in swap]
        if concern.status in ("open", "paused") and kept != concern.scope:
            update: JSON = {"scope": kept}
            if not kept:
                update |= {"status": "superseded", "resolution_reason": GOAL_CHANGED}
            revised_concern = concern.model_copy(update=update)
            tx.put(
                "concern",
                revised_concern.model_dump(),
                by=OWNER,
                id=record.id,
                base=record.revision,
            )
    for record in tx.current("practice_offer", by=OWNER):
        offer = OfferP.model_validate(record.payload)
        if offer.state == "reserved" and any(
            exact_key(s.target.model_dump()) in swap for s in offer.slots
        ):
            released = offer.model_copy(
                update={"state": "released", "released_at": tx.now, "reason": GOAL_CHANGED}
            )
            tx.put(
                "practice_offer",
                released.model_dump(),
                by=OWNER,
                id=record.id,
                base=record.revision,
            )


# --- reconciling needs with new evidence --------------------------------------------------


def reconcile(  # noqa: PLR0913 - one keyword per accepted input
    tx: Tx,
    *,
    attempt: JSON,
    assessment: JSON,
    results: dict[str, JSON],
    out: evidence.AssessmentOutput | None = None,
    question: JSON | None = None,
) -> None:
    """Recompute each covered target's schedule, update concerns, then settle the offer.

    The next check is dated from when the answer happened, never from grading time.
    ``question`` is the saved clarification exercise when ``wants_question`` said yes.
    """
    view = evidence.attempt_view(tx, attempt)
    for result in results.values():
        recompute_schedule(tx, result["target"], basis=[assessment])
    _update_concerns(
        tx, view=view, assessment=assessment, results=results, out=out, question=question
    )
    _set_offer_state(tx, attempt["id"], "settled")


# --- the one resolver (lifecycle section 4: effective event order and recomputation) -------

CORRECTION_RULE: JSON = {
    "name": "descendant-correction",
    "version": 1,
    "parameters": {"capability_policy": POLICY["name"], "first_check_hours": 24},
}
REANCHORED = "reanchored from a real later check"
INVALIDATED = "its generating answer no longer qualifies after a corrected judgment"
LATER_PENDING = "a later answer is still being assessed"


type Successors = dict[tuple[str, str, int], str]
"""Saved later-obligation identities by their generating occurrence (kind, id, revision)."""


@dataclass(frozen=True)
class _Ended:
    """Why an obligation ended during a replay."""

    basis: list[Ref]
    reason: str
    consumed_by: Ref | None


@dataclass
class _Replay:
    """The schedule state while replaying one target's effective history."""

    lineage: list[ObligationP]
    ended: dict[str, _Ended]
    need: Need
    due_at: str | None
    reason: str
    basis: list[Ref]
    hold_reason: str | None
    effects: dict[str, CheckEffectP] = field(default_factory=dict[str, CheckEffectP])

    @property
    def current(self) -> ObligationP:
        return self.lineage[-1]

    def set(
        self, need: Need, reason: str, basis: list[Ref], *, hold_reason: str | None = None
    ) -> None:
        """Set the current need; the due time changes only where a rule dates a check."""
        self.need, self.reason, self.basis, self.hold_reason = need, reason, basis, hold_reason

    def close(
        self,
        status: Literal["consumed", "replaced"],
        successor: ObligationP,
        *,
        basis: list[Ref],
        reason: str,
        consumed_by: Ref | None = None,
    ) -> None:
        """End the current obligation and open its successor."""
        ended = self.current.model_copy(update={"status": status, "successor_id": successor.id})
        self.lineage[-1] = ended
        self.ended[ended.id] = _Ended(basis=basis, reason=reason, consumed_by=consumed_by)
        self.lineage.append(successor)


def _later(origin: Ref, ids: Successors) -> ObligationP:
    """Return the later obligation an occurrence generates, reusing its saved identity."""
    key = (origin.kind, origin.id, origin.revision)
    return ObligationP(
        id=ids.get(key) or new_id(), kind="later", origin=[origin], status="open", successor_id=None
    )


def _plus_day(at: str) -> str:
    return utc(parse_utc(at) + FIRST_CHECK)


def _fold_owned(state: _Replay, answer: JSON, ids: Successors) -> None:
    """Apply one owned answer to the current obligation (the capability-interval policy)."""
    label, at, attempt = answer["label"], answer["at"], Ref(**answer["attempt"])
    basis = [Ref(**answer["assessment"])]
    if label in ("independent", "helped") and at is None:
        state.set(
            "held",
            f"{label} demonstration at an unknown time",
            basis,
            hold_reason="answer time unknown; a later check needs a known start",
        )
        state.due_at = None
    elif label == "independent" and state.current.kind == "initial":
        state.close(
            "consumed",
            _later(attempt, ids),
            basis=basis,
            reason="first independent demonstration",
            consumed_by=attempt,
        )
        state.set("independent_check", "first later check 24 hours after the demonstration", basis)
        state.due_at = _plus_day(at)
    elif label in ("independent", "helped"):
        why = (
            "independent retrieval 24 hours after helped practice"
            if label == "helped"
            else "independent check 24 hours later"
        )
        state.set("independent_check", why, basis)
        state.due_at = _plus_day(at)
    elif label == "error":
        state.set("repair", "supported error", basis)
    else:
        outcomes = {o["outcome"] for o in answer["observations"]}
        if outcomes == {"demonstrated"} and at is not None:  # shown; independence unknown
            state.set(
                "independent_check",
                "independent check 24 hours after an answer whose help is unknown",
                basis,
            )
            state.due_at = _plus_day(at)
            return
        misread = any(
            o["outcome"] == "error" and not evidence.supported_error(o)
            for o in answer["observations"]
        )
        state.set(
            "clarify" if "cannot_judge" in outcomes else state.need,
            "likely misread; not counted as a mistake" if misread else "evidence incomplete",
            basis,
        )


def _fold_descendant(
    state: _Replay,
    answer: JSON,
    offer: JSON,
    offered_due: str | None,
    ids: Successors,
) -> None:
    """Apply an owned answer whose opportunity no longer exists (descendant-correction-1).

    It re-anchors only as an independent demonstration at or after both its offered due
    time and the corrected due time; otherwise it has no scheduling effect, though a
    supported error still asks for repair.
    """
    at: str | None = answer["at"]
    basis = [Ref(**answer["assessment"])]
    eligible = at is not None and all(d is None or at >= d for d in (state.due_at, offered_due))
    if answer["label"] == "independent" and at is not None and eligible:
        state.close(
            "replaced", _later(Ref(**answer["attempt"]), ids), basis=basis, reason=REANCHORED
        )
        state.set("independent_check", REANCHORED, basis)
        state.due_at = _plus_day(at)
        disposition: Literal["reanchored", "no_advance"] = "reanchored"
    else:
        if answer["label"] == "error":
            state.set("repair", "supported error", basis)
        disposition = "no_advance"
    state.effects[offer["ref"]["id"]] = CheckEffectP(
        offer=Ref(**offer["ref"]),
        disposition=disposition,
        revokes_reservation=False,
        basis=basis,
        reason=REANCHORED if disposition == "reanchored" else "earlier history changed; no advance",
    )


def _slots(tx: Tx, target: JSON) -> dict[str, tuple[JSON, JSON]]:
    """Map each attempt to (offer, slot) for this exact target."""
    found: dict[str, tuple[JSON, JSON]] = {}
    for r in tx.current("practice_offer", by=OWNER):
        for slot in r.payload["slots"]:
            if exact_key(slot["target"]) == exact_key(target):
                found[r.payload["attempt"]["id"]] = (r.view, slot)
    return found


def _start(history: list[JSON]) -> _Replay:
    """Return the state at admission: the first revision's open initial obligation."""
    first = ScheduleP.model_validate({k: v for k, v in history[0].items() if k != "ref"})
    return _Replay(
        lineage=[first.obligation.model_copy(update={"status": "open", "successor_id": None})],
        ended={},
        need=first.need,
        due_at=first.due_at,
        reason=first.reason,
        basis=first.basis,
        hold_reason=first.hold_reason,
    )


def _replay(tx: Tx, target: JSON, history: list[JSON]) -> _Replay:
    """Replay one exact target's effective history from admission, in occurrence order."""
    state = _start(history)
    ids: Successors = {
        (o["kind"], o["id"], o["revision"]): h["obligation"]["id"]
        for h in history
        if h["obligation"]["kind"] == "later"
        for o in h["obligation"]["origin"][:1]
    }
    dues = {h["ref"]["revision"]: h["due_at"] for h in history}
    slots = _slots(tx, target)
    revocations = {
        e["offer"]["id"]
        for h in history
        for e in h.get("check_effects", [])
        if e["revokes_reservation"]
    }
    later_pending = False
    assessed: set[str] = set()
    for event in evidence.chronology(tx, target):
        if event["kind"] == "study":
            state.close(
                "replaced",
                _later(Ref(**event["study"]), ids),
                basis=[Ref(**event["study"])],
                reason="replaced after teaching",
            )
            state.set(
                "independent_check",
                "independent check 24 hours after completed teaching",
                [Ref(**event["study"])],
            )
            state.due_at = _plus_day(event["at"])
            continue
        offer, slot = slots.get(event["attempt"]["id"], (None, None))
        owned = bool(
            offer and slot and slot["role"] == "owner" and offer["ref"]["id"] not in revocations
        )
        used = {o.id for o in state.lineage[:-1]}
        if owned and slot and slot["obligation_id"] in used:
            owned = False  # its check was already met or replaced: another owner's answer is extra
        if event["label"] is None:  # submitted, not assessed yet
            later_pending = later_pending or owned
            continue
        later_pending = False
        assessed.add(event["attempt"]["id"])
        if not owned:
            if event["label"] == "error":
                state.set(
                    "repair", "supported error on a focused check", [Ref(**event["assessment"])]
                )
            continue
        assert offer  # noqa: S101 - owned implies an offer and a slot
        assert slot  # noqa: S101
        if slot["obligation_id"] == state.current.id:
            _fold_owned(state, event, ids)
        else:
            offered_due = dues.get(slot["schedule_at_offer"]["revision"])
            _fold_descendant(state, event, offer, offered_due, ids)
    if later_pending and state.need != "repair":  # never hide a supported current error
        state.hold_reason, state.need = LATER_PENDING, "held"
    _unsettled_owners(state, slots, assessed, revocations)
    return state


def _unsettled_owners(
    state: _Replay, slots: dict[str, tuple[JSON, JSON]], assessed: set[str], revoked: set[str]
) -> None:
    """Decide owned drafts and pending answers whose opportunity no longer exists."""
    lineage = {o.id for o in state.lineage}
    for offer, slot in slots.values():
        decided = offer["attempt"]["id"] in assessed  # the replay already applied its answer
        practice_now = offer["ref"]["id"] in revoked and offer["state"] != "reserved"
        if slot["role"] != "owner" or slot["obligation_id"] in lineage or decided or practice_now:
            continue
        if offer["state"] == "reserved":
            effect = CheckEffectP(
                offer=Ref(**offer["ref"]),
                disposition="held",
                revokes_reservation=True,
                basis=state.basis,
                reason="earlier history changed; this draft now counts as practice",
            )
        elif offer["state"] == "submitted":
            effect = CheckEffectP(
                offer=Ref(**offer["ref"]),
                disposition="pending",
                revokes_reservation=False,
                basis=state.basis,
                reason="earlier history changed; this answer is still being assessed",
            )
            if state.need != "repair":
                state.need, state.hold_reason = "held", effect.reason
        else:
            continue
        state.effects.setdefault(offer["ref"]["id"], effect)


def _decision(schedule: ScheduleP) -> JSON:
    """Return what a revision decides.

    A newer revision of the same basis record, or a correction stamp on an unchanged
    state, is not a new decision.
    """
    decided = schedule.model_dump(exclude={"previous", "basis", "resolution_rule"})
    return {**decided, "basis": [(b.kind, b.id) for b in schedule.basis]}


def recompute_schedule(
    tx: Tx, target: JSON, *, basis: list[JSON], correction: bool = False
) -> None:
    """Replay a target's schedule and append only what changed (one resolver).

    Terminal dispositions come first (predecessors that ended, opportunities whose
    generating answer no longer qualifies), then the current state. Replaying the same
    effective history writes nothing, so a repeated correction adds no effect.
    """
    record = _schedule(tx, target)
    if record is None:
        return
    history = [r.view for r in tx.history("schedule", record.id, by=OWNER)]
    state = _replay(tx, target, history)
    latest = ScheduleP.model_validate({k: v for k, v in history[-1].items() if k != "ref"})
    effective: dict[str, ObligationP] = {}
    for h in history:
        effective[h["obligation"]["id"]] = ObligationP.model_validate(h["obligation"])
    writes: list[ScheduleP] = []
    for o in state.lineage[:-1]:
        if effective.get(o.id) != o:
            ended = state.ended[o.id]
            writes.append(
                latest.model_copy(
                    update={
                        "obligation": o,
                        "consumed_by": ended.consumed_by,
                        "basis": ended.basis,
                        "reason": ended.reason,
                        "hold_reason": None,
                    }
                )
            )
    alive = {o.id for o in state.lineage}
    stated = [Ref(**b) for b in basis]
    writes += [
        latest.model_copy(
            update={
                "obligation": o.model_copy(update={"status": "invalidated", "successor_id": None}),
                "consumed_by": None,
                "basis": stated,
                "reason": INVALIDATED,
                "hold_reason": None,
            }
        )
        for oid, o in effective.items()
        if oid not in alive and o.status != "invalidated"
    ]
    effects = list(state.effects.values())
    current = latest.model_copy(
        update={
            "obligation": state.current,
            "consumed_by": None,
            "need": state.need,
            "due_at": state.due_at,
            "reason": state.reason,
            "basis": state.basis,
            "hold_reason": state.hold_reason,
            "resolution_rule": content.AlgorithmP(**CORRECTION_RULE)
            if correction or effects
            else None,
            "check_effects": effects,
        }
    )
    if writes or _decision(current) != _decision(latest):
        writes.append(current)
    last = record.ref
    for revision in writes:
        linked = revision.model_copy(update={"previous": Ref(**last)})
        last = tx.put(
            "schedule", linked.model_dump(), by=OWNER, id=record.id, base=last["revision"]
        )


# --- diagnosis and repair (everyday-learning-design.md section 5) ------------------------


def discriminates(question: evidence.AssessQuestion | None) -> bool:
    """Tell whether a correct answer and an error would lead to different practice."""
    if question is None:
        return False
    branch = {b.outcome: (b.next, b.hypothesis_key) for b in question.branches}
    return branch["demonstrated"] != branch["error"]


def _concern_id(attempt: JSON) -> str | None:
    """Return the concern a clarification or verification attempt is bound to."""
    concern: JSON | None = attempt.get("concern")
    return str(concern["id"]) if concern else None


def _observations(results: dict[str, JSON]) -> list[JSON]:
    return [
        {**o, "target_id": target_id, "target": result["target"]}
        for target_id, result in results.items()
        for o in result.get("observations", [])
    ]


type Pair = tuple[str, int, str]
"""One requirement of one exact goal revision: (target id, revision, requirement id)."""


def _pairs(scope: list[ConcernScopeP]) -> set[Pair]:
    return {(s.target.id, s.target.revision, r) for s in scope for r in s.requirement_ids}


def _criteria(observations: list[JSON], outcomes: set[str]) -> set[str]:
    return {
        o["criterion_id"]
        for o in observations
        if o["outcome"] in outcomes and (o["outcome"] != "error" or evidence.supported_error(o))
    }


def wants_question(
    tx: Tx, *, attempt: JSON, out: evidence.AssessmentOutput, results: dict[str, JSON]
) -> bool:
    """Decide whether the proposed clarification question is worth saving and asking.

    It must discriminate, address the answer's own unresolved criteria, and, for a
    supported error, choose between at least two hypotheses calling for different help.
    After a clarification it is asked only when that answer left the concern uncertain.
    """
    q = out.question
    if q is None or not discriminates(q):
        return False
    view = evidence.attempt_view(tx, attempt)
    observations = _observations(results)
    if view["purpose"] == "verification":
        return False
    if view["purpose"] == "clarification":
        concern = ConcernP.model_validate(
            tx.require("concern", view["concern"]["id"], by=OWNER).payload
        )
        return (
            concern.question is not None
            and _branch(concern, observations).next == "still_uncertain"
        )
    about = {c.about_criterion_key for c in q.criteria}
    erred = _criteria(observations, {"error"})
    if erred:
        # ponytail: "different help" compares the hypotheses' practice wording; the assessor
        # is told to name distinct practice per cause.
        practices = {
            h.practice.strip().lower() for h in out.hypotheses if set(h.criterion_keys) & erred
        }
        return about <= erred and len(practices) >= 2  # noqa: PLR2004 - two competing causes
    unsure = _criteria(observations, {"not_shown", "cannot_judge"})
    return bool(unsure) and about <= unsure


def _branch(concern: ConcernP, observations: list[JSON]) -> BranchP:
    assert concern.question is not None  # noqa: S101 - callers check
    outcome = evidence.scope_outcome(observations)
    key = "demonstrated" if outcome in ("demonstrated", "helped") else outcome
    return next(b for b in concern.question.branches if b.outcome == key)


def _scope(
    observations: list[JSON], outcomes: set[str], *, exclude: set[Pair]
) -> list[ConcernScopeP]:
    """Scope the exact goal requirements observed with these outcomes, minus ``exclude``."""
    wanted: dict[tuple[str, int], tuple[JSON, set[str]]] = {}
    for o in observations:
        if o["outcome"] not in outcomes or (
            o["outcome"] == "error" and not evidence.supported_error(o)
        ):
            continue
        key = exact_key(o["target"])
        wanted.setdefault(key, (o["target"], set()))[1].update(
            r for r in o["requirement_ids"] if (*key, r) not in exclude
        )
    return [
        ConcernScopeP(target=Ref(**target), requirement_ids=sorted(reqs))
        for target, reqs in wanted.values()
        if reqs
    ]


def _update_concerns(  # noqa: PLR0913 - the accepted assessment and its context
    tx: Tx,
    *,
    view: JSON,
    assessment: JSON,
    results: dict[str, JSON],
    out: evidence.AssessmentOutput | None,
    question: JSON | None,
) -> None:
    observations = _observations(results)
    handled: set[Pair] = set()
    bound = _concern_id(view)
    if bound:
        record = tx.require("concern", bound, by=OWNER)
        concern = ConcernP.model_validate(record.payload)
        handled = _pairs(concern.scope)
        if view["purpose"] == "clarification":
            concern = _after_clarification(concern, observations, out, question)
        else:
            concern = _after_verification(concern, observations, view)
        concern = concern.model_copy(update={"basis": [*concern.basis, Ref(**assessment)]})
        tx.put("concern", concern.model_dump(), by=OWNER, id=record.id, base=record.revision)
        question = None
    errors = _scope(observations, {"error"}, exclude=handled)
    if errors:
        _open_concern(
            tx,
            kind="error",
            scope=errors,
            view=view,
            assessment=assessment,
            out=out,
            question=question,
        )
    elif question is not None:
        unsure = _scope(observations, {"not_shown", "cannot_judge"}, exclude=handled)
        _open_concern(
            tx,
            kind="uncertainty",
            scope=unsure,
            view=view,
            assessment=assessment,
            out=out,
            question=question,
        )


def _hypotheses(out: evidence.AssessmentOutput | None, criteria: set[str]) -> list[HypothesisP]:
    if out is None:
        return []
    return [
        HypothesisP(key=h.key, cause=h.cause, practice=h.practice)
        for h in out.hypotheses
        if set(h.criterion_keys) & criteria
    ]


def _question(out: evidence.AssessmentOutput | None, question: JSON | None) -> QuestionP | None:
    if question is None or out is None or out.question is None:
        return None
    return QuestionP(
        exercise=Ref(**question),
        branches=[BranchP.model_validate(b.model_dump()) for b in out.question.branches],
    )


def _open_concern(  # noqa: PLR0913 - one concern from one answer
    tx: Tx,
    *,
    kind: Literal["error", "uncertainty"],
    scope: list[ConcernScopeP],
    view: JSON,
    assessment: JSON,
    out: evidence.AssessmentOutput | None,
    question: JSON | None,
) -> None:
    """Open one concern for this answer, or continue an unresolved one on the same scope."""
    criteria = {
        o.criterion_key for o in (out.observations if out else []) if o.outcome != "demonstrated"
    }
    hypotheses = _hypotheses(out, criteria)
    update: dict[str, Any] = {
        "kind": kind,
        "status": "open",
        "route": "diagnosis" if question else "repair",
        "hypotheses": hypotheses,
        "focus": hypotheses[0].key if len(hypotheses) == 1 else None,
        "question": _question(out, question),
        "resolution_reason": None,
    }
    wanted = _pairs(scope)
    for record in tx.current("concern", by=OWNER):
        old = ConcernP.model_validate(record.payload)
        if old.status in ("open", "paused") and wanted & _pairs(old.scope):
            update |= {
                "kind": "error" if "error" in (kind, old.kind) else kind,
                "scope": _merge(old.scope, scope),
                "basis": [*old.basis, Ref(**assessment)],
            }
            if _stopped(old):  # a recurrence cannot restart automatic repair
                update |= {**STOPPED_REPAIR, "question": None}
            revised = old.model_copy(update=update)
            tx.put("concern", revised.model_dump(), by=OWNER, id=record.id, base=record.revision)
            return
    concern = ConcernP(
        origin=Ref(**view["ref"]),
        scope=scope,
        previous_concern=None,
        basis=[Ref(**assessment)],
        **update,
    )
    tx.put("concern", concern.model_dump(), by=OWNER)


def _merge(*scopes: list[ConcernScopeP]) -> list[ConcernScopeP]:
    merged: dict[tuple[str, int], tuple[Ref, set[str]]] = {}
    for s in (s for scope in scopes for s in scope):
        key = (s.target.id, s.target.revision)
        merged.setdefault(key, (s.target, set()))[1].update(s.requirement_ids)
    return [ConcernScopeP(target=t, requirement_ids=sorted(r)) for t, r in merged.values()]


def _after_clarification(
    concern: ConcernP,
    observations: list[JSON],
    out: evidence.AssessmentOutput | None,
    question: JSON | None,
) -> ConcernP:
    """Follow the branch written before the question was asked."""
    if concern.question is None:
        return concern
    branch = _branch(concern, observations)
    if branch.next == "resolve":
        return concern.model_copy(
            update={
                "question": None,
                "status": "resolved",
                "resolution_reason": "the clarification showed it; no repair needed",
            }
        )
    if branch.next == "teach":
        return concern.model_copy(
            update={"question": None, "route": "repair", "focus": branch.hypothesis_key}
        )
    if question is not None:
        criteria = {o.criterion_key for o in (out.observations if out else [])}
        return concern.model_copy(
            update={"question": _question(out, question), "hypotheses": _hypotheses(out, criteria)}
        )
    return concern.model_copy(
        update={"question": None, "status": "paused", "resolution_reason": STILL_UNCERTAIN}
    )


CYCLE_OUTCOME: dict[str, Literal["recovered", "assisted", "unsuccessful", "incomplete"]] = {
    "demonstrated": "recovered",
    "helped": "assisted",
    "error": "unsuccessful",
    "inconclusive": "incomplete",
}


def _after_verification(concern: ConcernP, observations: list[JSON], view: JSON) -> ConcernP:
    """Settle the repair cycle this fresh check verifies; one outcome per cycle.

    Recovered resolves the concern (its later check stays due). The first unsuccessful
    cycle asks for a changed approach; the second stops automatic repair. Help or
    missing evidence never loops back into teaching.
    """
    cycle_id = view["verification_of"]["cycle_id"]
    outcome = CYCLE_OUTCOME[
        evidence.scope_outcome(observations, [s.model_dump() for s in concern.scope])
    ]
    cycles = [
        c.model_copy(update={"outcome": outcome, "verification": Ref(**view["ref"])})
        if c.id == cycle_id and c.outcome == "pending"
        else c
        for c in concern.cycles
    ]
    failed = sum(c.outcome == "unsuccessful" for c in cycles)
    update: JSON = {
        "recovered": {
            "status": "resolved",
            "resolution_reason": "recovered on a fresh check; the later check is still due",
        },
        "assisted": {
            "route": "later_check",
            "resolution_reason": "shown with help on the fresh check; an independent later "
            "check is due",
        },
        "incomplete": {
            "route": "assessment_review",
            "resolution_reason": "the fresh check did not show the repaired part",
        },
        "unsuccessful": {"route": "repair"}
        if failed < UNSUCCESSFUL_CYCLE_LIMIT
        else STOPPED_REPAIR,
    }[outcome]
    return concern.model_copy(update={"cycles": cycles, **update})


STOPPED_REPAIR: JSON = {
    "route": "content_review",
    "resolution_reason": "these two approaches have not resolved this yet",
}


def _stopped(concern: ConcernP) -> bool:
    """Tell whether two supported unsuccessful repair cycles stopped automatic repair."""
    return sum(c.outcome == "unsuccessful" for c in concern.cycles) >= UNSUCCESSFUL_CYCLE_LIMIT


def after_study(tx: Tx, *, study: JSON) -> None:
    """Completed teaching opens a repair cycle and replaces the open check.

    The open obligation is ``replaced`` (not satisfied) by a later check 24 hours after
    the completion; the immediate fresh check stays a separate session need.
    """
    record = tx.require("concern", study["concern"]["id"], by=OWNER)
    concern = ConcernP.model_validate(record.payload)
    cycles = list(concern.cycles)
    if cycles and cycles[-1].outcome == "pending":  # several explanations, one cycle
        cycles[-1] = cycles[-1].model_copy(
            update={"studies": [*cycles[-1].studies, Ref(**study["ref"])]}
        )
    else:
        cycles.append(
            CycleP(id=new_id(), studies=[Ref(**study["ref"])], verification=None, outcome="pending")
        )
    revised = concern.model_copy(update={"route": "verification", "cycles": cycles})
    tx.put("concern", revised.model_dump(), by=OWNER, id=record.id, base=record.revision)
    for s in study["scope"]:
        recompute_schedule(tx, s["target"], basis=[study["ref"]])


# --- corrected judgments (module design: "Accept a corrected assessment") -----------------

CORRECTED_AWAY = "a corrected judgment no longer supports this; the work done on it is kept"
SUPPORT: dict[str, set[str]] = {"error": {"error"}, "uncertainty": {"not_shown", "cannot_judge"}}


def reconcile_correction(
    tx: Tx,
    *,
    attempt: JSON,
    assessment: JSON,
    results: dict[str, JSON],
    out: evidence.AssessmentOutput,
) -> None:
    """Recompute schedules, concerns and cycles once from the corrected judgment.

    Schedules replay from admission in occurrence order. A concern citing the corrected
    judgment keeps only the scope its effective evidence still supports (superseded when
    none is left); a corrected fresh check re-derives its cycle. A newly supported error
    outside every unresolved concern opens an ordinary error concern.
    """
    view = evidence.attempt_view(tx, attempt)
    for result in results.values():
        recompute_schedule(tx, result["target"], basis=[assessment], correction=True)
    verified: JSON | None = view.get("verification_of")
    bound = verified["concern"]["id"] if verified else None
    for record in tx.current("concern", by=OWNER):
        concern = ConcernP.model_validate(record.payload)
        if not any(b.id == assessment["id"] for b in concern.basis):
            continue
        revised = (
            _recheck_cycle(concern, _observations(results), view)
            if record.id == bound
            else _recheck_support(tx, concern)
        )
        if revised != concern:  # an unchanged concern gets no new revision
            revised = revised.model_copy(update={"basis": [*concern.basis, Ref(**assessment)]})
            tx.put("concern", revised.model_dump(), by=OWNER, id=record.id, base=record.revision)
    covered = {
        pair
        for record in tx.current("concern", by=OWNER)
        if record.payload["status"] in ("open", "paused")
        for pair in _pairs(ConcernP.model_validate(record.payload).scope)
    }
    errors = _scope(_observations(results), {"error"}, exclude=covered)
    if errors:
        _open_concern(
            tx, kind="error", scope=errors, view=view, assessment=assessment, out=out, question=None
        )


def _recheck_support(tx: Tx, concern: ConcernP) -> ConcernP:
    """Keep the scope that the concern's effective evidence still supports."""
    if concern.status not in ("open", "paused"):
        return concern
    observed = evidence.observations_for(tx, {b.id for b in concern.basis})
    supported = {
        (*exact_key(o["target"]), r)
        for o in observed
        if o["outcome"] in SUPPORT[concern.kind]
        and (o["outcome"] != "error" or evidence.supported_error(o))
        for r in o["requirement_ids"]
    }
    scope = [
        s.model_copy(
            update={
                "requirement_ids": [
                    r for r in s.requirement_ids if (s.target.id, s.target.revision, r) in supported
                ]
            }
        )
        for s in concern.scope
    ]
    scope = [s for s in scope if s.requirement_ids]
    if not scope:
        return concern.model_copy(
            update={"status": "superseded", "resolution_reason": CORRECTED_AWAY}
        )
    return concern.model_copy(update={"scope": scope})


def _recheck_cycle(concern: ConcernP, observations: list[JSON], view: JSON) -> ConcernP:
    """Re-derive the outcome of the repair cycle a corrected fresh check verified.

    The latest cycle of an open or settled concern replays its settlement, which can
    reopen it; a paused or superseded concern keeps its status (the learner's pause and
    a changed goal stand), and only a recovery resolves it.
    """
    cycle_id = view["verification_of"]["cycle_id"]
    latest = bool(concern.cycles) and concern.cycles[-1].id == cycle_id
    if latest and concern.status in ("open", "resolved"):  # replay its settlement
        reset = concern.model_copy(
            update={
                "status": "open",
                "route": "verification",
                "resolution_reason": None,
                "cycles": [
                    c.model_copy(update={"outcome": "pending"}) if c.id == cycle_id else c
                    for c in concern.cycles
                ],
            }
        )
        return _after_verification(reset, observations, view)
    outcome = CYCLE_OUTCOME[
        evidence.scope_outcome(observations, [s.model_dump() for s in concern.scope])
    ]
    cycles = [
        c.model_copy(update={"outcome": outcome}) if c.id == cycle_id else c for c in concern.cycles
    ]
    if outcome == "recovered":
        return concern.model_copy(
            update={
                "cycles": cycles,
                "status": "resolved",
                "resolution_reason": "recovered on a fresh check (a corrected judgment)",
            }
        )
    return concern.model_copy(update={"cycles": cycles})


def diagnostic_allowance(tx: Tx, session_id: str, concern_id: str) -> int:
    """Return how many diagnostic requests this session and concern may still use.

    Each criterion of a delivered clarification question is one request, counted when
    its draft is delivered (resuming the same draft does not count again).
    """
    # ponytail: delivery counts as presentation (conservative for the cap); add the
    # reserved/confirmed/uncertain presentation states when burden reports need them.
    in_session = in_concern = 0
    for a in evidence.attempts(tx):
        if a["purpose"] != "clarification":
            continue
        slots = len(content.definition(tx, a["exercise"])["criteria"])
        if a["session"]["id"] == session_id:
            in_session += slots
        if _concern_id(a) == concern_id:
            in_concern += slots
    return DIAGNOSTIC_LIMIT - max(in_session, in_concern)


def _out_of_questions(concern: ConcernP) -> ConcernP:
    """No allowance for the pending question: help under uncertainty, or stop uncertain."""
    if concern.kind == "error":
        return concern.model_copy(update={"question": None, "route": "repair", "focus": None})
    return concern.model_copy(
        update={
            "question": None,
            "status": "paused",
            "resolution_reason": OUT_OF_QUESTIONS,
        }
    )


def next_step(tx: Tx, session_id: str) -> JSON:
    """Choose what this session does next (``bounded-session-1``, slice 2 subset).

    Resume an open draft, then a started study; then the oldest actionable open concern
    in this enrollment (ask, teach, verify, or report a stop); then the next unanswered
    exercise.
    """
    reserved = open_offer(tx, session_id)
    if reserved is not None:
        return {"kind": "resume", "offer": reserved}
    session = session_view(tx, session_id)
    enrollment = tx.require("enrollment", session["enrollments"][0]["id"], by=OWNER)
    goals = {
        exact_key(t)
        for t in enrollment.payload["goal_order"]
        if content.target_hold(tx, t) is None  # a concern on held material waits
    }
    open_ids = {
        r.id
        for r in tx.current("concern", by=OWNER)
        if r.payload["status"] == "open"
        and {exact_key(s["target"]) for s in r.payload["scope"]} <= goals
    }
    for study in evidence.studies(tx):
        if study["status"] == "started" and _concern_id(study) in open_ids:
            return {"kind": "study", "study": study["ref"]}
    for record in tx.current("concern", by=OWNER):
        concern = ConcernP.model_validate(record.payload)
        if (
            concern.status == "open"
            and {exact_key(s.target.model_dump()) for s in concern.scope} <= goals
        ):
            step = _concern_step(tx, session_id, record)
            if step is not None:
                return step
    exercise = choose_exercise(tx, session_id=session_id)
    return {"kind": "exercise", "exercise": exercise} if exercise else {"kind": "none"}


def _concern_step(tx: Tx, session_id: str, record: Record) -> JSON | None:
    concern = ConcernP.model_validate(record.payload)
    # ponytail: scans every attempt and its offer; index by concern if a library grows large.
    for a in evidence.attempts(tx):
        offer = offer_for(tx, a["ref"]["id"])
        if _concern_id(a) == record.id and offer and offer["state"] == "submitted":
            return {"kind": "pending", "attempt": a["ref"]}  # wait for its assessment
    if concern.route == "diagnosis" and concern.question is not None:
        exercise = content.definition(tx, concern.question.exercise.model_dump())
        if len(exercise["criteria"]) <= diagnostic_allowance(tx, session_id, record.id):
            return {"kind": "ask", "concern": _concern_view(record), "exercise": exercise}
        concern = _out_of_questions(concern)
        ref_ = tx.put("concern", concern.model_dump(), by=OWNER, id=record.id, base=record.revision)
        record = tx.at(ref_, by=OWNER)
        if concern.status != "open":
            return None
    view = _concern_view(record)
    kind = {
        "repair": "teach",
        "verification": "verify",
        "content_review": "stopped",
        "assessment_review": "stopped",
    }.get(concern.route)
    return {"kind": kind, "concern": view} if kind else None


# --- read views ----------------------------------------------------------------------


def schedule_view(tx: Tx, target: JSON) -> JSON | None:
    """Return an exact goal revision's current schedule, if it was ever admitted."""
    record = _schedule(tx, target)
    return record.view if record else None


def schedule_history(tx: Tx, target: JSON) -> list[JSON]:
    """Return every revision of an exact goal revision's schedule, oldest first."""
    record = _schedule(tx, target)
    if record is None:
        return []
    return [r.view for r in tx.history("schedule", record.id, by=OWNER)]


def open_concerns(tx: Tx) -> list[JSON]:
    """Return every open concern."""
    return [r.view for r in tx.current("concern", by=OWNER) if r.payload["status"] == "open"]


def pause_concern(tx: Tx, *, concern_id: str, base: int) -> JSON:
    """Pause a concern; its scope, evidence, cycles and diagnostic counts stay."""
    record = tx.require("concern", concern_id, by=OWNER)
    paused = ConcernP.model_validate(record.payload).model_copy(update={"status": "paused"})
    return tx.put("concern", paused.model_dump(), by=OWNER, id=concern_id, base=base)


def concern_ids_for(tx: Tx, attempt: JSON) -> list[str]:
    """Return the concerns an answer's judgments touch, or that cover its targets."""
    view = evidence.attempt_view(tx, attempt)
    exercise = content.definition(tx, view["exercise"])
    targets = {exact_key(t) for t in exercise["targets"]}
    return [
        r.id
        for r in tx.current("concern", by=OWNER)
        if r.payload["origin"]["id"] == attempt["id"]
        or any(exact_key(s["target"]) in targets for s in r.payload["scope"])
    ]


def concern_for(tx: Tx, assessment_id: str) -> JSON | None:
    """Return the concern an accepted assessment opened, continued or settled, if any."""
    for record in tx.current("concern", by=OWNER):
        if any(b["id"] == assessment_id for b in record.payload["basis"]):
            return concern_view(tx, record.id)
    return None


def help_basis(concern: ConcernP) -> Literal["supported", "uncertain", "direct"]:
    """Say what teaching for a concern rests on.

    A supported hypothesis; or several open ones (support under uncertainty); or, with
    no competing cause, the supported error itself.
    """
    if concern.focus:
        return "supported"
    return "uncertain" if len(concern.hypotheses) > 1 else "direct"


def concern_view(tx: Tx, concern_id: str) -> JSON:
    """Return a concern's current revision with every field filled."""
    return _concern_view(tx.require("concern", concern_id, by=OWNER))


def concern_at(tx: Tx, exact: JSON) -> JSON:
    """Return an exact concern revision (for example the one a teaching was written for)."""
    return _concern_view(tx.at(exact, by=OWNER))


def _concern_view(record: Record) -> JSON:
    concern = ConcernP.model_validate(record.payload)
    return {
        "ref": record.ref,
        **concern.model_dump(),
        "help": help_basis(concern),
        "still_uncertain": concern.status == "paused"
        and concern.resolution_reason in (STILL_UNCERTAIN, OUT_OF_QUESTIONS),
    }
