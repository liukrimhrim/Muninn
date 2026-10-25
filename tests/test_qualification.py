"""Slice 5: deterministic qualification cases the earlier slices left uncovered.

Each test names the acceptance cases it qualifies (see ``qualification/ledger.md``).
"""

import copy
import json

import pytest

from muninn import content, evidence, practice, workflows
from muninn.library import digest, learning_fingerprint
from muninn.workflows import App
from tests import qualify
from tests.conftest import Browser, FailIfCalled, ScriptedProvider, rid
from tests.drafts import (
    ALL_SHOWN,
    ANSWER,
    CONNECTION_ERROR,
    EXPLANATION,
    TWO_CAUSES,
    assessment,
    explained,
    explanation_outline,
    judged,
    outline,
    question,
    teaching,
    variant,
    with_modes,
)
from tests.test_corrections import (
    answered,
    edit_condition,
    fact_exercise,
    reviewed,
    two_exercises,
)
from tests.test_exit_check import GRADED, learn
from tests.test_repair import ask_about_the_connection, clarify, focused, study_and_check
from tests.test_slice2_exit_check import answer_current, next_step
from tests.test_workflows import answer, curriculum_id, drafted, targets

FACT_RIGHT = assessment({"c1": "demonstrated"}, {"c1": ["It must be sorted."]})


def stores(data):
    return sorted(p.name for p in data.glob("library-*.sqlite"))


SORTED = "It must be sorted."


def practise(  # noqa: PLR0913 - one keyword per way of answering
    app, curriculum, text=ANSWER, *, session=None, hint=False, fact=False, exercise_id=None
):
    """Answer the next exercise, optionally with hint h1 shown, and get it graded.

    Returns the session and the submission. ``fact`` picks the fact-only exercise of
    ``two_exercises``, ``exercise_id`` any other (the learner's own choice).
    """
    session = session or app.start_session(rid(), curriculum_id=curriculum)["session"]
    chosen = fact_exercise(app) if fact else exercise_id
    attempt = app.next_exercise(rid(), session_id=session["id"], exercise_id=chosen)["attempt"]
    if hint:
        app.reveal_hint(rid(), attempt_id=attempt["id"], hint_id="h1")
        attempt = app.acknowledge_hint(
            rid(), attempt_id=attempt["id"], base=attempt["revision"], hint_id="h1", client_at=None
        )["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response=text, client_at=None
    )
    app.run_operation(sent["operation"]["id"])
    return {"session": session, "sent": sent}


def test_a_restore_never_hides_work_the_archive_does_not_contain(tmp_path, clock):
    # C07 recovery after use, C19 switching back after cutover, C20 divergent copies
    data = tmp_path / "data"
    first = Browser(data, ScriptedProvider(outline(), GRADED, GRADED), clock)
    curriculum, _, attempt = learn(first)
    old = first.client.get("/api/export").text

    # learning continues after the export: an older archive may not replace it
    session = first.post(f"/curricula/{curriculum}/sessions")["session"]
    chosen = first.get(f"/sessions/{session['id']}/choices")["exercises"][0]["exercise"]
    later = first.post(f"/sessions/{session['id']}/next", exercise_id=chosen["id"])["attempt"]
    first.post(f"/attempts/{later['id']}/submit", base=later["revision"], response=ANSWER)
    before = stores(data)
    refused = first.post("/restore", expect=409, archive=old)
    assert "does not contain" in refused["error"]
    assert stores(data) == before  # nothing was created or switched
    assert first.get(f"/sessions/{session['id']}")["attempt"]["response"] == ANSWER

    # a copy restored elsewhere and given a different answer diverges, whatever its sequence
    copy = Browser(tmp_path / "copy", FailIfCalled(), clock)
    copy.post("/restore", archive=old)
    session = copy.post(f"/curricula/{curriculum}/sessions")["session"]
    other = copy.post(f"/sessions/{session['id']}/next", exercise_id=chosen["id"])["attempt"]
    copy.post(f"/attempts/{other['id']}/submit", base=other["revision"], response="Other words.")
    diverged = copy.client.get("/api/export").text
    first.post("/restore", expect=409, archive=diverged)

    # a store the archive extends may be brought forward to it
    behind = Browser(tmp_path / "behind", FailIfCalled(), clock)
    behind.post("/restore", archive=old)
    behind.post("/restore", archive=diverged)
    assert behind.get(f"/attempts/{other['id']}")["attempt"]["response"] == "Other words."
    assert behind.get(f"/attempts/{attempt['id']}")["attempt"]["response"] == ANSWER


def test_reading_any_page_writes_nothing_and_calls_no_model(tmp_path, clock):
    # M06 historical reads create no learning record; O13 progress has no effect on mastery
    data = tmp_path / "data"
    b = Browser(data, ScriptedProvider(outline(), GRADED, judged(ALL_SHOWN)), clock)
    curriculum, session, attempt = learn(b)
    review = b.post(f"/attempts/{attempt['id']}/dispute", reason="My answer is valid")
    cohort = b.post(f"/curricula/{curriculum}/tracking")["cohort"]
    b = Browser(data, FailIfCalled(), clock)  # a restart; only reads from here on
    target = b.get(f"/curricula/{curriculum}")["targets"][1]["ref"]["id"]
    op = review["operation"]["id"]
    pages = [
        "/home",
        f"/curricula/{curriculum}",
        f"/curricula/{curriculum}/checks",
        f"/curricula/{curriculum}/tracking",
        f"/tracking/{cohort['id']}",
        f"/proposal?curricula={curriculum}&budget=600",
        f"/sessions/{session['id']}",
        f"/sessions/{session['id']}/summary",
        f"/sessions/{session['id']}/choices",
        f"/attempts/{attempt['id']}",
        f"/targets/{target}/history",
        f"/operations/{op}",
        f"/operations/{op}/correction",
    ]
    before = b.client.get("/api/export").json()
    seen = [b.get(page) for page in pages]
    assert [b.get(page) for page in pages] == seen
    assert learning_fingerprint(b.client.get("/api/export").json()) == learning_fingerprint(before)


