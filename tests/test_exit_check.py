"""Slice 1 exit check, end to end over HTTP with a scripted model (first-build-plan.md)."""

import uuid

from tests.conftest import FailIfCalled, timeout
from tests.drafts import SOURCE, assessment, outline

ANSWER = "It must be sorted. Each comparison throws away half, so it takes about log2(n) steps."
GRADED = assessment(
    {"c1": "demonstrated", "c2": "demonstrated", "c3": "error"},
    {"c1": ["It must be sorted."], "c2": ["throws away half"], "c3": ["about log2(n) steps"]},
)


def learn(b):
    """Paste material, start practice and submit one free-text answer."""
    b.post("/materials", title="Binary search", text=SOURCE, purpose="Explain why it is fast")
    curriculum = b.get("/home")["curricula"][0]["id"]
    session = b.post(f"/curricula/{curriculum}/sessions")["session"]
    attempt = b.post(f"/sessions/{session['id']}/next")["attempt"]
    draft = b.post(
        f"/attempts/{attempt['id']}/draft", base=attempt["revision"], response="It must be"
    )
    submit_id = str(uuid.uuid4())
    body = {"base": draft["attempt"]["revision"], "response": ANSWER}
    first = b.post(f"/attempts/{attempt['id']}/submit", submit_id, **body)
    assert b.post(f"/attempts/{attempt['id']}/submit", submit_id, **body) == first  # retry
    return curriculum, session, attempt


def test_a_saved_encounter_survives_restart_and_restore(browser, tmp_path):
    b = browser(outline(), GRADED)
    curriculum, session, attempt = learn(b)
    seen = b.get(f"/attempts/{attempt['id']}")
    assert [c["outcome"] for c in seen["criteria"]] == ["demonstrated", "demonstrated", "error"]
    assert seen["explanation"]

    # restart the application: the exact source, exercise, answer and judgment are back
    again = browser(provider=FailIfCalled())
    assert again.get(f"/attempts/{attempt['id']}") == seen
    assert again.get(f"/curricula/{curriculum}")["source"]["text"] == SOURCE
    assert again.get(f"/sessions/{session['id']}")["attempt"]["response"] == ANSWER

    # export, restore into a separate store, and continue the same curriculum
    archive = again.client.get("/api/export")
    restored = again.post("/restore", archive=archive.text)
    assert restored["library_id"] == archive.json()["library_id"]
    assert again.get(f"/attempts/{attempt['id']}") == seen
    next_session = again.post(f"/curricula/{curriculum}/sessions")["session"]
    assert again.post(f"/sessions/{next_session['id']}/next")["attempt"] is None  # all answered
    stores = sorted(p.name for p in (tmp_path / "data").glob("library-*.sqlite"))
    assert len(stores) == 2  # the previous store is kept


def test_a_model_failure_preserves_the_answer_until_a_retry(browser):
    b = browser(outline(), timeout(), GRADED)
    _, session, _attempt = learn(b)
    pending = b.get(f"/sessions/{session['id']}")["attempt"]
    assert (pending["status"], pending["response"]) == ("submitted", ANSWER)
    assert pending["assessment"]["status"] == "failed"
    assert pending["feedback_ready"] is False
    b.post(f"/operations/{pending['assessment']['id']}/retry")
    assert b.get(f"/sessions/{session['id']}")["attempt"]["feedback_ready"] is True


def test_the_summary_separates_evidence_and_counts_time_once(browser):
    b = browser(outline(), GRADED)
    _, session, _attempt = learn(b)
    run = b.post("/timer", document_run_id="doc-1")["run"]
    spans = [
        {
            "id": str(uuid.uuid4()),
            "run_id": run["id"],
            "ordinal": n,
            "category": category,
            "monotonic_start_ms": start,
            "monotonic_end_ms": end,
            "raw_wall_start": f"2026-10-24T10:0{start // 60000}:00.000Z",
            "raw_wall_end": f"2026-10-24T10:0{end // 60000}:00.000Z",
            "session": session,
            "context": [],
        }
        for n, (category, start, end) in enumerate(
            [
                ("answer", 0, 120_000),
                ("blocked_wait", 120_000, 180_000),
                ("feedback", 180_000, 240_000),
            ],
            1,
        )
    ]
    b.post("/spans", spans=spans)
    b.post("/spans", spans=spans)  # a retried batch is not counted twice
    summary = b.get(f"/sessions/{session['id']}/summary")
    assert summary["effort"]["total_ms"] == 240_000
    assert summary["effort"]["groups"] == {"learning": 180_000, "waiting": 60_000}
    assert sorted(t["label"] for t in summary["targets"]) == ["error", "independent"]
    assert summary["headline"] == "Practiced today; later recall not checked yet."


