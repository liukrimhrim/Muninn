"""Slice 3 exit check, end to end over HTTP with a scripted model (first-build-plan.md).

A changed condition invalidates dependent exercise mappings. A corrected grade updates
the effective state once. Old definitions and judgments remain inspectable. A flagged
contradiction cannot disappear through reuse. Unrelated material remains usable.
"""

import uuid

from tests.conftest import FailIfCalled
from tests.drafts import (
    ALL_SHOWN,
    CONNECTION_ERROR,
    NOTES_SOURCE,
    TWO_CAUSES,
    VOCAB_SOURCE,
    judged,
    notes_outline,
    outline,
    vocab_outline,
)
from tests.test_exit_check import learn

CONNECTION = "Explain why binary search needs only about log2(n) comparisons"
SORTED = "Binary search only works on a sorted array."


def test_corrections_keep_history_and_leave_unrelated_work_usable(browser, clock):  # noqa: PLR0915
    b = browser(
        outline(),
        judged(CONNECTION_ERROR, hypotheses=[TWO_CAUSES[1]]),
        judged(ALL_SHOWN),
        vocab_outline(),
        notes_outline,
    )
    curriculum, _session, attempt = learn(b)
    before = b.get(f"/curricula/{curriculum}")
    t2 = before["targets"][1]
    assert (t2["evidence"]["label"], t2["schedule"]["need"]) == ("error", "repair")
    clock.advance(hours=2)

    # "this judgment is wrong": reviewed, previewed, then accepted once
    feedback = b.get(f"/attempts/{attempt['id']}")
    assert feedback["disputable"] is True
    review = b.post(f"/attempts/{attempt['id']}/dispute", reason="My answer is valid")["operation"]
    preview = b.get(f"/operations/{review['id']}/correction")
    assert preview["changes"] is True
    assert [c["after"]["outcome"] for c in preview["criteria"]] == ["demonstrated"] * 3
    accept = str(uuid.uuid4())
    shown = {"preview": preview["digest"]}
    accepted = b.post(f"/operations/{review['id']}/correction/accept", accept, **shown)
    assert b.post(f"/operations/{review['id']}/correction/accept", accept, **shown) == accepted
    corrected = b.get(f"/attempts/{attempt['id']}")
    assert corrected["attempt"]["response"] == feedback["attempt"]["response"]
    assert [c["outcome"] for c in corrected["criteria"]][2] == "demonstrated"
    assert [[r["outcome"] for r in j["results"]] for j in corrected["earlier_judgments"]] == [
        ["demonstrated", "demonstrated", "error"]
    ]
    after = b.get(f"/curricula/{curriculum}")
    t2 = after["targets"][1]
    assert (t2["evidence"]["label"], t2["schedule"]["need"], t2["schedule"]["due_at"]) == (
        "independent",
        "independent_check",
        "2026-10-25T10:00:00.000Z",  # the answer's own time + 24 h, not the correction's
    )
    assert after["counts"]["errors"] == 0

    # a changed condition holds the exercise written for the old goal
    goal = t2["ref"]
    b.post(
        f"/targets/{goal['id']}/revise",
        base=goal["revision"],
        action=t2["action"],
        mode=t2["mode"],
        conditions=[*t2["conditions"], "for a list that may arrive unsorted"],
        requirements=t2["requirements"],
        reason="the goal should cover unsorted input",
    )
    edited = b.get(f"/curricula/{curriculum}")
    assert edited["exercises"][0]["hold"] == f"written for an earlier version of: {CONNECTION}"
    later = b.post(f"/curricula/{curriculum}/sessions")["session"]
    assert b.post(f"/sessions/{later['id']}/next")["kind"] == "none"

    # old definitions and judgments stay inspectable, each with its own evidence
    history = b.get(f"/targets/{goal['id']}/history")
    old, new = history["revisions"]
    assert (old["ref"], old["current"], new["current"]) == (goal, False, True)
    assert old["evidence"]["label"] == "independent"
    assert new["evidence"]["label"] == "untested"
    assert new["mapping"]["relation"] == "changed"
    (answer,) = old["answers"]
    assert [j["current"] for j in answer["judgments"]] == [False, True]
    assert answer["judgments"][1]["revision_reason"] == "My answer is valid"
    assert any(s["resolution_rule"] for s in old["schedule"])

    # a flagged claim cannot be cleared by reusing it for new material
    claim = next(k for k in edited["targets"][0]["knowledge"] if k["statement"] == SORTED)
    b.post(
        f"/knowledge/{claim['ref']['id']}/flag",
        base=claim["ref"]["revision"],
        reason="it also needs random access",
    )
    b.post("/materials", title="Tarvi", text=VOCAB_SOURCE)
    b.post("/materials", title="Searching notes", text=NOTES_SOURCE)
    drafting = b.get("/home")["drafting"]
    (waiting,) = [d for d in drafting if d["operation"]["acceptance"] == "pending"]
    op = waiting["operation"]["id"]
    proposals = {p["key"]: p for p in b.get(f"/operations/{op}/proposals")["claims"]}
    assert proposals["b1"]["choices"] == ["hold"]
    refused = b.post(f"/operations/{op}/accept", decisions={"b1": "reuse"}, expect=422)
    assert "flagged" in refused["error"]
    notes = b.post(f"/operations/{op}/accept", decisions={"b2": "separate"})["curriculum"]
    notes_view = b.get(f"/curricula/{notes['id']}")
    repeated = next(k for k in notes_view["targets"][0]["knowledge"] if k["form"] == "fact")
    assert repeated["status"] == "disputed"
    flagged = next(
        k
        for k in b.get(f"/curricula/{curriculum}")["targets"][0]["knowledge"]
        if k["ref"]["id"] == claim["ref"]["id"]
    )
    assert flagged["status"] == "disputed"

    # unrelated material remains usable
    vocab = next(c for c in b.get("/home")["curricula"] if c["title"] == "Tarvi words")
    elsewhere = b.post(f"/curricula/{vocab['id']}/sessions")["session"]
    assert b.post(f"/sessions/{elsewhere['id']}/next")["kind"] == "exercise"
    assert notes_view["targets"][1]["hold"] is None

    # restart, export and restore: corrections, mappings and holds come back, no model call
    pages = [f"/targets/{goal['id']}/history", f"/attempts/{attempt['id']}"]
    pages += [f"/curricula/{curriculum}", f"/curricula/{notes['id']}"]
    saved = [b.get(page) for page in pages]
    again = browser(provider=FailIfCalled())
    archive = again.client.get("/api/export")
    again.post("/restore", archive=archive.text)
    assert [again.get(page) for page in pages] == saved
