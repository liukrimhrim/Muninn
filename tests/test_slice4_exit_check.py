"""Slice 4 exit check, end to end over HTTP (first-build-plan.md, build order row 4).

Use a controllable clock with the real store and scheduler adapter; restart across a due
boundary. Assert every capability transition, including failed, hinted and unresolved
checks. An immediate correction never advances a later-review interval. Combined
evidence satisfies only its actual targets. Overrun and too-small budgets preserve
unresolved needs.

The plan's capability transitions, and where each is asserted below:

| Plan row | Test (R = ``..._across_a_restart``, P = ``test_repair_...``) |
|---|---|
| Material selected, no practice: no dated review or backlog | R, day 0 |
| Targets chosen for practice: admitted, initial need, no credit | R, day 0 |
| First owned independent answer: check 24 h later | R, day 0 |
| First answer missing / supported error | R, day 0 / P, day 0 |
| Study or corrective help completed: check 24 h later | P, day 0 |
| Immediate unaided success after help: 24 h check kept | P, day 0 |
| On-time owned independent check: +7 days, once | R, day 1 |
| Due check with a supported error: repair, then 24 h after practice | P, day 1 |
| Help on a due check: helped practice, 24 h after the help | R, day 3 |
| Due answer missing or unjudgeable: still pending, no loop | R, day 4 |
| Extra check before due: due unchanged | R, days 0 and 1 |
| Answer-bearing exposure before a due check: next offer deferred | R, day 2 |
| A corrected assessment: recomputed from the original time | R, day 4 |
"""

import uuid

from tests.conftest import FailIfCalled, ScriptedProvider
from tests.drafts import (
    ALL_SHOWN,
    ANSWER,
    EXPLANATION,
    SOURCE,
    VOCAB_SOURCE,
    assessment,
    explained,
    explanation_outline,
    fresh_explanation,
    judged,
    teaching,
    vocab_outline,
    with_modes,
)
from tests.test_corrections import two_exercises

FACT = "It must be sorted."
FACT_SHOWN = assessment({"c1": "demonstrated"}, {"c1": [FACT]})
SHOWN = explained({"c1": "demonstrated", "c2": "demonstrated"})
WRONG = explained({"c1": "demonstrated", "c2": "error"})
BLUE = assessment({"c1": "demonstrated"}, {"c1": ["Blue"]})


def at(day, hour, minute):
    """Return the UTC time ``day`` days after 2026-10-24 (October has 31 days)."""
    month, date = 10 + (23 + day) // 31, (23 + day) % 31 + 1
    return f"2026-{month:02d}-{date:02d}T{hour:02d}:{minute:02d}:00.000Z"


def curriculum(b, title):
    return next(c for c in b.get("/home")["curricula"] if c["title"] == title)["id"]


def goals(b, curriculum_id):
    return {t["ref"]["id"]: t for t in b.get(f"/curricula/{curriculum_id}")["targets"]}


def schedule(b, curriculum_id, target):
    return goals(b, curriculum_id)[target["id"]]["schedule"]


def session(b, *curricula, budget=None):
    return b.post("/sessions", curricula=list(curricula), budget_seconds=budget)["session"]


def answer(b, session_id, text, *, exercise_id=None, hint=None):
    step = b.post(f"/sessions/{session_id}/next", exercise_id=exercise_id)
    attempt = step["attempt"]
    base = attempt["revision"]
    if hint:
        b.post(f"/attempts/{attempt['id']}/hints/{hint}/reveal")
        base = b.post(f"/attempts/{attempt['id']}/hints/{hint}/ack", base=base)["attempt"][
            "revision"
        ]
    b.post(f"/attempts/{attempt['id']}/submit", base=base, response=text)
    return step


def slots(b, session_id):
    return [r["role"] for r in b.get(f"/sessions/{session_id}")["attempt"]["roles"]]


def fact_exercise(b, curriculum_id):
    return next(
        e["ref"]["id"]
        for e in b.get(f"/curricula/{curriculum_id}")["exercises"]
        if e["prompt"].startswith("What must hold")
    )


