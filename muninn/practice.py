"""Practice: what learning work is needed and how to continue it.

Owns enrollment (goal admission), sessions, offers, selection, concerns and schedules.
Two scheduling paths: capability checks follow the simple interval policy (a check 24
hours after first or helped practice, then seven days after each on-time independent
check); directly reviewed recall items follow FSRS through a private adapter.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import timedelta
from itertools import combinations
from typing import TYPE_CHECKING, Any, Literal

import fsrs
from pydantic import BaseModel, ConfigDict

from muninn import content, evidence
from muninn.library import JSON, Record, exact_key, new_id, parse_utc, utc, validate_payloads

if TYPE_CHECKING:
    from muninn.library import Tx

OWNER = "practice"

FIRST_CHECK_HOURS = 24
LATER_CHECK_DAYS = 7
FIRST_CHECK = timedelta(hours=FIRST_CHECK_HOURS)
LATER_CHECK = timedelta(days=LATER_CHECK_DAYS)
POLICY: JSON = {
    "name": "capability-interval",
    "version": 2,
    "parameters": {
        "first_check_hours": FIRST_CHECK_HOURS,
        "later_check_days": LATER_CHECK_DAYS,
        "independence_claim": evidence.QUALIFICATION,
        "qualification_claim": evidence.DELAYED_CHECK,
    },
}
SELECTION_POLICY: JSON = {
    "name": "bounded-session",
    "version": 1,
    "parameters": {"budget": "budget-elapsed-1", "plan_candidates": 12},
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


class UnmetP(_Strict):
    """A need a session left unserved, and why (everyday-learning-design.md section 4)."""

    target: Ref
    need: str
    waiting_since: str | None
    reason: str


class SessionP(_Strict):
    """One sitting of practice over an ordered scope of enrollments."""

    enrollments: list[Ref]
    budget_seconds: int | None
    started_at: str
    ended_at: str | None
    status: Literal["open", "ended"]
    stop_reason: str | None
    next_action: str | None
    time_evidence: list[evidence.TimeEvidenceP]
    unmet: list[UnmetP] = []


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


class NextOfferP(_Strict):
    """When the next check may be offered, kept apart from its original due time."""

    at: str | None
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
    next_offer: NextOfferP | None = None


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


class ServedP(_Strict):
    """A pending need a selected exercise serves."""

    target: Ref
    need: str
    waiting_since: str | None


class LeftP(_Strict):
    """A pending need the selection passed over, and why."""

    target: Ref
    reason: str
    confirm_closed: bool = False
    """It waits only for the learner to confirm earlier views are closed."""


class SelectionP(_Strict):
    """Why an exercise was chosen."""

    session: Ref
    exercise: Ref
    policy: content.AlgorithmP
    reason: str
    served: list[ServedP] = []
    left: list[LeftP] = []
    cost_seconds: int | None = None
    remaining_seconds: int | None = None
    override: bool = False


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
    """Check every Practice-owned record against its payload contract.

    Across records: at most one live (reserved or submitted, unrevoked) owner per check.
    """
    errors = validate_payloads(records, OWNER, PAYLOADS)
    return errors or _one_live_owner(records)


def _one_live_owner(records: list[Record]) -> list[str]:
    latest: dict[tuple[str, str], Record] = {}
    for r in records:
        if r.kind in ("practice_offer", "schedule"):
            key = (r.kind, r.id)
            if key not in latest or r.revision > latest[key].revision:
                latest[key] = r
    revoked = {
        e["offer"]["id"]
        for r in records
        if r.kind == "schedule"
        for e in r.payload.get("check_effects", [])
        if e["revokes_reservation"]
    }
    owners: dict[tuple[str, str], int] = {}
    for (kind, offer_id), r in latest.items():
        if kind != "practice_offer" or r.payload["state"] not in ("reserved", "submitted"):
            continue
        if offer_id in revoked:
            continue
        for slot in r.payload["slots"]:
            if slot["role"] == "owner":
                key = (slot["obligation_id"], slot["target"]["id"])
                owners[key] = owners.get(key, 0) + 1
    return [
        f"two live offers own check {obligation} of target {target}"
        for (obligation, target), n in owners.items()
        if n > 1
    ]


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


def start_session(tx: Tx, *, enrollment_ids: list[str], budget_seconds: int | None) -> JSON:
    """Open a practice session over enrollments in the learner's chosen order."""
    refs: list[Ref] = []
    for enrollment_id in enrollment_ids:
        enrollment = tx.get("enrollment", enrollment_id, by=OWNER)
        if enrollment is None:
            msg = f"no enrollment {enrollment_id}"
            raise LookupError(msg)
        refs.append(Ref(**enrollment.ref))
    if not refs:
        msg = "a session needs at least one curriculum"
        raise ValueError(msg)
    if budget_seconds is not None and budget_seconds <= 0:
        msg = "a session budget must be positive"
        raise ValueError(msg)
    payload = SessionP(
        enrollments=refs,
        budget_seconds=budget_seconds,
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


def change_budget(tx: Tx, *, session_id: str, base: int, budget_seconds: int | None) -> JSON:
    """Change an open session's budget; the time already spent stays as it was."""
    record = tx.require("session", session_id, by=OWNER)
    session = SessionP.model_validate(record.payload)
    if session.status != "open":
        msg = "this session has ended"
        raise ValueError(msg)
    if budget_seconds is not None and budget_seconds <= 0:
        msg = "a session budget must be positive"
        raise ValueError(msg)
    revised = session.model_copy(update={"budget_seconds": budget_seconds})
    return tx.put("session", revised.model_dump(), by=OWNER, id=session_id, base=base)


def end_session(tx: Tx, *, session_id: str, base: int, stop_reason: str, elapsed_ms: int) -> JSON:
    """Close a session and save what it left unserved, with reasons.

    An unfinished draft stays resumable, never a failure; the schedules are untouched.
    """
    record = tx.require("session", session_id, by=OWNER)
    session = SessionP.model_validate(record.payload)
    unmet = [
        UnmetP(target=Ref(**p.target), need=p.need, waiting_since=p.waiting_since, reason=why)
        for p, why in _unserved(tx, session_id, remaining(session.model_dump(), elapsed_ms))
    ]
    ended = session.model_copy(
        update={"status": "ended", "ended_at": tx.now, "stop_reason": stop_reason, "unmet": unmet}
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
    """Return the latest unsubmitted draft offered in this session's scope, from any session.

    A draft stays bound to the session it was offered in; a later session resumes
    it rather than offering the same obligation again.
    """
    return _scope_offer(tx, session_id, "reserved")


def waiting_offer(tx: Tx, session_id: str) -> JSON | None:
    """Return a submitted answer in this session's scope still waiting for its assessment."""
    return _scope_offer(tx, session_id, "submitted")


def _scope_offer(tx: Tx, session_id: str, state: str) -> JSON | None:
    scope = {e["id"] for e in session_view(tx, session_id)["enrollments"]}
    sessions = {
        r.id
        for r in tx.current("session", by=OWNER)
        if scope & {e["id"] for e in r.payload["enrollments"]}
    }
    found: JSON | None = None
    for r in tx.current("practice_offer", by=OWNER):
        if r.payload["session"]["id"] in sessions and r.payload["state"] == state:
            if state == "reserved" and _held_draft(tx, r.payload["attempt"]):
                continue  # the draft is kept; it resumes if its material is settled again
            if found is None or r.payload["reserved_at"] >= found["reserved_at"]:
                found = r.view
    return found


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


def _schedule(tx: Tx, target: JSON) -> Record | None:
    """Return the schedule of one exact goal revision (each contract has its own)."""
    for r in tx.current("schedule", by=OWNER):
        if exact_key(r.payload["target"]) == exact_key(target):
            return r
    return None


def _live_owner(tx: Tx, target: JSON, obligation_id: str) -> JSON | None:
    """Return the reserved or submitted offer that owns this obligation, if any."""
    for r in tx.current("practice_offer", by=OWNER):
        if r.payload["state"] not in ("reserved", "submitted"):
            continue
        for slot in r.payload["slots"]:
            if (
                slot["role"] == "owner"
                and slot["obligation_id"] == obligation_id
                and exact_key(slot["target"]) == exact_key(target)
                and not revoked(tx, r.id)
            ):
                return r.view
    return None


def offer_at(schedule: JSON) -> tuple[bool, str | None]:
    """Return (known, time) from which a schedule's open obligation can be offered as a check.

    An initial obligation with no answer yet is offerable at once (``None``); otherwise
    the later of the due time and the next-offer deferral. Unknown means an earlier
    answer-bearing view may still be open.
    """
    deferred = schedule.get("next_offer")
    if deferred is not None:
        return (deferred["at"] is not None, deferred["at"])
    return (True, schedule["due_at"])


def role_now(tx: Tx, target: JSON) -> Literal["owner", "extra"]:
    """Decide whether a delivery may own this target's current check (lifecycle section 4).

    It owns it only when no live offer already does and the check is offerable now;
    otherwise the answer is extra: it keeps its evidence and never consumes the check.
    """
    record = _schedule(tx, target)
    if record is None:
        return "owner"  # admitted by this delivery
    if record.payload["need"] == "held" or _live_owner(
        tx, target, record.payload["obligation"]["id"]
    ):
        return "extra"
    known, at = offer_at(record.payload)
    return "owner" if known and (at is None or at <= tx.now) else "extra"


def deliver(  # noqa: PLR0913 - one keyword per delivery decision
    tx: Tx,
    *,
    session_id: str,
    exercise: JSON,
    attempt: JSON,
    role: Literal["owner", "extra"] | None = None,
    reason: str,
    policy: JSON = SELECTION_POLICY,
    selection: JSON | None = None,
) -> JSON:
    """Admit the exercise's new targets and reserve the offer for its draft.

    Admission happens only now, for the covered targets, in every enrollment of the
    session that selected them; each gets an open initial obligation with no due date.
    Admission gives no credit. Each slot owns its target's check only when ``_role``
    allows; a focused clarification or verification is always ``extra``.
    """
    session = session_view(tx, session_id)
    targets = exercise["targets"]
    covered = {exact_key(t) for t in targets}
    for scoped in session["enrollments"]:
        record = tx.require("enrollment", scoped["id"], by=OWNER)
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
        slot_role = role or role_now(tx, target)
        existing = _schedule(tx, target)
        if existing is None:
            schedule = _admitted(tx, target, exercise)
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
                role=slot_role,
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
            **(selection or {}),
        ).model_dump(),
        by=OWNER,
    )
    return offer


