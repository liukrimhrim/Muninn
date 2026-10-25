import json

import pytest

from muninn import evidence, practice, workflows
from muninn.library import Conflict, export_library, learning_fingerprint
from muninn.workflows import App
from tests.conftest import FailIfCalled, rid, timeout
from tests.drafts import SOURCE, assessment, outline

ANSWER = "It must be sorted. Each comparison throws away half, so it takes about log2(n) steps."
QUOTES = {"c1": ["It must be sorted."], "c2": ["throws away half"], "c3": ["about log2(n) steps"]}


def judged(**outcomes):
    return assessment(
        outcomes, {k: QUOTES[k] for k, v in outcomes.items() if v in ("demonstrated", "error")}
    )


ALL_RIGHT = judged(c1="demonstrated", c2="demonstrated", c3="demonstrated")


def drafted(app):
    added = app.add_material(
        rid(), title="Binary search", text=SOURCE, purpose="Explain why it is fast"
    )
    op = app.run_operation(added["operation"]["id"])
    return added, op


def curriculum_id(op):
    return next(o for o in op["outputs"] if o["kind"] == "curriculum")["id"]


def answer(app, op, text=ANSWER, *, hint=False):
    session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    delivered = app.next_exercise(rid(), session_id=session["id"])
    attempt = delivered["attempt"]
    if hint:
        app.reveal_hint(rid(), attempt_id=attempt["id"], hint_id="h1")
        attempt = app.acknowledge_hint(
            rid(), attempt_id=attempt["id"], base=attempt["revision"], hint_id="h1", client_at=None
        )["attempt"]
    submitted = app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response=text, client_at=None
    )
    return session, submitted


def need(app, target):
    schedule = app.store.read(lambda tx: practice.schedule_view(tx, target))
    assert schedule is not None
    return schedule["need"]


def targets(app, op):
    curriculum = next(o for o in op["outputs"] if o["kind"] == "curriculum")
    return app.store.read(
        lambda tx: [
            t for s in tx.at(curriculum, by="content").payload["sections"] for t in s["targets"]
        ]
    )


# --- drafting -----------------------------------------------------------------------


def test_a_drafted_outline_selects_goals_without_admitting_or_scheduling_them(make_app):
    app = make_app(outline())
    _, op = drafted(app)
    assert op["acceptance"] == "accepted"
    t1, _t2 = targets(app, op)
    enrollment = app.store.read(lambda tx: practice.enrollment_for(tx, curriculum_id(op)))
    assert [e["state"] for e in enrollment["practice"]] == ["unstarted", "unstarted"]
    assert app.store.read(lambda tx: practice.schedule_view(tx, t1)) is None


def test_a_refused_draft_gets_one_targeted_retry(make_app):
    bad = outline()
    bad["knowledge"][0]["quotes"] = ["Binary search is magic."]
    app = make_app(bad, outline())
    _, first = drafted(app)
    assert first["acceptance"] == "rejected"
    assert "not in the source" in first["acceptance_reason"]
    retry_request = app.provider.requests[1]
    assert "Your previous output was refused" in retry_request.user
    retry = app.store.read(lambda tx: [r.payload for r in tx.current("operation", by="workflows")])[
        -1
    ]
    assert (retry["try_index"], retry["acceptance"]) == (2, "accepted")
    assert retry["request_group"] == first["request_group"]


def test_two_refusals_leave_a_visible_authoring_need_and_no_third_call(make_app):
    bad = outline()
    bad["exercises"] = []
    app = make_app(bad, bad)
    added, _ = drafted(app)
    ops = app.store.read(lambda tx: [r.payload for r in tx.current("operation", by="workflows")])
    assert [o["acceptance"] for o in ops] == ["rejected", "rejected"]
    assert len(app.provider.requests) == 2
    assert app.store.read(lambda tx: tx.current("curriculum", by="content")) == []
    assert (
        app.store.read(lambda tx: tx.get("source", added["source"]["id"], by="content")) is not None
    )


def test_a_drafting_timeout_keeps_the_source_and_waits_for_an_explicit_retry(make_app):
    app = make_app(timeout(), outline())
    _added, op = drafted(app)
    assert op["status"] == "failed"
    assert len(app.provider.requests) == 1
    retried = app.retry_operation(rid(), op["ref"]["id"])["operation"]
    assert app.run_operation(retried["id"])["acceptance"] == "accepted"


# --- one encounter --------------------------------------------------------------------


def test_delivery_admits_only_the_covered_targets_with_open_initial_obligations(make_app):
    app = make_app(outline())
    _, op = drafted(app)
    session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    app.next_exercise(rid(), session_id=session["id"])
    enrollment = app.store.read(lambda tx: practice.enrollment_for(tx, curriculum_id(op)))
    assert {e["state"] for e in enrollment["practice"]} == {"active"}
    for t in targets(app, op):
        schedule = app.store.read(lambda tx, t=t: practice.schedule_view(tx, t))
        assert (schedule["need"], schedule["due_at"], schedule["obligation"]["status"]) == (
            "initial",
            None,
            "open",
        )


