import pytest

from muninn.content import DraftOutline
from muninn.evidence import AssessmentOutput, check_assessment, project, qualify
from tests.drafts import CONNECTION_ERROR, TWO_CAUSES, assessment, hypothesis, outline, question

ANSWER = "It has to be sorted. Each comparison throws away half, so about log2(n) steps."

# The exercise as Content stores it: criteria c1..c3; c1 covers t1/r1, c2 covers t2/r1,
# c3 covers t2/r2 (see tests/drafts.py).
EXERCISE = {
    "criteria": [
        {
            "id": "c1",
            "covers": [
                {"target": {"kind": "target", "id": "t1", "revision": 1}, "requirement_ids": ["r1"]}
            ],
        },
        {
            "id": "c2",
            "covers": [
                {"target": {"kind": "target", "id": "t2", "revision": 1}, "requirement_ids": ["r1"]}
            ],
        },
        {
            "id": "c3",
            "covers": [
                {"target": {"kind": "target", "id": "t2", "revision": 1}, "requirement_ids": ["r2"]}
            ],
        },
    ]
}
T1_REQUIREMENTS = ["r1"]
T2_REQUIREMENTS = ["r1", "r2"]
QUOTES = {"c1": ["It has to be sorted."], "c2": ["throws away half"], "c3": ["about log2(n) steps"]}


def output(outcomes, quotes=QUOTES):
    return AssessmentOutput.model_validate(
        assessment(
            outcomes,
            {k: quotes.get(k, []) for k in outcomes if outcomes[k] in ("demonstrated", "error")},
        )
    )


def all_demonstrated():
    return output({"c1": "demonstrated", "c2": "demonstrated", "c3": "demonstrated"})


def test_the_drafts_fixture_is_still_a_valid_outline():
    DraftOutline.model_validate(outline())


def test_a_complete_quoted_assessment_is_valid():
    assert check_assessment(all_demonstrated(), ["c1", "c2", "c3"], ANSWER) == []


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (assessment({"c1": "demonstrated", "c2": "demonstrated"}, QUOTES), "c3 was not assessed"),
        (
            assessment(
                {"c1": "demonstrated", "c2": "demonstrated", "c3": "demonstrated", "c9": "error"},
                QUOTES | {"c9": ["x"]},
            ),
            "unknown criterion c9",
        ),
        (
            assessment(
                {"c1": "demonstrated", "c2": "demonstrated", "c3": "demonstrated"},
                {"c1": [], "c2": QUOTES["c2"], "c3": QUOTES["c3"]},
            ),
            "c1 needs a quote",
        ),
        (
            assessment(
                {"c1": "demonstrated", "c2": "demonstrated", "c3": "demonstrated"},
                QUOTES | {"c1": ["It must be ordered."]},
            ),
            "not in the answer",
        ),
        (
            assessment({"c1": "not_shown", "c2": "demonstrated", "c3": "demonstrated"}, QUOTES),
            "not_shown with a quote",
        ),
    ],
    ids=[
        "missing-criterion",
        "unknown-criterion",
        "unquoted-judgment",
        "invented-quote",
        "quoted-absence",
    ],
)
def test_an_assessment_that_breaks_the_protocol_is_refused(raw, expected):
    errors = check_assessment(AssessmentOutput.model_validate(raw), ["c1", "c2", "c3"], ANSWER)
    assert any(expected in e for e in errors), errors


def v2_errors(outcomes=CONNECTION_ERROR, **extra):
    raw = assessment(
        outcomes,
        {k: QUOTES[k] for k, v in outcomes.items() if v in ("demonstrated", "error")},
        **extra,
    )
    return check_assessment(AssessmentOutput.model_validate(raw), ["c1", "c2", "c3"], ANSWER)


def test_competing_hypotheses_and_a_discriminating_question_are_valid():
    asked = question(["c3"], demonstrated=("teach", "h2"), error=("teach", "h1"))
    assert v2_errors(hypotheses=TWO_CAUSES, question=asked) == []