def _admitted(tx: Tx, target: JSON, exercise: JSON) -> ScheduleP:
    """Return the first schedule of a newly admitted target: an open initial check.

    A recall-mode goal is a directly reviewed item and follows FSRS; every other mode
    follows the capability intervals. The schedule keeps its path for good.
    """
    recall = content.definition(tx, target)["mode"] == "recall"
    return ScheduleP(
        target=Ref(**target),
        type="recall" if recall else "capability",
        policy=content.AlgorithmP(**(RECALL_POLICY if recall else POLICY)),
        state_format=CARD_FORMAT if recall else "none",
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
    "parameters": {
        "capability_policy": POLICY["name"],
        "first_check_hours": FIRST_CHECK_HOURS,
        "later_check_days": LATER_CHECK_DAYS,
    },
}
REANCHORED = "reanchored from a real later check"
INVALIDATED = "its generating answer no longer qualifies after a corrected judgment"
LATER_PENDING = "a later answer is still being assessed"
TOO_SOON = "answered too soon after seeing the answer; this check stays due"
AWAITING_RATING = "waiting for your recall rating"
VIEW_OPEN = "an earlier view of the answer may still be open"
DEFERRED = "offered 24 hours after the latest relevant exposure"


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
    card: str | None = None
    next_offer: NextOfferP | None = None

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


def _after(at: str, interval: timedelta) -> str:
    return utc(parse_utc(at) + interval)


def _qualifies(tx: Tx, target: JSON, answer: JSON) -> bool:
    """Tell whether an answer was far enough from relevant exposure (``DELAYED_CHECK``)."""
    gap = evidence.delay(tx, target, before=answer["at"], exclude=answer["attempt"]["id"])
    return gap.state(answer["at"]) == "eligible"


