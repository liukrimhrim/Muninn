"""Slice 2 exit check, end to end over HTTP with a scripted model (first-build-plan.md).

A fact and a connected explanation share one exercise and one core path. Correct parts
survive a connection error; omitted evidence and misreads take different paths; help
is recorded; the next task changes after the learner's response; a clarification can
end "still uncertain".
"""

import pytest

from muninn.practice import STILL_UNCERTAIN
from tests.conftest import FailIfCalled
from tests.drafts import (
    ALL_SHOWN,
    ANSWER,
    CONNECTION_ERROR,
    TWO_CAUSES,
    assessment,
    hypothesis,
    judged,
    outline,
    question,
    teaching,
    variant,
)
from tests.test_exit_check import learn

FACT = "State what binary search requires of the array"
CONNECTION = "Explain why binary search needs only about log2(n) comparisons"


DIAGNOSED = judged(
    CONNECTION_ERROR,
    hypotheses=TWO_CAUSES,
    question=question(["c3"], demonstrated=("teach", "h2"), error=("teach", "h1")),
)
COUNTED = assessment({"c1": "demonstrated"}, {"c1": ["32, 16, 8"]})
VERIFIED = judged(ALL_SHOWN)


def answer_current(b, session_id, text):
    """Answer the session's open draft (resumed by the practice view) and wait for grading."""
    attempt = b.get(f"/sessions/{session_id}")["attempt"]
    assert attempt["status"] == "draft"
    b.post(
        f"/attempts/{attempt['ref']['id']}/submit", base=attempt["ref"]["revision"], response=text
    )
    return b.get(f"/attempts/{attempt['ref']['id']}")


def next_step(b, session_id):
    """Ask for the next step; a step that had to be authored first is ready on the retry."""
    step = b.post(f"/sessions/{session_id}/next")
    if step["kind"] == "preparing":  # the authoring ran as a background task
        step = b.post(f"/sessions/{session_id}/next")
    return step


def test_a_connection_error_is_diagnosed_taught_and_checked_fresh(browser):
    b = browser(outline(), DIAGNOSED, COUNTED, teaching(), variant(), VERIFIED)
    curriculum, session, attempt = learn(b)
    sid = session["id"]

    first = b.get(f"/attempts/{attempt['id']}")
    labels = {t["action"]: t["label"] for t in first["targets"]}
    assert labels == {FACT: "independent", CONNECTION: "error"}  # correct parts survive
    assert first["concern"]["route"] == "diagnosis"
    assert [h["practice"] for h in first["concern"]["hypotheses"]] == [
        "practice repeated halving",
        "explain why the count is the exponent",
    ]

    # the next task changes after the response: one discriminating question
    assert next_step(b, sid)["kind"] == "clarification"
    asked = b.get(f"/sessions/{sid}")["attempt"]
    assert (asked["purpose"], asked["prompt"]) == (
        "clarification",
        "With 32 candidates, list the remaining counts and label each halving.",
    )
    clarified = answer_current(b, sid, "32, 16, 8, 4, 2, 1 — five halvings")
    assert (clarified["concern"]["route"], clarified["concern"]["focus"]) == ("repair", "h2")

    # help: checked teaching saved before delivery, completed only by the learner
    taught = next_step(b, sid)
    assert taught["kind"] == "study"
    study = b.get(f"/studies/{taught['study']['id']}")
    assert study["status"] == "started"
    assert study["approach"] == "worked example: reverse the halving sequence"
    assert "Six doublings take 1 to 64" in study["content"]
    b.post(f"/studies/{taught['study']['id']}/complete", base=study["ref"]["revision"])

    # a fresh integrated check, not the old prompt
    assert next_step(b, sid)["kind"] == "verification"
    fresh = b.get(f"/sessions/{sid}")["attempt"]
    assert fresh["purpose"] == "verification"
    assert fresh["prompt"].startswith("A sorted list has 128 names")
    verified = answer_current(b, sid, ANSWER)
    assert verified["concern"]["status"] == "resolved"
    assert {t["action"]: t["label"] for t in verified["targets"]} == {
        FACT: "independent",
        CONNECTION: "independent",
    }
    assert next_step(b, sid)["kind"] == "none"

    summary = b.get(f"/sessions/{sid}/summary")
    assert [(h["approach"], h["status"]) for h in summary["help"]] == [
        ("worked example: reverse the halving sequence", "completed")
    ]
    assert summary["clarifications"] == 1
    assert [c["status"] for c in summary["concerns"]] == ["resolved"]

    # restart, export and restore: the whole repair history is back, with no model call
    again = browser(provider=FailIfCalled())
    archive = again.client.get("/api/export")
    again.post("/restore", archive=archive.text)
    assert again.get(f"/attempts/{fresh['ref']['id']}") == verified
    assert again.get(f"/sessions/{sid}/summary")["help"] == summary["help"]
    assert again.get(f"/studies/{taught['study']['id']}")["content"] == study["content"]
    later = again.post(f"/curricula/{curriculum}/sessions")["session"]
    assert again.post(f"/sessions/{later['id']}/next")["kind"] == "none"