def test_every_capability_transition_holds_across_a_restart(browser, clock):  # noqa: PLR0915
    provider = ScriptedProvider(
        two_exercises(),
        judged({"c1": "demonstrated", "c2": "demonstrated", "c3": "not_shown"}),
        FACT_SHOWN,
        judged(ALL_SHOWN),
        FACT_SHOWN,
        judged(ALL_SHOWN),
        judged({"c1": "demonstrated", "c2": "demonstrated", "c3": "cannot_judge"}),
        judged(ALL_SHOWN),
    )
    b = browser(provider=provider)
    b.post("/materials", title="Binary search", text=SOURCE)
    c = curriculum(b, "Binary search")
    fact, connection = (t["ref"] for t in b.get(f"/curricula/{c}")["targets"])

    # material selected, nothing practised: no dated review, no backlog
    assert [(t["state"], t["schedule"]) for t in goals(b, c).values()] == [("unstarted", None)] * 2
    assert b.get("/home")["due"]["checks"] == 0

    # day 0 10:00: practice admits only the covered goals; the answer is judged per goal
    s1 = session(b, c)
    answer(b, s1["id"], ANSWER)
    now = goals(b, c)
    assert [now[g["id"]]["state"] for g in (fact, connection)] == ["active", "active"]
    assert schedule(b, c, fact)["due_at"] == at(1, 10, 0)  # first demonstration + 24 h
    assert schedule(b, c, connection) == {  # missing evidence: no failure, no date
        "type": "capability",
        "need": "initial",
        "hold_reason": None,
        "due_at": None,
        "next_offer": {
            "at": at(1, 10, 0),
            "reason": "offered 24 hours after the latest relevant exposure",
        },
    }
    attempt = b.get(f"/sessions/{s1['id']}")["attempt"]["ref"]
    clock.advance(minutes=1)
    shown = b.post(f"/attempts/{attempt['id']}/feedback-viewed")["exposure"]
    clock.advance(minutes=1)
    b.post(f"/exposures/{shown['id']}/close")  # the page leaves the feedback at 10:02
    waiting = b.post(f"/sessions/{s1['id']}/next")
    assert (waiting["kind"], waiting["upcoming"]) == ("none", [at(1, 10, 2)])  # no loop

    # day 0 10:30: an extra check before the due time leaves the due date alone
    clock.advance(minutes=28)
    answer(b, s1["id"], FACT, exercise_id=fact_exercise(b, c))
    assert slots(b, s1["id"]) == ["extra"]
    assert schedule(b, c, fact)["due_at"] == at(1, 10, 0)
    tracking = b.post(f"/curricula/{c}/tracking")["cohort"]

    # restart across the due boundary: day 1 12:30, a new process on the same store
    clock.advance(days=1, hours=2)
    b = browser(provider=provider)
    home = b.get("/home")
    assert (home["due"]["checks"], home["due"]["curricula"]) == (2, [c])
    s2 = session(b, c)
    check = answer(b, s2["id"], ANSWER)  # the oldest need first; one task serves both
    assert slots(b, s2["id"]) == ["owner", "owner"]
    assert schedule(b, c, fact)["due_at"] == at(8, 12, 30)  # on time: + 7 days, once
    assert schedule(b, c, connection)["due_at"] == at(2, 12, 30)  # its first demonstration
    clock.advance(minutes=1)
    answer(b, s2["id"], FACT, exercise_id=fact_exercise(b, c))
    assert slots(b, s2["id"]) == ["extra"]
    assert schedule(b, c, fact)["due_at"] == at(8, 12, 30)  # extra work cannot advance it again

    # day 2: seeing the answer defers the next offer; reopening defers it again
    views = [b.post(f"/attempts/{check['attempt']['id']}/feedback-viewed") for _ in "ab"]
    clock.advance(minutes=4)
    for view in views:  # the page was left; the reopened copy too
        b.post(f"/exposures/{view['exposure']['id']}/close")
    deferred = schedule(b, c, connection)
    assert (deferred["due_at"], deferred["next_offer"]["at"]) == (at(2, 12, 30), at(2, 12, 35))
    clock.advance(days=1, minutes=-3)  # day 2 12:32: due, but not yet eligible
    s3 = session(b, c)
    assert b.post(f"/sessions/{s3['id']}/next")["upcoming"] == [at(2, 12, 35)]
    again = b.post(f"/attempts/{check['attempt']['id']}/feedback-viewed")["exposure"]
    assert schedule(b, c, connection)["next_offer"]["at"] is None  # open: certifies nothing
    b.post(f"/exposures/{again['id']}/close")
    assert schedule(b, c, connection)["next_offer"]["at"] == at(3, 12, 32)

    # day 3 12:40: help on a due check is helped practice, not a pass
    clock.advance(days=1, minutes=8)
    s4 = session(b, c)
    answer(b, s4["id"], ANSWER, hint="h1")
    assert slots(b, s4["id"]) == ["extra", "owner"]  # combined: only the due goal is owned
    assert schedule(b, c, connection)["due_at"] == at(4, 12, 40)  # 24 h after the help
    assert schedule(b, c, fact)["due_at"] == at(8, 12, 30)  # the other goal is untouched

    # day 4 12:45: an unjudgeable due answer stays pending, without failure or a new interval
    clock.advance(days=1, minutes=5)
    s5 = session(b, c)
    unclear = answer(b, s5["id"], ANSWER)
    pending = schedule(b, c, connection)
    assert (pending["need"], pending["due_at"]) == ("clarify", at(4, 12, 40))
    assert b.post(f"/sessions/{s5['id']}/next")["kind"] == "none"  # not served again at once

    # a corrected judgment is replayed from the answer's own time, once
    clock.advance(hours=2)
    review = b.post(f"/attempts/{unclear['attempt']['id']}/dispute", reason="My answer is valid")
    preview = b.get(f"/operations/{review['operation']['id']}/correction")
    request = str(uuid.uuid4())
    body = {"preview": preview["digest"]}
    first = b.post(f"/operations/{review['operation']['id']}/correction/accept", request, **body)
    assert (
        b.post(f"/operations/{review['operation']['id']}/correction/accept", request, **body)
        == first
    )
    assert schedule(b, c, connection)["due_at"] == at(11, 12, 45)  # the answer + 7 days

    # the later-checks view keeps every check; tracking assigned the ordinary check in time
    checks = b.get(f"/curricula/{c}/checks")
    assert checks["counts"]["met_on_time"] == 2
    report = b.get(f"/tracking/{tracking['id']}")
    assigned = [e for e in report["endpoints"] if e["assigned_attempt"]]
    assert {e["assigned_attempt"]["id"] for e in assigned} == {check["attempt"]["id"]}

    # restart and restore: due times, next offers and tracking come back, no model call
    pages = ["/home", f"/curricula/{c}", f"/curricula/{c}/checks", f"/tracking/{tracking['id']}"]
    saved = [b.get(p) for p in pages]
    restarted = browser(provider=FailIfCalled())
    assert [restarted.get(p) for p in pages] == saved
    archive = restarted.client.get("/api/export")
    restarted.post("/restore", archive=archive.text)
    assert [restarted.get(p) for p in pages] == saved


