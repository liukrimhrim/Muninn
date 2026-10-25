"""Slice 4 at the application seam: later checks, exposure, ownership and recall reviews."""

import pytest

from muninn import practice, workflows
from muninn.library import Conflict
from tests.conftest import rid
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
)
from tests.test_corrections import two_exercises

SHOWN = explained({"c1": "demonstrated", "c2": "demonstrated"})


def begin(app):
    """Draft the material; return (curriculum id, its one goal)."""
    added = app.add_material(rid(), title="Binary search", text=SOURCE, purpose=None)
    op = app.run_operation(added["operation"]["id"])
    curriculum = next(o for o in op["outputs"] if o["kind"] == "curriculum")
    goals = app.read(
        lambda tx: [
            t for s in tx.at(curriculum, by="content").payload["sections"] for t in s["targets"]
        ]
    )
    return curriculum["id"], goals[0]


def practise(app, curriculum, text=EXPLANATION, **choice):
    """Start a session, take its next exercise, answer it and get it assessed."""
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    step = app.next_exercise(rid(), session_id=session["id"], **choice)
    attempt = step["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response=text, client_at=None
    )
    app.run_operation(sent["operation"]["id"])
    return {**step, "session": session}


def schedule(app, target):
    return app.read(practice.schedule_view, target)


def engine_state(app, target):
    """Read the saved FSRS card straight from the store (no public view exposes it)."""
    return app.read(
        lambda tx: next(
            r.payload["engine_state"]
            for r in tx.current("schedule", by="practice")
            if r.payload["target"] == target
        )
    )


def test_an_on_time_independent_check_is_met_once_and_the_next_comes_a_week_later(make_app, clock):
    app = make_app(explanation_outline(), SHOWN, SHOWN)
    curriculum, goal = begin(app)
    practise(app, curriculum)  # 10:00: the first demonstration
    assert schedule(app, goal)["due_at"] == "2026-10-25T10:00:00.000Z"

    clock.advance(hours=25)
    check = practise(app, curriculum)
    assert check["kind"] == "exercise"
    now = schedule(app, goal)
    assert (now["need"], now["due_at"], now["obligation"]["kind"]) == (
        "independent_check",
        "2026-11-01T11:00:00.000Z",  # this answer + 7 days
        "later",
    )
    met = [
        h
        for h in app.read(practice.schedule_history, goal)
        if h["obligation"]["status"] == "consumed"
    ]
    assert [m["consumed_by"]["id"] for m in met][-1] == check["attempt"]["id"]


def the_exercise(app):
    return app.read(lambda tx: next(r.id for r in tx.current("exercise", by="content")))


def roles(app, step):
    offer = app.read(lambda tx: tx.at(step["offer"], by="practice").payload)
    return [s["role"] for s in offer["slots"]]


def test_an_extra_check_before_the_due_time_leaves_the_due_date_alone(make_app, clock):
    app = make_app(explanation_outline(), SHOWN, SHOWN)
    curriculum, goal = begin(app)
    practise(app, curriculum)
    clock.advance(hours=3)
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    assert app.next_exercise(rid(), session_id=session["id"])["kind"] == "none"  # not due yet

    early = practise(app, curriculum, exercise_id=the_exercise(app))  # the learner's own choice
    assert roles(app, early) == ["extra"]
    now = schedule(app, goal)
    assert (now["due_at"], now["obligation"]["kind"]) == ("2026-10-25T10:00:00.000Z", "later")


def test_seeing_the_answer_defers_the_next_offer_but_never_moves_the_due_time(make_app, clock):
    app = make_app(explanation_outline(), SHOWN, SHOWN)
    curriculum, goal = begin(app)
    first = practise(app, curriculum)  # 10:00
    clock.advance(minutes=1)
    shown = app.view_feedback(rid(), attempt_id=first["attempt"]["id"])["exposure"]
    clock.advance(minutes=4)
    app.close_view(rid(), exposure_id=shown["id"])  # 10:05: the feedback page is left

    now = schedule(app, goal)
    assert now["due_at"] == "2026-10-25T10:00:00.000Z"  # the original due time is kept
    assert now["next_offer"]["at"] == "2026-10-25T10:05:00.000Z"  # 24 h after the closing
    clock.advance(hours=24, minutes=-3)  # 10:02 the next day: due, but not yet eligible
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    waiting = app.next_exercise(rid(), session_id=session["id"])
    assert (waiting["kind"], waiting["upcoming"]) == ("none", ["2026-10-25T10:05:00.000Z"])

    clock.advance(minutes=3)
    check = practise(app, curriculum)
    assert roles(app, check) == ["owner"]
    assert schedule(app, goal)["due_at"] == "2026-11-01T10:05:00.000Z"


