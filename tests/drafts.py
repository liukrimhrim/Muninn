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
                "existing": [],
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
                "existing": [],
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


VOCAB_SOURCE = "In the invented language Tarvi, the word mavo means blue and sel means stone."


def vocab_outline() -> dict[str, Any]:
    """Return a drafted outline for an invented association (a second, unrelated subject)."""
    return {
        "title": "Tarvi words",
        "purpose": "Remember what mavo means",
        "purpose_was_inferred": False,
        "knowledge": [
            {
                "key": "k1",
                "form": "fact",
                "statement": "In Tarvi, mavo means blue.",
                "scope": "Tarvi vocabulary",
                "quotes": ["the word mavo means blue"],
                "depends_on": [],
                "existing": [],
            }
        ],
        "targets": [
            {
                "key": "t1",
                "knowledge_keys": ["k1"],
                "action": "Recall what mavo means",
                "mode": "recall",
                "conditions": ["from memory"],
                "requirements": [
                    {"key": "r1", "statement": "Gives the meaning blue", "knowledge_keys": ["k1"]}
                ],
            }
        ],
        "sections": [{"title": "Words", "target_keys": ["t1"]}],
        "exercises": [
            {
                "prompt": "In Tarvi, what does mavo mean?",
                "criteria": [
                    {
                        "key": "c1",
                        "requirement": "Answers blue",
                        "covers": [{"target_key": "t1", "requirement_keys": ["r1"]}],
                    }
                ],
                "reference_response": "Blue.",
                "hints": [],
                "expected_seconds": {"setup": 5, "answer": 10, "feedback": 5},
            }
        ],
        "omitted": [],
        "doubts": [],
    }


NOTES_SOURCE = (
    "Notes on searching. Binary search requires a sorted array. Each comparison halves what "
    "remains, so about log2(n) comparisons suffice. Linear search checks every element in turn."
)


def existing_keys(request: Any) -> dict[str, str]:
    """Read the existing-claim keys (statement -> key) the drafting packet listed."""
    listing = request.user.split("<existing_claims>\n", 1)[1].split("\n</existing_claims>", 1)[0]
    keys: dict[str, str] = {}
    for line in listing.splitlines():
        key, _, rest = line.partition(": ")
        keys[rest.rsplit(" (scope: ", 1)[0]] = key
    return keys


def notes_outline(
    request: Any, *, sorted_relation: str = "same", halving_relation: str = "same"
) -> dict[str, Any]:
    """Draft second material that repeats (or contradicts) the binary-search claims."""
    keys = existing_keys(request)
    return {
        "title": "Searching notes",
        "purpose": "Compare searching methods",
        "purpose_was_inferred": True,
        "knowledge": [
            {
                "key": "b1",
                "form": "fact",
                "statement": "Binary search requires a sorted array.",
                "scope": "Searching arrays",
                "quotes": ["Binary search requires a sorted array."],
                "depends_on": [],
                "existing": [
                    {
                        "key": keys["Binary search only works on a sorted array."],
                        "relation": sorted_relation,
                        "why": "the same requirement",
                    }
                ],
            },
            {
                "key": "b2",
                "form": "relation",
                "statement": "Halving at each comparison takes about log2(n) comparisons.",
                "scope": "Sorted arrays of n elements",
                "quotes": ["Each comparison halves what remains"],
                "depends_on": [{"key": "b1", "role": "holds only when"}],
                "existing": [
                    {
                        "key": keys[
                            "Because each comparison discards the half that cannot contain the "
                            "target, the search needs only about log2(n) comparisons."
                        ],
                        "relation": halving_relation,
                        "why": "the same halving argument",
                    }
                ],
            },
            {
                "key": "b3",
                "form": "fact",
                "statement": "Linear search checks every element in turn.",
                "scope": "Searching lists",
                "quotes": ["Linear search checks every element in turn."],
                "depends_on": [],
                "existing": [],
            },
        ],
        "targets": [
            {
                "key": "t1",
                "knowledge_keys": ["b1", "b2"],
                "action": "Explain when binary search needs about log2(n) comparisons",
                "mode": "explain",
                "conditions": ["from memory"],
                "requirements": [
                    {"key": "r1", "statement": "Names sorted order", "knowledge_keys": ["b1"]},
                    {
                        "key": "r2",
                        "statement": "Connects halving to log2(n)",
                        "knowledge_keys": ["b2"],
                    },
                ],
            },
            {
                "key": "t2",
                "knowledge_keys": ["b3"],
                "action": "State how linear search proceeds",
                "mode": "recall",
                "conditions": ["from memory"],
                "requirements": [
                    {"key": "r1", "statement": "Every element in turn", "knowledge_keys": ["b3"]}
                ],
            },
        ],
        "sections": [{"title": "Searching", "target_keys": ["t1", "t2"]}],
        "exercises": [
            {
                "prompt": "When does binary search need only about log2(n) comparisons?",
                "criteria": [
                    {
                        "key": "c1",
                        "requirement": "Sorted array, halving each time",
                        "covers": [{"target_key": "t1", "requirement_keys": ["r1", "r2"]}],
                    }
                ],
                "reference_response": "On a sorted array, because each comparison halves the rest.",
                "hints": [],
                "expected_seconds": {"setup": 5, "answer": 60, "feedback": 20},
            },
            {
                "prompt": "How does linear search look for an element?",
                "criteria": [
                    {
                        "key": "c1",
                        "requirement": "Checks every element in turn",
                        "covers": [{"target_key": "t2", "requirement_keys": ["r1"]}],
                    }
                ],
                "reference_response": "It checks every element in turn.",
                "hints": [],
                "expected_seconds": {"setup": 5, "answer": 20, "feedback": 10},
            },
        ],
        "omitted": [],
        "doubts": [],
    }


