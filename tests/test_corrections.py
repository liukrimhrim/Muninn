"""Slice 3 at the application seam: content changes, reuse and judgment corrections."""

import pytest

from muninn import evidence, practice, workflows
from muninn.library import Conflict
from tests.conftest import rid
from tests.drafts import (
    ALL_SHOWN,
    ANSWER,
    CONNECTION_ERROR,
    NOTES_SOURCE,
    TWO_CAUSES,
    VOCAB_SOURCE,
    assessment,
    judged,
    notes_outline,
    outline,
    teaching,
    variant,
    vocab_outline,
)
from tests.test_workflows import answer, curriculum_id, drafted, targets

UNSORTED = "for a list that may arrive unsorted"


def answered(app):
    """Draft the outline and answer its exercise once; return (op, session, attempt, t1, t2)."""
    _, op = drafted(app)
    session, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    t1, t2 = targets(app, op)
    return op, session, submitted["attempt"], t1, t2


def edit_condition(app, target, condition=UNSORTED):
    definition = app.read(lambda tx: tx.at(target, by="content").payload)
    return app.revise_target(
        rid(),
        target_id=target["id"],
        base=target["revision"],
        action=definition["action"],
        mode=definition["mode"],
        conditions=[*definition["conditions"], condition],
        requirements=[
            {"id": r["id"], "statement": r["statement"]}
            for r in definition["evidence_requirements"]
        ],
        reason="the goal should cover unsorted input",
    )


def test_a_changed_condition_holds_the_exercise_written_for_the_old_goal(make_app):
    app = make_app(outline(), judged(ALL_SHOWN))
    op, _session, _attempt, t1, t2 = answered(app)
    due = app.read(practice.schedule_view, t2)["due_at"]

    revised = edit_condition(app, t2)
    new_t2 = revised["target"]
    assert new_t2 == {**t2, "revision": 2}

    view = app.read(workflows.outline_view, curriculum_id(op))
    assert [t["ref"] for t in view["targets"]] == [t1, new_t2]
    (exercise,) = view["exercises"]
    assert exercise["hold"] == (
        "written for an earlier version of: Explain why binary search needs only about "
        "log2(n) comparisons"
    )
    assert set(view["without_exercise"]) == {t1["id"], t2["id"]}

    # the old goal keeps its evidence and due check; the new one starts untested and unstarted
    assert app.read(evidence.target_evidence, t2)["label"] == "independent"
    assert app.read(practice.schedule_view, t2)["due_at"] == due
    assert app.read(evidence.target_evidence, new_t2)["label"] == "untested"
    assert app.read(practice.schedule_view, new_t2) is None
    states = {
        t["ref"]["revision"]: t["state"] for t in view["targets"] if t["ref"]["id"] == t2["id"]
    }
    assert states == {2: "unstarted"}

    # the change is explained: a changed mapping and one transition, nothing re-stamped
    mapping = app.read(lambda tx: tx.at(revised["mapping"], by="content").payload)
    assert (mapping["from"], mapping["to"], mapping["relation"], mapping["disposition"]) == (
        [t2],
        [new_t2],
        "changed",
        "accepted",
    )
    assert mapping["criterion_map"] == []
    transition = app.read(lambda tx: tx.at(revised["transition"], by="workflows").payload)
    assert transition["category"] == "curriculum"
    assert t2 in transition["before"]
    assert new_t2 in transition["after"]


def test_a_reviewed_exercise_is_rebound_to_the_edited_goal_and_old_answers_stay_put(make_app):
    app = make_app(outline(), judged(ALL_SHOWN))
    op, _session, attempt, t1, t2 = answered(app)
    new_t2 = edit_condition(app, t2)["target"]
    (held,) = app.read(workflows.outline_view, curriculum_id(op))["exercises"]

    rebound = app.rebind_exercise(
        rid(), exercise_id=held["ref"]["id"], base=held["ref"]["revision"]
    )
    exercise = app.read(lambda tx: tx.at(rebound["exercise"], by="content").payload)
    assert exercise["targets"] == [t1, new_t2]
    assert exercise["design_review"]["rebound_from"] == held["ref"]
    assert exercise["design_review"]["actor"] == "learner-review"
    view = app.read(workflows.outline_view, curriculum_id(op))
    assert [e["hold"] for e in view["exercises"]] == [None]
    assert view["without_exercise"] == []

    # the earlier answer stays bound to the exercise revision it answered
    old = app.read(lambda tx: evidence.attempt_view(tx, attempt))
    assert old["exercise"] == held["ref"]
    # the edited goal is practised again under its new contract; the unchanged one keeps its state
    session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    delivered = app.next_exercise(rid(), session_id=session["id"])
    assert delivered["kind"] == "exercise"
    assert app.read(practice.schedule_view, new_t2)["need"] == "initial"
    assert app.read(practice.schedule_view, t1)["need"] == "independent_check"