def _fold_owned(tx: Tx, target: JSON, state: _Replay, answer: JSON, ids: Successors) -> None:
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
    elif label == "independent" and state.current.kind == "initial" and state.due_at is None:
        state.close(
            "consumed",
            _later(attempt, ids),
            basis=basis,
            reason="first independent demonstration",
            consumed_by=attempt,
        )
        state.set("independent_check", "first later check 24 hours after the demonstration", basis)
        state.due_at = _after(at, FIRST_CHECK)
    elif label == "independent":
        if state.due_at is not None and at < state.due_at:
            return  # an extra check before the due time: the due date stays as it was
        if not _qualifies(tx, target, answer):
            state.set(state.need, TOO_SOON, basis)
            return
        state.close(
            "consumed", _later(attempt, ids), basis=basis, reason="met on time", consumed_by=attempt
        )
        state.set("independent_check", "next check seven days after an on-time check", basis)
        state.due_at = _after(at, LATER_CHECK)
    elif label == "helped":
        state.set(
            "independent_check", "independent retrieval 24 hours after helped practice", basis
        )
        state.due_at = _after(at, FIRST_CHECK)
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
            state.due_at = _after(at, FIRST_CHECK)
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


def _fold_descendant(  # noqa: PLR0913 - the answer, its offer and the replay so far
    tx: Tx,
    target: JSON,
    state: _Replay,
    answer: JSON,
    *,
    offer: JSON,
    offered_due: str | None,
    ids: Successors,
) -> None:
    """Apply an owned answer whose opportunity no longer exists (descendant-correction-1).

    It re-anchors only as an independent demonstration at or after both its offered due
    time and the corrected due time, far enough from relevant exposure; the next check
    is a week later, or a day later when corrected history makes it the first
    demonstration. Otherwise it has no scheduling effect, though a supported error
    still asks for repair.
    """
    at: str | None = answer["at"]
    basis = [Ref(**answer["assessment"])]
    on_time = at is not None and all(d is None or at >= d for d in (state.due_at, offered_due))
    if (
        answer["label"] == "independent"
        and at is not None
        and on_time
        and _qualifies(tx, target, answer)
    ):
        # no earlier anchor in corrected history: neither a later check nor a dated one
        first = state.current.kind == "initial" and state.due_at is None
        state.close(
            "replaced", _later(Ref(**answer["attempt"]), ids), basis=basis, reason=REANCHORED
        )
        state.set("independent_check", REANCHORED, basis)
        state.due_at = _after(at, FIRST_CHECK if first else LATER_CHECK)
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


# --- the recall adapter: pinned py-fsrs, private to Practice ----------------------------

CARD_FORMAT = "py-fsrs-6.3.2/card-json"
_ENGINE = fsrs.Scheduler(learning_steps=(), relearning_steps=(), enable_fuzzing=False)
RECALL_POLICY: JSON = {
    "name": "fsrs-recall",
    "version": 1,
    "parameters": {
        "engine": "py-fsrs 6.3.2 (FSRS-6)",
        "weights": [str(w) for w in _ENGINE.parameters],
        "desired_retention": str(_ENGINE.desired_retention),
        "learning_steps": [],
        "relearning_steps": [],
        "fuzzing": False,
        "rating_labels": evidence.RATING_LABELS,
        "qualification_claim": evidence.DELAYED_CHECK,
    },
}
_RATING = {
    "again": fsrs.Rating.Again,
    "hard": fsrs.Rating.Hard,
    "good": fsrs.Rating.Good,
    "easy": fsrs.Rating.Easy,
}


CHOICES: dict[str, list[str]] = {
    "independent": ["forgot", "difficult", "remembered", "easy"],
    "error": ["forgot"],
}
"""The ratings an owned recall answer's judgment supports; a failed recall is never Hard."""
RATEABLE: dict[str, set[str]] = {
    label: {evidence.RATING_LABELS["parameters"][c] for c in choices}
    for label, choices in CHOICES.items()
}
"""The same rule as FSRS ratings (forgot is Again)."""


def _fsrs_review(card: str | None, rating: str, at: str) -> tuple[str, str]:
    """Review a card (None: a new one) and return the new card text and its due time."""
    before = (
        fsrs.Card.from_dict(json.loads(card)) if card else fsrs.Card(card_id=1, due=parse_utc(at))
    )
    after, _log = _ENGINE.review_card(before, _RATING[rating], parse_utc(at))
    return json.dumps(after.to_dict(), sort_keys=True), utc(after.due)


def _effective_review(tx: Tx, target: JSON, state: _Replay, answer: JSON) -> JSON | None:
    """Return the learner's rating of an owned recall answer, if it can enter the stream.

    Its rating must fit the effective judgment (a now-helped or unresolved answer, or
    "remembered" on a now-error answer, cannot), and a later review must be far enough
    from relevant exposure. An ineligible review stays saved; nothing replaces it.
    """
    review = evidence.review_for(tx, answer["attempt"]["id"], target)
    if review is None or review["rating"] not in RATEABLE.get(answer["label"] or "", set()):
        return None
    if state.current.kind == "later" and not _qualifies(tx, target, answer):
        return None
    return review


def _fold_recall(tx: Tx, target: JSON, state: _Replay, answer: JSON, ids: Successors) -> bool:
    """Apply one owned recall answer; return True when it still waits for a rating."""
    review = _effective_review(tx, target, state, answer)
    basis = [Ref(**answer["assessment"])]
    if review is not None:
        state.card, due = _fsrs_review(state.card, review["rating"], answer["at"])
        state.close(
            "consumed",
            _later(Ref(**answer["attempt"]), ids),
            basis=[Ref(**review["ref"])],
            reason=f"reviewed: {review['choice']}",
            consumed_by=Ref(**answer["attempt"]),
        )
        need: Need = "repair" if answer["label"] == "error" else "independent_check"
        state.set(need, "next review from the recall schedule", [Ref(**review["ref"])])
        state.due_at = due
        return False
    if answer["label"] == "error":
        state.set("repair", "supported error", basis)
    elif answer["label"] == "helped":
        state.set(state.need, "helped; a hint cannot stand in for a recall review", basis)
    elif answer["label"] != "independent":
        state.set(state.need, "evidence incomplete", basis)
    return answer["label"] in RATEABLE and (
        state.current.kind == "initial" or _qualifies(tx, target, answer)
    )