EXPLANATION = "Each comparison throws away half, so it takes about log2(n) steps."
EXPLANATION_QUOTES = {"c1": ["throws away half"], "c2": ["about log2(n) steps"]}


def explanation_outline() -> dict[str, Any]:
    """Return an outline with one connected-explanation goal and its own exercise."""
    drafted = outline()
    drafted["targets"] = [drafted["targets"][1]]
    drafted["sections"] = [{"title": "Binary search", "target_keys": ["t2"]}]
    drafted["exercises"] = [
        {
            "prompt": "Why does binary search on a sorted array need only about log2(n) "
            "comparisons?",
            "criteria": [
                {
                    "key": "c1",
                    "requirement": "Explains that each comparison discards half of the "
                    "remaining range",
                    "covers": [{"target_key": "t2", "requirement_keys": ["r1"]}],
                },
                {
                    "key": "c2",
                    "requirement": "Connects repeated halving to about log2(n) comparisons",
                    "covers": [{"target_key": "t2", "requirement_keys": ["r2"]}],
                },
            ],
            "reference_response": "Each comparison rules out half of what remains, and n can "
            "be halved only about log2(n) times.",
            "hints": [
                {"text": "Think about what one comparison rules out.", "criterion_keys": ["c1"]}
            ],
            "expected_seconds": {"setup": 10, "answer": 60, "feedback": 20},
        }
    ]
    return drafted


def explained(outcomes: dict[str, str]) -> dict[str, Any]:
    """Return an assessment of ``EXPLANATION`` for criteria c1, c2."""
    shown = {
        k: EXPLANATION_QUOTES[k] for k, v in outcomes.items() if v in ("demonstrated", "error")
    }
    return assessment(outcomes, shown)


def with_modes(drafted: dict[str, Any], *modes: str) -> dict[str, Any]:
    """Return the drafted outline with its targets' modes replaced, in order."""
    for target, mode in zip(drafted["targets"], modes, strict=True):
        target["mode"] = mode
    return drafted


def fresh_explanation() -> dict[str, Any]:
    """Return a fresh variant of ``explanation_outline``'s exercise (its target keyed T1)."""
    return {
        "prompt": "A sorted list has 128 names. Why do about 7 comparisons find any name?",
        "criteria": [
            {
                "key": "c1",
                "requirement": "Each comparison discards half of what remains",
                "covers": [{"target_key": "T1", "requirement_keys": ["r1"]}],
            },
            {
                "key": "c2",
                "requirement": "128 halves to 1 in 7 steps",
                "covers": [{"target_key": "T1", "requirement_keys": ["r2"]}],
            },
        ],
        "reference_response": "Each comparison halves the rest; 128 halves to 1 in 7 steps.",
        "hints": [],
        "expected_seconds": {"setup": 10, "answer": 60, "feedback": 20},
        "variation_kind": "new_instance",
        "changed": ["list size 128", "names"],
        "held_fixed": ["halving-to-exponent connection"],
        "old_answer_insufficient": "The earlier answer named no count for 128.",
    }