def test_resuming_a_session_returns_the_same_draft(make_app):
    app = make_app(outline())
    _, op = drafted(app)
    session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    first = app.next_exercise(rid(), session_id=session["id"])
    again = app.next_exercise(rid(), session_id=session["id"])
    assert again["resumed"] is True
    assert again["attempt"]["id"] == first["attempt"]["id"]


def test_a_retried_submission_creates_one_answer_and_one_assessment_operation(make_app):
    app = make_app(outline())
    _, op = drafted(app)
    session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    attempt = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    request_id = rid()
    args = {
        "attempt_id": attempt["id"],
        "base": attempt["revision"],
        "response": ANSWER,
        "client_at": None,
    }
    first = app.submit_answer(request_id, **args)
    assert app.submit_answer(request_id, **args) == first
    with pytest.raises(Conflict):
        app.submit_answer(request_id, **{**args, "response": "different"})
    ops = app.store.read(
        lambda tx: [
            r
            for r in tx.current("operation", by="workflows")
            if r.payload["purpose"] == "assess_answer"
        ]
    )
    assert len(ops) == 1


def test_first_independent_success_schedules_a_check_a_day_after_the_answer(make_app, clock):
    # lifecycle CCA01: answered at 10:00, graded at 10:20, due the next day at 10:00
    app = make_app(outline(), ALL_RIGHT)
    _, op = drafted(app)
    _, submitted = answer(app, op)
    clock.advance(minutes=20)
    assessed = app.run_operation(submitted["operation"]["id"])
    assert assessed["acceptance"] == "accepted"
    for t in targets(app, op):
        history = app.store.read(lambda tx, t=t: practice.schedule_history(tx, t))
        assert history[-2]["obligation"]["status"] == "consumed"
        assert history[-1]["obligation"]["kind"] == "later"
        assert (history[-1]["need"], history[-1]["due_at"]) == (
            "independent_check",
            "2026-10-25T10:00:00.000Z",
        )
        assert (
            app.store.read(lambda tx, t=t: evidence.target_evidence(tx, t)["label"])
            == "independent"
        )


def test_mixed_outcomes_resolve_each_target_separately(make_app):
    # lifecycle CCA02: the fact stands, the connection error opens a repair concern
    app = make_app(outline(), judged(c1="demonstrated", c2="demonstrated", c3="error"))
    _, op = drafted(app)
    _, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    t1, t2 = targets(app, op)
    assert need(app, t1) == "independent_check"
    t2_schedule = app.store.read(lambda tx: practice.schedule_view(tx, t2))
    assert (t2_schedule["need"], t2_schedule["due_at"]) == ("repair", None)
    concerns = app.store.read(practice.open_concerns)
    assert [
        (c["scope"][0]["target"]["id"], c["scope"][0]["requirement_ids"]) for c in concerns
    ] == [(t2["id"], ["r2"])]


def test_not_shown_is_never_a_failure(make_app):
    app = make_app(outline(), judged(c1="demonstrated", c2="not_shown", c3="cannot_judge"))
    _, op = drafted(app)
    _, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    _, t2 = targets(app, op)
    assert app.store.read(lambda tx: evidence.target_evidence(tx, t2)["label"]) == "unresolved"
    schedule = app.store.read(lambda tx: practice.schedule_view(tx, t2))
    assert (schedule["need"], schedule["due_at"]) == ("clarify", None)
    assert app.store.read(practice.open_concerns) == []


def test_an_acknowledged_hint_makes_its_targets_helped_and_bounds_its_time(make_app):
    app = make_app(outline(), ALL_RIGHT)
    _, op = drafted(app)
    _, submitted = answer(app, op, hint=True)
    app.run_operation(submitted["operation"]["id"])
    t1, t2 = targets(app, op)
    assert app.store.read(lambda tx: evidence.target_evidence(tx, t1)["label"]) == "independent"
    assert app.store.read(lambda tx: evidence.target_evidence(tx, t2)["label"]) == "helped"
    attempt = app.store.read(
        lambda tx: evidence.attempt_view(tx, attempt_id=submitted["attempt"]["id"])
    )
    help_time = attempt["assistance"][0]["time_evidence"][0]
    assert attempt["assistance"][0]["shown_at"] is None
    assert help_time["precision"] == "bounded"
    # a helped success keeps the initial obligation open and asks for a check tomorrow
    schedule = app.store.read(lambda tx: practice.schedule_view(tx, t2))
    assert (schedule["obligation"]["kind"], schedule["need"]) == ("initial", "independent_check")