def test_an_answer_too_soon_after_seeing_the_answer_cannot_advance_the_check(make_app, clock):
    app = make_app(explanation_outline(), SHOWN, SHOWN)
    curriculum, goal = begin(app)
    practise(app, curriculum)
    clock.advance(hours=25)
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    check = app.next_exercise(rid(), session_id=session["id"])["attempt"]  # owned, due
    material = app.read_material(rid(), targets=[goal], what="claims")["exposure"]
    clock.advance(minutes=1)
    app.close_view(rid(), exposure_id=material["id"])  # the claims were opened, then closed
    sent = app.submit_answer(
        rid(), attempt_id=check["id"], base=check["revision"], response=EXPLANATION, client_at=None
    )
    app.run_operation(sent["operation"]["id"])

    now = schedule(app, goal)
    assert (now["due_at"], now["obligation"]["kind"], now["reason"]) == (
        "2026-10-25T10:00:00.000Z",  # still due: no seven-day advance from an exposed answer
        "later",
        "answered too soon after seeing the answer; this check stays due",
    )
    assert now["next_offer"]["at"] == "2026-10-26T11:01:00.000Z"  # 24 h after this answer


def test_a_view_never_closed_certifies_no_delay_until_the_learner_confirms_it(make_app, clock):
    app = make_app(explanation_outline(), SHOWN, SHOWN)
    curriculum, goal = begin(app)
    first = practise(app, curriculum)
    app.view_feedback(rid(), attempt_id=first["attempt"]["id"])  # then the tab was closed
    clock.advance(hours=25)
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    blocked = app.next_exercise(rid(), session_id=session["id"])
    assert blocked["kind"] == "none"
    assert [x["reason"] for x in blocked["left"]] == [
        "an earlier view of the answer may still be open"
    ]
    assert blocked["left"][0]["confirm_closed"] is True
    assert schedule(app, goal)["next_offer"]["at"] is None

    checkpoint = app.confirm_closed(rid(), targets=[goal])["checkpoint"]
    boundary = app.read(lambda tx: tx.at(checkpoint, by="evidence").payload)
    assert (boundary["purpose"], boundary["basis"], boundary["established_at"]) == (
        "exposure_ended",
        "learner_confirmation",
        "2026-10-25T11:00:00.000Z",
    )
    assert schedule(app, goal)["next_offer"]["at"] == "2026-10-26T11:00:00.000Z"
    assert schedule(app, goal)["due_at"] == "2026-10-25T10:00:00.000Z"  # unchanged history
    clock.advance(hours=24)
    check = practise(app, curriculum)
    assert roles(app, check) == ["owner"]
    assert schedule(app, goal)["due_at"] == "2026-11-02T11:00:00.000Z"


def answer_due_check(app, curriculum, clock, outcome, *, hint=False):
    """Demonstrate once at 10:00, then answer the due check the next day at 11:00."""
    practise(app, curriculum)
    clock.advance(hours=25)
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    attempt = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    if hint:
        app.reveal_hint(rid(), attempt_id=attempt["id"], hint_id="h1")
        attempt = app.acknowledge_hint(
            rid(), attempt_id=attempt["id"], base=attempt["revision"], hint_id="h1", client_at=None
        )["attempt"]
    sent = app.submit_answer(
        rid(),
        attempt_id=attempt["id"],
        base=attempt["revision"],
        response=EXPLANATION,
        client_at=None,
    )
    app.run_operation(sent["operation"]["id"])
    return session


@pytest.mark.parametrize(
    ("outcome", "hint", "expected"),
    [
        # help on a due check is helped practice: an independent check 24 h after it
        ("demonstrated", True, ("independent_check", "2026-10-26T11:00:00.000Z", "open")),
        # a supported error asks for repair; the due time and the open check stay
        ("error", False, ("repair", "2026-10-25T10:00:00.000Z", "open")),
        # missing evidence is no failure and no new interval
        ("not_shown", False, ("independent_check", "2026-10-25T10:00:00.000Z", "open")),
        ("cannot_judge", False, ("clarify", "2026-10-25T10:00:00.000Z", "open")),
    ],
    ids=["helped", "error", "not-shown", "cannot-judge"],
)
def test_a_due_check_that_is_not_an_independent_pass_keeps_the_check_open(
    make_app, clock, outcome, hint, expected
):
    app = make_app(explanation_outline(), SHOWN, explained({"c1": outcome, "c2": "demonstrated"}))
    curriculum, goal = begin(app)
    answer_due_check(app, curriculum, clock, outcome, hint=hint)
    now = schedule(app, goal)
    assert (now["need"], now["due_at"], now["obligation"]["status"]) == expected
    assert now["obligation"]["kind"] == "later"
    # the same prompt is not served again straight away
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    assert app.next_exercise(rid(), session_id=session["id"])["kind"] in ("none", "preparing")


