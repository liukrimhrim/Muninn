"""Slice 2 at the application seam: diagnosis, clarification, teaching and repair cycles."""

import pytest

from muninn import content, evidence, practice, workflows
from tests.conftest import rid
from tests.drafts import (
    ALL_SHOWN,
    ANSWER,
    CONNECTION_ERROR,
    OMITTED,
    TWO_CAUSES,
    assessment,
    hypothesis,
    judged,
    outline,
    question,
    teaching,
    variant,
)
from tests.test_workflows import answer, curriculum_id, drafted, need, targets


def concerns(app):
    return app.store.read(lambda tx: [r.view for r in tx.current("concern", by="practice")])


def label(app, target):
    return app.store.read(lambda tx: evidence.target_evidence(tx, target))


def test_a_supported_misread_gets_a_brief_correction_and_no_repair(make_app):
    app = make_app(outline(), judged(CONNECTION_ERROR, misread=["c3"]))
    _, op = drafted(app)
    session, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    _t1, t2 = targets(app, op)
    result = label(app, t2)
    assert result["label"] == "unresolved"
    assert "misread" in result["reasons"][0]
    assert need(app, t2) == "initial"  # no repair need, no failure, no due date
    assert concerns(app) == []
    graded = app.store.read(lambda tx: evidence.assessment_for(tx, submitted["attempt"]["id"]))
    assert (graded["interpretation"], graded["interpretation_criteria"]) == (
        "supported_misread",
        ["c3"],
    )
    assert app.next_exercise(rid(), session_id=session["id"])["kind"] == "none"


def test_omitted_evidence_asks_a_neutral_question_instead_of_recording_a_failure(make_app):
    omitted = hypothesis("h1", ["c3"], "explain why the count is the exponent")
    out = judged(OMITTED, hypotheses=[omitted], question=question(["c3"]))
    app = make_app(outline(), out)
    _, op = drafted(app)
    session, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    t1, t2 = targets(app, op)
    assert label(app, t1)["label"] == "independent"
    assert label(app, t2)["label"] == "unresolved"
    assert need(app, t2) == "initial"
    (concern,) = concerns(app)
    assert (concern["kind"], concern["route"], concern["status"]) == (
        "uncertainty",
        "diagnosis",
        "open",
    )
    assert [(s["target"]["id"], s["requirement_ids"]) for s in concern["scope"]] == [
        (t2["id"], ["r2"])
    ]
    asked = app.next_exercise(rid(), session_id=session["id"])
    assert asked["kind"] == "clarification"
    attempt = app.store.read(
        lambda tx: evidence.attempt_view(tx, attempt_id=asked["attempt"]["id"])
    )
    assert (attempt["purpose"], attempt["concern"]["id"]) == ("clarification", concern["ref"]["id"])
    exercise = app.store.read(lambda tx: content.definition(tx, attempt["exercise"]))
    assert exercise["prompt"].startswith("With 32 candidates")
    assert exercise["use"] == "clarification"
    assert [c["covers"][0]["requirement_ids"] for c in exercise["criteria"]] == [["r2"]]
    offer = app.store.read(lambda tx: practice.offer_for(tx, attempt["ref"]["id"]))
    assert {s["role"] for s in offer["slots"]} == {"extra"}


def ask_about_the_connection(app_script, clarification):
    """Answer the larger task with a connection error, then answer the clarification."""
    asked = question(["c3"], demonstrated=("teach", "h2"), error=("teach", "h1"))
    first = judged(CONNECTION_ERROR, hypotheses=TWO_CAUSES, question=asked)
    return [outline(), first, clarification, *app_script]


def clarify(app, op, text="32, 16, 8, 4, 2, 1"):
    session, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    asked = app.next_exercise(rid(), session_id=session["id"])
    assert asked["kind"] == "clarification"
    attempt = asked["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response=text, client_at=None
    )
    app.run_operation(sent["operation"]["id"])
    return session