def test_caught_up_speaks_about_now_and_never_hides_an_unstarted_goal(make_app, clock):
    # I04 the whole selected scope, R06 the due boundary, R11 a live indicator ages
    app = make_app(two_exercises(), FACT_RIGHT, FACT_RIGHT)
    _, op = drafted(app)
    curriculum = curriculum_id(op)
    practise(
        app, curriculum, SORTED, fact=True
    )  # day 0 10:00: first demonstration; the other goal unstarted
    clock.advance(hours=25)
    practise(
        app, curriculum, SORTED, fact=True
    )  # day 1 11:00: the on-time later check; next due day 8 11:00
    caught = app.read(workflows.later_checks_view, curriculum)["caught_up"]
    assert (caught["state"], caught["scope"]) == ("caught_up", "active")
    assert [p["code"] for p in caught["pending"]] == ["not_started"]
    clock.advance(days=7)  # exactly at the next due time: not caught up any more
    caught = app.read(workflows.later_checks_view, curriculum)["caught_up"]
    assert (caught["state"], caught["scope"]) == ("due", "curriculum")


def timing_line(app, submitted):
    """Return the line of a saved assessment request that says when the answer came."""
    op = app.operation(submitted["operation"]["id"])
    return op["input_snapshot"]["user"].split("<attempt>\n", 1)[1].split("\n", 1)[0]


def test_the_assessor_is_told_truthfully_whether_an_answer_is_immediate(make_app, clock):
    # assessor protocol v2 (spikes/answer-intake): the caller says whether this is a later
    # session; never promote an immediate answer to a delayed check (plan acceptance row
    # "Single fact, intended recall direction" relies on it; O04)
    app = make_app(two_exercises(), FACT_RIGHT, FACT_RIGHT, FACT_RIGHT)
    _, op = drafted(app)
    session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]

    first = practise(app, curriculum_id(op), SORTED, session=session, fact=True)["sent"]
    assert "first recorded answer" in timing_line(app, first)
    again = practise(app, curriculum_id(op), SORTED, session=session, fact=True)["sent"]
    assert "same session" in timing_line(app, again)
    clock.advance(hours=25)
    later = practise(app, curriculum_id(op), SORTED, fact=True)["sent"]
    assert "later session" in timing_line(app, later)


def test_teaching_authored_for_material_that_changed_meanwhile_is_never_delivered(make_app):
    # CCA06 the source changes during generation; X08 a late candidate stays with its input
    supported = judged(CONNECTION_ERROR, hypotheses=[TWO_CAUSES[1]])
    app = make_app(outline(), supported, teaching())
    _op, session, attempt, _t1, t2 = answered(app)
    preparing = app.next_exercise(rid(), session_id=session["id"])
    assert preparing["kind"] == "preparing"
    edit_condition(app, t2)  # the goal's meaning changes while the teaching is being written
    late = app.run_operation(preparing["operation"]["id"])
    assert (late["acceptance"], late["outputs"]) == ("stale", [])
    assert app.read(content.teachings) == []
    assert app.next_exercise(rid(), session_id=session["id"])["kind"] != "study"
    kept = app.read(lambda tx: evidence.attempt_view(tx, attempt_id=attempt["id"]))
    assert kept["response"] == ANSWER  # the earlier answer and its judgment stay
    assert app.read(evidence.assessment_for, attempt["id"]) is not None


def test_feedback_seen_before_the_grade_never_reclassifies_the_answer(make_app, clock):
    # CCA09 feedback between answer and grade; X19 a check is not its own prior exposure
    app = make_app(explanation_outline(), explained({"c1": "demonstrated", "c2": "demonstrated"}))
    _, op = drafted(app)
    (goal,) = app.read(
        lambda tx: [
            t
            for s in tx.at(
                next(o for o in op["outputs"] if o["kind"] == "curriculum"), by="content"
            ).payload["sections"]
            for t in s["targets"]
        ]
    )
    session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    attempt = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    sent = app.submit_answer(
        rid(),
        attempt_id=attempt["id"],
        base=attempt["revision"],
        response=EXPLANATION,
        client_at=None,
    )  # 10:00
    clock.advance(minutes=1)
    seen = app.view_feedback(rid(), attempt_id=attempt["id"])["exposure"]  # 10:01
    app.close_view(rid(), exposure_id=seen["id"])
    clock.advance(minutes=1)
    app.run_operation(sent["operation"]["id"])  # graded at 10:02
    assert app.read(evidence.target_evidence, goal)["label"] == "independent"
    schedule = app.read(practice.schedule_view, goal)
    assert schedule["due_at"] == "2026-10-25T10:00:00.000Z"  # the answer's own time + 24 h
    assert schedule["next_offer"]["at"] == "2026-10-25T10:01:00.000Z"  # the feedback's end + 24 h


def test_a_frozen_plan_keeps_its_goals_anchors_and_windows_whatever_changes_later(make_app, clock):
    # X14 a changed goal keeps its old endpoint; X18 a later checkpoint is no frozen anchor;
    # X11 the half-open window: an offer exactly at a window's end belongs to the next one
    app = make_app(two_exercises(), judged(ALL_SHOWN), FACT_RIGHT)
    op, _session, _attempt, t1, t2 = answered(app)
    curriculum = curriculum_id(op)
    clock.advance(minutes=30)
    cohort = app.start_tracking(rid(), curriculum_id=curriculum)["cohort"]
    frozen = app.read(workflows.tracking_view, cohort["id"])
    edit_condition(app, t2)  # a new meaning for the connection goal
    app.confirm_closed(rid(), targets=[t1])  # a prospective checkpoint after the freeze
    clock.advance(days=7)  # exactly the end of window 1
    practise(app, curriculum, SORTED, fact=True)
    report = app.read(workflows.tracking_view, cohort["id"])
    assert [m["target"] for m in report["population"]] == [t1, t2]  # the frozen revisions
    assert [m["anchor"] for m in report["population"]] == [
        m["anchor"] for m in frozen["population"]
    ]
    first, second = report["windows"][:2]
    assert first["mature"]
    assert [(e["raw"], e["reason"]) for e in first["endpoints"]] == [
        ("M", "no ordinary check was offered in this window"),
    ] * 2
    assigned = [(e["target"], bool(e["assigned_attempt"])) for e in second["endpoints"]]
    assert assigned == [(t1, True), (t2, False)]  # the edited goal's checks are not its endpoint