NO_RATING: dict[str, str] = {
    "helped": "help was used, so this answer cannot stand in for a review",
    "unresolved": "the answer did not settle it either way",
}


def rating_choices(
    tx: Tx, attempt_id: str, target: JSON, *, under_review: bool = False
) -> tuple[list[str], str | None]:
    """Return the recall ratings an answer may take for one target, or why it takes none.

    Only an owned answer on a recall schedule can be rated, and only with a rating its
    judgment supports: anything for an independent recall, "forgot" for an error. Help,
    an unsettled judgment, extra practice, or a later review too soon after seeing the
    answer take no rating; no review is ever made for them. While the judgment itself is
    under review (``under_review``) a disputed grade cannot carry a rating either.
    """
    record = _schedule(tx, target)
    if record is None or record.payload["type"] != "recall":
        return [], "this goal is not a recall item"
    if under_review:
        return [], "its judgment is being reviewed"
    offer, slot = _slots(tx, target).get(attempt_id, (None, None))
    if offer is None or slot is None or slot["role"] != "owner" or revoked(tx, offer["ref"]["id"]):
        return [], "this was extra practice, not a scheduled review"
    label = evidence.answer_label(tx, attempt_id, target)
    why = _rating_blocked(tx, attempt_id, target, record, slot=slot, label=label)
    return ([], why) if why or label is None else (CHOICES[label], None)


def _rating_blocked(  # noqa: PLR0913 - the owned slot and its judgment
    tx: Tx, attempt_id: str, target: JSON, record: Record, *, slot: JSON, label: str | None
) -> str | None:
    if label is None:
        return "the answer is not graded yet"
    if label not in CHOICES:
        return NO_RATING.get(label, "the answer did not show it")
    rated = evidence.review_for(tx, attempt_id, target) is not None
    current = record.payload["obligation"]
    if not rated and slot["obligation_id"] != current["id"]:
        return "its review was already made"
    answer = {
        "attempt": {"id": attempt_id},
        "at": evidence.attempt_view(tx, attempt_id=attempt_id)["submitted_at"],
    }
    later = current["kind"] == "later" if not rated else _was_later(tx, record, slot)
    if later and not _qualifies(tx, target, answer):
        return "it came too soon after seeing the answer"
    return None


def _was_later(tx: Tx, record: Record, slot: JSON) -> bool:
    """Tell whether the obligation a slot owned was a later check (not the first review)."""
    return any(
        r.payload["obligation"]["id"] == slot["obligation_id"]
        and r.payload["obligation"]["kind"] == "later"
        for r in tx.history("schedule", record.id, by=OWNER)
    )


def review_binding(
    tx: Tx, *, attempt_id: str, target: JSON, choice: str, under_review: bool
) -> JSON:
    """Validate an owned recall review before Evidence saves it; return its offer.

    Raises ``ValueError`` saying why the answer cannot be rated (lifecycle section 4).
    """
    choices, why = rating_choices(tx, attempt_id, target, under_review=under_review)
    if choice not in choices:
        msg = f"this answer cannot be rated {choice!r}: {why or 'its judgment does not support it'}"
        raise ValueError(msg)
    offer, _slot = _slots(tx, target)[attempt_id]
    return offer


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


def _study(state: _Replay, event: JSON, ids: Successors, *, recall: bool) -> None:
    """Completed teaching replaces a capability check; a recall card is left as it is."""
    study = Ref(**event["study"])
    if recall:
        need: Need = "independent_check" if state.need == "repair" else state.need
        state.set(need, "teaching completed; reviews follow the recall schedule", [study])
        return
    state.close("replaced", _later(study, ids), basis=[study], reason="replaced after teaching")
    state.set("independent_check", "independent check 24 hours after completed teaching", [study])
    state.due_at = _after(event["at"], FIRST_CHECK)


def _replay(tx: Tx, target: JSON, history: list[JSON]) -> _Replay:  # noqa: C901 - one fold
    """Replay one exact target's effective history from admission, in occurrence order."""
    state = _start(history)
    recall = history[0]["type"] == "recall"
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
    later_pending = awaiting = False
    assessed: set[str] = set()
    events = evidence.chronology(tx, target)
    for event in events:
        if event["kind"] == "study":
            _study(state, event, ids, recall=recall)
            continue
        offer, slot = slots.get(event["attempt"]["id"], (None, None))
        owned = bool(
            offer and slot and slot["role"] == "owner" and offer["ref"]["id"] not in revocations
        )
        used = {o.id for o in state.lineage[:-1]}
        if owned and not recall and slot and slot["obligation_id"] in used:
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
        if recall:
            awaiting = _fold_recall(tx, target, state, event, ids)
        elif slot["obligation_id"] == state.current.id:
            _fold_owned(tx, target, state, event, ids)
        else:
            due = dues.get(slot["schedule_at_offer"]["revision"])
            _fold_descendant(tx, target, state, event, offer=offer, offered_due=due, ids=ids)
    if state.need != "repair":  # never hide a supported current error
        if later_pending:
            state.hold_reason, state.need = LATER_PENDING, "held"
        elif awaiting:
            state.hold_reason, state.need = AWAITING_RATING, "held"
    _unsettled_owners(state, slots, assessed, revocations)
    state.next_offer = _deferral(tx, target, state, answered=bool(events))
    return state


def _deferral(tx: Tx, target: JSON, state: _Replay, *, answered: bool) -> NextOfferP | None:
    """Defer the next offer to 24 hours after the latest relevant exposure.

    The due time itself never moves for an exposure. A first practice with no answer
    yet is not a delayed check, so nothing defers it.
    """
    if state.current.kind == "initial" and not answered:
        return None
    gap = evidence.delay(tx, target)
    if not gap.known:
        return NextOfferP(at=None, basis=[Ref(**r) for r in gap.open], reason=VIEW_OPEN)
    eligible = gap.eligible_at
    if eligible and (state.due_at is None or eligible > state.due_at):
        return NextOfferP(at=eligible, basis=[Ref(**r) for r in gap.basis], reason=DEFERRED)
    return None


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
            "engine_state": {"card": state.card} if state.card else {},
            "next_offer": state.next_offer,
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