def step(b, session_id):
    """Take the next step over HTTP; authoring runs in the background task."""
    taken = b.post(f"/sessions/{session_id}/next")
    if taken["kind"] == "preparing":
        taken = b.post(f"/sessions/{session_id}/next")
    return taken


def test_repair_dates_checks_from_practice_and_an_immediate_success_never_advances(browser, clock):
    b = browser(
        explanation_outline(),
        WRONG,
        teaching(),
        fresh_explanation(),
        SHOWN,
        WRONG,
        teaching(),
        fresh_explanation(),
    )
    b.post("/materials", title="Why binary search is fast", text=SOURCE)
    c = curriculum(b, "Binary search")
    (goal,) = (t["ref"] for t in b.get(f"/curricula/{c}")["targets"])
    s1 = session(b, c)
    answer(b, s1["id"], EXPLANATION)  # day 0 10:00: a supported error on the first answer
    assert schedule(b, c, goal)["need"] == "repair"
    assert schedule(b, c, goal)["due_at"] is None  # no dated mastery claim

    study = step(b, s1["id"])["study"]
    clock.advance(minutes=5)
    b.post(f"/studies/{study['id']}/complete", base=study["revision"])
    assert schedule(b, c, goal)["due_at"] == at(1, 10, 5)  # completed help + 24 h
    fresh = step(b, s1["id"])
    assert fresh["kind"] == "verification"
    b.post(
        f"/attempts/{fresh['attempt']['id']}/submit",
        base=fresh["attempt"]["revision"],
        response=EXPLANATION,
    )
    after = schedule(b, c, goal)
    assert (after["need"], after["due_at"]) == ("independent_check", at(1, 10, 5))  # not 7 days

    # day 1 10:10: the due check fails; repair comes next, not the failed prompt again
    clock.advance(days=1, minutes=5)
    s2 = session(b, c)
    due = answer(b, s2["id"], EXPLANATION)
    assert due["kind"] == "exercise"
    failed = schedule(b, c, goal)
    assert (failed["need"], failed["due_at"]) == ("repair", at(1, 10, 5))
    b.post(
        f"/sessions/{s2['id']}/end",
        base=b.get(f"/sessions/{s2['id']}")["session"]["ref"]["revision"],
        reason="stopped",
    )
    s3 = session(b, c)
    study = step(b, s3["id"])
    assert study["kind"] == "study"  # corrective practice, not a repeat of the failed check
    clock.advance(minutes=10)
    b.post(f"/studies/{study['study']['id']}/complete", base=study["study"]["revision"])
    assert schedule(b, c, goal)["due_at"] == at(2, 10, 20)  # a new 24 h check after practice
    checks = b.get(f"/curricula/{c}/checks")["targets"][0]["checks"]
    assert [(h["status"], h["due_at"], h["ended"]) for h in checks] == [
        ("replaced", at(1, 10, 5), "replaced after teaching"),  # the failed check stays visible
        ("open", at(2, 10, 20), None),
    ]
    assert [(a["role"], a["label"]) for a in checks[0]["answers"]] == [
        ("extra", "independent"),  # the immediate fresh check met nothing
        ("owner", "error"),
    ]