def test_reorganising_the_outline_changes_no_evidence_due_date_or_count(make_app, clock):
    # C09 reorder (the shared-target half is not reachable), O09 curriculum evolution
    app = make_app(two_exercises(), judged(ALL_SHOWN))
    op, _session, _attempt, t1, t2 = answered(app)
    curriculum = curriculum_id(op)
    clock.advance(hours=2)

    def state():
        outline_now = app.read(workflows.outline_view, curriculum)
        checks = app.read(workflows.later_checks_view, curriculum)
        return {
            "schedules": [app.read(practice.schedule_history, t) for t in (t1, t2)],
            "labels": [app.read(evidence.target_evidence, t) for t in (t1, t2)],
            "counts": outline_now["counts"],
            "effort": outline_now["effort"],
            "checks": checks["counts"],
            "caught_up": checks["caught_up"],
        }

    before = state()
    view = app.read(workflows.outline_view, curriculum)["curriculum"]
    app.edit_outline(
        rid(),
        curriculum_id=curriculum,
        base=view["ref"]["revision"],
        title="Searching, reorganised",
        purpose=view["purpose"],
        sections=[
            {"id": "why", "title": "Why it is fast", "target_ids": [t2["id"]]},
            {"id": "needs", "title": "What it needs", "target_ids": [t1["id"]]},
        ],
    )
    after = app.read(workflows.outline_view, curriculum)
    assert [t["ref"] for t in after["targets"]] == [t2, t1]  # the order did change
    assert state() == before


def test_a_month_away_leaves_one_overdue_check_per_goal_not_thirty_misses(make_app, clock):
    # P20 return after thirty missed reminders; P01 time passing invents no failure
    app = make_app(two_exercises(), judged(ALL_SHOWN))
    op, _session, _attempt, t1, t2 = answered(app)
    curriculum = curriculum_id(op)
    clock.advance(days=30)
    for goal in (t1, t2):
        schedule = app.read(practice.schedule_view, goal)
        assert (schedule["need"], schedule["due_at"]) == (
            "independent_check",
            "2026-10-25T10:00:00.000Z",  # still the original due time
        )
        assert app.read(evidence.target_evidence, goal)["label"] == "independent"
    checks = app.read(workflows.later_checks_view, curriculum)
    assert [len(row["checks"]) for row in checks["targets"]] == [1, 1]
    assert (checks["counts"]["overdue"], checks["counts"]["with_errors"]) == (2, 0)
    due = app.read(workflows.home_view)["due"]
    assert (due["checks"], due["oldest"]) == (2, "2026-10-25T10:00:00.000Z")


def test_a_real_later_check_keeps_its_week_when_an_earlier_success_is_corrected(make_app, clock):
    # I01 completed descendant: an earlier anchor exists, so B re-anchors seven days on
    shown = judged(ALL_SHOWN)
    app = make_app(two_exercises(), shown, shown, shown, judged(CONNECTION_ERROR))
    _, op = drafted(app)
    curriculum = curriculum_id(op)
    _t1, t2 = targets(app, op)
    practise(app, curriculum, hint=True)  # day 0 10:00: helped; the check is due day 1
    clock.advance(hours=25)
    a = practise(app, curriculum)["sent"][
        "attempt"
    ]  # day 1 11:00: A meets it; next due day 8 11:00
    clock.advance(days=7, hours=1)
    practise(app, curriculum)  # day 8 12:00: B meets A's successor; next due day 15 12:00
    assert app.read(practice.schedule_view, t2)["due_at"] == "2026-11-08T12:00:00.000Z"
    clock.advance(days=1)
    app.accept_correction(rid(), operation_id=reviewed(app, a, "I guessed")["ref"]["id"])
    schedule = app.read(practice.schedule_view, t2)
    assert (schedule["due_at"], schedule["reason"]) == (
        "2026-11-08T12:00:00.000Z",  # B's own answer + 7 days: it still stands
        "reanchored from a real later check",
    )
    assert [e["disposition"] for e in schedule["check_effects"]] == ["reanchored"]


def test_a_later_check_with_the_answer_in_view_cannot_reanchor_after_a_correction(make_app, clock):
    # R01 the correction leaves B's exposure in force: no week; next offer B's retrieval + 24 h
    shown = judged(ALL_SHOWN)
    app = make_app(two_exercises(), shown, shown, shown, judged(CONNECTION_ERROR))
    _, op = drafted(app)
    curriculum = curriculum_id(op)
    _t1, t2 = targets(app, op)
    practise(app, curriculum, hint=True)  # day 0 10:00
    clock.advance(hours=25)
    a = practise(app, curriculum)["sent"]["attempt"]  # day 1 11:00: next due day 8 11:00
    clock.advance(days=7, minutes=30)
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    attempt = app.next_exercise(rid(), session_id=session["id"])["attempt"]  # owned at 11:30
    clock.advance(minutes=15)
    seen = app.read_material(rid(), targets=[t2], what="claims")["exposure"]
    app.close_view(rid(), exposure_id=seen["id"])  # the claims were open while B was written
    clock.advance(minutes=15)
    sent = app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response=ANSWER, client_at=None
    )
    app.run_operation(sent["operation"]["id"])  # B at 12:00: helped, so the check stays due
    clock.advance(days=1)
    app.accept_correction(rid(), operation_id=reviewed(app, a, "I guessed")["ref"]["id"])
    schedule = app.read(practice.schedule_view, t2)
    assert [e["disposition"] for e in schedule["check_effects"]] == ["no_advance"]
    assert schedule["need"] == "repair"  # A's corrected error, not a week from B
    assert schedule["next_offer"]["at"] == "2026-11-02T12:00:00.000Z"


