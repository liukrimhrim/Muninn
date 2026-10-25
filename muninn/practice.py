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
    """Apply each target's qualified label to its schedule and concerns, then settle.

    The next check is dated from when the answer happened, never from grading time.
    ``question`` is the saved clarification exercise when ``wants_question`` said yes.
    """
    view = evidence.attempt_view(tx, attempt)
    answered_at = view["submitted_at"]
    offer = offer_for(tx, attempt["id"])
    roles = {s["target"]["id"]: s["role"] for s in offer["slots"]} if offer else {}
    for target_id, result in results.items():
        record = _schedule(tx, target_id)
        if record is None:
            continue
        schedule = ScheduleP.model_validate(record.payload)
        revisions = (
            _extra_transition(schedule, result, assessment)
            if roles.get(target_id) == "extra"
            else _transition(schedule, result, attempt, assessment, answered_at)
        )
        last = record.ref
        for revision in revisions:
            linked = revision.model_copy(update={"previous": Ref(**last)})
            last = tx.put(
                "schedule", linked.model_dump(), by=OWNER, id=record.id, base=last["revision"]
            )
    _update_concerns(
        tx, view=view, assessment=assessment, results=results, out=out, question=question
    )
    _set_offer_state(tx, attempt["id"], "settled")


def _extra_transition(schedule: ScheduleP, result: JSON, assessment: JSON) -> list[ScheduleP]:
    """Keep every due date on a focused check; only a supported error changes the need."""
    if result["label"] != "error":
        return []
    return [
        schedule.model_copy(
            update={
                "basis": [Ref(**assessment)],
                "need": "repair",
                "reason": "supported error on a focused check",
                "hold_reason": None,
            }
        )
    ]


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
    misread = any(
        o["outcome"] == "error" and not evidence.supported_error(o)
        for o in result.get("observations", [])
    )
    reason = "likely misread; not counted as a mistake" if misread else "evidence incomplete"
    return [schedule.model_copy(update={**common, "need": need, "reason": reason})]


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
        {**o, "target_id": target_id}
        for target_id, result in results.items()
        for o in result.get("observations", [])
    ]


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
    observations: list[JSON],
    targets: dict[str, JSON],
    outcomes: set[str],
    *,
    exclude: set[tuple[str, str]],
) -> list[ConcernScopeP]:
    wanted: dict[str, set[str]] = {}
    for o in observations:
        if o["outcome"] not in outcomes or (
            o["outcome"] == "error" and not evidence.supported_error(o)
        ):
            continue
        wanted.setdefault(o["target_id"], set()).update(
            r for r in o["requirement_ids"] if (o["target_id"], r) not in exclude
        )
    return [
        ConcernScopeP(target=Ref(**targets[t]), requirement_ids=sorted(reqs))
        for t, reqs in wanted.items()
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
    targets = {t: r["target"] for t, r in results.items()}
    handled: set[tuple[str, str]] = set()
    bound = _concern_id(view)
    if bound:
        record = tx.require("concern", bound, by=OWNER)
        concern = ConcernP.model_validate(record.payload)
        handled = {(s.target.id, r) for s in concern.scope for r in s.requirement_ids}
        if view["purpose"] == "clarification":
            concern = _after_clarification(concern, observations, out, question)
        else:
            concern = _after_verification(concern, observations, view)
        concern = concern.model_copy(update={"basis": [*concern.basis, Ref(**assessment)]})
        tx.put("concern", concern.model_dump(), by=OWNER, id=record.id, base=record.revision)
        question = None
    errors = _scope(observations, targets, {"error"}, exclude=handled)
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
        unsure = _scope(observations, targets, {"not_shown", "cannot_judge"}, exclude=handled)
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
    wanted = {(s.target.id, r) for s in scope for r in s.requirement_ids}
    for record in tx.current("concern", by=OWNER):
        old = ConcernP.model_validate(record.payload)
        if old.status in ("open", "paused") and wanted & {
            (s.target.id, r) for s in old.scope for r in s.requirement_ids
        }:
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
    merged: dict[str, tuple[Ref, set[str]]] = {}
    for s in (s for scope in scopes for s in scope):
        merged.setdefault(s.target.id, (s.target, set()))[1].update(s.requirement_ids)
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
    due = utc(parse_utc(study["completed_at"]) + FIRST_CHECK)
    for s in concern.scope:
        existing = _schedule(tx, s.target.id)
        if existing is None:
            continue
        schedule = ScheduleP.model_validate(existing.payload)
        successor = ObligationP(
            id=new_id(),
            kind="later",
            origin=[Ref(**study["ref"])],
            status="open",
            successor_id=None,
        )
        replaced = schedule.model_copy(
            update={
                "basis": [Ref(**study["ref"])],
                "previous": Ref(**existing.ref),
                "reason": "replaced after teaching",
                "obligation": schedule.obligation.model_copy(
                    update={"status": "replaced", "successor_id": successor.id}
                ),
                "consumed_by": None,
                "hold_reason": None,
            }
        )
        last = tx.put(
            "schedule", replaced.model_dump(), by=OWNER, id=existing.id, base=existing.revision
        )
        current = replaced.model_copy(
            update={
                "previous": Ref(**last),
                "need": "independent_check",
                "due_at": due,
                "reason": "independent check 24 hours after completed teaching",
                "obligation": successor,
            }
        )
        tx.put("schedule", current.model_dump(), by=OWNER, id=existing.id, base=last["revision"])


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
    goals = {t["id"] for t in enrollment.payload["goal_order"]}
    open_ids = {
        r.id
        for r in tx.current("concern", by=OWNER)
        if r.payload["status"] == "open"
        and {s["target"]["id"] for s in r.payload["scope"]} <= goals
    }
    for study in evidence.studies(tx):
        if study["status"] == "started" and _concern_id(study) in open_ids:
            return {"kind": "study", "study": study["ref"]}
    for record in tx.current("concern", by=OWNER):
        concern = ConcernP.model_validate(record.payload)
        if concern.status == "open" and {s.target.id for s in concern.scope} <= goals:
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


def pause_concern(tx: Tx, *, concern_id: str, base: int) -> JSON:
    """Pause a concern; its scope, evidence, cycles and diagnostic counts stay."""
    record = tx.require("concern", concern_id, by=OWNER)
    paused = ConcernP.model_validate(record.payload).model_copy(update={"status": "paused"})
    return tx.put("concern", paused.model_dump(), by=OWNER, id=concern_id, base=base)


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
