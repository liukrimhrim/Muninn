"""Scripted model outputs shared by tests (saved outputs, not live judgments)."""

from typing import Any

SOURCE = (
    "Binary search finds a target in a sorted array. Each step compares the target with "
    "the middle element and discards the half that cannot contain it, so the search takes "
    "about log2(n) comparisons."
)


def outline() -> dict[str, Any]:
    """Return a valid drafted outline: one fact and one connected explanation."""
    return {
        "title": "Binary search",
        "purpose": "Explain why binary search is fast",
        "purpose_was_inferred": False,
        "knowledge": [
            {
                "key": "k1",
                "form": "fact",
                "statement": "Binary search only works on a sorted array.",
                "scope": "Searching arrays",
                "quotes": ["Binary search finds a target in a sorted array."],
                "depends_on": [],
            },
            {
                "key": "k2",
                "form": "relation",
                "statement": "Because each comparison discards the half that cannot contain the "
                "target, the search needs only about log2(n) comparisons.",
                "scope": "Sorted arrays of n elements",
                "quotes": [
                    (
                        "discards the half that cannot contain it, so the search takes about "
                        "log2(n) comparisons"
                    )
                ],
                "depends_on": [{"key": "k1", "role": "holds only when"}],
            },
        ],
        "targets": [
            {
                "key": "t1",
                "knowledge_keys": ["k1"],
                "action": "State what binary search requires of the array",
                "mode": "recall",
                "conditions": ["from memory"],
                "requirements": [
                    {"key": "r1", "statement": "Names sorted order", "knowledge_keys": ["k1"]}
                ],
            },
            {
                "key": "t2",
                "knowledge_keys": ["k1", "k2"],
                "action": "Explain why binary search needs only about log2(n) comparisons",
                "mode": "explain",
                "conditions": ["from memory"],
                "requirements": [
                    {
                        "key": "r1",
                        "statement": "Each comparison discards half of the remaining range",
                        "knowledge_keys": ["k2"],
                    },
                    {
                        "key": "r2",
                        "statement": "Repeated halving of n takes about log2(n) steps",
                        "knowledge_keys": ["k2"],
                    },
                ],
            },
        ],
        "sections": [{"title": "Binary search", "target_keys": ["t1", "t2"]}],
        "exercises": [
            {
                "prompt": "What must be true of an array before you can binary-search it, and "
                "why does the search need only about log2(n) comparisons?",
                "criteria": [
                    {
                        "key": "c1",
                        "requirement": "States that the array must be sorted",
                        "covers": [{"target_key": "t1", "requirement_keys": ["r1"]}],
                    },
                    {
                        "key": "c2",
                        "requirement": "Explains that each comparison discards half of the "
                        "remaining range (any equivalent wording)",
                        "covers": [{"target_key": "t2", "requirement_keys": ["r1"]}],
                    },
                    {
                        "key": "c3",
                        "requirement": "Connects repeated halving to about log2(n) comparisons",
                        "covers": [{"target_key": "t2", "requirement_keys": ["r2"]}],
                    },
                ],
                "reference_response": "The array must be sorted. Each comparison with the "
                "middle element rules out half of what remains, and n can be halved only "
                "about log2(n) times.",
                "hints": [
                    {"text": "Think about what one comparison rules out.", "criterion_keys": ["c2"]}
                ],
                "expected_seconds": {"setup": 10, "answer": 90, "feedback": 30},
            }
        ],
        "omitted": [],
        "doubts": [],
    }