def test_reanchoring_cannot_clear_a_later_error(make_app, clock):
    # R07 a later ordered error still leaves repair pending and withholds caught-up
    shown = judged(ALL_SHOWN)
    error = judged(CONNECTION_ERROR)
    app = make_app(two_exercises(), shown, shown, shown, error, error)
    _, op = drafted(app)
    curriculum = curriculum_id(op)
    _t1, t2 = targets(app, op)
    practise(app, curriculum, hint=True)  # day 0
    clock.advance(hours=25)
    a = practise(app, curriculum)["sent"]["attempt"]  # day 1: A
    clock.advance(days=7, hours=1)
    practise(app, curriculum)  # day 8: B, on time
    clock.advance(minutes=10)
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    chosen = app.read(workflows.choices_view, session["id"])["exercises"][0]["exercise"]
    c = app.next_exercise(rid(), session_id=session["id"], exercise_id=chosen["id"])["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=c["id"], base=c["revision"], response=ANSWER, client_at=None
    )
    app.run_operation(sent["operation"]["id"])  # C: an extra answer with the connection wrong
    clock.advance(days=1)
    app.accept_correction(rid(), operation_id=reviewed(app, a, "I guessed")["ref"]["id"])
    schedule = app.read(practice.schedule_view, t2)
    assert schedule["need"] == "repair"
    assert app.read(evidence.target_evidence, t2)["label"] == "error"
    caught = app.read(workflows.later_checks_view, curriculum)["caught_up"]
    assert caught["state"] == "unresolved"


def with_hint_time(archive, **time):
    """Return the archive with its hinted answer's display time replaced (resealed)."""
    changed = copy.deepcopy(archive)
    for record in changed["records"]:
        for help_ in record["payload"].get("assistance", []) if record["kind"] == "attempt" else []:
            help_["shown_at"] = time.pop("shown_at", help_["shown_at"])
            help_["time_evidence"][0].update(time)
    body = {k: v for k, v in changed.items() if k != "integrity"}
    changed["integrity"] = {"algorithm": "sha256-jcs", "digest": digest(body)}
    return json.dumps(changed)


UNKNOWN: dict[str, str | None] = {
    "precision": "unknown",
    "earliest_at": None,
    "latest_at": None,
    "basis": "unavailable",
    "explanation": "acknowledged before submission; no reliable display time",
}


def test_a_known_hint_without_a_clock_is_kept_and_an_invented_time_refused(
    make_app, tmp_path, clock
):
    # W01 known hint, unknown time; B01 an invalid or invented hint time fails validation
    app = make_app(outline(), judged(ALL_SHOWN))
    _, op = drafted(app)
    _, submitted = answer(app, op, hint=True)
    app.run_operation(submitted["operation"]["id"])
    archive = app.export()

    kept = App.restore(tmp_path / "kept.sqlite", with_hint_time(archive, **UNKNOWN), clock=clock)
    try:
        _t1, t2 = targets(app, op)
        assert kept.read(lambda tx: evidence.target_evidence(tx, t2)["label"]) == "helped"
    finally:
        kept.close()
    invented: list[dict[str, str | None]] = [
        {**UNKNOWN, "shown_at": "2026-10-24T10:00:00.000Z"},  # an instant with no clock
        {**UNKNOWN, "earliest_at": "2026-10-24T09:00:00.000Z"},  # bounds with no basis
        {"precision": "bounded", "shown_at": "2026-10-24T10:00:00.000Z"},  # midpoint as fact
    ]
    for n, time in enumerate(invented):
        with pytest.raises(ValueError, match="archive refused"):
            App.restore(tmp_path / f"bad{n}.sqlite", with_hint_time(archive, **time), clock=clock)


def test_a_refreshed_or_second_tab_question_uses_one_diagnostic_slot(make_app):
    # P24 shown, not answered, refreshed; P33 two tabs compete for the allowance
    asked = question(["c3"], demonstrated=("teach", "h2"), error=("teach", "h1"))
    app = make_app(outline(), judged(CONNECTION_ERROR, hypotheses=TWO_CAUSES, question=asked))
    op, session, _attempt, _t1, _t2 = answered(app)
    shown = app.next_exercise(rid(), session_id=session["id"])
    assert shown["kind"] == "clarification"
    app.save_draft(
        rid(), attempt_id=shown["attempt"]["id"], base=shown["attempt"]["revision"], response="32"
    )
    refreshed = app.next_exercise(rid(), session_id=session["id"])
    other_tab = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    competing = app.next_exercise(rid(), session_id=other_tab["id"])
    assert [s["attempt"]["id"] for s in (refreshed, competing)] == [shown["attempt"]["id"]] * 2
    assert all(s["resumed"] for s in (refreshed, competing))
    questions = [a for a in app.read(evidence.attempts) if a["purpose"] == "clarification"]
    assert [(a["response"], a["status"]) for a in questions] == [("32", "draft")]
    (concern,) = app.read(practice.open_concerns)
    allowance = practice.diagnostic_allowance
    assert app.read(allowance, other_tab["id"], concern["ref"]["id"]) == 2  # one of three used


