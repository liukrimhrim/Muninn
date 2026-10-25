"""Measurement: observe effort honestly.

Owns timing runs (which browser tab may time), activity spans and optional session
feedback. Durations come from the browser's monotonic clock; wall-clock times only
place a span. Totals are the union of placed, accepted spans: overlapping categories
count once, pauses overlapping work are disputed, and unknown time stays unknown.
"""

from __future__ import annotations

from datetime import timedelta
from itertools import pairwise
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from muninn import content, evidence, practice
from muninn.library import (
    JSON,
    Conflict,
    Record,
    exact_key,
    new_id,
    parse_utc,
    utc,
    validate_payloads,
)

if TYPE_CHECKING:
    from muninn.library import Tx

OWNER = "measurement"

Category = Literal[
    "setup",
    "answer",
    "diagnosis",
    "study",
    "feedback",
    "authoring",
    "assessment_correction",
    "progress_inspection",
    "blocked_wait",
    "maintenance",
    "pause",
    "unaccounted",
]
GROUPS: dict[str, str] = {
    "answer": "learning",
    "diagnosis": "learning",
    "study": "learning",
    "feedback": "learning",
    "setup": "overhead",
    "authoring": "overhead",
    "assessment_correction": "overhead",
    "progress_inspection": "overhead",
    "maintenance": "overhead",
    "blocked_wait": "waiting",
}
COLLECTOR: JSON = {
    "name": "browser-foreground-timer",
    "version": 1,
    "parameters": {"checkpoint_seconds": 30},
}
# ponytail: wall and monotonic deltas within 2 s place a span; a clock jump leaves it unplaced.
PLACEMENT_TOLERANCE_MS = 2000

Ref = content.RefP


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TimingRunP(_Strict):
    """One browser document's grant to record time."""

    session: Ref | None
    activation_id: str
    document_run_id: str
    generation: int
    collector: content.AlgorithmP
    status: Literal["active", "closed", "interrupted"]
    opened_at: str
    closed_at: str | None
    close_reason: str | None


class SpanP(_Strict):
    """One interval of activity, with how well its duration and placement are known."""

    session: Ref | None
    enrollment: Ref | None
    context: list[Ref]
    targets: list[Ref]
    category: Category
    started_at: str | None
    ended_at: str | None
    duration_ms: int | None
    measurement: Literal["foreground_estimate", "self_report", "unverified"]
    collector: content.AlgorithmP
    revision_reason: str | None
    run: Ref | None
    ordinal: int | None
    monotonic_start_ms: int | None
    monotonic_end_ms: int | None
    raw_wall_start: str | None
    raw_wall_end: str | None
    placement: Literal["anchored", "uncertain", "unplaced"]
    duration_quality: Literal["continuous", "self_report", "unknown"]
    authority: Literal["accepted", "stale", "not_applicable"]
    continuity: Literal["closed", "checkpoint", "unknown_tail"]
    quality_reasons: list[str]


class SessionFeedbackP(_Strict):
    """Optional ratings; a missing rating stays missing."""

    session: Ref
    effort: Literal["easy", "moderate", "hard"] | None
    usefulness: Literal["useful", "mixed", "not_useful"] | None
    note: str | None


class WindowP(_Strict):
    """One observation window, half-open [start, end)."""

    index: int
    start: str
    end: str


class BaselineP(_Strict):
    """The frozen baseline answer of one goal."""

    state: Literal["selected", "missing", "order_uncertain"]
    attempts: list[Ref]
    assessment: Ref | None


class MemberP(_Strict):
    """One frozen goal of the tracked population."""

    target: Ref
    hold: str | None
    families: list[str]
    authoring_unavailable: bool
    baseline: BaselineP
    anchor: Ref | None
    anchor_reason: str | None


class OutsideP(_Strict):
    """A selected goal outside the frozen comparison, and why."""

    target: Ref
    reason: str


class EndpointP(_Strict):
    """One planned check of one goal in one window; assigned before its answer exists."""

    id: str
    target: Ref
    window: int
    assigned_attempt: Ref | None
    assignment_offer: Ref | None
    assignment_rule: str


class CohortP(_Strict):
    """A frozen comparison of the same goals over three windows (``routine-tracking-1``)."""

    curriculum: Ref
    enrollment: Ref
    plan_rule: content.AlgorithmP
    creation_source: dict[str, int]
    frozen_at: str
    windows: list[WindowP]
    population: list[MemberP]
    outside: list[OutsideP]
    claim_definitions: list[content.AlgorithmP]
    effort_membership: content.AlgorithmP
    effort_scope: list[Ref]
    investment_window: list[str]
    endpoints: list[EndpointP]
    lifecycle: Literal["active", "stopped", "completed"]
    stopped_at: str | None
    stop_reason: str | None
    predecessor: Ref | None
    baseline_rule: str