# --- what to do next: bounded-session-1 (everyday-learning-design.md section 4) ----------

PLAN_CANDIDATES = 12
NO_EXERCISE = "no usable exercise can check this yet"
TOO_LONG = "too long for the time left"
NOT_REACHED = "not reached in this session"
TIME_UP = "the session's time ran out"
WAITING_GRADE = "waiting for the grade of an answer"
REPAIR_PAUSED = "its repair is paused"
UNKNOWN_LENGTH = "includes an explanation of unknown length"


type Goals = dict[tuple[str, int], tuple[JSON, tuple[int, int, str], str]]
"""Selected exact goals in a session's scope: (ref, curriculum/goal order, entry state)."""


@dataclass(frozen=True)
class Pending:
    """One exact goal's pending need in a session's scope (ready unless ``blocked``)."""

    target: JSON
    need: str
    waiting_since: str | None
    order: tuple[int, int, str]
    blocked: str | None = None
    view_open: bool = False


def full_cost(exercise: JSON) -> int:
    """Return an exercise's full estimated cost in seconds: setup, answering and feedback."""
    seconds = exercise["expected_seconds"]
    return int(seconds["setup"] + seconds["answer"] + seconds["feedback"])


def _goals(tx: Tx, enrollments: list[JSON]) -> Goals:
    """Return each selected exact goal in scope: (ref, order, best entry state).

    A goal shared by several curricula takes its earliest position and is active when
    any active enrollment practises it; a paused or archived enrollment adds nothing.
    """
    found: dict[tuple[str, int], tuple[JSON, tuple[int, int, str], str]] = {}
    for n, scoped in enumerate(enrollments):
        record = tx.require("enrollment", scoped["id"], by=OWNER)
        if record.payload["status"] != "active":
            continue
        for m, entry in enumerate(record.payload["practice"]):
            key = exact_key(entry["target"])
            state = entry["state"]
            if key in found:
                ref_, order, before = found[key]
                state = "active" if "active" in (before, state) else before
                found[key] = (ref_, order, state)
            else:
                found[key] = (entry["target"], (n, m, entry["target"]["id"]), state)
    return found


def _waiting_since(tx: Tx, record: Record) -> str | None:
    """Return when the current need started waiting.

    That is its original due time, else when it opened. A check that replaced an unmet
    one after teaching keeps the unmet check's waiting time (lifecycle section 4).
    """
    history = [r.payload for r in tx.history("schedule", record.id, by=OWNER)]
    obligation = record.payload["obligation"]["id"]
    while True:
        replaced = next(
            (
                h["obligation"]["id"]
                for h in history
                if h["obligation"]["status"] == "replaced"
                and h["obligation"]["successor_id"] == obligation
            ),
            None,
        )
        if replaced is None:
            break
        obligation = replaced
    revisions = [
        (h, r.recorded_at)
        for h, r in zip(history, tx.history("schedule", record.id, by=OWNER), strict=True)
        if h["obligation"]["id"] == obligation
    ]
    dues = [h["due_at"] for h, _at in revisions if h["due_at"]]
    if dues:
        return str(min(dues))
    return revisions[0][1] if revisions else None


def pending(tx: Tx, enrollments: list[JSON], now: str) -> tuple[list[Pending], list[str]]:
    """Return the pending checks in scope (ready or blocked) and the times others come due.

    Repairs are served through their concerns; a repair whose concern is paused is
    reported as blocked so it is not forgotten.
    """
    repairing = {
        exact_key(s["target"])
        for r in tx.current("concern", by=OWNER)
        if r.payload["status"] == "open"
        for s in r.payload["scope"]
    }
    found: list[Pending] = []
    upcoming: list[str] = []
    for key, (target, order, state) in _goals(tx, enrollments).items():
        record = _schedule(tx, target)
        if state != "active" or record is None:
            continue
        schedule = record.payload
        need = schedule["need"]
        hold = content.target_hold(tx, target)
        known, at = offer_at(schedule)
        blocked: str | None = None
        if hold is not None:
            blocked = hold.reason
        elif need == "held":
            blocked = schedule["hold_reason"]
        elif need == "repair":
            if key in repairing:
                continue
            blocked = REPAIR_PAUSED
        elif _live_owner(tx, target, schedule["obligation"]["id"]):
            blocked = WAITING_GRADE
        elif not known:
            blocked = VIEW_OPEN
        elif at is not None and at > now:
            upcoming.append(at)
            continue
        found.append(
            Pending(target, need, _waiting_since(tx, record), order, blocked, view_open=not known)
        )
    found.sort(key=lambda p: (p.waiting_since or "", p.order))
    return found, sorted(upcoming)


def plan_checks(ready: list[Pending], candidates: list[JSON], remaining: int | None) -> list[JSON]:
    """Choose the exercises that best serve ``ready[0]`` and the checks after it.

    Plans must cover the first need; they compare by the needs they cover in priority
    order, then lower total full cost, then fewer exercises, then exercise identity.
    No weighted sum. Returns [] when no exercise that fits covers the first need.
    """
    index = {exact_key(p.target): n for n, p in enumerate(ready)}
    covers = {
        e["ref"]["id"]: {index[exact_key(t)] for t in e["targets"] if exact_key(t) in index}
        for e in candidates
    }
    fitting = [
        e
        for e in candidates
        if covers[e["ref"]["id"]] and (remaining is None or full_cost(e) <= remaining)
    ]
    if not any(0 in covers[e["ref"]["id"]] for e in fitting):
        return []
    # ponytail: exhaustive over the 12 cheapest useful exercises; past that, a greedy cover.
    pool = sorted(fitting, key=lambda e: (full_cost(e), e["ref"]["id"]))[:PLAN_CANDIDATES]
    best: tuple[Any, ...] | None = None
    chosen: list[JSON] = []
    for size in range(1, len(pool) + 1):
        for plan in combinations(pool, size):
            covered = {n for e in plan for n in covers[e["ref"]["id"]]}
            cost = sum(full_cost(e) for e in plan)
            if 0 not in covered or (remaining is not None and cost > remaining):
                continue
            rank = (
                tuple(n not in covered for n in range(len(ready))),
                cost,
                size,
                sorted(e["ref"]["id"] for e in plan),
            )
            if best is None or rank < best:
                best, chosen = rank, list(plan)
    return sorted(chosen, key=lambda e: (min(covers[e["ref"]["id"]]), full_cost(e)))