def focused(outcome, **extra):
    quotes = {"c1": ["32, 16, 8"]} if outcome in ("demonstrated", "error") else {}
    return assessment({"c1": outcome}, quotes, **extra)


@pytest.mark.parametrize(("outcome", "supported"), [("demonstrated", "h2"), ("error", "h1")])
def test_competing_causes_get_one_question_and_its_answer_chooses_the_help(
    make_app, outcome, supported
):
    app = make_app(*ask_about_the_connection([], focused(outcome)))
    _, op = drafted(app)
    session = clarify(app, op)
    t1, t2 = targets(app, op)
    assert label(app, t1)["label"] == "independent"  # the correct fact survives
    assert label(app, t2)["label"] == "error"  # a cued, focused answer cannot clear the task
    (concern,) = concerns(app)
    assert (concern["route"], concern["focus"]) == ("repair", supported)
    assert [h["key"] for h in concern["hypotheses"]] == ["h1", "h2"]
    assert need(app, t1) == "independent_check"
    assert need(app, t2) == "repair"  # from the original supported error
    step = app.next_exercise(rid(), session_id=session["id"])
    assert step["kind"] == "preparing"  # teaching is authored next, not more questions


def test_a_clarification_that_shows_the_part_resolves_without_repair(make_app):
    omitted = hypothesis("h1", ["c3"], "explain why the count is the exponent")
    app = make_app(
        outline(),
        judged(OMITTED, hypotheses=[omitted], question=question(["c3"])),
        focused("demonstrated"),
    )
    _, op = drafted(app)
    session, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    attempt = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    sent = app.submit_answer(
        rid(),
        attempt_id=attempt["id"],
        base=attempt["revision"],
        response="32, 16, 8",
        client_at=None,
    )
    app.run_operation(sent["operation"]["id"])
    (concern,) = concerns(app)
    assert concern["status"] == "resolved"
    _, t2 = targets(app, op)
    assert need(app, t2) == "initial"  # a focused answer moves no schedule
    assert app.next_exercise(rid(), session_id=session["id"])["kind"] == "none"


def test_a_clarification_can_end_still_uncertain(make_app):
    app = make_app(*ask_about_the_connection([], focused("not_shown")))
    _, op = drafted(app)
    session = clarify(app, op, text="because it gets smaller")
    (concern,) = concerns(app)
    assert (concern["status"], concern["resolution_reason"]) == (
        "paused",
        practice.STILL_UNCERTAIN,
    )
    _, t2 = targets(app, op)
    assert label(app, t2)["label"] == "error"  # the original supported error stays visible
    assert app.next_exercise(rid(), session_id=session["id"])["kind"] == "none"


def test_an_inconclusive_answer_may_ask_once_more_within_the_allowance(make_app):
    again = question(["c1"], prompt="If the starting number doubles, how do the halvings change?")
    simpler = focused("not_shown", hypotheses=[hypothesis("h3", ["c1"], "x")], question=again)
    simpler["question"]["branches"][0].update(next="resolve", hypothesis_key=None)
    simpler["question"]["branches"][1].update(next="teach", hypothesis_key="h3")
    app = make_app(*ask_about_the_connection([], simpler))
    _, op = drafted(app)
    session = clarify(app, op, text="because it gets smaller")
    second = app.next_exercise(rid(), session_id=session["id"])
    assert second["kind"] == "clarification"
    prompt = app.store.read(
        lambda tx: content.definition(
            tx, evidence.attempt_view(tx, attempt_id=second["attempt"]["id"])["exercise"]
        )["prompt"]
    )
    assert prompt.startswith("If the starting number doubles")


def study_view(app, study_id):
    return app.store.read(lambda tx: evidence.study_view(tx, study_id))


def schedule_history(app, target):
    return app.store.read(lambda tx: practice.schedule_history(tx, target["id"]))