PAYLOADS: dict[str, type[BaseModel]] = {
    "timing_run": TimingRunP,
    "activity_span": SpanP,
    "session_feedback": SessionFeedbackP,
    "measurement_cohort": CohortP,
}


def validate_records(records: list[Record]) -> list[str]:
    """Check every Measurement-owned record against its payload contract."""
    return validate_payloads(records, OWNER, PAYLOADS)


# --- timing runs ------------------------------------------------------------------


def _active_runs(tx: Tx) -> list[Record]:
    return [r for r in tx.current("timing_run", by=OWNER) if r.payload["status"] == "active"]


def open_run(tx: Tx, *, activation_id: str, document_run_id: str, takeover: bool) -> JSON:
    """Grant this browser document the timer.

    Another active document keeps it unless ``takeover`` is set; taking over closes
    the old run and records the unknown time after its last acknowledged span.
    """
    active = _active_runs(tx)
    mine = [r for r in active if r.payload["document_run_id"] == document_run_id]
    if mine:
        return mine[0].ref
    current = [r for r in active if r.payload["activation_id"] == activation_id]
    if current and not takeover:
        msg = "another tab is timing this library"
        raise Conflict(msg)
    for r in active:
        _close(
            tx, r, "interrupted", "taken over by another tab" if r in current else "app restarted"
        )
    generation = 1 + max(
        (r.payload["generation"] for r in tx.current("timing_run", by=OWNER)), default=0
    )
    run = TimingRunP(
        session=None,
        activation_id=activation_id,
        document_run_id=document_run_id,
        generation=generation,
        collector=content.AlgorithmP(**COLLECTOR),
        status="active",
        opened_at=tx.now,
        closed_at=None,
        close_reason=None,
    )
    return tx.put("timing_run", run.model_dump(), by=OWNER)


def _close(tx: Tx, run: Record, status: Literal["closed", "interrupted"], reason: str) -> None:
    closed = TimingRunP.model_validate(run.payload).model_copy(
        update={"status": status, "closed_at": tx.now, "close_reason": reason}
    )
    tx.put("timing_run", closed.model_dump(), by=OWNER, id=run.id, base=run.revision)
    if status == "interrupted":
        last = [
            s
            for s in tx.current("activity_span", by=OWNER)
            if s.payload["run"] and s.payload["run"]["id"] == run.id
        ]
        anchor = last[-1].payload if last else {}
        tail = SpanP(
            session=_maybe_ref(anchor.get("session")),
            enrollment=_maybe_ref(anchor.get("enrollment")),
            context=[Ref(**(last[-1].ref if last else run.ref))],
            targets=[],
            category="unaccounted",
            started_at=None,
            ended_at=None,
            duration_ms=None,
            measurement="unverified",
            collector=content.AlgorithmP(**COLLECTOR),
            revision_reason=None,
            run=Ref(**run.ref),
            ordinal=None,
            monotonic_start_ms=None,
            monotonic_end_ms=None,
            raw_wall_start=None,
            raw_wall_end=None,
            placement="unplaced",
            duration_quality="unknown",
            authority="not_applicable",
            continuity="unknown_tail",
            quality_reasons=[f"time after the last saved span is unknown ({reason})"],
        )
        tx.put("activity_span", tail.model_dump(), by=OWNER)


def holds_timer(tx: Tx, *, run_id: str, activation_id: str) -> bool:
    """Return whether a run still holds the timer in this activation."""
    run = tx.get("timing_run", run_id, by=OWNER)
    return (
        run is not None
        and run.payload["status"] == "active"
        and run.payload["activation_id"] == activation_id
    )


def interrupt_other_activations(tx: Tx, *, activation_id: str) -> None:
    """At startup, end runs granted by an earlier process; their tails are unknown."""
    for r in _active_runs(tx):
        if r.payload["activation_id"] != activation_id:
            _close(tx, r, "interrupted", "app restarted")