def test_a_paused_repair_comes_back_from_restore_exactly_and_stays_paused(tmp_path, clock):
    # P34 export/restore during paused repair; P27 two unsuccessful cycles stop repair
    wrong = judged(CONNECTION_ERROR)
    second = variant(prompt="A sorted list has 256 entries. What must hold, and why 8 comparisons?")
    data = tmp_path / "data"
    b = Browser(
        data,
        ScriptedProvider(
            outline(),
            judged(CONNECTION_ERROR, hypotheses=[TWO_CAUSES[1]]),
            teaching(),
            variant(),
            wrong,
            teaching(approach="contrast with a near miss"),
            second,
            wrong,
        ),
        clock,
    )
    curriculum, session, _attempt = learn(b)
    sid = session["id"]
    for _ in range(2):
        taught = next_step(b, sid)
        study = b.get(f"/studies/{taught['study']['id']}")
        b.post(f"/studies/{study['ref']['id']}/complete", base=study["ref"]["revision"])
        next_step(b, sid)
        answer_current(b, sid, ANSWER)
    concern = b.post(f"/sessions/{sid}/next")["concern"]["ref"]
    b.post(f"/concerns/{concern['id']}/pause", base=concern["revision"])
    clock.advance(hours=1)
    pages = [
        f"/sessions/{sid}/summary",
        f"/curricula/{curriculum}",
        f"/curricula/{curriculum}/checks",
    ]
    saved = [b.get(page) for page in pages]
    (paused,) = saved[0]["concerns"]
    assert (paused["status"], [c["outcome"] for c in paused["cycles"]]) == (
        "paused",
        ["unsuccessful", "unsuccessful"],
    )

    restored = Browser(tmp_path / "elsewhere", FailIfCalled(), clock)
    restored.post("/restore", archive=b.client.get("/api/export").text)
    assert [restored.get(page) for page in pages] == saved
    later = restored.post(f"/curricula/{curriculum}/sessions")["session"]
    assert restored.post(f"/sessions/{later['id']}/next")["kind"] == "none"  # no third cycle


def test_a_fresh_check_that_shows_a_different_gap_opens_an_ordinary_concern(make_app, clock):
    # P40 each integrated verification reveals a different supported gap
    other_gap = judged({"c1": "error", "c2": "demonstrated", "c3": "demonstrated"})
    app = make_app(
        outline(),
        judged(CONNECTION_ERROR, hypotheses=[TWO_CAUSES[1]]),
        teaching(),
        variant(),
        other_gap,
    )
    _op, session, _attempt, t1, t2 = answered(app)
    taught = app.next_exercise(rid(), session_id=session["id"])
    app.run_operation(taught["operation"]["id"])
    study = app.next_exercise(rid(), session_id=session["id"])["study"]
    app.complete_study(rid(), study_id=study["id"], base=study["revision"], client_at=None)
    prepared = app.next_exercise(rid(), session_id=session["id"])
    app.run_operation(prepared["operation"]["id"])
    check = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    clock.advance(minutes=3)
    sent = app.submit_answer(
        rid(), attempt_id=check["id"], base=check["revision"], response=ANSWER, client_at=None
    )
    app.run_operation(sent["operation"]["id"])
    first, second = app.read(lambda tx: [r.view for r in tx.current("concern", by="practice")])
    assert (first["status"], first["cycles"][0]["outcome"]) == ("resolved", "recovered")
    assert [s["target"] for s in second["scope"]] == [t1]  # the new gap, its own concern
    assert (second["kind"], second["status"], second["question"]) == ("error", "open", None)
    assert first["scope"][0]["target"] == t2


def test_an_answer_view_open_elsewhere_while_answering_counts_as_help_everywhere(make_app, clock):
    # W04 help in another screen; M04/V03 Practice and Measurement read one qualification
    shown = explained({"c1": "demonstrated", "c2": "demonstrated"})
    app = make_app(explanation_outline(), shown, shown)
    _, op = drafted(app)
    curriculum = curriculum_id(op)
    (goal,) = targets(app, op)
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    first = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=first["id"], base=first["revision"], response=EXPLANATION, client_at=None
    )
    app.run_operation(sent["operation"]["id"])  # day 0 10:00, independent
    clock.advance(minutes=30)
    cohort = app.start_tracking(rid(), curriculum_id=curriculum)["cohort"]
    clock.advance(hours=24, minutes=30)  # day 1 11:00
    later = app.start_session(rid(), curriculum_id=curriculum)["session"]
    check = app.next_exercise(rid(), session_id=later["id"])["attempt"]
    clock.advance(minutes=1)
    panel = app.read_material(rid(), targets=[goal], what="claims")["exposure"]  # another tab
    clock.advance(minutes=4)
    sent = app.submit_answer(
        rid(), attempt_id=check["id"], base=check["revision"], response=EXPLANATION, client_at=None
    )
    app.run_operation(sent["operation"]["id"])
    # still open: availability unknown, so the raw judgment stands and nothing advances
    assert app.read(evidence.answer_label, check["id"], goal) == "independent"
    assert app.read(practice.schedule_view, goal)["due_at"] == "2026-10-25T10:00:00.000Z"
    clock.advance(minutes=5)
    app.close_view(rid(), exposure_id=panel["id"])  # known open during the answer: help
    assert app.read(evidence.answer_label, check["id"], goal) == "helped"
    assert app.read(evidence.target_evidence, goal)["label"] == "helped"
    schedule = app.read(practice.schedule_view, goal)
    assert (schedule["need"], schedule["due_at"]) == (
        "independent_check",
        "2026-10-26T11:05:00.000Z",  # helped practice: an independent check a day later
    )
    clock.advance(days=6)  # window 1 closes
    (endpoint,) = app.read(workflows.tracking_view, cohort["id"])["windows"][0]["endpoints"]
    performance = endpoint["claims"]["performance"]
    assert (endpoint["raw"], performance["bucket"]) == ("H", "QH")
    aid = next(r for r in performance["reasons"] if r["code"] == "aid_availability")
    assert (aid["result"], aid["basis"]) == ("ineligible", [{**panel, "revision": 2}])


def three_goals():
    """Return the outline with a third goal and one larger task with one criterion each."""
    drafted_outline = with_modes(outline(), "explain", "explain")
    drafted_outline["targets"].append(
        {
            "key": "t3",
            "knowledge_keys": ["k2"],
            "action": "Say how many comparisons a sorted array of 1024 needs",
            "mode": "explain",
            "conditions": ["from memory"],
            "requirements": [{"key": "r1", "statement": "About 10", "knowledge_keys": ["k2"]}],
        }
    )
    drafted_outline["sections"][0]["target_keys"].append("t3")
    criteria = drafted_outline["exercises"][0]["criteria"]
    criteria[1]["covers"] = [{"target_key": "t2", "requirement_keys": ["r1", "r2"]}]
    criteria[2]["covers"] = [{"target_key": "t3", "requirement_keys": ["r1"]}]
    return drafted_outline