def add(app, title, text):
    added = app.add_material(rid(), title=title, text=text, purpose=None)
    return app.run_operation(added["operation"]["id"])


def claims(app, op):
    view = app.read(workflows.outline_view, curriculum_id(op))
    return {k["statement"]: k for t in view["targets"] for k in t["knowledge"]}


def test_flagged_material_holds_what_rests_on_it_and_unrelated_material_stays_usable(make_app):
    app = make_app(outline(), vocab_outline())
    _, op = drafted(app)
    vocab = add(app, "Tarvi", VOCAB_SOURCE)
    sorted_claim = claims(app, op)["Binary search only works on a sorted array."]

    flagged = app.flag_material(
        rid(),
        knowledge_id=sorted_claim["ref"]["id"],
        base=sorted_claim["ref"]["revision"],
        reason="Binary search also needs random access",
    )
    assert flagged["knowledge"]["revision"] == sorted_claim["ref"]["revision"] + 1
    view = app.read(workflows.outline_view, curriculum_id(op))
    held = "rests on material flagged as wrong: Binary search only works on a sorted array."
    assert [t["hold"] for t in view["targets"]] == [held, held]  # t2 builds on it
    assert [e["hold"] for e in view["exercises"]] == [held]
    claim = claims(app, op)["Binary search only works on a sorted array."]
    assert (claim["status"], claim["dispute"]["reason"]) == (
        "disputed",
        "Binary search also needs random access",
    )

    # nothing to practise there now; the unrelated curriculum still works
    blocked = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    assert app.next_exercise(rid(), session_id=blocked["id"])["kind"] == "none"
    other = app.start_session(rid(), curriculum_id=curriculum_id(vocab))["session"]
    assert app.next_exercise(rid(), session_id=other["id"])["kind"] == "exercise"

    # keeping the wording clears the flag without changing any goal
    app.revise_material(
        rid(),
        knowledge_id=claim["ref"]["id"],
        base=claim["ref"]["revision"],
        statement=claim["statement"],
        scope=claim["scope"],
        reason="checked: the source is right for arrays",
    )
    view = app.read(workflows.outline_view, curriculum_id(op))
    assert [t["hold"] for t in view["targets"]] == [None, None]
    assert [t["ref"]["revision"] for t in view["targets"]] == [1, 1]
    assert app.next_exercise(rid(), session_id=blocked["id"])["kind"] == "exercise"


def test_correcting_a_claim_versions_the_claims_and_goals_that_build_on_it(make_app):
    app = make_app(outline(), judged(ALL_SHOWN))
    op, _session, _attempt, t1, t2 = answered(app)
    claim = claims(app, op)["Binary search only works on a sorted array."]
    flagged = app.flag_material(
        rid(), knowledge_id=claim["ref"]["id"], base=claim["ref"]["revision"], reason="incomplete"
    )["knowledge"]
    corrected = app.revise_material(
        rid(),
        knowledge_id=flagged["id"],
        base=flagged["revision"],
        statement="Binary search needs a sorted array with random access.",
        scope=claim["scope"],
        reason="a linked list cannot be halved in one step",
    )
    view = app.read(workflows.outline_view, curriculum_id(op))
    assert [t["ref"] for t in view["targets"]] == [{**t1, "revision": 2}, {**t2, "revision": 2}]
    assert [t["hold"] for t in view["targets"]] == [None, None]
    assert view["exercises"][0]["hold"].startswith("written for an earlier version of")
    statements = {k["statement"] for t in view["targets"] for k in t["knowledge"]}
    assert "Binary search needs a sorted array with random access." in statements
    # the relation built on the claim got a new revision citing the corrected one
    relation = next(k for k in view["targets"][1]["knowledge"] if k["form"] == "relation")
    payload = app.read(lambda tx: tx.at(relation["ref"], by="content").payload)
    assert payload["dependencies"][0]["ref"] == corrected["knowledge"]
    # old goals keep their evidence under their old definitions
    assert app.read(evidence.target_evidence, t1)["label"] == "independent"
    transition = app.read(lambda tx: tx.at(corrected["transition"], by="workflows").payload)
    assert t1 in transition["before"]
    assert t2 in transition["before"]