def record_span(tx: Tx, *, activation_id: str, span: JSON) -> JSON | None:
    """Accept one browser span; retries with the same span ID write nothing new.

    A span from a run that no longer holds the timer is kept as stale and never
    counted. A wall-clock jump keeps the duration but leaves the span unplaced. A span
    naming no run of this library, or malformed, is refused (``None``) without
    blocking the rest of its batch.
    """
    existing = tx.get("activity_span", span["id"], by=OWNER)
    if existing is not None:
        return existing.ref
    run = tx.get("timing_run", span["run_id"], by=OWNER)
    start, end = span["monotonic_start_ms"], span["monotonic_end_ms"]
    if run is None or end < start:
        return None  # not this library's timer, or impossible: refused, never counted
    fresh = run.payload["status"] == "active" and run.payload["activation_id"] == activation_id
    reasons: list[str] = [] if fresh else ["recorded by a tab that no longer held the timer"]
    wall_start, wall_end = span.get("raw_wall_start"), span.get("raw_wall_end")
    placed = (
        wall_start is not None
        and wall_end is not None
        and abs(
            (parse_utc(wall_end) - parse_utc(wall_start)).total_seconds() * 1000 - (end - start)
        )
        <= PLACEMENT_TOLERANCE_MS
    )
    if not placed:
        reasons.append("the wall clock disagreed with the elapsed time")
    try:
        payload = _span_payload(span, run, placed=placed, fresh=fresh, reasons=reasons)
    except ValidationError:
        return None  # malformed (for example a context that is not an exact ref): refused
    return tx.put("activity_span", payload.model_dump(), by=OWNER, id=span["id"])


def _span_payload(
    span: JSON, run: Record, *, placed: bool, fresh: bool, reasons: list[str]
) -> SpanP:
    start, end = span["monotonic_start_ms"], span["monotonic_end_ms"]
    wall_start, wall_end = span.get("raw_wall_start"), span.get("raw_wall_end")
    return SpanP(
        session=_maybe_ref(span.get("session")),
        enrollment=_maybe_ref(span.get("enrollment")),
        context=[Ref(**c) for c in span.get("context", [])],
        targets=[Ref(**t) for t in span.get("targets", [])],
        category=span["category"],
        started_at=utc(parse_utc(wall_start)) if placed and wall_start else None,
        ended_at=utc(parse_utc(wall_end)) if placed and wall_end else None,
        duration_ms=end - start,
        measurement="foreground_estimate" if fresh else "unverified",
        collector=content.AlgorithmP(**COLLECTOR),
        revision_reason=None,
        run=Ref(**run.ref),
        ordinal=span["ordinal"],
        monotonic_start_ms=start,
        monotonic_end_ms=end,
        raw_wall_start=wall_start,
        raw_wall_end=wall_end,
        placement="anchored" if placed else "uncertain",
        duration_quality="continuous",
        authority="accepted" if fresh else "stale",
        continuity="closed",
        quality_reasons=reasons,
    )


def _maybe_ref(value: Any) -> Ref | None:  # noqa: ANN401 - optional JSON from the browser
    return Ref(**value) if value else None


def save_feedback(
    tx: Tx, *, session: JSON, effort: str | None, usefulness: str | None, note: str | None
) -> JSON:
    """Save optional end-of-session ratings."""
    payload = SessionFeedbackP.model_validate(
        {"session": session, "effort": effort, "usefulness": usefulness, "note": note}
    )
    return tx.put("session_feedback", payload.model_dump(), by=OWNER)


# --- the time ledger --------------------------------------------------------------------


def ledger(spans: list[JSON]) -> JSON:
    """Account effort as the union of placed, accepted spans (data-contract.md D09).

    Overlapping effort categories count once as unattributed; a pause or unaccounted
    claim overlapping effort is withheld as disputed. Unplaced known durations, stale
    spans and unknown tails are reported separately and never added.
    """
    placed = [
        s
        for s in spans
        if s["authority"] == "accepted"
        and s["placement"] == "anchored"
        and s["duration_ms"] is not None
    ]
    intervals = [
        (
            int(parse_utc(s["started_at"]).timestamp() * 1000),
            int(parse_utc(s["ended_at"]).timestamp() * 1000),
            s["category"],
        )
        for s in placed
    ]
    bounds = sorted({b for a, z, _ in intervals for b in (a, z)})
    by_category: dict[str, int] = {}
    unattributed = disputed = 0
    for lo, hi in pairwise(bounds):
        active = {c for a, z, c in intervals if a <= lo and hi <= z}
        effort = active - {"pause", "unaccounted"}
        if not effort:
            continue
        if active - effort:
            disputed += hi - lo
        elif len(effort) > 1:
            unattributed += hi - lo
        else:
            (category,) = effort
            by_category[category] = by_category.get(category, 0) + hi - lo
    groups: dict[str, int] = {}
    for category, ms in by_category.items():
        groups[GROUPS[category]] = groups.get(GROUPS[category], 0) + ms
    known = sum(by_category.values()) + unattributed
    return {
        "total_ms": known if placed else None,
        "by_category": by_category,
        "groups": groups,
        "unattributed_ms": unattributed,
        "disputed_ms": disputed,
        "unplaced_known_ms": sum(
            s["duration_ms"]
            for s in spans
            if s["authority"] == "accepted"
            and s["placement"] != "anchored"
            and s["duration_ms"] is not None
        ),
        "unknown_tails": sum(1 for s in spans if s["continuity"] == "unknown_tail"),
        "stale_spans": sum(1 for s in spans if s["authority"] == "stale"),
    }