def test_one_larger_answer_settles_each_goal_on_its_own_evidence(make_app):
    # CCA02 mixed larger answer: A demonstrated, B omitted, C a supported error
    graded = judged({"c1": "demonstrated", "c2": "not_shown", "c3": "error"})
    app = make_app(three_goals(), graded)
    _, op = drafted(app)
    _session, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    a, b, c = targets(app, op)
    found = [
        (
            app.read(evidence.target_evidence, t)["label"],
            (s := app.read(practice.schedule_view, t))["need"],
            s["due_at"],
        )
        for t in (a, b, c)
    ]
    assert found == [
        ("independent", "independent_check", "2026-10-25T10:00:00.000Z"),
        ("unresolved", "initial", None),  # omitted: no failure, no date
        ("error", "repair", None),
    ]
    (concern,) = app.read(practice.open_concerns)
    assert [s["target"] for s in concern["scope"]] == [c]


def test_selecting_two_hundred_goals_and_starting_three_invents_no_backlog(make_app):
    # CCA03 import 200, begin 3: 197 stay unstarted, not 197 missed reviews
    drafted_outline = outline()
    first = drafted_outline["targets"][0]
    drafted_outline["targets"] = [{**first, "key": f"t{n}"} for n in range(1, 201)]
    drafted_outline["sections"] = [
        {"title": "Many goals", "target_keys": [f"t{n}" for n in range(1, 201)]}
    ]
    exercise = drafted_outline["exercises"][0]
    exercise["criteria"] = [
        {
            **exercise["criteria"][0],
            "key": f"c{n}",
            "covers": [{"target_key": f"t{n}", "requirement_keys": ["r1"]}],
        }
        for n in (1, 2, 3)
    ]
    exercise["hints"] = []
    app = make_app(drafted_outline)
    _, op = drafted(app)
    curriculum = curriculum_id(op)
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    app.next_exercise(rid(), session_id=session["id"])  # begin: the task covering three goals
    counts = app.read(workflows.outline_view, curriculum)["counts"]
    assert (counts["selected"], counts["active"], counts["unstarted"]) == (200, 3, 197)
    assert (counts["independent"], counts["errors"], counts["untested"]) == (0, 0, 200)
    checks = app.read(workflows.later_checks_view, curriculum)
    assert (checks["counts"]["overdue"], checks["counts"]["upcoming"]) == (0, 0)
    assert app.read(workflows.home_view)["due"]["checks"] == 0


def test_an_eligible_later_success_closes_a_repair_that_was_shown_only_with_help(make_app, clock):
    # P06 an eligible later due success closes the recovery concern, with no extra test;
    # P39 a helped fresh check never loops back into teaching
    helped_check = variant()
    helped_check["hints"] = [{"text": "Count the halvings of 128.", "criterion_keys": ["c3"]}]
    script = [teaching(), helped_check, judged(ALL_SHOWN), judged(ALL_SHOWN)]
    script.append(judged(CONNECTION_ERROR))  # the later answer's corrected judgment
    app = make_app(*ask_about_the_connection(script, focused("demonstrated")))
    _, op = drafted(app)
    session = clarify(app, op)
    study_and_check(app, session, hint=True)  # recovered only with help: wait for a later check
    (concern,) = app.read(practice.open_concerns)
    assert concern["route"] == "later_check"
    clock.advance(hours=25)
    later = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    step = app.next_exercise(rid(), session_id=later["id"])
    assert step["kind"] == "exercise"  # the ordinary due check, not a repair task
    sent = app.submit_answer(
        rid(),
        attempt_id=step["attempt"]["id"],
        base=step["attempt"]["revision"],
        response=ANSWER,
        client_at=None,
    )
    app.run_operation(sent["operation"]["id"])
    assert app.read(practice.open_concerns) == []
    concerns = app.read(lambda tx: [r.view for r in tx.current("concern", by="practice")])
    assert [(c["status"], len(c["cycles"])) for c in concerns] == [("resolved", 1)]
    _fact, connection = targets(app, op)
    caught = app.read(workflows.later_checks_view, curriculum_id(op))["caught_up"]
    assert connection not in [p["target"] for p in caught["pending"]]  # the fact awaits a rating
    assert app.read(practice.schedule_view, connection)["due_at"] == "2026-11-01T11:00:00.000Z"

    # that later answer's judgment is corrected to an error: the same concern repairs again
    clock.advance(hours=1)
    review = reviewed(app, sent["attempt"], "I mixed up the halvings")
    app.accept_correction(rid(), operation_id=review["ref"]["id"])
    (reopened,) = app.read(practice.open_concerns)
    assert (reopened["ref"]["id"], reopened["route"]) == (concern["ref"]["id"], "repair")
    assert app.read(practice.schedule_view, connection)["need"] == "repair"


def test_a_success_and_an_error_at_the_same_instant_cannot_certify_recovery(make_app, clock):
    # X04 exact simultaneous success and error: deterministic order, the concern stays
    fact_wrong = assessment({"c1": "error"}, {"c1": ["It can be in any order."]})
    app = make_app(two_exercises(), judged(ALL_SHOWN), fact_wrong, judged(ALL_SHOWN))
    op, _session, _attempt, t1, _t2 = answered(app)
    clock.advance(hours=25)
    session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    owned = app.next_exercise(rid(), session_id=session["id"])  # the due larger task
    extra = app.next_exercise(rid(), session_id=session["id"], exercise_id=fact_exercise(app))
    for step, text in ((extra, "It can be in any order."), (owned, ANSWER)):  # one instant
        sent = app.submit_answer(
            rid(),
            attempt_id=step["attempt"]["id"],
            base=step["attempt"]["revision"],
            response=text,
            client_at=None,
        )
        app.run_operation(sent["operation"]["id"])
    (concern,) = app.read(practice.open_concerns)
    assert [s["target"] for s in concern["scope"]] == [t1]  # the error is kept, not outvoted
    caught = app.read(workflows.later_checks_view, curriculum_id(op))["caught_up"]
    assert caught["state"] == "unresolved"