# --- recall items: FSRS reviews from the learner's own ratings ---------------------------

BLUE = assessment({"c1": "demonstrated"}, {"c1": ["Blue"]})
NOT_BLUE = assessment({"c1": "error"}, {"c1": ["Red"]})


def begin_recall(app):
    added = app.add_material(rid(), title="Tarvi", text=VOCAB_SOURCE, purpose=None)
    op = app.run_operation(added["operation"]["id"])
    curriculum = next(o for o in op["outputs"] if o["kind"] == "curriculum")
    word = app.read(lambda tx: tx.at(curriculum, by="content").payload["sections"][0]["targets"][0])
    return curriculum["id"], word


def test_a_recall_review_is_the_learners_own_rating_and_fsrs_dates_the_next(make_app, clock):
    app = make_app(vocab_outline(), BLUE, BLUE)
    curriculum, word = begin_recall(app)
    first = practise(app, curriculum, text="Blue.")
    waiting = schedule(app, word)
    assert (waiting["type"], waiting["need"], waiting["hold_reason"]) == (
        "recall",
        "held",
        "waiting for your recall rating",
    )
    rating = app.read(workflows.feedback_view, first["attempt"]["id"])["ratings"]
    assert [(r["choices"], r["choice"]) for r in rating] == [
        (["forgot", "difficult", "remembered", "easy"], None)
    ]

    review = app.rate_recall(
        rid(), attempt_id=first["attempt"]["id"], target=word, choice="remembered"
    )
    saved = app.read(lambda tx: tx.at(review["review"], by="evidence").payload)
    assert (saved["choice"], saved["rating"], saved["occurred_at"]) == (
        "remembered",
        "good",
        "2026-10-24T10:00:00.000Z",  # the retrieval, not the rating's arrival
    )
    rated = schedule(app, word)
    assert (rated["need"], rated["due_at"], rated["obligation"]["kind"]) == (
        "independent_check",
        "2026-10-26T10:00:00.000Z",  # FSRS-6, Good on a new card: about 2.3 days, rounded
        "later",
    )
    assert rated["policy"]["name"] == "fsrs-recall"
    assert "engine_state" not in rated  # FSRS internals stay inside Practice
    assert set(engine_state(app, word)) == {"card"}

    clock.advance(days=2, hours=1)  # restartless: the next review is due and offered
    second = practise(app, curriculum, text="Blue.")
    assert roles(app, second) == ["owner"]
    app.rate_recall(rid(), attempt_id=second["attempt"]["id"], target=word, choice="easy")
    assert schedule(app, word)["due_at"] > "2026-11-01T00:00:00.000Z"


def test_help_an_extra_answer_or_a_corrected_grade_never_makes_a_review(make_app, clock):
    app = make_app(vocab_outline(), BLUE, NOT_BLUE, BLUE)
    curriculum, word = begin_recall(app)
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    attempt = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response="Blue.", client_at=None
    )
    app.run_operation(sent["operation"]["id"])
    app.rate_recall(rid(), attempt_id=attempt["id"], target=word, choice="remembered")

    # an extra answer before the review is due: no rating control, no review
    early = practise(app, curriculum, text="Red.", exercise_id=the_exercise(app))
    assert roles(app, early) == ["extra"]
    assert app.read(workflows.feedback_view, early["attempt"]["id"])["ratings"] == []
    with pytest.raises(ValueError, match="cannot be rated"):
        app.rate_recall(rid(), attempt_id=early["attempt"]["id"], target=word, choice="forgot")
    assert schedule(app, word)["due_at"] == "2026-10-26T10:00:00.000Z"
    assert schedule(app, word)["need"] == "repair"  # the error still asks for repair