def elapsed_ms(started_at: str, ended_at: str) -> int:
    """Return wall-clock session length, breaks and unaccounted gaps included."""
    return int((parse_utc(ended_at) - parse_utc(started_at)).total_seconds() * 1000)


def session_elapsed_ms(tx: Tx, session_id: str) -> int:
    """Return a session's elapsed time so far, breaks included (its budget summary)."""
    session = practice.session_view(tx, session_id)
    return elapsed_ms(session["started_at"], session["ended_at"] or tx.now)


def spans_for(tx: Tx, *, session_ids: set[str], context_ids: set[str]) -> list[JSON]:
    """Return spans recorded in the given sessions or naming any given context."""
    return [
        r.payload
        for r in tx.current("activity_span", by=OWNER)
        if (r.payload["session"] and r.payload["session"]["id"] in session_ids)
        or any(c["id"] in context_ids for c in r.payload["context"])
        or (r.payload["enrollment"] and r.payload["enrollment"]["id"] in context_ids)
    ]


def curriculum_effort(tx: Tx, *, enrollment_id: str | None, preparation_ids: set[str]) -> JSON:
    """Account a curriculum's effort: its enrollment's work plus the preparation behind it.

    Membership follows ``cost-membership-1``: explicit enrollment attribution, else the
    session's single enrollment, plus spans whose context names a preparation record.
    Time in a session over several curricula without attribution is reported as
    uncertain membership, never split or guessed.
    """
    roots = {enrollment_id} if enrollment_id else set[str]()
    known, maybe = _scoped(tx, roots)
    prepared = [
        s
        for s in all_spans(tx)
        if s not in known and any(c["id"] in preparation_ids for c in s["context"])
    ]
    known += prepared
    uncertain = sum(s["duration_ms"] or 0 for s in maybe if s not in prepared)
    return {**ledger(known), "uncertain_membership_ms": uncertain}


def all_spans(tx: Tx) -> list[JSON]:
    """Return every span's current revision."""
    return [r.payload for r in tx.current("activity_span", by=OWNER)]


def clipped(spans: list[JSON], start: str, upper: str) -> list[JSON]:
    """Clip reliably placed spans to ``[start, upper)`` (``cost-cutoff-1``).

    A crossing span keeps only its part inside; a span outside, or one that cannot be
    placed, contributes nothing to the clipped union (unplaced time stays separate).
    """
    kept: list[JSON] = []
    for s in spans:
        if s["placement"] != "anchored" or s["started_at"] is None or s["ended_at"] is None:
            continue
        lo, hi = max(s["started_at"], start), min(s["ended_at"], upper)
        if lo < hi:
            ms = int((parse_utc(hi) - parse_utc(lo)).total_seconds() * 1000)
            kept.append({**s, "started_at": lo, "ended_at": hi, "duration_ms": ms})
    return kept


# --- routine tracking: claim-outcomes-1 (tracking-contract.md section 4) -----------------

REASON_ORDER = [
    "contract",
    "occurrence_window",
    "aid_availability",
    "minimum_delay",
    "relevant_exposure",
    "mode",
    "coverage",
    "baseline",
    "later_session",
]
"""Tracking section 4's fixed reason order (the later-session condition added last)."""


def partition(raw: str, reasons: list[JSON]) -> tuple[str, str]:
    """Place one endpoint in exactly one bucket for one claim; return (bucket, eligibility).

    Precedence: not matured, missing, unusable, helped, then a usable S/E whose claim
    conditions are not all eligible, then qualified success or error.
    """
    results = {r["result"] for r in reasons}
    eligibility = (
        "ineligible"
        if "ineligible" in results
        else "uncertain"
        if "uncertain" in results
        else "eligible"
    )
    fixed = {"N": "QN", "M": "QM", "U": "QU", "H": "QH"}
    if raw in fixed:
        return fixed[raw], eligibility
    if eligibility != "eligible":
        return "QX", eligibility
    return ("QS" if raw == "S" else "QE"), eligibility