def test_a_concern_on_flagged_material_waits_instead_of_teaching_it(make_app):
    app = make_app(outline(), judged(CONNECTION_ERROR, hypotheses=[TWO_CAUSES[1]]))
    op, session, _attempt, _t1, _t2 = answered(app)
    claim = claims(app, op)["Binary search only works on a sorted array."]
    app.flag_material(
        rid(), knowledge_id=claim["ref"]["id"], base=claim["ref"]["revision"], reason="incomplete"
    )
    assert app.next_exercise(rid(), session_id=session["id"])["kind"] == "none"
    (concern,) = app.read(practice.open_concerns)
    assert concern["route"] == "repair"  # kept as it was; it resumes once the claim is settled


SORTED = "Binary search only works on a sorted array."


def proposals(app, op):
    return {p["key"]: p for p in app.read(workflows.proposals_view, op["ref"]["id"])["claims"]}


def test_a_flagged_claim_cannot_be_cleared_by_reusing_it_for_new_material(make_app):
    app = make_app(outline(), notes_outline)
    _, op = drafted(app)
    sorted_claim = claims(app, op)[SORTED]
    app.flag_material(
        rid(),
        knowledge_id=sorted_claim["ref"]["id"],
        base=sorted_claim["ref"]["revision"],
        reason="also needs random access",
    )
    notes = add(app, "Searching notes", NOTES_SOURCE)
    assert (notes["status"], notes["acceptance"]) == ("succeeded", "pending")

    found = proposals(app, notes)
    assert set(found) == {"b1", "b2"}  # b3 matches nothing
    assert found["b1"]["choices"] == ["hold"]  # it repeats a flagged claim
    assert found["b1"]["proposals"][0]["existing"]["status"] == "disputed"
    assert found["b2"]["choices"] == ["reuse", "separate"]

    with pytest.raises(ValueError, match="flagged"):
        app.accept_material(rid(), operation_id=notes["ref"]["id"], decisions={"b1": "reuse"})
    accepted = app.accept_material(
        rid(), operation_id=notes["ref"]["id"], decisions={"b2": "reuse"}
    )
    curriculum = accepted["curriculum"]["id"]
    view = app.read(workflows.outline_view, curriculum)
    explain, linear = view["targets"]
    by_form = {k["form"]: k for k in explain["knowledge"]}
    # b2 reused the existing relation, which now also quotes the new source
    halving = claims(app, op)[
        "Because each comparison discards the half that cannot contain the target, the search "
        "needs only about log2(n) comparisons."
    ]
    assert by_form["relation"]["ref"]["id"] == halving["ref"]["id"]
    assert "Each comparison halves what remains" in by_form["relation"]["quotes"]
    # b1 stays a separate claim, saved disputed; the old flag is still there
    assert by_form["fact"]["ref"]["id"] != sorted_claim["ref"]["id"]
    assert by_form["fact"]["status"] == "disputed"
    assert by_form["fact"]["dispute"]["related"] == [claims(app, op)[SORTED]["ref"]]
    assert claims(app, op)[SORTED]["status"] == "disputed"
    assert explain["hold"].startswith("rests on material flagged as wrong")
    assert linear["hold"] is None  # unrelated new material is usable
    session = app.start_session(rid(), curriculum_id=curriculum)["session"]
    delivered = app.next_exercise(rid(), session_id=session["id"])
    assert app.read(lambda tx: evidence.attempt_view(tx, delivered["attempt"]))["exercise"] == (
        next(e["ref"] for e in view["exercises"] if e["hold"] is None)
    )


def test_a_conflicting_claim_is_kept_separate_and_held(make_app):
    app = make_app(outline(), lambda request: notes_outline(request, halving_relation="conflicts"))
    drafted(app)
    notes = add(app, "Searching notes", NOTES_SOURCE)
    found = proposals(app, notes)
    assert found["b2"]["choices"] == ["hold"]
    accepted = app.accept_material(
        rid(), operation_id=notes["ref"]["id"], decisions={"b1": "separate"}
    )
    explain, linear = app.read(workflows.outline_view, accepted["curriculum"]["id"])["targets"]
    relation = next(k for k in explain["knowledge"] if k["form"] == "relation")
    assert relation["status"] == "disputed"
    assert relation["dispute"]["reason"].startswith("conflicts with an existing claim")
    assert explain["hold"] is not None
    assert linear["hold"] is None