def test_teaching_is_checked_and_saved_before_delivery_and_completion_is_explicit(make_app, clock):
    app = make_app(*ask_about_the_connection([teaching()], focused("demonstrated")))
    _, op = drafted(app)
    session = clarify(app, op)
    preparing = app.next_exercise(rid(), session_id=session["id"])
    assert preparing["kind"] == "preparing"
    authored = app.run_operation(preparing["operation"]["id"])
    assert (authored["intent"], authored["acceptance"]) == ("teaching_intervention", "accepted")
    request = app.provider.requests[-1].user
    assert "explain why the count is the exponent" in request  # the supported hypothesis
    assert "32, 16, 8, 4, 2, 1" in request  # the learner's actual evidence
    step = app.next_exercise(rid(), session_id=session["id"])
    assert step["kind"] == "study"
    study = study_view(app, step["study"]["id"])
    taught = app.store.read(lambda tx: content.definition(tx, study["teaching"]))
    assert taught["authoring_operation"]["id"] == authored["ref"]["id"]
    assert taught["status"] == "accepted"
    assert {c["result"] for c in taught["review"]["checks"]} == {"pass"}
    assert (study["status"], study["content"]) == ("started", taught["content"])
    resumed = app.next_exercise(rid(), session_id=session["id"])
    assert (resumed["kind"], resumed["study"]["id"]) == ("study", study["ref"]["id"])
    _, t2 = targets(app, op)
    clock.advance(minutes=5)
    app.complete_study(
        rid(), study_id=study["ref"]["id"], base=study["ref"]["revision"], client_at=None
    )
    assert study_view(app, study["ref"]["id"])["status"] == "completed"
    (concern,) = concerns(app)
    assert concern["route"] == "verification"
    assert [(c["studies"][0]["id"], c["outcome"]) for c in concern["cycles"]] == [
        (study["ref"]["id"], "pending")
    ]
    history = schedule_history(app, t2)
    assert history[-2]["obligation"]["status"] == "replaced"  # replaced after teaching, not passed
    assert (history[-1]["obligation"]["kind"], history[-1]["due_at"]) == (
        "later",
        "2026-10-25T10:05:00.000Z",
    )


def test_teaching_refused_twice_is_not_ready_and_never_tried_a_third_time(make_app):
    invented = teaching(quotes=["Binary search is magic."])
    app = make_app(*ask_about_the_connection([invented, invented], focused("demonstrated")))
    _, op = drafted(app)
    session = clarify(app, op)
    preparing = app.next_exercise(rid(), session_id=session["id"])
    app.run_operation(preparing["operation"]["id"])
    calls = len(app.provider.requests)
    step = app.next_exercise(rid(), session_id=session["id"])
    assert step["kind"] == "not_ready"
    assert "not in the source" in step["operation"]["reason"]
    assert len(app.provider.requests) == calls
    assert app.store.read(lambda tx: tx.current("teaching", by="content")) == []


VERIFIED = judged(ALL_SHOWN)
STILL_WRONG = judged(CONNECTION_ERROR)


def step(app, session):
    """Take the next step, running any authoring it had to start."""
    taken = app.next_exercise(rid(), session_id=session["id"])
    if taken["kind"] == "preparing":
        app.run_operation(taken["operation"]["id"])
        taken = app.next_exercise(rid(), session_id=session["id"])
    return taken


def study_and_check(app, session, *, hint=False, text=ANSWER):
    """Work through the teaching, then answer the fresh check."""
    taught = step(app, session)
    assert taught["kind"] == "study"
    study = study_view(app, taught["study"]["id"])
    app.complete_study(
        rid(), study_id=study["ref"]["id"], base=study["ref"]["revision"], client_at=None
    )
    check = step(app, session)
    assert check["kind"] == "verification"
    attempt = check["attempt"]
    if hint:
        app.reveal_hint(rid(), attempt_id=attempt["id"], hint_id="h1")
        attempt = app.acknowledge_hint(
            rid(), attempt_id=attempt["id"], base=attempt["revision"], hint_id="h1", client_at=None
        )["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response=text, client_at=None
    )
    app.run_operation(sent["operation"]["id"])
    return study, check