def endpoint_counts(endpoints: list[JSON]) -> JSON:
    """Count raw outcomes and one claim's buckets, with the tracking formulas as fractions.

    Not-matured endpoints stay outside the matured denominator P. Each fraction is
    [numerator, denominator]; a zero denominator means unavailable, never zero percent.
    """
    raw = dict.fromkeys(["S", "E", "H", "U", "M", "N"], 0)
    claim = dict.fromkeys(["QS", "QE", "QH", "QU", "QM", "QX", "QN"], 0)
    split = {"ineligible": 0, "uncertain": 0}
    for e in endpoints:
        raw[e["raw"]] += 1
        claim[e["bucket"]] += 1
        if e["bucket"] == "QX":
            split[e.get("eligibility", "uncertain")] += 1
    p = len(endpoints) - raw["N"]
    clean = p > 0 and claim["QH"] == claim["QU"] == claim["QX"] == 0
    return {
        "raw": raw,
        "claim": claim,
        "qx": split,
        "matured": p,
        "missing_only_range": [[claim["QS"], p], [claim["QS"] + claim["QM"], p]] if clean else None,
        "formulas": {
            "raw_correct": [raw["S"], raw["S"] + raw["E"]],
            "graded": [raw["S"] + raw["E"] + raw["H"], p - raw["M"]],
            "qualified_coverage": [claim["QS"], p],
            "qualified_correct": [claim["QS"], claim["QS"] + claim["QE"]],
            "checked": [p - raw["M"], p],
        },
    }


# --- routine tracking: freeze, assign, report (tracking-contract.md sections 2-5) ---------

WINDOWS = 3
WINDOW = timedelta(days=7)
TRACKING_RULE: JSON = {
    "name": "routine-tracking",
    "version": 1,
    "parameters": {"windows": WINDOWS, "window_days": 7},
}
COST_MEMBERSHIP: JSON = {"name": "cost-membership", "version": 1, "parameters": {"scope": "roots"}}
CLAIMS = [evidence.QUALIFICATION, evidence.LATER_CHECK_CLAIM]
BASELINE_RULE = "the last submitted answer for each exact goal before tracking began"
ASSIGNMENT_RULE = "the first ordinary owned check offered for the goal in this window"
NO_OFFER = "no ordinary check was offered in this window"
STOPPED = "tracking was stopped"
UNANSWERED = "the assigned check was not answered"


def _member(tx: Tx, target: JSON, frozen_at: str, usable: list[JSON]) -> MemberP:
    """Freeze one goal's baseline, anchor and allowed exercise families."""
    answers = [
        e
        for e in evidence.chronology(tx, target)
        if e["kind"] == "answer" and (e["at"] or "") < frozen_at
    ]
    tied = [a for a in answers if answers and a["at"] == answers[-1]["at"]]
    state: Literal["selected", "missing", "order_uncertain"] = (
        "missing" if not answers else "order_uncertain" if len(tied) > 1 else "selected"
    )
    chosen = tied if state == "order_uncertain" else answers[-1:]
    last = chosen[-1] if chosen else None
    gap = evidence.delay(tx, target, before=frozen_at)
    families = sorted(
        {
            e["family_id"]
            for e in usable
            if any(exact_key(t) == exact_key(target) for t in e["targets"])
        }
    )
    hold = content.target_hold(tx, target)
    return MemberP(
        target=Ref(**target),
        hold=hold.reason if hold else None,
        families=families,
        authoring_unavailable=not families,
        baseline=BaselineP(
            state=state,
            attempts=[Ref(**a["attempt"]) for a in chosen],
            assessment=Ref(**last["assessment"]) if last and last["assessment"] else None,
        ),
        anchor=Ref(**gap.basis[0]) if gap.known and gap.basis else None,
        anchor_reason=None
        if gap.known and gap.basis
        else ("an earlier view may still be open" if not gap.known else "nothing earlier recorded"),
    )


def tracking_preview(tx: Tx, *, curriculum: JSON, enrollment: JSON) -> JSON:
    """Preview a plan: who would be tracked, their baselines and the three windows.

    Disposable: nothing is saved.
    """
    frozen_at = tx.now
    usable = content.exercises_for(tx, enrollment["goal_order"])
    population: list[MemberP] = []
    outside: list[OutsideP] = []
    for entry in enrollment["practice"]:
        if entry["state"] == "active" and enrollment["status"] == "active":
            population.append(_member(tx, entry["target"], frozen_at, usable))
        else:
            why = "not started yet" if entry["state"] == "unstarted" else f"{entry['state']}"
            outside.append(OutsideP(target=Ref(**entry["target"]), reason=why))
    start = parse_utc(frozen_at)
    windows = [
        WindowP(index=n, start=utc(start + n * WINDOW), end=utc(start + (n + 1) * WINDOW))
        for n in range(WINDOWS)
    ]
    return {
        "curriculum": curriculum,
        "enrollment": enrollment["ref"],
        "frozen_at": frozen_at,
        "population": [m.model_dump() for m in population],
        "outside": [o.model_dump() for o in outside],
        "windows": [w.model_dump() for w in windows],
        "scheduled": [
            {"target": m.target.model_dump(), "due_at": s["due_at"]}
            for m in population
            if (s := practice.schedule_view(tx, m.target.model_dump())) and s["due_at"]
        ],
    }