def two_exercises():
    """Return the outline plus a second exercise checking only the fact (t1)."""
    drafted_outline = outline()
    drafted_outline["exercises"].append(
        {
            "prompt": "What must hold before you binary-search an array?",
            "criteria": [
                {
                    "key": "c1",
                    "requirement": "States that the array must be sorted",
                    "covers": [{"target_key": "t1", "requirement_keys": ["r1"]}],
                }
            ],
            "reference_response": "It must be sorted.",
            "hints": [],
            "expected_seconds": {"setup": 5, "answer": 20, "feedback": 10},
        }
    )
    return drafted_outline


FACT_WRONG = assessment({"c1": "error"}, {"c1": ["It can be in any order."]})


def submit(app, session):
    delivered = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    exercise = app.read(lambda tx: evidence.attempt_view(tx, delivered))["exercise"]
    prompt = app.read(lambda tx: tx.at(exercise, by="content").payload["prompt"])
    text = ANSWER if prompt.startswith("What must be true") else "It can be in any order."
    return app.submit_answer(
        rid(), attempt_id=delivered["id"], base=delivered["revision"], response=text, client_at=None
    )


def test_results_graded_out_of_order_apply_in_the_order_the_answers_happened(make_app, clock):
    app = make_app(two_exercises(), FACT_WRONG, judged(ALL_SHOWN))
    _, op = drafted(app)
    t1, _t2 = targets(app, op)
    session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    first = submit(app, session)  # 10:00: the larger task (graded last)
    clock.advance(minutes=5)
    second = submit(app, session)  # 10:05: the fact alone, wrong (graded first)
    app.run_operation(second["operation"]["id"])
    app.run_operation(first["operation"]["id"])

    # the early success keeps its historical transition but cannot clear the later error
    assert app.read(evidence.target_evidence, t1)["label"] == "error"
    schedule = app.read(practice.schedule_view, t1)
    assert (schedule["need"], schedule["due_at"]) == ("repair", "2026-10-25T10:00:00.000Z")
    history = app.read(practice.schedule_history, t1)
    consumed = [h for h in history if h["obligation"]["status"] == "consumed"]
    assert [h["consumed_by"] for h in consumed] == [first["attempt"]]


# --- "this judgment is wrong" ----------------------------------------------------------


def reviewed(app, attempt, reason="My answer is valid"):
    """Dispute a judgment and let the scripted assessor review it."""
    op = app.dispute_judgment(rid(), attempt_id=attempt["id"], reason=reason)["operation"]
    return app.run_operation(op["id"])


def assessments(app, attempt):
    return app.read(evidence.assessment_history, attempt["id"])


def test_a_corrected_grade_updates_the_effective_state_once_at_the_answer_time(make_app, clock):
    app = make_app(
        outline(), judged(CONNECTION_ERROR, hypotheses=[TWO_CAUSES[1]]), judged(ALL_SHOWN)
    )
    _op, session, attempt, _t1, t2 = answered(app)
    assert app.read(practice.schedule_view, t2)["need"] == "repair"
    (concern,) = app.read(practice.open_concerns)
    clock.advance(hours=3)

    review = reviewed(app, attempt)
    assert (review["status"], review["acceptance"]) == ("succeeded", "pending")
    request = app.provider.requests[-1]
    assert request.protocol["name"] == "reassess-answer"
    assert "My answer is valid" in request.user
    assert ANSWER in request.user

    # the preview shows exactly what accepting does, and writes nothing
    preview = app.correction_preview(review["ref"]["id"])
    assert [(c["before"]["outcome"], c["after"]["outcome"]) for c in preview["criteria"]] == [
        ("demonstrated", "demonstrated"),
        ("demonstrated", "demonstrated"),
        ("error", "demonstrated"),
    ]
    change = next(t for t in preview["targets"] if t["ref"] == t2)
    assert (change["before"]["label"], change["after"]["label"]) == ("error", "independent")
    assert change["after"]["schedule"]["due_at"] == "2026-10-25T10:00:00.000Z"  # answer + 24 h
    assert [c["after"]["status"] for c in preview["concerns"]] == ["superseded"]
    assert len(assessments(app, attempt)) == 1
    assert app.read(practice.schedule_view, t2)["need"] == "repair"

    corrected = app.accept_correction(rid(), operation_id=review["ref"]["id"])
    first, second = assessments(app, attempt)
    assert second["ref"] == {**first["ref"], "revision": 2}
    assert second["supersedes"] == first["ref"]
    assert second["revision_reason"] == "My answer is valid"
    assert [r["outcome"] for r in first["results"]] == ["demonstrated", "demonstrated", "error"]
    assert app.read(lambda tx: evidence.attempt_view(tx, attempt))["response"] == ANSWER

    assert app.read(evidence.target_evidence, t2)["label"] == "independent"
    schedule = app.read(practice.schedule_view, t2)
    assert (schedule["need"], schedule["due_at"]) == (
        "independent_check",
        "2026-10-25T10:00:00.000Z",
    )
    assert schedule["resolution_rule"]["name"] == "descendant-correction"
    consumed = [
        h
        for h in app.read(practice.schedule_history, t2)
        if h["obligation"]["status"] == "consumed"
    ]
    assert [h["consumed_by"] for h in consumed] == [attempt]  # once, by the original answer
    superseded = app.read(lambda tx: practice.concern_view(tx, concern["ref"]["id"]))
    assert superseded["status"] == "superseded"
    transition = app.read(lambda tx: tx.at(corrected["transition"], by="workflows").payload)
    assert transition["category"] == "assessment"
    assert first["ref"] in transition["before"]
    assert second["ref"] in transition["after"]

    # nothing more happens on a repeat: same receipt, no second effect
    revisions = len(app.read(practice.schedule_history, t2))
    with pytest.raises(ValueError, match="not waiting"):
        app.accept_correction(rid(), operation_id=review["ref"]["id"])
    assert len(app.read(practice.schedule_history, t2)) == revisions
    assert app.next_exercise(rid(), session_id=session["id"])["kind"] == "none"