def span(run, session, category, minutes, *, ordinal):
    start_minute, end_minute = minutes
    return {
        "id": str(uuid.uuid4()),
        "run_id": run["id"],
        "ordinal": ordinal,
        "category": category,
        "monotonic_start_ms": start_minute * 60_000,
        "monotonic_end_ms": end_minute * 60_000,
        "raw_wall_start": f"2026-10-24T10:{start_minute:02d}:00.000Z",
        "raw_wall_end": f"2026-10-24T10:{end_minute:02d}:00.000Z",
        "session": session,
        "context": [],
    }


def test_a_second_tab_must_take_over_the_timer(browser):
    b = browser(outline())
    b.post("/materials", title="t", text=SOURCE)
    curriculum = b.get("/home")["curricula"][0]["id"]
    session = b.post(f"/curricula/{curriculum}/sessions")["session"]
    first = b.post("/timer", document_run_id="tab-1")["run"]
    b.post("/spans", spans=[span(first, session, "answer", (0, 1), ordinal=1)])
    b.post("/timer", document_run_id="tab-2", expect=409)
    second = b.post("/timer", document_run_id="tab-2", takeover=True)["run"]
    assert second["id"] != first["id"]
    late = {
        "id": str(uuid.uuid4()),
        "run_id": first["id"],
        "ordinal": 1,
        "category": "answer",
        "monotonic_start_ms": 0,
        "monotonic_end_ms": 60_000,
        "raw_wall_start": "2026-10-24T10:00:00.000Z",
        "raw_wall_end": "2026-10-24T10:01:00.000Z",
        "session": session,
        "context": [],
    }
    b.post("/spans", spans=[late])  # the old tab's late span is kept but never counted
    effort = b.get(f"/sessions/{session['id']}/summary")["effort"]
    assert (effort["total_ms"], effort["stale_spans"]) == (60_000, 1)
    assert effort["unknown_tails"] == 1  # the first tab's unsaved tail is a visible gap


def test_a_stale_page_must_refresh_before_writing(browser):
    b = browser(outline())
    response = b.client.post("/api/materials", json={"request_id": "x", "title": "t", "text": "x"})
    assert response.status_code == 409
    assert b.get("/home")["drafting"] == []


def test_after_a_restart_the_page_is_told_to_claim_the_timer_again(browser):
    b = browser(outline())
    run = b.post("/timer", document_run_id="tab-1")["run"]
    span = {
        "id": str(uuid.uuid4()),
        "run_id": run["id"],
        "ordinal": 1,
        "category": "authoring",
        "monotonic_start_ms": 0,
        "monotonic_end_ms": 1000,
        "raw_wall_start": "2026-10-24T10:00:00.000Z",
        "raw_wall_end": "2026-10-24T10:00:01.000Z",
        "context": [],
    }
    assert b.post("/spans", spans=[span])["holds_timer"] is True
    restarted = browser(provider=FailIfCalled())
    late = {**span, "id": str(uuid.uuid4()), "ordinal": 2}
    assert restarted.post("/spans", spans=[late])["holds_timer"] is False
    again = restarted.post("/timer", document_run_id="tab-1")["run"]
    assert again["id"] != run["id"]


def test_time_outside_any_curriculum_stays_visible_as_library_overhead(browser):
    b = browser(outline())
    run = b.post("/timer", document_run_id="tab-1")["run"]
    b.post("/spans", spans=[span(run, None, "authoring", (0, 2), ordinal=1)])
    assert b.get("/home")["effort"]["total_ms"] == 120_000


def test_a_span_from_another_library_is_refused_without_blocking_the_batch(browser):
    b = browser(outline())
    run = b.post("/timer", document_run_id="tab-1")["run"]
    good = span(run, None, "authoring", (0, 1), ordinal=1)
    foreign = span({"id": "no-such-run"}, None, "authoring", (1, 2), ordinal=2)
    result = b.post("/spans", spans=[good, foreign])
    assert result["rejected"] == [foreign["id"]]
    assert b.get("/home")["effort"]["total_ms"] == 60_000


def test_a_malformed_span_is_refused_without_blocking_the_batch(browser):
    b = browser(outline())
    run = b.post("/timer", document_run_id="tab-1")["run"]
    good = span(run, None, "authoring", (0, 1), ordinal=1)
    bad = span(run, None, "blocked_wait", (1, 2), ordinal=2) | {
        "context": [{"id": "op-1", "status": "pending"}]  # not an exact reference
    }
    result = b.post("/spans", spans=[good, bad])
    assert result["rejected"] == [bad["id"]]
    assert b.get("/home")["effort"]["total_ms"] == 60_000