# --- the live qualification harness, proved with its scripted stand-in --------------------


def test_the_harness_reports_every_finding_and_never_a_percentage(tmp_path):
    # plan "Acceptance pack and verification": report each substantive error, disagreement,
    # abstention and prompt version; never a quality percentage (proved with the stand-in)
    out = tmp_path / "reports"
    assert qualify.main(["--scripted", "--out", str(out), "--data", str(tmp_path / "lib")]) == 0
    (path,) = out.glob("pack-v1-*-scripted.md")
    text = path.read_text()
    assert "%" not in text
    assert "SCRIPTED RUN" in text
    pack = json.loads(qualify.PACK.read_text())
    for material in pack["materials"]:
        assert f"### {material['id']}: {material['title']}" in text
    for held in pack["held_out"]:
        for response in held["responses"]:
            assert f"### {response['id']} ({held['id']})" in text
    findings = text.split("## Authoring", 1)[0]
    assert "- H2-b c4: reference not_shown, model error (scripted)" in findings
    assert "- H3-c c1: reference not_shown, model cannot_judge (scripted)" in findings
    assert "- H3-c: a question was expected; the model proposed none" in findings
    assert "**Substantive errors the checks found (0):**" in findings
    assert "assess-answer` v3" in text  # the prompt versions are named


def test_held_out_text_in_any_drafting_request_is_caught(tmp_path):
    # held-out assessment variants stay out of the authoring prompts (P14's harness half)
    pack = json.loads(qualify.PACK.read_text())
    pack["materials"][1]["text"] += " " + pack["held_out"][0]["responses"][0]["text"]
    results = qualify.run(pack, qualify.scripted(pack), tmp_path / "lib")
    assert results["held_out_in_drafting"] == ["H1 response H1-a"]
    assert results["learner_credit_after_authoring"] == {
        "attempt": 0,
        "assessment": 0,
        "schedule": 0,
    }


def test_the_live_run_refuses_to_start_without_a_key(monkeypatch, tmp_path):
    # the live run needs ANTHROPIC_API_KEY; without it nothing runs and nothing is written
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert qualify.main(["--out", str(tmp_path / "reports")]) == 2
    assert not (tmp_path / "reports").exists()


# --- progress views: defects found in the browser qualification ----------------------------


def test_a_session_summary_says_when_later_checks_were_met(make_app, clock):
    # O05 maintenance is visible; O01 the headline never hides a real later check
    shown = explained({"c1": "demonstrated", "c2": "demonstrated"})
    app = make_app(explanation_outline(), shown, shown)
    _, op = drafted(app)
    curriculum = curriculum_id(op)
    first = practise(app, curriculum, EXPLANATION)["session"]
    clock.advance(hours=25)
    later = practise(app, curriculum, EXPLANATION)["session"]  # the on-time later check, met
    headline = [app.read(workflows.summary_view, s["id"])["headline"] for s in (first, later)]
    assert headline == [
        "Practiced today; later recall not checked yet.",
        "Later checks in this session: 1 answered, 1 met on time.",
    ]


def test_a_session_summary_counts_a_later_check_answered_with_a_mistake(make_app, clock):
    # O01/O04 a due check that failed was still a later check, not "not checked yet"
    shown = explained({"c1": "demonstrated", "c2": "demonstrated"})
    wrong = explained({"c1": "demonstrated", "c2": "error"})
    app = make_app(explanation_outline(), shown, wrong)
    _, op = drafted(app)
    practise(app, curriculum_id(op), EXPLANATION)
    clock.advance(hours=25)
    failed = practise(app, curriculum_id(op), EXPLANATION)["session"]
    assert app.read(workflows.summary_view, failed["id"])["headline"] == (
        "Later checks in this session: 1 answered, 0 met on time."
    )


def test_a_due_check_after_a_helped_first_answer_is_listed_when_it_fails(make_app, clock):
    # O04/O16 a failed or replaced due check stays in the later-checks history and counts
    shown = explained({"c1": "demonstrated", "c2": "demonstrated"})
    wrong = explained({"c1": "demonstrated", "c2": "error"})
    app = make_app(explanation_outline(), shown, wrong, teaching())
    _, op = drafted(app)
    curriculum = curriculum_id(op)
    practise(app, curriculum, EXPLANATION, hint=True)  # helped: a check is due a day later
    clock.advance(hours=25)
    failed = practise(app, curriculum, EXPLANATION)[
        "session"
    ]  # the due check has a supported error
    taught = app.next_exercise(rid(), session_id=failed["id"])
    app.run_operation(taught["operation"]["id"])
    study = app.next_exercise(rid(), session_id=failed["id"])["study"]
    app.complete_study(rid(), study_id=study["id"], base=study["revision"], client_at=None)
    view = app.read(workflows.later_checks_view, curriculum)
    (row,) = view["targets"]
    assert [(c["due_at"], c["status"]) for c in row["checks"]] == [
        ("2026-10-25T10:00:00.000Z", "replaced"),
        ("2026-10-26T11:00:00.000Z", "open"),
    ]
    # the helped first answer set this due time; it is not an answer to the check
    assert [(a["role"], a["label"]) for a in row["checks"][0]["answers"]] == [("owner", "error")]
    counts = view["counts"]
    assert (counts["replaced_after_teaching"], counts["with_errors"]) == (1, 1)