def test_a_fresh_integrated_check_resolves_the_concern_without_moving_the_later_check(
    make_app, clock
):
    app = make_app(
        *ask_about_the_connection([teaching(), variant(), VERIFIED], focused("demonstrated"))
    )
    _, op = drafted(app)
    session = clarify(app, op)
    t1, t2 = targets(app, op)
    study, check = study_and_check(app, session)
    attempt = app.store.read(
        lambda tx: evidence.attempt_view(tx, attempt_id=check["attempt"]["id"])
    )
    bound = attempt["verification_of"]
    assert [s["id"] for s in bound["studies"]] == [study["ref"]["id"]]
    assert attempt["purpose"] == "verification"
    fresh = app.store.read(lambda tx: content.definition(tx, attempt["exercise"]))
    assert fresh["use"] == "verification"
    assert fresh["design_review"]["variation"]["kind"] == "new_instance"
    assert {t["id"] for t in fresh["targets"]} == {t1["id"], t2["id"]}  # integrated, same coverage
    packet = app.provider.requests[-2].user  # the variant request
    assert "Six doublings take 1 to 64" in packet  # the teaching it must not let be copied
    assert "What must be true of an array" in packet  # the earlier prompt it must not repeat
    (concern,) = concerns(app)
    assert (concern["status"], concern["cycles"][0]["outcome"]) == ("resolved", "recovered")
    assert label(app, t2)["label"] == "independent"
    due = app.store.read(lambda tx: practice.schedule_view(tx, t2["id"]))["due_at"]
    assert due == "2026-10-25T10:00:00.000Z"  # 24 h after the completed teaching, unchanged
    assert step(app, session)["kind"] == "none"


def test_two_unsuccessful_repair_cycles_stop_automatic_repair(make_app):
    second = variant(prompt="A sorted list has 256 entries. What must hold, and why 8 comparisons?")
    script = [
        teaching(),
        variant(),
        STILL_WRONG,
        teaching(),  # the same approach again: refused, retried once with the reason
        teaching(approach="contrast with a near miss"),
        second,
        STILL_WRONG,
    ]
    app = make_app(*ask_about_the_connection(script, focused("demonstrated")))
    _, op = drafted(app)
    session = clarify(app, op)
    study_and_check(app, session)
    (concern,) = concerns(app)
    assert (concern["route"], [c["outcome"] for c in concern["cycles"]]) == (
        "repair",
        ["unsuccessful"],
    )
    study_and_check(app, session)
    refused = app.provider.requests[-4].user  # the refused same-approach request
    assert "did not resolve it" in refused
    taught = app.store.read(lambda tx: [t["approach"] for t in content.teachings(tx)])
    assert taught == ["worked example: reverse the halving sequence", "contrast with a near miss"]
    (concern,) = concerns(app)
    assert concern["route"] == "content_review"
    assert [c["outcome"] for c in concern["cycles"]] == ["unsuccessful", "unsuccessful"]
    stopped = step(app, session)
    assert stopped["kind"] == "stopped"
    calls = len(app.provider.requests)
    app.pause_concern(rid(), concern_id=concern["ref"]["id"], base=concern["ref"]["revision"])
    assert step(app, session)["kind"] == "none"
    assert len(app.provider.requests) == calls  # no third repair was authored