def _new_material(tx: Tx, goals: Goals, usable: list[JSON]) -> list[JSON]:
    """Return usable exercises that start unstarted goals, in outline order."""
    fresh = {
        k: v[1] for k, v in goals.items() if v[2] == "unstarted" and _schedule(tx, v[0]) is None
    }
    starting = [e for e in usable if any(exact_key(t) in fresh for t in e["targets"])]
    return sorted(
        starting, key=lambda e: min(fresh.get(exact_key(t), (99, 99, "")) for t in e["targets"])
    )


def _concern_items(
    tx: Tx, session: JSON, goals: Goals
) -> list[tuple[Record, bool, str | None, tuple[int, int, str]]]:
    """Return open concerns in scope.

    Each item is (record, from this session's answers, waiting since, order).
    """
    here = {
        a["ref"]["id"] for a in evidence.attempts(tx) if a["session"]["id"] == session["ref"]["id"]
    }
    items: list[tuple[Record, bool, str | None, tuple[int, int, str]]] = []
    for record in tx.current("concern", by=OWNER):
        concern = ConcernP.model_validate(record.payload)
        targets = [s.target.model_dump() for s in concern.scope]
        if concern.status != "open" or not {exact_key(t) for t in targets} <= set(goals):
            continue
        if any(content.target_hold(tx, t) for t in targets):
            continue  # a concern on held material waits
        current = concern.origin.id in here or any(
            a["ref"]["id"] in here for a in evidence.attempts(tx) if _concern_id(a) == record.id
        )
        dues = [s["due_at"] for t in targets if (s := schedule_view(tx, t)) and s["due_at"]]
        origin = evidence.attempt_view(tx, concern.origin.model_dump())["submitted_at"]
        since = min([d for d in [*dues, origin] if d], default=None)
        order = min(goals[exact_key(t)][1] for t in targets)
        items.append((record, current, since, order))
    return items


def _step_cost(tx: Tx, step: JSON, origin: JSON) -> tuple[int, bool]:
    """Return a concern step's known cost in seconds and whether part of it is unknown.

    A question reserves its worst branch: teaching (unknown length) and a fresh check
    sized like the original task. Teaching alone has unknown length.
    """
    task = full_cost(content.definition(tx, evidence.attempt_view(tx, origin)["exercise"]))
    if step["kind"] == "ask":
        teaches = any(b["next"] == "teach" for b in step["concern"]["question"]["branches"])
        return full_cost(step["exercise"]) + (task if teaches else 0), teaches
    if step["kind"] == "teach":
        return 0, True
    if step["kind"] == "verify":
        return task, False
    return 0, False


def _fits(cost: tuple[int, bool], remaining: int | None) -> bool:
    known, unknown = cost
    return remaining is None or known < remaining or (known == remaining and not unknown)


def remaining(session: JSON, elapsed_ms: int) -> int | None:
    """Return a session's budget left in seconds under ``budget-elapsed-1`` (None: no budget).

    Spent time is the session's elapsed time, breaks included; unknown effort never
    becomes time left.
    """
    if session["budget_seconds"] is None:
        return None
    return int(session["budget_seconds"]) - elapsed_ms // 1000


def next_step(  # noqa: C901, PLR0911, PLR0912 - one ordered policy
    tx: Tx,
    session_id: str,
    *,
    elapsed_ms: int,
    exercise_id: str | None = None,
    new_material: bool = False,
) -> JSON:
    """Choose what this session does next under ``bounded-session-1``.

    Resume a reserved draft, then a started study, then concerns from this session's
    answers; then older concerns and ready checks by waiting time; then new material.
    ``elapsed_ms`` is the session's elapsed time from Measurement; Practice applies its
    budget policy to it. A learner override names an exercise or asks for new material;
    it is recorded as such.
    """
    session = session_view(tx, session_id)
    left_s = remaining(session, elapsed_ms)
    reserved = open_offer(tx, session_id)
    goals = _goals(tx, session["enrollments"])
    usable = content.exercises_for(tx, [g[0] for g in goals.values()])
    if exercise_id is not None:
        chosen = next((e for e in usable if e["ref"]["id"] == exercise_id), None)
        if chosen is None:
            msg = "that exercise cannot be practised in this session now"
            raise ValueError(msg)
        if reserved is not None and _offered_exercise(tx, reserved) == chosen["ref"]:
            return {"kind": "resume", "offer": reserved}
        return _choice(chosen, [], [], left_s, "chosen by the learner", override=True)
    if reserved is not None:
        return {"kind": "resume", "offer": reserved}
    open_ids = {item[0].id for item in _concern_items(tx, session, goals)}
    for study in evidence.studies(tx):
        if study["status"] == "started" and _concern_id(study) in open_ids:
            return {"kind": "study", "study": study["ref"]}
    if left_s is not None and left_s <= 0:
        return {"kind": "budget_spent", "left": unserved_view(tx, session_id, elapsed_ms)}
    checks, upcoming = pending(tx, session["enrollments"], tx.now)
    ready = [p for p in checks if p.blocked is None]
    left: list[LeftP] = []
    if not new_material:
        concerns = _concern_items(tx, session, goals)
        queue: list[tuple[tuple[Any, ...], str, Any]] = [
            ((0 if current else 1, since or "", order), "concern", record)
            for record, current, since, order in concerns
        ]
        queue += [((1, p.waiting_since or "", p.order), "check", p) for p in checks]
        for _rank, kind, item in sorted(queue, key=lambda q: q[0]):
            if kind == "concern":
                step = _concern_step(tx, session_id, item)
                if step is None:
                    continue
                if _fits(_step_cost(tx, step, item.payload["origin"]), left_s):
                    return step
                left.append(LeftP(target=item.payload["scope"][0]["target"], reason=TOO_LONG))
                continue
            if item.blocked is not None:
                left.append(
                    LeftP(
                        target=Ref(**item.target),
                        reason=item.blocked,
                        confirm_closed=item.view_open and item.blocked == VIEW_OPEN,
                    )
                )
                continue
            plan = plan_checks(ready[ready.index(item) :], usable, left_s)
            if plan:
                return _choice(plan[0], ready, left, left_s, "the oldest ready check")
            left.append(LeftP(target=Ref(**item.target), reason=_unfit(item, usable)))
    fresh = _new_material(tx, goals, usable)
    for exercise in fresh:
        if left_s is None or full_cost(exercise) <= left_s:
            reason = "new material, chosen by the learner" if new_material else "new material"
            return _choice(exercise, ready, left, left_s, reason, override=new_material)
    too_long = bool(fresh) or any(x.reason == TOO_LONG for x in left)
    return {
        "kind": "nothing_fits" if too_long else "none",
        "left": [x.model_dump() for x in left],
        "upcoming": upcoming[:1],
        "new_material_waits": bool(fresh),
    }


