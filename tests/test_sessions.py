"""Slice 4 at the application seam: sessions that fit useful practice into real time."""

from muninn import practice, workflows
from tests.conftest import rid
from tests.drafts import (
    ANSWER,
    CONNECTION_ERROR,
    EXPLANATION,
    SOURCE,
    TWO_CAUSES,
    VOCAB_SOURCE,
    assessment,
    explained,
    explanation_outline,
    judged,
    outline,
    question,
    vocab_outline,
    with_modes,
)

SHOWN = explained({"c1": "demonstrated", "c2": "demonstrated"})
BLUE = assessment({"c1": "demonstrated"}, {"c1": ["Blue"]})


def add(app, title, text):
    added = app.add_material(rid(), title=title, text=text, purpose=None)
    op = app.run_operation(added["operation"]["id"])
    curriculum = next(o for o in op["outputs"] if o["kind"] == "curriculum")
    goal = app.read(lambda tx: tx.at(curriculum, by="content").payload["sections"][0]["targets"][0])
    return curriculum["id"], goal


def answer(app, session, text):
    step = app.next_exercise(rid(), session_id=session["id"])
    attempt = step["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response=text, client_at=None
    )
    app.run_operation(sent["operation"]["id"])
    return step


def two_due_goals(app, clock):
    """Two curricula, each with one goal demonstrated yesterday (10:00, then 10:05)."""
    explanation, e_goal = add(app, "Binary search", SOURCE)
    vocabulary, v_goal = add(app, "Tarvi", VOCAB_SOURCE)
    answer(app, app.start_session(rid(), curriculum_id=explanation)["session"], EXPLANATION)
    clock.advance(minutes=5)
    answer(app, app.start_session(rid(), curriculum_id=vocabulary)["session"], "Blue.")
    clock.advance(hours=25)  # 11:05 the next day: both checks are due
    return (explanation, e_goal), (vocabulary, v_goal)


def scripted(*more):
    return (explanation_outline(), with_modes(vocab_outline(), "explain"), SHOWN, BLUE, *more)


def test_a_budget_too_small_for_any_check_keeps_every_need_and_says_why(make_app, clock):
    app = make_app(*scripted())
    (explanation, e_goal), (vocabulary, v_goal) = two_due_goals(app, clock)
    before = [app.read(practice.schedule_view, g) for g in (e_goal, v_goal)]
    session = app.start_session(rid(), curriculum_ids=[explanation, vocabulary], budget_seconds=15)[
        "session"
    ]
    step = app.next_exercise(rid(), session_id=session["id"])
    assert step["kind"] == "nothing_fits"
    assert [x["reason"] for x in step["left"]] == ["too long for the time left"] * 2

    ended = app.end_session(
        rid(), session_id=session["id"], base=session["revision"], reason="done"
    )
    unmet = app.read(practice.session_view, ended["session"]["id"])["unmet"]
    assert [(u["target"], u["waiting_since"], u["reason"]) for u in unmet] == [
        (e_goal, "2026-10-25T10:00:00.000Z", "too long for the time left"),
        (v_goal, "2026-10-25T10:05:00.000Z", "too long for the time left"),
    ]
    assert [app.read(practice.schedule_view, g) for g in (e_goal, v_goal)] == before


def test_an_overrun_stops_offering_keeps_the_answer_and_more_time_continues(make_app, clock):
    app = make_app(*scripted(SHOWN, BLUE))
    (explanation, e_goal), (vocabulary, v_goal) = two_due_goals(app, clock)
    session = app.start_session(
        rid(), curriculum_ids=[vocabulary, explanation], budget_seconds=100
    )["session"]
    first = app.next_exercise(rid(), session_id=session["id"])
    # the oldest waiting check comes first, whichever curriculum is listed first
    assert app.read(practice.schedule_view, e_goal)["obligation"]["id"] in [
        s["obligation_id"]
        for s in app.read(lambda tx: tx.at(first["offer"], by="practice").payload)["slots"]
    ]
    clock.advance(minutes=3)
    sent = app.submit_answer(
        rid(),
        attempt_id=first["attempt"]["id"],
        base=first["attempt"]["revision"],
        response=EXPLANATION,
        client_at=None,
    )
    app.run_operation(sent["operation"]["id"])
    spent = app.next_exercise(rid(), session_id=session["id"])
    assert spent["kind"] == "budget_spent"
    assert [(x["target"], x["reason"]) for x in spent["left"]] == [
        (v_goal, "the session's time ran out")
    ]
    assert app.read(workflows.feedback_view, first["attempt"]["id"])["explanation"]  # kept
    assert app.read(practice.schedule_view, e_goal)["due_at"] == "2026-11-01T11:08:00.000Z"

    current = app.read(practice.session_view, session["id"])
    app.change_budget(
        rid(), session_id=session["id"], base=current["ref"]["revision"], budget_seconds=600
    )
    assert app.next_exercise(rid(), session_id=session["id"])["kind"] == "exercise"


