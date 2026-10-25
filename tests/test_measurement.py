from muninn.measurement import ledger

MIN = 60_000
T0 = "2026-10-24T10:00:00.000Z"


def at(minute):
    return f"2026-10-24T10:{minute:02d}:00.000Z"


def span(category, start, end, **extra):
    return {
        "category": category,
        "started_at": at(start),
        "ended_at": at(end),
        "duration_ms": (end - start) * MIN,
        "placement": "anchored",
        "authority": "accepted",
        "duration_quality": "continuous",
        "continuity": "closed",
        **extra,
    }


def test_overlapping_categories_count_once_as_unattributed():
    # data-contract D09: study [0,10), feedback [8,13), setup [13,15) is 15 minutes, not 17
    result = ledger([span("study", 0, 10), span("feedback", 8, 13), span("setup", 13, 15)])
    assert result["total_ms"] == 15 * MIN
    assert result["by_category"] == {"study": 8 * MIN, "feedback": 3 * MIN, "setup": 2 * MIN}
    assert result["unattributed_ms"] == 2 * MIN


def test_every_kind_of_work_is_counted_in_its_group():
    # observability O06: 12 + 5 + 8 + 4 + 6 + 2 + 3 = 40 minutes
    spans, t = [], 0
    for category, minutes in [
        ("answer", 12),
        ("diagnosis", 5),
        ("study", 8),
        ("feedback", 4),
        ("authoring", 6),
        ("assessment_correction", 2),
        ("blocked_wait", 3),
    ]:
        spans.append(span(category, t, t + minutes))
        t += minutes
    result = ledger(spans)
    assert result["total_ms"] == 40 * MIN
    assert result["groups"] == {"learning": 29 * MIN, "overhead": 8 * MIN, "waiting": 3 * MIN}


def test_a_pause_overlapping_work_is_disputed_not_counted():
    result = ledger([span("answer", 0, 10), span("pause", 5, 15)])
    assert result["total_ms"] == 5 * MIN
    assert result["disputed_ms"] == 5 * MIN


def test_stale_unplaced_and_unknown_time_stay_out_of_the_total():
    result = ledger(
        [
            span("answer", 0, 10),
            span("answer", 20, 25, authority="stale"),
            span(
                "feedback",
                0,
                0,
                started_at=None,
                ended_at=None,
                placement="uncertain",
                duration_ms=60_000,
            ),
            span(
                "unaccounted",
                0,
                0,
                started_at=None,
                ended_at=None,
                placement="unplaced",
                duration_ms=None,
                continuity="unknown_tail",
            ),
        ]
    )
    assert result["total_ms"] == 10 * MIN
    assert result["stale_spans"] == 1
    assert result["unplaced_known_ms"] == 60_000
    assert result["unknown_tails"] == 1


def test_no_spans_means_unknown_not_zero():
    assert ledger([])["total_ms"] is None