def test_a_success_corrected_to_an_error_reopens_the_first_check_and_asks_for_repair(make_app):
    app = make_app(outline(), judged(ALL_SHOWN), judged(CONNECTION_ERROR))
    _op, _session, attempt, t1, t2 = answered(app)
    later = app.read(practice.schedule_view, t2)["obligation"]
    app.accept_correction(
        rid(), operation_id=reviewed(app, attempt, "I made a mistake")["ref"]["id"]
    )

    assert app.read(evidence.target_evidence, t2)["label"] == "error"
    history = app.read(practice.schedule_history, t2)
    current = history[-1]
    assert (current["need"], current["obligation"]["kind"], current["obligation"]["status"]) == (
        "repair",
        "initial",
        "open",
    )
    assert current["consumed_by"] is None
    assert [h["obligation"]["status"] for h in history if h["obligation"]["id"] == later["id"]][
        -1
    ] == "invalidated"
    assert app.read(practice.schedule_view, t1)["need"] == "independent_check"  # unaffected
    (concern,) = app.read(practice.open_concerns)
    assert (concern["kind"], concern["route"]) == ("error", "repair")


def test_keeping_the_original_judgment_changes_nothing(make_app):
    app = make_app(outline(), judged(CONNECTION_ERROR), judged(ALL_SHOWN))
    _op, _session, attempt, _t1, t2 = answered(app)
    review = reviewed(app, attempt)
    kept = app.keep_judgment(rid(), operation_id=review["ref"]["id"])
    assert kept["operation"]["acceptance"] == "cancelled"
    assert len(assessments(app, attempt)) == 1
    assert app.read(evidence.target_evidence, t2)["label"] == "error"


def test_a_misread_correction_removes_the_error_without_inventing_a_success(make_app):
    app = make_app(outline(), judged(CONNECTION_ERROR), judged(CONNECTION_ERROR, misread=["c3"]))
    _op, _session, attempt, _t1, t2 = answered(app)
    app.accept_correction(rid(), operation_id=reviewed(app, attempt, "I misread it")["ref"]["id"])
    result = app.read(evidence.target_evidence, t2)
    assert result["label"] == "unresolved"
    assert "misread" in result["reasons"][0]
    assert app.read(practice.schedule_view, t2)["need"] == "initial"
    assert app.read(practice.open_concerns) == []


def test_clarification_answers_cannot_be_disputed(make_app):
    from tests.test_repair import ask_about_the_connection, clarify, focused

    app = make_app(*ask_about_the_connection([], focused("demonstrated")))
    _, op = drafted(app)
    clarify(app, op)
    asked = [a for a in app.read(evidence.attempts) if a["purpose"] == "clarification"][-1]
    with pytest.raises(ValueError, match="clarification"):
        app.dispute_judgment(rid(), attempt_id=asked["ref"]["id"], reason="My answer is valid")


FACT_RIGHT = assessment({"c1": "demonstrated"}, {"c1": ["It must be sorted."]})
FACT_WRONG_ON_THE_LARGER_TASK = judged({"c1": "error", "c2": "demonstrated", "c3": "demonstrated"})