def _unfit(item: Pending, usable: list[JSON]) -> str:
    covering = any(exact_key(t) == exact_key(item.target) for e in usable for t in e["targets"])
    return TOO_LONG if covering else NO_EXERCISE


def _offered_exercise(tx: Tx, offer: JSON) -> JSON:
    return dict(evidence.attempt_view(tx, offer["attempt"])["exercise"])


def _choice(  # noqa: PLR0913 - the chosen exercise and why
    exercise: JSON,
    ready: list[Pending],
    left: list[LeftP],
    remaining: int | None,
    reason: str,
    *,
    override: bool = False,
) -> JSON:
    """Return the chosen exercise with the selection facts its delivery records."""
    covered = {exact_key(t) for t in exercise["targets"]}
    served = [
        ServedP(target=Ref(**p.target), need=p.need, waiting_since=p.waiting_since)
        for p in ready
        if exact_key(p.target) in covered
    ]
    selection = {
        "served": served,
        "left": left,
        "cost_seconds": full_cost(exercise),
        "remaining_seconds": remaining,
        "override": override,
    }
    return {"kind": "exercise", "exercise": exercise, "reason": reason, "selection": selection}


def _unserved(tx: Tx, session_id: str, remaining: int | None) -> list[tuple[Pending, str]]:
    """Return every pending need in a session's scope with why it is still waiting."""
    session = session_view(tx, session_id)
    goals = _goals(tx, session["enrollments"])
    usable = content.exercises_for(tx, [g[0] for g in goals.values()])
    checks, _upcoming = pending(tx, session["enrollments"], tx.now)
    found: list[tuple[Pending, str]] = []
    for p in checks:
        if p.blocked is not None:
            found.append((p, p.blocked))
            continue
        fits = any(
            exact_key(t) == exact_key(p.target) and (remaining is None or full_cost(e) <= remaining)
            for e in usable
            for t in e["targets"]
        )
        if remaining is not None and remaining <= 0:
            found.append((p, TIME_UP))
        else:
            found.append((p, NOT_REACHED if fits else _unfit(p, usable)))
    for record, _current, since, _order in _concern_items(tx, session, goals):
        for s in record.payload["scope"]:
            route = record.payload["route"]
            why = TIME_UP if remaining is not None and remaining <= 0 else NOT_REACHED
            found.append((Pending(s["target"], route, since, (0, 0, s["target"]["id"])), why))
    return found


def proposal(tx: Tx, enrollments: list[JSON], budget_seconds: int | None) -> JSON:
    """Preview a session: what is ready, how much of it fits, and what comes first.

    A read only: it admits nothing and reserves nothing (lifecycle section 1).
    """
    checks, upcoming = pending(tx, enrollments, tx.now)
    ready = [p for p in checks if p.blocked is None]
    goals = _goals(tx, enrollments)
    usable = content.exercises_for(tx, [g[0] for g in goals.values()])
    plan: list[JSON] = []
    for n in range(len(ready)):
        plan = plan_checks(ready[n:], usable, budget_seconds)
        if plan:
            break
    covered = {exact_key(t) for e in plan for t in e["targets"]}
    served = [p for p in ready if exact_key(p.target) in covered]
    first: JSON | None = None
    if served:
        due = schedule_view(tx, served[0].target)
        first = {
            "kind": "check",
            "action": content.definition(tx, served[0].target)["action"],
            "overdue": bool(due and due["due_at"] and due["due_at"] < tx.now),
        }
    repairs = [c for c in tx.current("concern", by=OWNER) if c.payload["status"] == "open"]
    waits = [p.waiting_since for p in ready if p.waiting_since]
    return {
        "oldest": min(waits, default=None),
        "budget_seconds": budget_seconds,
        "ready": len(ready),
        "fits": len(served),
        "first": first,
        "repairs": sum(
            1 for c in repairs if {exact_key(s["target"]) for s in c.payload["scope"]} <= set(goals)
        ),
        "blocked": [{"target": p.target, "reason": p.blocked} for p in checks if p.blocked],
        "new_material": bool(_new_material(tx, goals, usable)),
        "upcoming": upcoming[:1],
    }


def enrollment_view(tx: Tx, enrollment_id: str) -> JSON:
    """Return an enrollment's current revision."""
    return tx.require("enrollment", enrollment_id, by=OWNER).view


def unserved_view(tx: Tx, session_id: str, elapsed_ms: int) -> list[JSON]:
    """Return what an open session has left unserved so far, with reasons."""
    left = remaining(session_view(tx, session_id), elapsed_ms)
    return [
        {"target": p.target, "need": p.need, "waiting_since": p.waiting_since, "reason": why}
        for p, why in _unserved(tx, session_id, left)
    ]


# --- read views ----------------------------------------------------------------------