def test_cost_follows_the_enrollment_identity_across_its_revisions(make_app, clock):
    # W05 same goals, new enrollment revision: 10 m against E@1 and 20 m against E@2 = 30 m
    app = make_app(two_exercises(), judged(ALL_SHOWN))
    op, session, _attempt, _t1, t2 = answered(app)
    curriculum = curriculum_id(op)
    first = app.read(practice.enrollment_for, curriculum)["ref"]
    cohort = app.start_tracking(rid(), curriculum_id=curriculum)["cohort"]
    edit_condition(app, t2)  # a goal edit appends an enrollment revision
    second = app.read(practice.enrollment_for, curriculum)["ref"]
    assert (second["id"], second["revision"]) == (first["id"], first["revision"] + 1)
    run = app.open_timer(rid(), document_run_id="tab-1", takeover=False)["run"]

    def span(start, minutes, enrollment):
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
            "enrollment": enrollment,
        }

    app.record_spans(rid(), spans=[span(5, 10, first), span(20, 20, second)])
    clock.advance(hours=1)
    cost = app.read(workflows.tracking_view, cohort["id"])["cost"]
    assert cost["period"]["total_ms"] == 30 * 60_000


def test_two_hints_in_one_answer_stay_two_scoped_entries(make_app):
    # B03 several hints in one attempt: separate entries, each with its own criteria
    drafted_outline = outline()
    drafted_outline["exercises"][0]["hints"].append(
        {"text": "How many times can n be halved?", "criterion_keys": ["c3"]}
    )
    app = make_app(drafted_outline, judged(ALL_SHOWN))
    _, op = drafted(app)
    session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    attempt = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    for hint in ("h1", "h2"):
        app.reveal_hint(rid(), attempt_id=attempt["id"], hint_id=hint)
        attempt = app.acknowledge_hint(
            rid(), attempt_id=attempt["id"], base=attempt["revision"], hint_id=hint, client_at=None
        )["attempt"]
    saved = app.read(lambda tx: evidence.attempt_view(tx, attempt))
    assert [a["criterion_ids"] for a in saved["assistance"]] == [["c2"], ["c3"]]
    shown = app.read(evidence.exposures_for, attempt["id"])
    assert sorted(e["details"]["hint_id"] for e in shown) == ["h1", "h2"]


def test_correcting_an_earlier_answer_never_reopens_a_repair_a_later_check_closed(make_app, clock):
    # P06 / decision 8: only a correction of the answer that closed it can reopen it
    helped_check = variant()
    helped_check["hints"] = [{"text": "Count the halvings of 128.", "criterion_keys": ["c3"]}]
    unclear = judged({"c1": "demonstrated", "c2": "demonstrated", "c3": "not_shown"})
    script = [teaching(), helped_check, judged(ALL_SHOWN), judged(ALL_SHOWN), unclear]
    app = make_app(*ask_about_the_connection(script, focused("demonstrated")))
    _, op = drafted(app)
    session = clarify(app, op)
    study_and_check(app, session, hint=True)
    clock.advance(hours=25)
    practise(app, curriculum_id(op))  # the later success closes the concern
    original = app.read(evidence.attempts)[0]  # the answer that opened it
    clock.advance(hours=1)
    review = reviewed(app, original["ref"], "I did not really make a mistake")
    app.accept_correction(rid(), operation_id=review["ref"]["id"])  # now not shown, not wrong
    concerns = app.read(lambda tx: [r.view for r in tx.current("concern", by="practice")])
    assert [c["status"] for c in concerns] == ["resolved"]  # the later success still stands


def test_a_recall_review_closes_a_repair_waiting_for_its_later_check(make_app, clock):
    # P06 for a recall goal: its later check is met by the learner's own rating
    helped_check = variant()
    helped_check["hints"] = [{"text": "Think about order.", "criterion_keys": ["c1"]}]
    fact_error = judged({"c1": "error", "c2": "demonstrated", "c3": "demonstrated"})
    app = make_app(
        outline(), fact_error, teaching(), helped_check, judged(ALL_SHOWN), judged(ALL_SHOWN)
    )
    _, op = drafted(app)
    fact, _connection = targets(app, op)
    first = practise(app, curriculum_id(op))
    app.rate_recall(rid(), attempt_id=first["sent"]["attempt"]["id"], target=fact, choice="forgot")
    study_and_check(app, first["session"], hint=True)  # shown only with help: wait
    (concern,) = app.read(practice.open_concerns)
    assert concern["route"] == "later_check"
    clock.advance(days=2)
    later = practise(app, curriculum_id(op))["sent"]["attempt"]
    assert len(app.read(practice.open_concerns)) == 1  # graded, not yet rated: still waiting
    app.rate_recall(rid(), attempt_id=later["id"], target=fact, choice="remembered")
    assert app.read(practice.open_concerns) == []


def test_an_answer_after_seeing_the_claims_keeps_its_success_but_not_a_week(make_app, clock):
    # P15 reveal the answer, then answer without in-task help: success and exposure kept,
    # no delayed qualification and no seven-day advance
    shown = explained({"c1": "demonstrated", "c2": "demonstrated"})
    app = make_app(explanation_outline(), shown, shown)
    _, op = drafted(app)
    curriculum = curriculum_id(op)
    (goal,) = targets(app, op)
    practise(app, curriculum, EXPLANATION)  # day 0 10:00: due day 1 10:00
    clock.advance(hours=25)
    seen = app.read_material(rid(), targets=[goal], what="claims")["exposure"]
    clock.advance(minutes=1)
    app.close_view(rid(), exposure_id=seen["id"])  # read the claims, then closed them
    clock.advance(minutes=4)
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    assert app.next_exercise(rid(), session_id=session["id"])["kind"] == "none"  # deferred
    chosen = app.read(workflows.outline_view, curriculum)["exercises"][0]["id"]
    practise(app, curriculum, EXPLANATION, session=session, exercise_id=chosen)
    assert app.read(evidence.target_evidence, goal)["label"] == "independent"  # success kept
    schedule = app.read(practice.schedule_view, goal)
    assert (schedule["due_at"], schedule["obligation"]["status"]) == (
        "2026-10-25T10:00:00.000Z",  # no week was earned
        "open",
    )
    assert schedule["next_offer"]["at"] == "2026-10-26T11:05:00.000Z"  # this answer + 24 h