def submit_fact(app, session):
    """Answer the fact-only exercise correctly (the second exercise of ``two_exercises``)."""
    delivered = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    return app.submit_answer(
        rid(),
        attempt_id=delivered["id"],
        base=delivered["revision"],
        response="It must be sorted.",
        client_at=None,
    )


def test_a_later_real_check_reanchors_when_an_earlier_success_is_corrected(make_app, clock):
    app = make_app(two_exercises(), judged(ALL_SHOWN), FACT_RIGHT, FACT_WRONG_ON_THE_LARGER_TASK)
    _op, session, attempt, t1, _t2 = answered(app)
    clock.advance(hours=25)  # B answers after A's first later check was due
    later = submit_fact(app, session)
    app.run_operation(later["operation"]["id"])

    app.accept_correction(
        rid(), operation_id=reviewed(app, attempt, "I made a mistake")["ref"]["id"]
    )
    schedule = app.read(practice.schedule_view, t1)
    assert (schedule["need"], schedule["due_at"]) == (
        "independent_check",
        "2026-10-26T11:00:00.000Z",  # B's own answer + 24 h
    )
    assert schedule["reason"] == "reanchored from a real later check"
    (effect,) = schedule["check_effects"]
    assert effect["disposition"] == "reanchored"
    history = app.read(practice.schedule_history, t1)
    first = history[0]["obligation"]["id"]
    assert [h["obligation"]["status"] for h in history if h["obligation"]["id"] == first][-1] == (
        "replaced"  # replaced by the later evidence, not passed by A
    )
    assert app.read(evidence.target_evidence, t1)["label"] == "independent"


def test_a_later_answer_still_being_assessed_holds_the_corrected_schedule(make_app, clock):
    unclear = judged({"c1": "not_shown", "c2": "demonstrated", "c3": "demonstrated"})
    app = make_app(two_exercises(), judged(ALL_SHOWN), unclear, FACT_RIGHT)
    _op, session, attempt, t1, _t2 = answered(app)
    clock.advance(hours=25)
    later = submit_fact(app, session)  # submitted; its assessment has not run

    app.accept_correction(rid(), operation_id=reviewed(app, attempt, "I guessed")["ref"]["id"])
    schedule = app.read(practice.schedule_view, t1)
    assert (schedule["need"], schedule["hold_reason"]) == (
        "held",
        "earlier history changed; this answer is still being assessed",
    )
    assert [e["disposition"] for e in schedule["check_effects"]] == ["pending"]

    app.run_operation(later["operation"]["id"])  # the late result settles the hold
    schedule = app.read(practice.schedule_view, t1)
    assert (schedule["need"], schedule["due_at"]) == (
        "independent_check",
        "2026-10-26T11:00:00.000Z",
    )


def test_a_corrected_fresh_check_rederives_its_repair_cycle(make_app):
    wrong = judged(CONNECTION_ERROR)
    app = make_app(
        outline(),
        judged(CONNECTION_ERROR, hypotheses=[TWO_CAUSES[1]]),
        teaching(),
        variant(),
        wrong,
        judged(ALL_SHOWN),
    )
    _op, session, _attempt, _t1, t2 = answered(app)
    taught = app.next_exercise(rid(), session_id=session["id"])
    app.run_operation(taught["operation"]["id"])
    study = app.next_exercise(rid(), session_id=session["id"])["study"]
    app.complete_study(rid(), study_id=study["id"], base=study["revision"], client_at=None)
    preparing = app.next_exercise(rid(), session_id=session["id"])
    app.run_operation(preparing["operation"]["id"])
    fresh = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=fresh["id"], base=fresh["revision"], response=ANSWER, client_at=None
    )
    app.run_operation(sent["operation"]["id"])
    (concern,) = app.read(practice.open_concerns)
    assert [c["outcome"] for c in concern["cycles"]] == ["unsuccessful"]

    app.accept_correction(rid(), operation_id=reviewed(app, fresh)["ref"]["id"])
    settled = app.read(lambda tx: practice.concern_view(tx, concern["ref"]["id"]))
    assert ([c["outcome"] for c in settled["cycles"]], settled["status"]) == (
        ["recovered"],
        "resolved",
    )
    assert app.read(evidence.target_evidence, t2)["label"] == "independent"