def test_a_corrected_grade_takes_its_rating_out_of_the_review_stream(make_app):
    blue_was_wrong = assessment({"c1": "error"}, {"c1": ["Blue"]})
    app = make_app(vocab_outline(), BLUE, blue_was_wrong)
    curriculum, word = begin_recall(app)
    first = practise(app, curriculum, text="Blue.")
    attempt = first["attempt"]["id"]
    app.rate_recall(rid(), attempt_id=attempt, target=word, choice="remembered")
    op = app.dispute_judgment(rid(), attempt_id=attempt, reason="I guessed")["operation"]
    with pytest.raises(ValueError, match="being reviewed"):
        app.rate_recall(rid(), attempt_id=attempt, target=word, choice="easy")
    assert app.read(workflows.feedback_view, attempt)["ratings"] == []  # no buttons meanwhile
    app.run_operation(op["id"])
    app.accept_correction(rid(), operation_id=op["id"])

    now = schedule(app, word)
    assert (now["need"], now["obligation"]["kind"], now["due_at"]) == ("repair", "initial", None)
    assert engine_state(app, word) == {}  # no review stands; none was invented
    kept = app.read(lambda tx: [r.payload["choice"] for r in tx.current("review", by="evidence")])
    assert kept == ["remembered"]  # the rating itself is kept
    assert [r["choices"] for r in app.read(workflows.feedback_view, attempt)["ratings"]] == [
        ["forgot"]
    ]


# --- two tabs, one due check (module design M05) ----------------------------------------

FACT_SHOWN = assessment({"c1": "demonstrated"}, {"c1": ["It must be sorted."]})


def goals_of(app, curriculum):
    return app.read(
        lambda tx: [
            t
            for s in tx.get("curriculum", curriculum, by="content").payload["sections"]
            for t in s["targets"]
        ]
    )


def exercise_ids(app):
    return app.read(
        lambda tx: {r.payload["prompt"][:13]: r.id for r in tx.current("exercise", by="content")}
    )


def test_a_second_tab_resumes_the_draft_or_starts_extra_work_without_a_second_owner(
    make_app, clock
):
    app = make_app(two_exercises(), judged(ALL_SHOWN), FACT_SHOWN, judged(ALL_SHOWN))
    curriculum, fact = begin(app)
    _fact, connection = goals_of(app, curriculum)
    practise(app, curriculum, text=ANSWER)  # both goals demonstrated at 10:00
    clock.advance(hours=25)
    ids = exercise_ids(app)
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    tab_a = app.next_exercise(rid(), session_id=session["id"], exercise_id=ids["What must hol"])
    assert roles(app, tab_a) == ["owner"]

    tab_b = app.next_exercise(rid(), session_id=session["id"])  # same pre-offer state, new command
    assert (tab_b["resumed"], tab_b["attempt"]) == (True, tab_a["attempt"])
    other = app.next_exercise(rid(), session_id=session["id"], exercise_id=ids["What must be "])
    assert roles(app, other) == ["extra", "owner"]  # the fact is owned by tab A's draft

    # a stale tab cannot overwrite the draft it never saw change
    saved = app.save_draft(
        rid(), attempt_id=tab_a["attempt"]["id"], base=tab_a["attempt"]["revision"], response="It"
    )
    with pytest.raises(Conflict):
        app.submit_answer(
            rid(),
            attempt_id=tab_a["attempt"]["id"],
            base=tab_a["attempt"]["revision"],
            response="It must be sorted.",
            client_at=None,
        )
    one = app.submit_answer(
        rid(),
        attempt_id=tab_a["attempt"]["id"],
        base=saved["attempt"]["revision"],
        response="It must be sorted.",
        client_at=None,
    )
    app.run_operation(one["operation"]["id"])
    assert schedule(app, fact)["due_at"] == "2026-11-01T11:00:00.000Z"  # met once, by its owner
    clock.advance(minutes=1)
    both = app.submit_answer(
        rid(),
        attempt_id=other["attempt"]["id"],
        base=other["attempt"]["revision"],
        response=ANSWER,
        client_at=None,
    )
    app.run_operation(both["operation"]["id"])
    assert schedule(app, connection)["due_at"] == "2026-11-01T11:01:00.000Z"  # its owner met it
    assert schedule(app, fact)["due_at"] == "2026-11-01T11:00:00.000Z"  # extra: no second advance


# --- the later-checks view and caught-up-1 ----------------------------------------------

WRONG = explained({"c1": "demonstrated", "c2": "error"})