def test_an_unacknowledged_hint_cannot_certify_independence(make_app):
    app = make_app(outline(), ALL_RIGHT)
    _, op = drafted(app)
    session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    attempt = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    app.reveal_hint(rid(), attempt_id=attempt["id"], hint_id="h1")
    submitted = app.submit_answer(
        rid(), attempt_id=attempt["id"], base=attempt["revision"], response=ANSWER, client_at=None
    )
    app.run_operation(submitted["operation"]["id"])
    _, t2 = targets(app, op)
    result = app.store.read(lambda tx: evidence.target_evidence(tx, t2))
    assert result["label"] == "unresolved"
    assert "not confirmed" in result["reasons"][0]
    # the demonstration still earns a check tomorrow, but cannot consume the first obligation
    schedule = app.store.read(lambda tx: practice.schedule_view(tx, t2))
    assert (schedule["obligation"]["kind"], schedule["need"]) == ("initial", "independent_check")
    assert schedule["due_at"] is not None


def test_a_hint_cannot_be_revealed_after_the_answer_is_submitted(make_app):
    app = make_app(outline())
    _, op = drafted(app)
    _, submitted = answer(app, op)
    with pytest.raises(ValueError, match="already submitted"):
        app.reveal_hint(rid(), attempt_id=submitted["attempt"]["id"], hint_id="h1")


def test_an_explicit_retry_stays_in_its_request_group_and_cannot_draft_twice(make_app):
    app = make_app(timeout(), outline())
    _, failed = drafted(app)
    retried = app.retry_operation(rid(), failed["ref"]["id"])["operation"]
    accepted = app.run_operation(retried["id"])
    assert accepted["request_group"] == failed["request_group"]
    assert app.store.read(workflows.home_view)["drafting"] == []
    with pytest.raises(ValueError, match="already"):
        app.retry_operation(rid(), failed["ref"]["id"])


def test_a_new_session_resumes_the_unfinished_draft(make_app):
    app = make_app(outline())
    _, op = drafted(app)
    first = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    draft = app.next_exercise(rid(), session_id=first["id"])["attempt"]
    app.save_draft(rid(), attempt_id=draft["id"], base=draft["revision"], response="half an answer")
    app.end_session(rid(), session_id=first["id"], base=first["revision"], reason="stopped")
    second = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    resumed = app.next_exercise(rid(), session_id=second["id"])
    assert (resumed["attempt"]["id"], resumed["resumed"]) == (draft["id"], True)
    view = app.store.read(lambda tx: workflows.practice_view(tx, second["id"]))
    assert view["attempt"]["response"] == "half an answer"
    offers = app.store.read(lambda tx: tx.current("practice_offer", by="practice"))
    assert len(offers) == 1


def two_exercises():
    draft = outline()
    first = draft["exercises"][0]
    draft["exercises"] = [
        {
            **first,
            "prompt": "Why only about log2(n) comparisons?",
            "criteria": first["criteria"][1:],
            "hints": [],
        },
        {
            **first,
            "prompt": "What must be true of the array?",
            "criteria": first["criteria"][:1],
            "hints": [],
        },
    ]
    return draft


def test_exercises_follow_the_current_outline_order(make_app):
    app = make_app(two_exercises())
    _, op = drafted(app)
    session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
    first = app.next_exercise(rid(), session_id=session["id"])["attempt"]
    prompt = app.store.read(lambda tx: workflows.practice_view(tx, session["id"]))["attempt"][
        "prompt"
    ]
    assert prompt == "What must be true of the array?"  # t1 comes first in the outline
    del first


def test_a_past_session_summary_keeps_its_own_results(make_app):
    draft = outline()
    full = draft["exercises"][0]
    draft["exercises"] = [
        {
            **full,
            "prompt": "What must be true of the array?",
            "criteria": full["criteria"][:1],
            "hints": [],
        },
        full,
    ]
    later_mistake = judged(c1="error", c2="demonstrated", c3="demonstrated")
    app = make_app(draft, judged(c1="demonstrated"), later_mistake)
    _, op = drafted(app)
    sessions = []
    for _ in range(2):
        session = app.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
        attempt = app.next_exercise(rid(), session_id=session["id"])["attempt"]
        submitted = app.submit_answer(
            rid(),
            attempt_id=attempt["id"],
            base=attempt["revision"],
            response=ANSWER,
            client_at=None,
        )
        app.run_operation(submitted["operation"]["id"])
        sessions.append(session)
    first = app.store.read(lambda tx: workflows.summary_view(tx, sessions[0]["id"]))
    assert [t["label"] for t in first["targets"]] == ["independent"]
    second = app.store.read(lambda tx: workflows.summary_view(tx, sessions[1]["id"]))
    assert sorted(t["label"] for t in second["targets"]) == ["error", "independent"]