@pytest.mark.parametrize(
    ("graded", "kind", "concern"),
    [
        (judged(CONNECTION_ERROR, misread=["c3"]), "none", None),
        (
            judged(
                {"c1": "demonstrated", "c2": "demonstrated", "c3": "not_shown"},
                hypotheses=[hypothesis("h1", ["c3"], "explain the link")],
                question=question(["c3"]),
            ),
            "clarification",
            "uncertainty",
        ),
    ],
    ids=["misread", "omitted"],
)
def test_omitted_evidence_and_misreads_take_different_paths(browser, graded, kind, concern):
    b = browser(outline(), graded)
    _, session, attempt = learn(b)
    feedback = b.get(f"/attempts/{attempt['id']}")
    connection = next(t for t in feedback["targets"] if t["action"] == CONNECTION)
    assert connection["label"] == "unresolved"  # neither path records a failure
    assert [c["misread"] for c in feedback["criteria"]] == [False, False, concern is None]
    assert (feedback["concern"] or {}).get("kind") == concern
    assert b.post(f"/sessions/{session['id']}/next")["kind"] == kind


def test_a_clarification_can_end_still_uncertain(browser):
    unclear = assessment({"c1": "not_shown"})
    b = browser(outline(), DIAGNOSED, unclear)
    _, session, _attempt = learn(b)
    assert next_step(b, session["id"])["kind"] == "clarification"
    after = answer_current(b, session["id"], "because it gets smaller")
    assert (after["concern"]["status"], after["concern"]["resolution_reason"]) == (
        "paused",
        STILL_UNCERTAIN,
    )
    assert b.post(f"/sessions/{session['id']}/next")["kind"] == "none"
    summary = b.get(f"/sessions/{session['id']}/summary")
    assert [c["resolution_reason"] for c in summary["concerns"]] == [STILL_UNCERTAIN]


def test_a_stopped_repair_can_be_paused_from_the_page(browser):
    wrong = judged(CONNECTION_ERROR)
    second = variant(prompt="A sorted list has 256 entries. What must hold, and why 8 comparisons?")
    b = browser(
        outline(),
        judged(CONNECTION_ERROR, hypotheses=[TWO_CAUSES[1]]),  # one cause: straight to teaching
        teaching(),
        variant(),
        wrong,
        teaching(approach="contrast with a near miss"),
        second,
        wrong,
    )
    _, session, _attempt = learn(b)
    sid = session["id"]
    for _ in range(2):
        taught = next_step(b, sid)
        assert taught["kind"] == "study"
        study = b.get(f"/studies/{taught['study']['id']}")
        b.post(f"/studies/{study['ref']['id']}/complete", base=study["ref"]["revision"])
        assert next_step(b, sid)["kind"] == "verification"
        answer_current(b, sid, ANSWER)
    stopped = b.post(f"/sessions/{sid}/next")
    assert stopped["kind"] == "stopped"
    assert stopped["concern"]["route"] == "content_review"
    concern = stopped["concern"]["ref"]
    b.post(f"/concerns/{concern['id']}/pause", base=concern["revision"])
    assert b.post(f"/sessions/{sid}/next")["kind"] == "none"