@pytest.mark.parametrize(
    ("extra", "expected"),
    [
        ({"misread": ["c1"]}, "misread c1 must be judged error"),
        ({"hypotheses": [hypothesis("h1", ["c1"], "x")]}, "explains c1, which was demonstrated"),
        ({"hypotheses": [hypothesis("h1", ["c9"], "x")]}, "unknown criterion c9"),
        ({"question": question(["c1"])}, "asks again about c1, which was demonstrated"),
        ({"question": question(["c3"], error=("resolve", None))}, "error branch must teach"),
        (
            {"question": question(["c3"], inconclusive=("teach", "h1"))},
            "inconclusive branch must stay uncertain",
        ),
        ({"question": question(["c3"], error=("teach", "h7"))}, "unknown hypothesis h7"),
    ],
    ids=[
        "misread-not-error",
        "explains-success",
        "explains-unknown",
        "asks-about-success",
        "error-resolves",
        "inconclusive-teaches",
        "unknown-hypothesis",
    ],
)
def test_a_diagnosis_that_breaks_the_protocol_is_refused(extra, expected):
    errors = v2_errors(**extra)
    assert any(expected in e for e in errors), errors


def test_a_misread_needs_sound_reasoning_elsewhere_in_the_answer():
    outcomes = {"c1": "not_shown", "c2": "not_shown", "c3": "error"}
    errors = v2_errors(outcomes, misread=["c3"])
    assert any("no demonstrated part" in e for e in errors), errors


def labels(out, assisted=(), unconfirmed=()):
    observations = project(EXERCISE, out, assisted=set(assisted), unconfirmed=set(unconfirmed))
    return (
        qualify(T1_REQUIREMENTS, observations["t1"]).label,
        qualify(T2_REQUIREMENTS, observations["t2"]).label,
    )


def test_all_criteria_demonstrated_without_help_is_independent():
    assert labels(all_demonstrated()) == ("independent", "independent")


def test_help_on_one_criterion_only_affects_the_targets_it_covers():
    assert labels(all_demonstrated(), assisted={"c2"}) == ("independent", "helped")


def test_a_hint_that_may_have_been_seen_leaves_independence_unknown():
    assert labels(all_demonstrated(), unconfirmed={"c2"}) == ("independent", "unresolved")


def test_not_shown_or_cannot_judge_is_unresolved_never_an_error():
    out = output({"c1": "cannot_judge", "c2": "demonstrated", "c3": "not_shown"})
    assert labels(out) == ("unresolved", "unresolved")


def test_a_connection_error_keeps_the_demonstrated_part():
    out = output({"c1": "demonstrated", "c2": "demonstrated", "c3": "error"})
    assert labels(out) == ("independent", "error")


def test_a_supported_misread_is_not_counted_as_an_error():
    observations = project(
        EXERCISE, output(CONNECTION_ERROR), assisted=set(), unconfirmed=set(), misread={"c3"}
    )
    t2 = qualify(T2_REQUIREMENTS, observations["t2"])
    assert t2.label == "unresolved"
    assert "misread" in t2.reasons[0]
    assert [o["misread"] for o in observations["t2"]] == [False, True]


def scoped(outcomes, assisted=(), unconfirmed=(), misread=()):
    from muninn.evidence import scope_outcome

    projected = project(
        EXERCISE,
        output(outcomes),
        assisted=set(assisted),
        unconfirmed=set(unconfirmed),
        misread=set(misread),
    )
    observations = [{**o, "target_id": t} for t, obs in projected.items() for o in obs]
    t2_r2 = [{"target": {"kind": "target", "id": "t2", "revision": 1}, "requirement_ids": ["r2"]}]
    return scope_outcome(observations, t2_r2), scope_outcome(observations)


def test_a_scoped_outcome_looks_only_at_the_repaired_requirement():
    assert scoped(CONNECTION_ERROR) == ("error", "error")
    assert scoped({"c1": "error", "c2": "demonstrated", "c3": "demonstrated"}) == (
        "demonstrated",
        "error",
    )
    assert scoped(CONNECTION_ERROR | {"c3": "demonstrated"}, assisted={"c3"})[0] == "helped"
    assert scoped(CONNECTION_ERROR | {"c3": "demonstrated"}, unconfirmed={"c3"})[0] == (
        "inconclusive"
    )
    assert scoped(CONNECTION_ERROR, misread={"c3"})[0] == "inconclusive"
    assert scoped(CONNECTION_ERROR | {"c3": "not_shown"})[0] == "inconclusive"