# --- failures ---------------------------------------------------------------------


def test_an_assessment_timeout_preserves_the_answer_and_changes_nothing_else(make_app):
    app = make_app(outline(), timeout())
    _, op = drafted(app)
    _, submitted = answer(app, op)
    assessed = app.run_operation(submitted["operation"]["id"])
    assert assessed["status"] == "failed"
    attempt = app.store.read(
        lambda tx: evidence.attempt_view(tx, attempt_id=submitted["attempt"]["id"])
    )
    assert (attempt["status"], attempt["response"]) == ("submitted", ANSWER)
    assert (
        app.store.read(lambda tx: evidence.assessment_for(tx, submitted["attempt"]["id"])) is None
    )
    for t in targets(app, op):
        assert need(app, t) == "initial"


def test_an_invented_quote_is_refused_and_retried_once(make_app):
    invented = judged(c1="demonstrated", c2="demonstrated", c3="demonstrated")
    invented["observations"][0]["quotes"] = ["The array is ordered."]
    app = make_app(outline(), invented, ALL_RIGHT)
    _, op = drafted(app)
    _, submitted = answer(app, op)
    first = app.run_operation(submitted["operation"]["id"])
    assert first["acceptance"] == "rejected"
    assert "not in the answer" in first["acceptance_reason"]
    assert (
        app.store.read(lambda tx: evidence.assessment_for(tx, submitted["attempt"]["id"]))
        is not None
    )


def test_a_failure_between_evidence_and_practice_writes_leaves_nothing_half_done(
    make_app, monkeypatch
):
    app = make_app(outline(), ALL_RIGHT)
    _, op = drafted(app)
    _, submitted = answer(app, op)

    def broken(*args, **kwargs):
        msg = "crash after the assessment was written"
        raise RuntimeError(msg)

    monkeypatch.setattr(practice, "reconcile", broken)
    with pytest.raises(RuntimeError):
        app.run_operation(submitted["operation"]["id"])
    assert (
        app.store.read(lambda tx: evidence.assessment_for(tx, submitted["attempt"]["id"])) is None
    )
    assert app.operation(submitted["operation"]["id"])["status"] == "running"


def test_a_refusal_after_partial_writes_keeps_none_of_them(make_app, monkeypatch):
    app = make_app(outline(), outline())

    def refuse(*args, **kwargs):
        msg = "enrollment refused after the outline was written"
        raise ValueError(msg)

    monkeypatch.setattr(practice, "enroll", refuse)
    _, first = drafted(app)
    assert first["acceptance"] == "rejected"
    assert app.store.read(lambda tx: tx.current("curriculum", by="content")) == []
    assert app.store.read(lambda tx: tx.current("knowledge", by="content")) == []


def test_a_restart_interrupts_unfinished_operations_and_ignores_their_late_output(
    make_app, tmp_path
):
    app = make_app(outline())
    _, op = drafted(app)
    _, submitted = answer(app, op)
    app.store.close()
    restarted = make_app(ALL_RIGHT, path=tmp_path / "lib.sqlite")
    assert restarted.operation(submitted["operation"]["id"])["status"] == "interrupted"
    assert restarted.run_operation(submitted["operation"]["id"])["status"] == "interrupted"
    assert restarted.provider.requests == []
    retried = restarted.retry_operation(rid(), submitted["operation"]["id"])["operation"]
    assert retried["id"] != submitted["operation"]["id"]
    assert restarted.run_operation(retried["id"])["acceptance"] == "accepted"


# --- export and restore -------------------------------------------------------------------


def test_restore_continues_the_same_curriculum_without_calling_the_model(make_app, tmp_path, clock):
    app = make_app(outline(), ALL_RIGHT)
    _, op = drafted(app)
    _, submitted = answer(app, op)
    app.run_operation(submitted["operation"]["id"])
    archive = app.export()
    restored_store = App.restore(tmp_path / "restored.sqlite", json.dumps(archive), clock=clock)
    restored = App(restored_store, FailIfCalled())
    restored.recover()
    try:
        # restoring and starting the app add nothing to the learning history
        assert learning_fingerprint(export_library(restored_store, writer_release="x")) == (
            learning_fingerprint(archive)
        )
        attempt = restored_store.read(
            lambda tx: evidence.attempt_view(tx, attempt_id=submitted["attempt"]["id"])
        )
        assert attempt["response"] == ANSWER
        assert (
            restored_store.read(lambda tx: evidence.assessment_for(tx, submitted["attempt"]["id"]))
            is not None
        )
        next_session = restored.start_session(rid(), curriculum_id=curriculum_id(op))["session"]
        assert restored.next_exercise(rid(), session_id=next_session["id"])["attempt"] is None
    finally:
        restored_store.close()