def test_a_draft_on_a_corrected_away_opportunity_counts_only_as_practice(make_app, clock):
    app = make_app(two_exercises(), judged(ALL_SHOWN), FACT_WRONG_ON_THE_LARGER_TASK, FACT_RIGHT)
    _op, session, attempt, t1, _t2 = answered(app)
    clock.advance(hours=25)
    draft = app.next_exercise(rid(), session_id=session["id"])["attempt"]  # reserved, owned

    app.accept_correction(
        rid(), operation_id=reviewed(app, attempt, "I made a mistake")["ref"]["id"]
    )
    schedule = app.read(practice.schedule_view, t1)
    assert schedule["need"] == "repair"
    (effect,) = schedule["check_effects"]
    assert (effect["disposition"], effect["revokes_reservation"]) == ("held", True)
    assert app.read(workflows.practice_view, session["id"])["attempt"]["counts_as_practice"]

    sent = app.submit_answer(
        rid(),
        attempt_id=draft["id"],
        base=draft["revision"],
        response="It must be sorted.",
        client_at=None,
    )
    app.run_operation(sent["operation"]["id"])
    schedule = app.read(practice.schedule_view, t1)
    assert (schedule["need"], schedule["obligation"]["kind"]) == ("repair", "initial")


def test_a_review_still_running_cannot_be_decided_yet(make_app):
    app = make_app(outline(), judged(CONNECTION_ERROR), judged(ALL_SHOWN))
    _op, _session, attempt, _t1, _t2 = answered(app)
    op = app.dispute_judgment(rid(), attempt_id=attempt["id"], reason="My answer is valid")
    with pytest.raises(ValueError, match="not waiting"):
        app.keep_judgment(rid(), operation_id=op["operation"]["id"])
    review = app.run_operation(op["operation"]["id"])  # its result is not overwritten later
    assert review["acceptance"] == "pending"


# --- regressions from the slice-3 spec review -------------------------------------------


def test_a_second_owner_of_a_consumed_check_does_not_move_it(make_app, clock):
    app = make_app(two_exercises(), judged(ALL_SHOWN), FACT_RIGHT)
    _, op = drafted(app)
    t1, _t2 = targets(app, op)
    session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    first = submit(app, session)  # owns the first check; graded later
    clock.advance(hours=2)
    second = submit_fact(app, session)  # offered while the first was ungraded: same check
    app.run_operation(first["operation"]["id"])
    app.run_operation(second["operation"]["id"])
    schedule = app.read(practice.schedule_view, t1)
    assert schedule["due_at"] == "2026-10-25T10:00:00.000Z"  # the first answer + 24 h, unmoved


def test_a_late_grade_on_an_old_goal_version_stays_with_that_version(make_app):
    app = make_app(outline(), judged(CONNECTION_ERROR), judged(CONNECTION_ERROR))
    _, op = drafted(app)
    session, first = answer(app, op)  # submitted under version 1, graded later
    _t1, t2 = targets(app, op)
    edit_condition(app, t2)
    (held,) = app.read(workflows.outline_view, curriculum_id(op))["exercises"]
    app.rebind_exercise(rid(), exercise_id=held["ref"]["id"], base=held["ref"]["revision"])
    again = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=again["id"], base=again["revision"], response=ANSWER, client_at=None
    )
    app.run_operation(sent["operation"]["id"])  # an error on version 2 opens a concern
    app.run_operation(first["operation"]["id"])  # the late error belongs to version 1
    scopes = sorted(
        (s["target"]["revision"], c["status"])
        for c in app.read(lambda tx: [r.view for r in tx.current("concern", by="practice")])
        for s in c["scope"]
    )
    assert scopes == [(1, "open"), (2, "open")]


def test_a_pending_answer_on_a_revoked_draft_does_not_hold_the_schedule(make_app, clock):
    unclear = judged({"c1": "not_shown", "c2": "demonstrated", "c3": "demonstrated"})
    app = make_app(two_exercises(), judged(ALL_SHOWN), unclear, unclear)
    _op, session, attempt, t1, _t2 = answered(app)
    clock.advance(hours=25)
    draft = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    app.accept_correction(rid(), operation_id=reviewed(app, attempt, "I guessed")["ref"]["id"])
    app.submit_answer(
        rid(),
        attempt_id=draft["id"],
        base=draft["revision"],
        response="It must be sorted.",
        client_at=None,
    )  # now practice, waiting for its grade
    app.accept_correction(rid(), operation_id=reviewed(app, attempt, "still unsure")["ref"]["id"])
    assert app.read(practice.schedule_view, t1)["need"] == "initial"


