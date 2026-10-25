from muninn.measurement import clipped, endpoint_counts, ledger, partition

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


# --- routine tracking: one qualified partition per claim (tracking-contract.md) ---------


def test_each_endpoint_lands_in_exactly_one_bucket_by_precedence():
    ok = [{"code": "minimum_delay", "result": "eligible"}]
    early = [{"code": "minimum_delay", "result": "ineligible"}]
    unsure = [{"code": "relevant_exposure", "result": "uncertain"}]
    assert partition("N", ok) == ("QN", "eligible")
    assert partition("M", early) == ("QM", "ineligible")
    assert partition("U", ok) == ("QU", "eligible")
    assert partition("H", early) == ("QH", "ineligible")  # help wins; both reasons stay
    assert partition("S", early) == ("QX", "ineligible")
    assert partition("E", unsure) == ("QX", "uncertain")
    assert partition("S", ok) == ("QS", "eligible")
    assert partition("E", ok) == ("QE", "eligible")


def test_the_worked_example_keeps_raw_and_qualified_counts_apart():
    # tracking §5: eight matured endpoints, raw 5S 2E 1M, one S known too early
    early = [{"code": "minimum_delay", "result": "ineligible"}]
    ok = [{"code": "minimum_delay", "result": "eligible"}]
    rows = [("S", ok)] * 4 + [("S", early)] + [("E", ok)] * 2 + [("M", ok)] + [("N", ok)]
    counts = endpoint_counts(
        [
            dict(zip(("bucket", "eligibility"), partition(raw, r), strict=True), raw=raw)
            for raw, r in rows
        ]
    )
    assert counts["raw"] == {"S": 5, "E": 2, "H": 0, "U": 0, "M": 1, "N": 1}
    assert counts["claim"] == {"QS": 4, "QE": 2, "QH": 0, "QU": 0, "QM": 1, "QX": 1, "QN": 1}
    assert counts["matured"] == 8
    assert counts["qx"] == {"ineligible": 1, "uncertain": 0}
    assert counts["missing_only_range"] is None  # withheld: QX is not zero
    assert counts["formulas"] == {
        "raw_correct": [5, 7],
        "graded": [7, 7],
        "qualified_coverage": [4, 8],
        "qualified_correct": [4, 6],
        "checked": [7, 8],
    }


def at_day(day, hour, minute=0):
    return f"2026-10-{day:02d}T{hour:02d}:{minute:02d}:00.000Z"


def test_cost_is_clipped_to_its_evaluation_interval_never_rounded_to_whole_spans():
    # data-contract I08/I09: 20 m on Oct 5, 30 m on Oct 15, and 11:58-12:03 on Oct 8
    spans = [
        span("answer", 0, 20, started_at=at_day(5, 10), ended_at=at_day(5, 10, 20)),
        span("answer", 0, 30, started_at=at_day(15, 10), ended_at=at_day(15, 10, 30)),
        span("study", 0, 5, started_at=at_day(8, 11, 58), ended_at=at_day(8, 12, 3)),
    ]
    start, upper = at_day(1, 0), at_day(8, 12)
    assert ledger(clipped(spans, start, upper))["total_ms"] == 22 * MIN
    assert ledger(clipped(spans, start, at_day(22, 0)))["total_ms"] == 55 * MIN
    assert ledger(clipped(spans, at_day(8, 12), at_day(8, 12)))["total_ms"] is None  # empty


def test_a_missing_only_range_needs_every_other_endpoint_qualified():
    ok = [{"code": "minimum_delay", "result": "eligible"}]
    rows = [("S", ok)] * 3 + [("E", ok), ("M", ok)]
    counts = endpoint_counts(
        [
            dict(zip(("bucket", "eligibility"), partition(raw, r), strict=True), raw=raw)
            for raw, r in rows
        ]
    )
    assert counts["missing_only_range"] == [[3, 5], [4, 5]]
