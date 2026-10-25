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
    outcomes: dict[str, str], quotes: dict[str, list[str]] | None = None
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
        "explanation": "Feedback for the learner.",
        "next": {"kind": "stop", "criterion_keys": [], "text": "Done.", "reason": "All judged."},
    }
