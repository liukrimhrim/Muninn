"""Slice 4 at the application seam: following the same skills over time (routine-tracking-1)."""

import pytest

from muninn import workflows
from tests.conftest import rid
from tests.drafts import ALL_SHOWN, ANSWER, CONNECTION_ERROR, SOURCE, judged
from tests.test_corrections import two_exercises


def begin(app):
    added = app.add_material(rid(), title="Binary search", text=SOURCE, purpose=None)
    op = app.run_operation(added["operation"]["id"])
    return next(o for o in op["outputs"] if o["kind"] == "curriculum")["id"]


def practise(app, curriculum, text=ANSWER):
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    step = app.next_exercise(rid(), session_id=session["id"])
    attempt = step["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response=text, client_at=None
    )
    app.run_operation(sent["operation"]["id"])
    return step


def report(app, cohort):
    return app.read(workflows.tracking_view, cohort)


def test_a_tracking_plan_needs_admitted_goals(make_app):
    app = make_app(two_exercises())
    curriculum = begin(app)
    preview = app.read(workflows.tracking_preview_view, curriculum)
    assert (preview["population"], len(preview["outside"])) == ([], 2)
    with pytest.raises(ValueError, match="start practice"):
        app.start_tracking(rid(), curriculum_id=curriculum)


def test_tracking_freezes_its_population_and_assigns_ordinary_checks_before_answers(
    make_app, clock
):
    app = make_app(two_exercises(), judged(ALL_SHOWN), judged(CONNECTION_ERROR))
    curriculum = begin(app)
    first = practise(app, curriculum)  # day 0, 10:00: both goals shown
    clock.advance(minutes=30)
    preview = app.read(workflows.tracking_preview_view, curriculum)
    assert [p["baseline"]["state"] for p in preview["population"]] == ["selected", "selected"]
    assert [w["start"] for w in preview["windows"]] == [
        "2026-10-24T10:30:00.000Z",
        "2026-10-31T10:30:00.000Z",
        "2026-11-07T10:30:00.000Z",
    ]
    request = rid()
    cohort = app.start_tracking(request, curriculum_id=curriculum)["cohort"]
    assert app.start_tracking(request, curriculum_id=curriculum)["cohort"] == cohort  # retried
    with pytest.raises(ValueError, match="already"):
        app.start_tracking(rid(), curriculum_id=curriculum)
    frozen = report(app, cohort["id"])
    baselines = [m["baseline"]["attempts"] for m in frozen["population"]]
    assert baselines == [[{**first["attempt"], "revision": 2}]] * 2  # the submitted revision
    assert len(frozen["endpoints"]) == 6

    clock.advance(hours=25)  # window 1: the ordinary due check is assigned when offered
    check = practise(app, curriculum)
    assigned = [e for e in report(app, cohort["id"])["endpoints"] if e["assigned_attempt"]]
    assert [(e["window"], e["assigned_attempt"]["id"]) for e in assigned] == [
        (0, check["attempt"]["id"]),
        (0, check["attempt"]["id"]),
    ]
    assert report(app, cohort["id"])["windows"][0]["counts"]["claim"]["QN"] == 2  # not mature

    clock.advance(days=7)  # window 1 has closed
    window = report(app, cohort["id"])["windows"][0]
    assert [
        (e["raw"], e["claims"]["performance"]["bucket"], e["claims"]["later_check"]["bucket"])
        for e in window["endpoints"]
    ] == [
        ("S", "QS", "QS"),  # the fact: correct, independent, a day after its anchor
        ("E", "QE", "QE"),  # the connection: a supported error
    ]
    assert [r["code"] for r in window["endpoints"][0]["claims"]["later_check"]["reasons"]] == [
        "contract",
        "occurrence_window",
        "aid_availability",
        "minimum_delay",
        "relevant_exposure",
        "later_session",
    ]
    assert window["counts"]["formulas"]["raw_correct"] == [1, 2]
    assert (window["changes"]["S->S"], window["changes"]["S->E"]) == (1, 1)  # from baselines

    clock.advance(days=8)  # window 2 closed with no ordinary check offered in it
    second = report(app, cohort["id"])["windows"][1]
    assert [(e["raw"], e["reason"]) for e in second["endpoints"]] == [
        ("M", "no ordinary check was offered in this window"),
    ] * 2
    effort = report(app, cohort["id"])["cost"]
    assert effort["membership_rule"]["name"] == "cost-membership"
    assert effort["window"] == ["2026-10-24T10:30:00.000Z", "2026-11-09T11:30:00.000Z"]


def test_stopping_tracking_ends_assignment_and_later_windows_become_missing(make_app, clock):
    app = make_app(two_exercises(), judged(ALL_SHOWN), judged(ALL_SHOWN))
    curriculum = begin(app)
    practise(app, curriculum)
    cohort = app.start_tracking(rid(), curriculum_id=curriculum)["cohort"]
    current = report(app, cohort["id"])
    app.stop_tracking(rid(), cohort_id=cohort["id"], base=current["ref"]["revision"], reason="busy")
    clock.advance(hours=25)
    practise(app, curriculum)  # an ordinary check, no longer assigned
    clock.advance(days=21)
    stopped = report(app, cohort["id"])
    assert stopped["lifecycle"] == "stopped"
    assert {(e["raw"], e["reason"]) for w in stopped["windows"] for e in w["endpoints"]} == {
        ("M", "tracking was stopped")
    }


def test_a_hint_never_confirmed_keeps_the_raw_grade_but_cannot_qualify_the_claim(make_app, clock):
    app = make_app(two_exercises(), judged(ALL_SHOWN), judged(ALL_SHOWN))
    curriculum = begin(app)
    practise(app, curriculum)
    cohort = app.start_tracking(rid(), curriculum_id=curriculum)["cohort"]
    clock.advance(hours=25)
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    attempt = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    app.reveal_hint(rid(), attempt_id=attempt["id"], hint_id="h1")  # sent, never acknowledged
    sent = app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response=ANSWER, client_at=None
    )
    app.run_operation(sent["operation"]["id"])
    clock.advance(days=7)
    window = report(app, cohort["id"])["windows"][0]
    connection = window["endpoints"][1]  # the hint covers the connection's first criterion
    performance = connection["claims"]["performance"]
    assert (connection["raw"], performance["bucket"], performance["eligibility"]) == (
        "S",
        "QX",
        "uncertain",
    )
    assert window["counts"]["qx"] == {"ineligible": 0, "uncertain": 1}
