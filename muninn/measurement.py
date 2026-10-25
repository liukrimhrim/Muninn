"""Measurement: observe effort honestly.

Owns timing runs (which browser tab may time), activity spans and optional session
feedback. Durations come from the browser's monotonic clock; wall-clock times only
place a span. Totals are the union of placed, accepted spans: overlapping categories
count once, pauses overlapping work are disputed, and unknown time stays unknown.
"""

from __future__ import annotations

from itertools import pairwise
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from muninn import content, practice
from muninn.library import JSON, Conflict, Record, parse_utc, utc, validate_payloads

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


PAYLOADS: dict[str, type[BaseModel]] = {
    "timing_run": TimingRunP,
    "activity_span": SpanP,
    "session_feedback": SessionFeedbackP,
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
    """Account a curriculum's effort: its sessions plus the preparation that produced it.

    Membership: spans in any session of the enrollment, spans naming the enrollment,
    and spans whose context names one of the curriculum's preparation records.
    """
    sessions = {
        s["ref"]["id"]
        for s in practice.sessions(tx)
        if enrollment_id and s["enrollments"][0]["id"] == enrollment_id
    }
    context: set[str] = preparation_ids | ({enrollment_id} if enrollment_id else set[str]())
    return ledger(spans_for(tx, session_ids=sessions, context_ids=context))


def all_spans(tx: Tx) -> list[JSON]:
    """Return every span's current revision."""
    return [r.payload for r in tx.current("activity_span", by=OWNER)]