def test_a_corrected_check_does_not_unpause_a_paused_concern(make_app):
    wrong = judged(CONNECTION_ERROR)
    also_wrong = judged({"c1": "demonstrated", "c2": "error", "c3": "error"})
    app = make_app(
        outline(),
        judged(CONNECTION_ERROR, hypotheses=[TWO_CAUSES[1]]),
        teaching(),
        variant(),
        wrong,
        also_wrong,
    )
    _op, session, _attempt, _t1, _t2 = answered(app)
    taught = app.next_exercise(rid(), session_id=session["id"])
    app.run_operation(taught["operation"]["id"])
    study = app.next_exercise(rid(), session_id=session["id"])["study"]
    app.complete_study(rid(), study_id=study["id"], base=study["revision"], client_at=None)
    app.run_operation(app.next_exercise(rid(), session_id=session["id"])["operation"]["id"])
    fresh = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    sent = app.submit_answer(
        rid(), attempt_id=fresh["id"], base=fresh["revision"], response=ANSWER, client_at=None
    )
    app.run_operation(sent["operation"]["id"])
    (concern,) = app.read(practice.open_concerns)
    app.pause_concern(rid(), concern_id=concern["ref"]["id"], base=concern["ref"]["revision"])
    app.accept_correction(
        rid(), operation_id=reviewed(app, fresh, "a different mistake")["ref"]["id"]
    )
    after = app.read(lambda tx: practice.concern_view(tx, concern["ref"]["id"]))
    assert after["status"] == "paused"


def test_a_repeated_correction_adds_no_concern_or_schedule_revision(make_app):
    app = make_app(outline(), judged(CONNECTION_ERROR), judged(ALL_SHOWN), judged(ALL_SHOWN))
    _op, _session, attempt, _t1, t2 = answered(app)
    app.accept_correction(rid(), operation_id=reviewed(app, attempt)["ref"]["id"])
    concerns_before = app.read(
        lambda tx: [
            len(tx.history("concern", r.id, by="practice"))
            for r in tx.current("concern", by="practice")
        ]
    )
    schedules_before = len(app.read(practice.schedule_history, t2))
    app.accept_correction(rid(), operation_id=reviewed(app, attempt, "again")["ref"]["id"])
    concerns_after = app.read(
        lambda tx: [
            len(tx.history("concern", r.id, by="practice"))
            for r in tx.current("concern", by="practice")
        ]
    )
    assert concerns_after == concerns_before
    assert len(app.read(practice.schedule_history, t2)) == schedules_before


def test_reuse_is_refused_when_the_existing_claim_was_reworded_after_drafting(make_app):
    app = make_app(outline(), notes_outline)
    _, op = drafted(app)
    notes = add(app, "Searching notes", NOTES_SOURCE)
    halving = claims(app, op)[
        "Because each comparison discards the half that cannot contain the target, the search "
        "needs only about log2(n) comparisons."
    ]
    app.flag_material(
        rid(), knowledge_id=halving["ref"]["id"], base=halving["ref"]["revision"], reason="vague"
    )
    flagged = app.read(lambda tx: tx.require("knowledge", halving["ref"]["id"], by="content").ref)
    app.revise_material(
        rid(),
        knowledge_id=flagged["id"],
        base=flagged["revision"],
        statement="Halving the range each time needs about log2(n) comparisons.",
        scope=halving["scope"],
        reason="clearer",
    )
    assert proposals(app, notes)["b2"]["choices"] == ["separate"]
    with pytest.raises(ValueError, match="changed after"):
        app.accept_material(
            rid(), operation_id=notes["ref"]["id"], decisions={"b1": "separate", "b2": "reuse"}
        )


def test_only_a_stale_practice_exercise_can_be_rebound(make_app):
    from tests.test_repair import ask_about_the_connection, clarify, focused

    app = make_app(*ask_about_the_connection([], focused("demonstrated")))
    _, op = drafted(app)
    clarify(app, op)
    _t1, t2 = targets(app, op)
    edit_condition(app, t2)
    question = app.read(
        lambda tx: next(
            r.ref
            for r in tx.current("exercise", by="content")
            if r.payload["use"] == "clarification"
        )
    )
    with pytest.raises(ValueError, match="earlier version"):
        app.rebind_exercise(rid(), exercise_id=question["id"], base=question["revision"])


def test_accepting_does_exactly_what_the_preview_showed(make_app):
    app = make_app(outline(), judged(CONNECTION_ERROR), judged(ALL_SHOWN))
    _op, _session, attempt, _t1, _t2 = answered(app)
    review = reviewed(app, attempt)
    preview = app.correction_preview(review["ref"]["id"])
    with pytest.raises(Conflict):
        app.accept_correction(rid(), operation_id=review["ref"]["id"], preview="0" * 64)
    app.accept_correction(rid(), operation_id=review["ref"]["id"], preview=preview["digest"])