def test_a_session_proposal_names_what_fits_and_that_new_material_waits(make_app, clock):
    app = make_app(*scripted(), outline())
    (explanation, _e), (vocabulary, _v) = two_due_goals(app, clock)
    fresh, _goal = add(app, "More binary search", SOURCE)
    proposal = app.read(workflows.session_proposal_view, [explanation, vocabulary, fresh], 600)
    assert (proposal["ready"], proposal["fits"], proposal["new_material"]) == (2, 2, True)
    assert proposal["first"] == {
        "kind": "check",
        "action": "Explain why binary search needs only about log2(n) comparisons",
        "overdue": True,
    }
    small = app.read(workflows.session_proposal_view, [explanation, vocabulary], 30)
    assert (small["fits"], small["first"]["kind"]) == (1, "check")


def test_a_question_reserves_room_for_its_worst_branch(make_app):
    asked = judged(
        CONNECTION_ERROR,
        hypotheses=TWO_CAUSES,
        question=question(["c3"], demonstrated=("teach", "h2"), error=("teach", "h1")),
    )
    app = make_app(outline(), asked)
    curriculum, _goal = add(app, "Binary search", SOURCE)
    session = app.start_session(rid(), curriculum_id=curriculum, budget_seconds=189)["session"]
    answer(app, session, ANSWER)  # on a frozen clock no time is spent
    # the question (60 s) plus its worst branch, a fresh 130 s check after teaching of
    # unknown length, needs more than 190 s
    step = app.next_exercise(rid(), session_id=session["id"])
    assert step["kind"] == "nothing_fits"
    current = app.read(practice.session_view, session["id"])
    app.change_budget(
        rid(), session_id=session["id"], base=current["ref"]["revision"], budget_seconds=191
    )
    assert app.next_exercise(rid(), session_id=session["id"])["kind"] == "clarification"


def test_time_in_a_session_over_two_curricula_is_never_split_by_guessing(make_app):
    app = make_app(*scripted())
    explanation, _e = add(app, "Binary search", SOURCE)
    vocabulary, _v = add(app, "Tarvi", VOCAB_SOURCE)
    session = app.start_session(rid(), curriculum_ids=[explanation, vocabulary])["session"]
    run = app.open_timer(rid(), document_run_id="tab-1", takeover=False)["run"]
    enrollment = app.read(workflows.outline_view, explanation)["enrollment"]

    def span(minutes, start, **context):
        return {
            "id": rid(),
            "run_id": run["id"],
            "ordinal": start,
            "category": "answer",
            "monotonic_start_ms": start * 60_000,
            "monotonic_end_ms": (start + minutes) * 60_000,
            "raw_wall_start": f"2026-10-24T10:{start:02d}:00.000Z",
            "raw_wall_end": f"2026-10-24T10:{start + minutes:02d}:00.000Z",
            "session": session,
            **context,
        }

    app.record_spans(rid(), spans=[span(10, 0), span(5, 20, enrollment=enrollment)])
    e_effort = app.read(workflows.outline_view, explanation)["effort"]
    v_effort = app.read(workflows.outline_view, vocabulary)["effort"]
    assert (e_effort["total_ms"], e_effort["uncertain_membership_ms"]) == (5 * 60_000, 10 * 60_000)
    assert (v_effort["total_ms"], v_effort["uncertain_membership_ms"]) == (None, 10 * 60_000)


def test_a_budget_too_small_even_for_new_material_says_so(make_app):
    app = make_app(explanation_outline())
    curriculum, _goal = add(app, "Binary search", SOURCE)
    session = app.start_session(rid(), curriculum_id=curriculum, budget_seconds=60)["session"]
    step = app.next_exercise(rid(), session_id=session["id"])
    assert (step["kind"], step["new_material_waits"]) == ("nothing_fits", True)