def schedule_view(tx: Tx, target: JSON) -> JSON | None:
    """Return an exact goal revision's current schedule, if it was ever admitted.

    The recall engine's state stays private to Practice; the view leaves it out.
    """
    record = _schedule(tx, target)
    return _public(record.view) if record else None


def schedule_history(tx: Tx, target: JSON) -> list[JSON]:
    """Return every revision of an exact goal revision's schedule, oldest first."""
    record = _schedule(tx, target)
    if record is None:
        return []
    return [_public(r.view) for r in tx.history("schedule", record.id, by=OWNER)]


def _public(view: JSON) -> JSON:
    return {k: v for k, v in view.items() if k != "engine_state"}


def later_checks(tx: Tx, target: JSON) -> list[JSON]:
    """Return every later check one exact goal was owed, oldest first, with what met it.

    Each keeps its original due time; failed and replaced checks stay visible. A recall
    review (any rating, "forgot" included) is "reviewed"; a capability check is "met"
    only by an on-time independent success.
    """
    history = schedule_history(tx, target)
    slots = _slots(tx, target)
    checks: list[JSON] = []
    for oid in dict.fromkeys(h["obligation"]["id"] for h in history):
        revisions = [h for h in history if h["obligation"]["id"] == oid]
        first, last = revisions[0], revisions[-1]
        if first["obligation"]["kind"] != "later":
            continue
        status = last["obligation"]["status"]
        too_soon = {b["id"] for h in revisions if h["reason"] == TOO_SOON for b in h["basis"]}
        answers: list[JSON] = []
        for offer, slot in slots.values():
            if slot["obligation_id"] != oid:
                continue
            attempt = evidence.attempt_view(tx, attempt_id=offer["attempt"]["id"])
            if attempt["status"] != "submitted":
                continue
            graded = evidence.assessment_for(tx, attempt["ref"]["id"])
            consumed_by: JSON | None = last["consumed_by"]
            met = consumed_by is not None and consumed_by["id"] == attempt["ref"]["id"]
            answers.append(
                {
                    "attempt": attempt["ref"],
                    "at": attempt["submitted_at"],
                    "role": slot["role"],
                    "label": evidence.answer_label(tx, attempt["ref"]["id"], target),
                    "effect": _effect(
                        met=met,
                        recall=first["type"] == "recall",
                        too_soon=bool(graded and graded["ref"]["id"] in too_soon),
                    ),
                }
            )
        checks.append(
            {
                "obligation": oid,
                "due_at": first["due_at"],
                "status": status,
                "ended": last["reason"] if status != "open" else None,
                "next_offer": last.get("next_offer") if status == "open" else None,
                "answers": sorted(answers, key=lambda a: a["at"] or ""),
            }
        )
    return checks


def _effect(*, met: bool, recall: bool, too_soon: bool) -> str | None:
    if met:
        return "reviewed" if recall else "met"
    return "too soon" if too_soon else None


CAUGHT_UP_RULE: JSON = {"name": "caught-up", "version": 1, "parameters": {}}
WAITING: dict[str, str] = {
    "not_started": "not started yet",
    "paused": "paused",
    "held": "its material is on hold",
    "unresolved": "has an unresolved need",
    "grading": "an answer is still being graded",
    "first_check_pending": "first later check pending",
    "after_repair_pending": "later check after repair pending",
    "due": "a later check is due",
}


def caught_up(tx: Tx, enrollment: JSON) -> JSON:
    """Evaluate "Caught up on later checks as of [time]" for one enrollment (``caught-up-1``).

    The whole selected curriculum is caught up only when every selected goal is; when
    only unstarted, paused or held goals stand in the way, an active subset can be,
    and says so. It is a statement about now, never permanent completion.
    """
    waiting: list[JSON] = []
    for entry in enrollment["practice"]:
        target = entry["target"]
        code = "paused" if entry["state"] == "paused" else None
        if entry["state"] == "unstarted" or _schedule(tx, target) is None:
            code = "not_started"
        elif content.target_hold(tx, target) is not None:
            code = "held"
        code = code or _later_state(tx, target)
        if code:
            waiting.append({"target": target, "code": code, "reason": WAITING[code]})
    outside = {"not_started", "paused", "held"}
    active = [p for p in waiting if p["code"] not in outside]
    if not waiting:
        state, scope = "caught_up", "curriculum"
    elif not active and len(waiting) < len(enrollment["practice"]):
        state, scope = "caught_up", "active"
    else:
        state, scope = (active or waiting)[0]["code"], "curriculum"
    return {"state": state, "scope": scope, "as_of": tx.now, "pending": waiting}


def _later_state(tx: Tx, target: JSON) -> str | None:
    """Say what keeps one admitted goal from being caught up now, or None."""
    record = _schedule(tx, target)
    assert record is not None  # noqa: S101 - callers check admission
    schedule = record.payload
    if schedule["need"] in ("initial", "repair", "clarify", "held") or any(
        c.payload["status"] == "open" and exact_key(s["target"]) == exact_key(target)
        for c in tx.current("concern", by=OWNER)
        for s in c.payload["scope"]
    ):
        return "unresolved"
    if _live_owner(tx, target, schedule["obligation"]["id"]):
        return "grading"
    taught = [
        s["completed_at"]
        for s in evidence.studies(tx)
        if s["status"] == "completed"
        and exact_key(target) in {exact_key(x["target"]) for x in s["scope"]}
    ]
    checks = later_checks(tx, target)
    met = [
        a["at"]
        for c in checks
        if c["status"] == "consumed"
        for a in c["answers"]
        if a["effect"] in ("met", "reviewed") and _succeeded(tx, a, target)
    ]
    if not met:
        return "after_repair_pending" if taught else "first_check_pending"
    if taught and max(taught) > max(met):
        return "after_repair_pending"
    current = checks[-1] if checks else None
    if current is None or current["status"] != "open" or not current["due_at"]:
        return "unresolved"
    return "due" if current["due_at"] <= tx.now else None


def _succeeded(tx: Tx, answer: JSON, target: JSON) -> bool:
    """Tell whether a check-meeting answer was a success (a recall rated "forgot" is not)."""
    review = evidence.review_for(tx, answer["attempt"]["id"], target)
    return review is None or review["rating"] != "again"


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