def assessment(
    outcomes: dict[str, str],
    quotes: dict[str, list[str]] | None = None,
    *,
    misread: list[str] | None = None,
    hypotheses: list[dict[str, Any]] | None = None,
    question: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return an assessor output for criteria c1..c3 of the outline's exercise."""
    quotes = quotes or {}
    return {
        "observations": [
            {
                "criterion_key": key,
                "outcome": outcome,
                "quotes": quotes.get(key, []),
                "reason": f"{key} judged {outcome}",
            }
            for key, outcome in outcomes.items()
        ],
        "misread_criterion_keys": misread or [],
        "hypotheses": hypotheses or [],
        "question": question,
        "explanation": "Feedback for the learner.",
    }


def hypothesis(key: str, criteria: list[str], practice: str) -> dict[str, Any]:
    """Return one competing explanation of the judged criteria."""
    return {"key": key, "criterion_keys": criteria, "cause": f"cause {key}", "practice": practice}


def question(
    about: list[str],
    *,
    demonstrated: tuple[str, str | None] = ("resolve", None),
    error: tuple[str, str | None] = ("teach", "h1"),
    inconclusive: tuple[str, str | None] = ("still_uncertain", None),
    prompt: str = "With 32 candidates, list the remaining counts and label each halving.",
) -> dict[str, Any]:
    """Return a proposed clarification question with one criterion per original criterion."""
    branches = {"demonstrated": demonstrated, "error": error, "inconclusive": inconclusive}
    return {
        "prompt": prompt,
        "criteria": [
            {"key": f"q{n}", "requirement": f"Re-shows {c}", "about_criterion_key": c}
            for n, c in enumerate(about, 1)
        ],
        "reference_response": "32, 16, 8, 4, 2, 1: five halvings.",
        "expected_seconds": 60,
        "branches": [
            {"outcome": outcome, "next": nxt, "hypothesis_key": key, "why": f"{outcome} → {nxt}"}
            for outcome, (nxt, key) in branches.items()
        ],
    }


def teaching(
    approach: str = "worked example: reverse the halving sequence",
    quotes: list[str] | None = None,
) -> dict[str, Any]:
    """Return a teaching intervention for the connection between halving and log2(n)."""
    return {
        "content": f"{approach.capitalize()}. Six doublings take 1 to 64, so six halvings "
        "take 64 back to 1. In general, n/2^k = 1 when k = log2(n): the count of halvings is "
        "the exponent.",
        "approach": approach,
        "derivation": "n/2^k = 1 gives 2^k = n, so k = log2(n).",
        "source_quotes": ["discards the half that cannot contain it"] if quotes is None else quotes,
    }


def variant(
    prompt: str = "A sorted list has 128 names. What must hold before you binary-search it, "
    "and why do you need about 7 comparisons?",
    kind: str = "new_instance",
) -> dict[str, Any]:
    """Return a fresh variant of the outline's exercise; targets are keyed T1, T2."""
    return {
        "prompt": prompt,
        "criteria": [
            {
                "key": "c1",
                "requirement": "States that the list must be sorted",
                "covers": [{"target_key": "T1", "requirement_keys": ["r1"]}],
            },
            {
                "key": "c2",
                "requirement": "Explains that each comparison discards half of what remains",
                "covers": [{"target_key": "T2", "requirement_keys": ["r1"]}],
            },
            {
                "key": "c3",
                "requirement": "Connects 7 halvings of 128 to log2(128) = 7",
                "covers": [{"target_key": "T2", "requirement_keys": ["r2"]}],
            },
        ],
        "reference_response": "It must be sorted; each comparison halves the rest, and 128 "
        "halves to 1 in 7 steps because 2^7 = 128.",
        "hints": [],
        "expected_seconds": {"setup": 10, "answer": 90, "feedback": 30},
        "variation_kind": kind,
        "changed": ["list size 64 → 128", "names instead of numbers"],
        "held_fixed": ["sortedness condition", "halving-to-exponent connection"],
        "old_answer_insufficient": "The earlier count of six no longer fits; 128 needs seven.",
    }


ANSWER = "It must be sorted. Each comparison throws away half, so it takes about log2(n) steps."
QUOTES = {"c1": ["It must be sorted."], "c2": ["throws away half"], "c3": ["about log2(n) steps"]}
CONNECTION_ERROR = {"c1": "demonstrated", "c2": "demonstrated", "c3": "error"}
OMITTED = {"c1": "demonstrated", "c2": "demonstrated", "c3": "not_shown"}
ALL_SHOWN = {"c1": "demonstrated", "c2": "demonstrated", "c3": "demonstrated"}
TWO_CAUSES = [
    hypothesis("h1", ["c3"], "practice repeated halving"),
    hypothesis("h2", ["c3"], "explain why the count is the exponent"),
]


def judged(outcomes: dict[str, str], **extra: Any) -> dict[str, Any]:
    """Return an assessment of ``ANSWER`` quoting it for every demonstrated or erred part."""
    shown = {k: QUOTES[k] for k, v in outcomes.items() if v in ("demonstrated", "error")}
    return assessment(outcomes, shown, **extra)
