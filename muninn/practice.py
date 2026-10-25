"""Practice: what learning work is needed and how to continue it.

Owns enrollment (goal admission), sessions, offers, selection, concerns and schedules.
Slice 1 schedules capability checks with the simple interval policy: the first later
check 24 hours after a full demonstration. FSRS recall scheduling arrives later.
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict

from muninn import content, evidence
from muninn.library import JSON, Record, new_id, parse_utc, utc, validate_payloads

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
    enrollment_id = session_view(tx, session_id)["enrollments"][0]["id"]
    sessions = {
        r.id
        for r in tx.current("session", by=OWNER)
        if r.payload["enrollments"][0]["id"] == enrollment_id
    }
    for r in tx.current("practice_offer", by=OWNER):
        if r.payload["session"]["id"] in sessions and r.payload["state"] == "reserved":
            return r.view
    return None


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
    answered = {a["exercise"]["id"] for a in evidence.attempts(tx) if a["status"] == "submitted"}
    candidates = [
        e
        for e in content.exercises_for(tx, enrollment.payload["goal_order"])
        if e["ref"]["id"] not in answered
    ]
    position = {target_id: n for n, target_id in enumerate(order)}
    candidates.sort(key=lambda e: min(position.get(t["id"], len(order)) for t in e["targets"]))
    return candidates[0] if candidates else None


def _schedule(tx: Tx, target_id: str) -> Record | None:
    for r in tx.current("schedule", by=OWNER):
        if r.payload["target"]["id"] == target_id:
            return r
    return None


def deliver(tx: Tx, *, session_id: str, exercise: JSON, attempt: JSON) -> JSON:
    """Admit the exercise's targets and reserve the offer for its draft.

    Admission happens only now, for the covered targets; each gets an open initial
    obligation with no due date. Admission gives no credit.
    """
    session = session_view(tx, session_id)
    record = tx.get("enrollment", session["enrollments"][0]["id"], by=OWNER)
    if record is None:
        msg = "the session has no enrollment"
        raise LookupError(msg)
    targets = exercise["targets"]
    covered = {t["id"] for t in targets}
    enrollment = EnrollmentP.model_validate(record.payload)
    entries = [
        e.model_copy(
            update={"state": "active", "admitted_at": tx.now, "basis": [Ref(**exercise["ref"])]}
        )
        if e.target.id in covered and e.state == "unstarted"
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
        existing = _schedule(tx, target["id"])
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
                role="owner",
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
            policy=content.AlgorithmP(**SELECTION_POLICY),
            reason="first exercise in outline order without a submitted answer",
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


# --- reconciling needs with new evidence --------------------------------------------------


def reconcile(tx: Tx, *, attempt: JSON, assessment: JSON, results: dict[str, JSON]) -> None:
    """Apply each target's qualified label to its schedule and concerns, then settle.

    The next check is dated from when the answer happened, never from grading time.
    """
    answered_at = evidence.attempt_view(tx, attempt)["submitted_at"]
    for target_id, result in results.items():
        record = _schedule(tx, target_id)
        if record is None:
            continue
        schedule = ScheduleP.model_validate(record.payload)
        last = record.ref
        for revision in _transition(schedule, result, attempt, assessment, answered_at):
            linked = revision.model_copy(update={"previous": Ref(**last)})
            last = tx.put(
                "schedule", linked.model_dump(), by=OWNER, id=record.id, base=last["revision"]
            )
        if result["label"] == "error":
            _open_concern(tx, result, attempt, assessment)
    _set_offer_state(tx, attempt["id"], "settled")


def _transition(
    schedule: ScheduleP,
    result: JSON,
    attempt: JSON,
    assessment: JSON,
    answered_at: str | None,
) -> list[ScheduleP]:
    label = result["label"]
    common: dict[str, Any] = {"basis": [Ref(**assessment)], "hold_reason": None}
    due = utc(parse_utc(answered_at) + FIRST_CHECK) if answered_at else None
    if label in ("independent", "helped") and due is None:
        return [
            schedule.model_copy(
                update={
                    **common,
                    "need": "held",
                    "due_at": None,
                    "reason": f"{label} demonstration at an unknown time",
                    "hold_reason": "answer time unknown; a later check needs a known start",
                }
            )
        ]
    if label == "independent" and schedule.obligation.kind == "initial":
        successor = ObligationP(
            id=new_id(), kind="later", origin=[Ref(**attempt)], status="open", successor_id=None
        )
        consumed = schedule.model_copy(
            update={
                **common,
                "reason": "first independent demonstration",
                "obligation": schedule.obligation.model_copy(
                    update={"status": "consumed", "successor_id": successor.id}
                ),
                "consumed_by": Ref(**attempt),
            }
        )
        return [
            consumed,
            consumed.model_copy(
                update={
                    "need": "independent_check",
                    "due_at": due,
                    "reason": "first later check 24 hours after the demonstration",
                    "obligation": successor,
                    "consumed_by": None,
                }
            ),
        ]
    if label in ("independent", "helped"):
        return [
            schedule.model_copy(
                update={
                    **common,
                    "need": "independent_check",
                    "due_at": due,
                    "reason": "independent retrieval 24 hours after helped practice"
                    if label == "helped"
                    else "independent check 24 hours later",
                }
            )
        ]
    if label == "error":
        return [
            schedule.model_copy(update={**common, "need": "repair", "reason": "supported error"})
        ]
    outcomes = {o["outcome"] for o in result.get("observations", [])}
    if outcomes == {"demonstrated"} and due is not None:  # shown; independence unknown
        return [
            schedule.model_copy(
                update={
                    **common,
                    "need": "independent_check",
                    "due_at": due,
                    "reason": "independent check 24 hours after an answer whose help is unknown",
                }
            )
        ]
    need: Need = "clarify" if "cannot_judge" in outcomes else schedule.need
    return [schedule.model_copy(update={**common, "need": need, "reason": "evidence incomplete"})]


def _open_concern(tx: Tx, result: JSON, attempt: JSON, assessment: JSON) -> None:
    erred = [o for o in result.get("observations", []) if o["outcome"] == "error"]
    concern = ConcernP(
        origin=Ref(**attempt),
        scope=[
            ConcernScopeP(
                target=Ref(**result["target"]),
                requirement_ids=sorted({rid for o in erred for rid in o["requirement_ids"]}),
            )
        ],
        previous_concern=None,
        status="open",
        route="repair",
        basis=[Ref(**assessment)],
        resolution_reason=None,
    )
    tx.put("concern", concern.model_dump(), by=OWNER)


# --- read views ----------------------------------------------------------------------


def schedule_view(tx: Tx, target_id: str) -> JSON | None:
    """Return a target's current schedule, if it was ever admitted."""
    record = _schedule(tx, target_id)
    return record.view if record else None


def schedule_history(tx: Tx, target_id: str) -> list[JSON]:
    """Return every revision of a target's schedule, oldest first."""
    record = _schedule(tx, target_id)
    if record is None:
        return []
    return [r.view for r in tx.history("schedule", record.id, by=OWNER)]


def open_concerns(tx: Tx) -> list[JSON]:
    """Return every open concern."""
    return [r.view for r in tx.current("concern", by=OWNER) if r.payload["status"] == "open"]