def start_tracking(tx: Tx, *, curriculum: JSON, enrollment: JSON) -> JSON:
    """Freeze a tracking plan in one command, before any endpoint is assigned."""
    for r in tx.current("measurement_cohort", by=OWNER):
        if (
            r.payload["enrollment"]["id"] == enrollment["ref"]["id"]
            and r.payload["lifecycle"] == "active"
        ):
            msg = "tracking is already running for this curriculum; stop it to start a new plan"
            raise ValueError(msg)
    preview = tracking_preview(tx, curriculum=curriculum, enrollment=enrollment)
    if not preview["population"]:
        msg = "nothing is admitted yet: start practice first, then track it"
        raise ValueError(msg)
    windows = [WindowP.model_validate(w) for w in preview["windows"]]
    population = [MemberP.model_validate(m) for m in preview["population"]]
    cohort = CohortP(
        curriculum=Ref(**curriculum),
        enrollment=Ref(**enrollment["ref"]),
        plan_rule=content.AlgorithmP(**TRACKING_RULE),
        creation_source={"through_sequence": tx.watermark},
        frozen_at=preview["frozen_at"],
        windows=windows,
        population=population,
        outside=[OutsideP.model_validate(o) for o in preview["outside"]],
        claim_definitions=[content.AlgorithmP(**c) for c in CLAIMS],
        effort_membership=content.AlgorithmP(**COST_MEMBERSHIP),
        effort_scope=[Ref(**enrollment["ref"])],
        investment_window=[windows[0].start, windows[-1].end],
        endpoints=[
            EndpointP(
                id=new_id(),
                target=m.target,
                window=w.index,
                assigned_attempt=None,
                assignment_offer=None,
                assignment_rule=ASSIGNMENT_RULE,
            )
            for w in windows
            for m in population
        ],
        lifecycle="active",
        stopped_at=None,
        stop_reason=None,
        predecessor=None,
        baseline_rule=BASELINE_RULE,
    )
    return tx.put("measurement_cohort", cohort.model_dump(), by=OWNER)


def stop_tracking(tx: Tx, *, cohort_id: str, base: int, reason: str) -> JSON:
    """Stop assigning checks; frozen endpoints stay and later ones become missing."""
    record = tx.require("measurement_cohort", cohort_id, by=OWNER)
    cohort = CohortP.model_validate(record.payload)
    if cohort.lifecycle != "active":
        msg = "this tracking plan is not running"
        raise ValueError(msg)
    stopped = cohort.model_copy(
        update={"lifecycle": "stopped", "stopped_at": tx.now, "stop_reason": reason}
    )
    return tx.put("measurement_cohort", stopped.model_dump(), by=OWNER, id=cohort_id, base=base)


def assign_endpoints(tx: Tx, *, offer: JSON, exercise: JSON) -> None:
    """Assign still-open endpoints to an ordinary owned check as it is offered.

    Only an owned slot of a tracked goal, inside a running plan's current window and
    from an allowed exercise family, is assigned; never after its answer exists.
    """
    owned = {exact_key(s["target"]) for s in offer["slots"] if s["role"] == "owner"}
    for record in tx.current("measurement_cohort", by=OWNER):
        cohort = CohortP.model_validate(record.payload)
        if cohort.lifecycle != "active":
            continue
        window = next((w for w in cohort.windows if w.start <= tx.now < w.end), None)
        families = {exact_key(m.target.model_dump()): set(m.families) for m in cohort.population}
        changed = False
        endpoints: list[EndpointP] = []
        for e in cohort.endpoints:
            key = exact_key(e.target.model_dump())
            if (
                window is not None
                and e.window == window.index
                and e.assigned_attempt is None
                and key in owned
                and exercise["family_id"] in families.get(key, set())
            ):
                endpoints.append(
                    e.model_copy(
                        update={
                            "assigned_attempt": Ref(**offer["attempt"]),
                            "assignment_offer": Ref(**offer["ref"]),
                        }
                    )
                )
                changed = True
            else:
                endpoints.append(e)
        if changed:
            revised = cohort.model_copy(update={"endpoints": endpoints})
            tx.put(
                "measurement_cohort",
                revised.model_dump(),
                by=OWNER,
                id=record.id,
                base=record.revision,
            )