@pytest.mark.parametrize(
    ("verification", "hint", "route", "kind"),
    [
        (VERIFIED, True, "later_check", "none"),
        (
            judged({"c1": "demonstrated", "c2": "demonstrated", "c3": "not_shown"}),
            False,
            "assessment_review",
            "stopped",
        ),
    ],
    ids=["helped", "unanswered"],
)
def test_a_helped_or_missing_check_never_loops_back_into_teaching(
    make_app, verification, hint, route, kind
):
    fresh = variant()
    fresh["hints"] = [{"text": "Count the halvings of 128.", "criterion_keys": ["c3"]}]
    app = make_app(
        *ask_about_the_connection([teaching(), fresh, verification], focused("demonstrated"))
    )
    _, op = drafted(app)
    session = clarify(app, op)
    study_and_check(app, session, hint=hint)
    (concern,) = concerns(app)
    assert (concern["route"], concern["cycles"][0]["outcome"]) == (
        route,
        "assisted" if hint else "incomplete",
    )
    assert step(app, session)["kind"] == kind


def answer_clarification(app, session, text="not sure"):
    asked = app.next_exercise(rid(), session_id=session["id"])
    assert asked["kind"] == "clarification"
    attempt = asked["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response=text, client_at=None
    )
    app.run_operation(sent["operation"]["id"])


def unsure_again():
    """Return an inconclusive clarification judgment that proposes one more question."""
    causes = [hypothesis("h1", ["c1"], "practice halving"), hypothesis("h2", ["c1"], "link")]
    asked = question(["c1"], demonstrated=("teach", "h2"), error=("teach", "h1"))
    return focused("not_shown", hypotheses=causes, question=asked)


def test_one_question_with_three_requests_uses_the_whole_session_allowance(make_app):
    nothing = {"c1": "not_shown", "c2": "not_shown", "c3": "not_shown"}
    compound = judged(
        nothing,
        hypotheses=[hypothesis("h1", ["c1", "c2", "c3"], "explain the whole search")],
        question=question(["c1", "c2", "c3"]),
    )
    retry_question = assessment(
        nothing, hypotheses=[hypothesis("h1", ["c1"], "x")], question=question(["c1"])
    )
    app = make_app(outline(), compound, retry_question)
    _, op = drafted(app)
    session, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    answer_clarification(app, session)
    assert step(app, session)["kind"] == "none"  # three requests already asked this session
    summary = app.store.read(lambda tx: workflows.summary_view(tx, session["id"]))
    assert (summary["clarifications"], summary["clarification_limit"]) == (3, 3)
    (concern,) = concerns(app)
    assert concern["status"] == "paused"
    assert "allowance is used up" in concern["resolution_reason"]


def test_three_questions_per_concern_across_sessions_then_help_under_uncertainty(make_app):
    app = make_app(
        *ask_about_the_connection([unsure_again(), unsure_again(), teaching()], unsure_again())
    )
    _, op = drafted(app)
    first = clarify(app, op, text="not sure")  # question 1 of this concern
    answer_clarification(app, first)  # question 2
    app.end_session(rid(), session_id=first["id"], base=first["revision"], reason="stopped")
    second = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    answer_clarification(app, second)  # question 3: reopening does not reset the concern's count
    taken = app.next_exercise(rid(), session_id=second["id"])
    assert taken["kind"] == "preparing"  # no fourth question; support under uncertainty
    (concern,) = concerns(app)
    assert (concern["route"], concern["focus"]) == ("repair", None)
    app.run_operation(taken["operation"]["id"])
    assert "support under uncertainty" in app.provider.requests[-1].user


def test_a_question_waiting_for_its_assessment_is_not_asked_again(make_app):
    app = make_app(*ask_about_the_connection([], focused("demonstrated")))
    _, op = drafted(app)
    session, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    attempt = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response="32, 16", client_at=None
    )
    waiting = app.next_exercise(rid(), session_id=session["id"])
    assert (waiting["kind"], waiting["attempt"]["id"]) == ("pending", attempt["id"])
    clarifications = [
        a for a in app.store.read(evidence.attempts) if a["purpose"] == "clarification"
    ]
    assert len(clarifications) == 1


