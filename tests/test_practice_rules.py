"""Pure Practice rules for diagnosis and repair (everyday-learning-design.md section 5)."""

import pytest

from muninn.evidence import AssessQuestion
from muninn.practice import ConcernP, discriminates, help_basis
from tests.drafts import question


@pytest.mark.parametrize(
    ("demonstrated", "error", "useful"),
    [
        (("resolve", None), ("teach", "h1"), True),
        (("teach", "h2"), ("teach", "h1"), True),
        (("teach", "h1"), ("teach", "h1"), False),  # every answer leads to the same help
    ],
    ids=["resolve-or-teach", "different-help", "same-help"],
)
def test_a_question_earns_its_time_only_if_its_answers_change_the_help(demonstrated, error, useful):
    asked = AssessQuestion.model_validate(question(["c3"], demonstrated=demonstrated, error=error))
    assert discriminates(asked) is useful
    assert discriminates(None) is False


def concern(**fields):
    ref = {"kind": "attempt", "id": "a1", "revision": 2}
    return ConcernP.model_validate(
        {
            "origin": ref,
            "scope": [],
            "previous_concern": None,
            "status": "open",
            "route": "repair",
            "basis": [],
            "resolution_reason": None,
            **fields,
        }
    )


def cause(key):
    return {"key": key, "cause": f"cause {key}", "practice": f"practice {key}"}


def test_teaching_rests_on_a_supported_cause_open_alternatives_or_the_error_itself():
    assert help_basis(concern(hypotheses=[cause("h1"), cause("h2")], focus="h2")) == "supported"
    assert help_basis(concern(hypotheses=[cause("h1"), cause("h2")])) == "uncertain"
    assert help_basis(concern()) == "direct"


def test_a_slice_one_concern_still_reads_with_the_slice_two_fields():
    old = concern()
    assert (old.kind, old.hypotheses, old.question, old.cycles) == ("error", [], None, [])


def offer_record(offer_id, state, obligation="o1"):
    from muninn.library import Record

    target = {"kind": "target", "id": "t1", "revision": 1}
    payload = {
        "attempt": {"kind": "attempt", "id": f"a-{offer_id}", "revision": 1},
        "session": {"kind": "session", "id": "s1", "revision": 1},
        "slots": [
            {
                "target": target,
                "obligation_id": obligation,
                "schedule_at_offer": {"kind": "schedule", "id": "sc", "revision": 1},
                "role": "owner",
            }
        ],
        "state": state,
        "reserved_at": "2026-10-24T10:00:00.000Z",
        "released_at": None,
        "reason": None,
    }
    return Record("practice_offer", offer_id, 1, 1, "2026-10-24T10:00:00.000Z", payload)


def test_an_import_with_two_live_owners_of_one_check_is_refused():
    from muninn.practice import validate_records

    assert validate_records([offer_record("x", "reserved"), offer_record("y", "settled")]) == []
    errors = validate_records([offer_record("x", "reserved"), offer_record("y", "submitted")])
    assert errors == ["two live offers own check o1 of target t1"]


def test_a_failed_recall_is_only_ever_forgotten_never_hard():
    from muninn.practice import RATEABLE

    assert {"independent": {"again", "hard", "good", "easy"}, "error": {"again"}} == RATEABLE


def test_an_exercises_full_cost_counts_setup_answering_and_feedback():
    from muninn.practice import full_cost

    assert full_cost({"expected_seconds": {"setup": 10, "answer": 90, "feedback": 30}}) == 130