def cohorts(tx: Tx, enrollment_id: str) -> list[JSON]:
    """Return every tracking plan of an enrollment, oldest first."""
    return [
        r.view
        for r in tx.current("measurement_cohort", by=OWNER)
        if r.payload["enrollment"]["id"] == enrollment_id
    ]


RAW_OF: dict[str, str] = {"independent": "S", "error": "E"}
CLAIM_ROLES = {
    "independent-demonstration": "performance",
    "delayed-independent-check": "later_check",
}
"""The tracking contract's two claims by role: recorded performance, and a later check."""


def _answer_raw(tx: Tx, attempt_id: str, target: JSON) -> tuple[str, str | None]:
    """Map Evidence's judgment of one answer onto the raw axis S/E/H/U.

    Help shown makes it H; a hint never confirmed keeps the raw judgment (its claim
    eligibility is uncertain instead); missing or unjudgeable evidence is U.
    """
    found = evidence.answer_evidence(tx, attempt_id, target)
    if found is None:
        return "U", "not graded yet"
    if found["judged"] not in RAW_OF and found["judged"] != "helped":
        return "U", "; ".join(found["reasons"])
    if found["help"] == "shown":
        return "H", "answered with help"
    return RAW_OF[found["judged"]], None


def _raw(tx: Tx, cohort: CohortP, endpoint: EndpointP, window: WindowP) -> tuple[str, str | None]:
    """Return an endpoint's raw outcome S/E/H/U/M/N and why, at the current time."""
    if tx.now < window.end:
        return "N", "this window has not closed yet"
    if endpoint.assigned_attempt is None:
        stopped = cohort.stopped_at is not None and cohort.stopped_at < window.end
        return "M", STOPPED if stopped else NO_OFFER
    attempt = evidence.attempt_view(tx, attempt_id=endpoint.assigned_attempt.id)
    if attempt["status"] != "submitted":
        return "M", UNANSWERED
    return _answer_raw(tx, attempt["ref"]["id"], endpoint.target.model_dump())


def _baseline_raw(tx: Tx, member: MemberP) -> str:
    """Return the frozen baseline's raw outcome under today's effective judgment."""
    if member.baseline.state != "selected":
        return "M"
    return _answer_raw(tx, member.baseline.attempts[0].id, member.target.model_dump())[0]


def _claims(tx: Tx, cohort: CohortP, endpoint: EndpointP, window: WindowP, raw: str) -> JSON:
    """Partition one endpoint under each frozen claim, every reason kept in fixed order."""
    attempt = (
        evidence.attempt_view(tx, attempt_id=endpoint.assigned_attempt.id)
        if endpoint.assigned_attempt
        else None
    )
    member = next(m for m in cohort.population if m.target == endpoint.target)
    found: JSON = {}
    for claim in cohort.claim_definitions:
        reasons = (
            evidence.claim_reasons(
                tx,
                claim.model_dump(),
                target=endpoint.target.model_dump(),
                attempt=attempt,
                window=(window.start, window.end),
                anchor=member.anchor.model_dump() if member.anchor else None,
            )
            if attempt and attempt["status"] == "submitted"
            else []
        )
        reasons.sort(key=lambda r: REASON_ORDER.index(r["code"]))
        bucket, eligibility = partition(raw, reasons)
        found[CLAIM_ROLES[claim.name]] = {
            "claim": claim.model_dump(),
            "bucket": bucket,
            "eligibility": eligibility,
            "reasons": reasons,
            "baseline_qualification": "not_required",
        }
    return found


def _pair(baseline: str, bucket: str) -> str:
    """Name the same-target change from baseline to a qualified endpoint, or why not."""
    if bucket == "QN":
        return "not_matured"
    if baseline in ("S", "E") and bucket in ("QS", "QE"):
        return f"{baseline}->{bucket[1]}"
    return "incomparable"


