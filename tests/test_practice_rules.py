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