def test_recall_reviews_and_budgets_keep_unmet_needs_and_survive_restore(browser, clock):
    b = browser(
        with_modes(vocab_outline(), "recall"), explanation_outline(), BLUE, SHOWN, BLUE, SHOWN
    )
    b.post("/materials", title="Tarvi", text=VOCAB_SOURCE)
    b.post("/materials", title="Binary search", text=SOURCE)
    v, e = curriculum(b, "Tarvi words"), curriculum(b, "Binary search")
    (word,) = (t["ref"] for t in b.get(f"/curricula/{v}")["targets"])

    # a recall answer is reviewed only by the learner's own rating; FSRS dates the next
    s1 = session(b, v)
    first = answer(b, s1["id"], "Blue.")
    rating = b.get(f"/attempts/{first['attempt']['id']}")["ratings"]
    assert [r["choices"] for r in rating] == [["forgot", "difficult", "remembered", "easy"]]
    assert schedule(b, v, word)["need"] == "held"  # waiting for the rating
    b.post(f"/attempts/{first['attempt']['id']}/rate", target=word, choice="remembered")
    assert schedule(b, v, word)["due_at"] == at(2, 10, 0)
    s2 = session(b, e)
    answer(b, s2["id"], EXPLANATION)  # the explanation goal: due tomorrow at 10:00

    # day 2 11:00: both are due; a budget too small for either keeps both
    clock.advance(days=2, hours=1)
    small = session(b, v, e, budget=15)
    assert b.post(f"/sessions/{small['id']}/next")["kind"] == "nothing_fits"
    b.post(f"/sessions/{small['id']}/end", base=small["revision"], reason="no time")
    unmet = b.get(f"/sessions/{small['id']}/summary")["unmet"]
    assert [(u["action"], u["reason"]) for u in unmet] == [
        (
            "Explain why binary search needs only about log2(n) comparisons",
            "too long for the time left",
        ),
        ("Recall what mavo means", "too long for the time left"),
    ]

    # an overrun stops new work but keeps the answer; the other need stays with its time
    roomy = session(b, v, e, budget=100)
    taken = answer(b, roomy["id"], EXPLANATION)  # the older need: the explanation
    clock.advance(minutes=3)
    assert b.post(f"/sessions/{roomy['id']}/next")["kind"] == "budget_spent"
    assert b.get(f"/attempts/{taken['attempt']['id']}")["explanation"]
    current = b.get(f"/sessions/{roomy['id']}")["session"]
    b.post(f"/sessions/{roomy['id']}/end", base=current["ref"]["revision"], reason="time up")
    summary = b.get(f"/sessions/{roomy['id']}/summary")
    assert [(u["action"], u["reason"], u["waiting_since"]) for u in summary["unmet"]] == [
        ("Recall what mavo means", "the session's time ran out", at(2, 10, 0))
    ]
    assert schedule(b, v, word)["due_at"] == at(2, 10, 0)  # nothing was marked done

    # restore keeps reviews, FSRS state and unmet needs with no model call
    pages = [
        f"/curricula/{v}",
        f"/sessions/{roomy['id']}/summary",
        f"/attempts/{first['attempt']['id']}",
    ]
    saved = [b.get(p) for p in pages]
    restored = browser(provider=FailIfCalled())
    restored.post("/restore", archive=restored.client.get("/api/export").text)
    assert [restored.get(p) for p in pages] == saved