def test_a_repaired_check_is_kept_as_history_and_caught_up_is_reachable_again(make_app, clock):
    app = make_app(
        explanation_outline(), SHOWN, WRONG, teaching(), fresh_explanation(), SHOWN, SHOWN
    )
    curriculum, goal = begin(app)
    practise(app, curriculum)  # day 0 10:00: first demonstration
    assert app.read(workflows.later_checks_view, curriculum)["caught_up"]["state"] == (
        "first_check_pending"
    )
    clock.advance(hours=25)
    failed = practise(app, curriculum)  # day 1 11:00: the due check has a supported error
    session = failed["session"]
    taught = app.next_exercise(rid(), session_id=session["id"])
    app.run_operation(taught["operation"]["id"])
    study = app.next_exercise(rid(), session_id=session["id"])["study"]
    clock.advance(minutes=5)
    app.complete_study(rid(), study_id=study["id"], base=study["revision"], client_at=None)
    prepared = app.next_exercise(rid(), session_id=session["id"])
    app.run_operation(prepared["operation"]["id"])
    fresh = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=fresh["id"], base=fresh["revision"], response=EXPLANATION, client_at=None
    )
    app.run_operation(sent["operation"]["id"])  # the immediate fresh check recovers
    now = schedule(app, goal)
    assert (now["need"], now["due_at"]) == ("independent_check", "2026-10-26T11:05:00.000Z")
    view = app.read(workflows.later_checks_view, curriculum)
    assert view["caught_up"]["state"] == "after_repair_pending"

    clock.advance(hours=24)
    practise(app, curriculum)  # day 2 11:05: an on-time, independent later check
    view = app.read(workflows.later_checks_view, curriculum)
    (row,) = view["targets"]
    assert [(c["status"], c["due_at"], c["ended"]) for c in row["checks"]] == [
        ("replaced", "2026-10-25T10:00:00.000Z", "replaced after teaching"),  # failed, kept
        ("consumed", "2026-10-26T11:05:00.000Z", "met on time"),
        ("open", "2026-11-02T11:05:00.000Z", None),
    ]
    assert [(a["role"], a["label"]) for a in row["checks"][0]["answers"]] == [("owner", "error")]
    assert [(a["role"], a["label"]) for a in row["checks"][1]["answers"]] == [
        ("extra", "independent"),  # the immediate fresh check met nothing
        ("owner", "independent"),
    ]
    assert view["caught_up"] == {
        "state": "caught_up",
        "scope": "curriculum",
        "as_of": "2026-10-26T11:05:00.000Z",
        "pending": [],
    }


# --- regressions from the slice-4 spec review --------------------------------------------


def test_after_a_helped_first_answer_the_next_on_time_check_earns_a_week(make_app, clock):
    app = make_app(explanation_outline(), SHOWN, SHOWN)
    curriculum, goal = begin(app)
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    attempt = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    app.reveal_hint(rid(), attempt_id=attempt["id"], hint_id="h1")
    attempt = app.acknowledge_hint(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], hint_id="h1", client_at=None
    )["attempt"]
    sent = app.submit_answer(
        rid(),
        attempt_id=attempt["id"],
        base=attempt["revision"],
        response=EXPLANATION,
        client_at=None,
    )
    app.run_operation(sent["operation"]["id"])  # helped: the first later check is due at +24 h
    assert schedule(app, goal)["due_at"] == "2026-10-25T10:00:00.000Z"
    clock.advance(hours=25)
    practise(app, curriculum)
    assert schedule(app, goal)["due_at"] == "2026-11-01T11:00:00.000Z"  # + 7 days, not 24 h


def test_a_check_replaced_after_teaching_keeps_the_failed_checks_waiting_time(make_app, clock):
    app = make_app(explanation_outline(), SHOWN, WRONG, teaching())
    curriculum, goal = begin(app)
    practise(app, curriculum)
    clock.advance(hours=25)
    failed = practise(app, curriculum)  # the check due at 10:00 fails at 11:00
    taught = app.next_exercise(rid(), session_id=failed["session"]["id"])
    app.run_operation(taught["operation"]["id"])
    study = app.next_exercise(rid(), session_id=failed["session"]["id"])["study"]
    app.complete_study(rid(), study_id=study["id"], base=study["revision"], client_at=None)
    clock.advance(days=2)
    assert schedule(app, goal)["due_at"] == "2026-10-26T11:00:00.000Z"  # teaching + 24 h
    due = app.read(workflows.home_view)["due"]
    assert (due["checks"], due["oldest"]) == (1, "2026-10-25T10:00:00.000Z")  # the failed check's