RECURS = assessment({"c1": "error"}, {"c1": ["about log2(n) steps"]})
GOES_MISSING = assessment(
    {"c1": "not_shown"},
    hypotheses=[hypothesis("h1", ["c1"], "explain the link")],
    question=question(["c1"]),
)


@pytest.mark.parametrize("recurring", [RECURS, GOES_MISSING], ids=["error", "omitted"])
def test_a_stopped_concern_does_not_restart_repair_when_the_part_comes_up_again(
    make_app, recurring
):
    draft = outline()
    full = draft["exercises"][0]
    draft["exercises"].append(
        {**full, "prompt": "Why only about log2(n)?", "criteria": full["criteria"][2:], "hints": []}
    )
    second = variant(prompt="A sorted list has 256 entries. What must hold, and why 8 comparisons?")
    script = [
        judged(CONNECTION_ERROR, hypotheses=[TWO_CAUSES[1]]),
        teaching(),
        variant(),
        STILL_WRONG,
        teaching(approach="contrast with a near miss"),
        second,
        STILL_WRONG,
        recurring,
    ]
    app = make_app(draft, *script)
    _, op = drafted(app)
    session, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    study_and_check(app, session)
    study_and_check(app, session)
    (concern,) = concerns(app)
    app.pause_concern(rid(), concern_id=concern["ref"]["id"], base=concern["ref"]["revision"])
    later = step(app, session)
    assert later["kind"] == "exercise"  # the other practice exercise
    sent = app.submit_answer(
        rid(),
        attempt_id=later["attempt"]["id"],
        base=later["attempt"]["revision"],
        response=ANSWER,
        client_at=None,
    )
    app.run_operation(sent["operation"]["id"])
    (concern,) = concerns(app)  # the same concern continues; its count is not reset
    assert (concern["route"], concern["kind"]) == ("content_review", "error")
    assert step(app, session)["kind"] == "stopped"


def test_a_reused_concern_takes_in_new_errors_from_the_same_answer(make_app):
    draft = outline()
    draft["exercises"].append(
        {**draft["exercises"][0], "prompt": "Again: sorted, and why log2(n)?"}
    )
    later = judged({"c1": "error", "c2": "demonstrated", "c3": "error"})
    app = make_app(draft, judged(CONNECTION_ERROR, hypotheses=[TWO_CAUSES[1]]), later)
    _, op = drafted(app)
    session, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    (concern,) = concerns(app)
    app.pause_concern(rid(), concern_id=concern["ref"]["id"], base=concern["ref"]["revision"])
    again = step(app, session)
    assert again["kind"] == "exercise"
    sent = app.submit_answer(
        rid(),
        attempt_id=again["attempt"]["id"],
        base=again["attempt"]["revision"],
        response=ANSWER,
        client_at=None,
    )
    app.run_operation(sent["operation"]["id"])
    t1, t2 = targets(app, op)
    (concern,) = concerns(app)
    assert sorted((s["target"]["id"], s["requirement_ids"]) for s in concern["scope"]) == sorted(
        [(t1["id"], ["r1"]), (t2["id"], ["r2"])]
    )
    assert concern["status"] == "open"


def test_a_question_from_an_earlier_session_still_waiting_for_grading_is_shown(make_app):
    from tests.conftest import timeout

    app = make_app(*ask_about_the_connection([], timeout()))
    _, op = drafted(app)
    first, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    attempt = app.next_exercise(rid(), session_id=first["id"])["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response="32", client_at=None
    )
    assert app.run_operation(sent["operation"]["id"])["status"] == "failed"
    app.end_session(rid(), session_id=first["id"], base=first["revision"], reason="stopped")
    second = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    assert app.next_exercise(rid(), session_id=second["id"])["kind"] == "pending"
    page = app.store.read(lambda tx: workflows.practice_view(tx, second["id"]))["attempt"]
    assert (page["ref"]["id"], page["assessment"]["status"]) == (attempt["id"], "failed")