def tracking_report(tx: Tx, cohort_id: str) -> JSON:
    """Report a plan live at the current time: raw outcomes and each claim's partition.

    Windows mature at their end; the cost follows the frozen enrollment identity over
    the investment window, capped at the current time (``cost-cutoff-1``).
    """
    record = tx.require("measurement_cohort", cohort_id, by=OWNER)
    cohort = CohortP.model_validate(record.payload)
    baselines = {exact_key(m.target.model_dump()): _baseline_raw(tx, m) for m in cohort.population}
    windows: list[JSON] = []
    for w in cohort.windows:
        rows: list[JSON] = []
        for e in (e for e in cohort.endpoints if e.window == w.index):
            raw, why = _raw(tx, cohort, e, w)
            claims = _claims(tx, cohort, e, w, raw)
            baseline = baselines[exact_key(e.target.model_dump())]
            rows.append(
                {
                    **e.model_dump(),
                    "raw": raw,
                    "reason": why,
                    "claims": claims,
                    "baseline_raw": baseline,
                    "comparison": _pair(baseline, claims["performance"]["bucket"]),
                }
            )
        windows.append(
            {
                **w.model_dump(),
                "mature": tx.now >= w.end,
                "endpoints": rows,
                "counts": endpoint_counts(
                    [{"raw": r["raw"], **r["claims"]["performance"]} for r in rows]
                ),
                "later_counts": endpoint_counts(
                    [{"raw": r["raw"], **r["claims"]["later_check"]} for r in rows]
                ),
                "changes": {
                    pair: sum(1 for r in rows if r["comparison"] == pair)
                    for pair in ("E->S", "S->S", "S->E", "E->E", "incomparable", "not_matured")
                },
            }
        )
    return {
        "ref": record.ref,
        **cohort.model_dump(),
        "windows": windows,
        "cost": _cohort_cost(tx, cohort),
    }


def _scoped(tx: Tx, roots: set[str]) -> tuple[list[JSON], list[JSON]]:
    """Split every span into in-scope and uncertain-membership spans for enrollment roots."""
    sessions = {s["ref"]["id"]: s for s in practice.sessions(tx)}
    known: list[JSON] = []
    uncertain: list[JSON] = []
    for s in all_spans(tx):
        state = _membership(s, roots, sessions)
        if state == "in_scope":
            known.append(s)
        elif state == "uncertain":
            uncertain.append(s)
    return known, uncertain


def _cohort_cost(tx: Tx, cohort: CohortP) -> JSON:
    """Cost of the frozen enrollment identity in the investment window, capped at now.

    Unplaced known durations and uncertain membership stay beside it, never added.
    """
    known, uncertain = _scoped(tx, {r.id for r in cohort.effort_scope})
    start, end = cohort.investment_window
    upper = min(end, tx.now)
    maybe = clipped(uncertain, start, upper)
    return {
        "membership_rule": cohort.effort_membership.model_dump(),
        "roots": [r.model_dump() for r in cohort.effort_scope],
        "window": [start, upper],
        "period": ledger(clipped(known, start, upper)),
        "before_tracking": ledger(clipped(known, "0000-01-01T00:00:00.000Z", start)),
        "unplaced_known_ms": sum(
            s["duration_ms"] or 0 for s in known if s["placement"] != "anchored"
        ),
        "uncertain_spans": len(maybe),
        "uncertain_known_ms": sum(s["duration_ms"] for s in maybe),
    }


def _membership(span: JSON, roots: set[str], sessions: dict[str, JSON]) -> str:
    """Resolve one span's scope under ``cost-membership-1`` (enrollment roots)."""
    named: set[str] = {span["enrollment"]["id"]} if span["enrollment"] else set()
    named |= {str(c["id"]) for c in span["context"] if c["kind"] == "enrollment"}
    if named:
        return "in_scope" if named & roots else "out_of_scope"
    session = sessions.get(span["session"]["id"]) if span["session"] else None
    if session is None:
        return "out_of_scope"
    enrolled = {e["id"] for e in session["enrollments"]}
    if enrolled & roots:
        return "in_scope" if len(enrolled) == 1 else "uncertain"
    return "out_of_scope"


def later_check_counts(checks: list[JSON], now: str) -> JSON:
    """Count later checks by how they stand; delayed successes only from real checks.

    Missed (overdue), helped and unresolved checks stay visible beside the met ones.
    """
    answers = [a for c in checks for a in c["answers"] if a["role"] == "owner"]
    closing = [a for a in answers if a["effect"] in ("met", "reviewed")]
    return {
        "met_on_time": sum(1 for a in closing if a["label"] != "error"),
        "reviewed_as_forgotten": sum(1 for a in closing if a["label"] == "error"),
        "replaced_after_teaching": sum(1 for c in checks if c["status"] == "replaced"),
        "no_longer_applies": sum(1 for c in checks if c["status"] == "invalidated"),
        "overdue": sum(
            1 for c in checks if c["status"] == "open" and c["due_at"] and c["due_at"] <= now
        ),
        "upcoming": sum(
            1 for c in checks if c["status"] == "open" and c["due_at"] and c["due_at"] > now
        ),
        "answered_with_help": sum(1 for a in answers if a["label"] == "helped"),
        "unresolved_answers": sum(1 for a in answers if a["label"] == "unresolved"),
        "with_errors": sum(1 for a in answers if a["label"] == "error"),
        "too_soon": sum(1 for a in answers if a["effect"] == "too soon"),
    }
