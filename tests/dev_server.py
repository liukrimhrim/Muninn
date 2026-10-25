"""Serve the app with a scripted model for checking the UI without an API key.

``uv run python -m tests.dev_server`` then paste ``tests.drafts.SOURCE`` as material.
The scripted assessor quotes the answer's first words; it checks screens and flows,
never judgment quality. The larger task always shows a connection error with two
possible causes, so the clarification → teaching → fresh check flow can be walked.
Words in an answer pick other paths: "misread" (a supported misread of the task) and,
on the clarification, "not sure" (the concern ends still uncertain).

Slice 3: "This judgment is wrong" is reviewed as all criteria shown (a reason containing
"keep" leaves the judgment as it was). Material starting "Notes on searching"
(``tests.drafts.NOTES_SOURCE``) proposes reusing the binary-search claims, and
``tests.drafts.VOCAB_SOURCE`` adds an unrelated curriculum.

Slice 4: the store clock can be moved forward to cross due boundaries:
``curl -X POST 'http://127.0.0.1:8766/dev/clock?hours=25'``. The Tarvi exercise is a
recall item (FSRS): an answer containing "blue" is judged correct, anything else wrong.
"""

import json
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI

from muninn.library import utc
from muninn.web import create_app
from muninn.workflows import OUTPUTS, ProviderResult
from tests.drafts import (
    hypothesis,
    notes_outline,
    outline,
    question,
    teaching,
    variant,
    vocab_outline,
)


def judged(outcomes: dict[str, str], quote: str, **extra: Any) -> dict[str, Any]:
    return {
        "observations": [
            {
                "criterion_key": key,
                "outcome": outcome,
                "quotes": [quote] if outcome in ("demonstrated", "error") else [],
                "reason": "scripted",
            }
            for key, outcome in outcomes.items()
        ],
        "misread_criterion_keys": [],
        "hypotheses": [],
        "question": None,
        "explanation": "Scripted feedback for checking the screens.",
        **extra,
    }


def assess(user: str) -> dict[str, Any]:
    prompt = user.split("<prompt>\n", 1)[1].split("\n</prompt>", 1)[0]
    answer = user.split("<answer>\n", 1)[1].rsplit("\n</answer>", 1)[0]
    quote = answer[: min(len(answer), 12)]
    if "mavo" in prompt:
        return judged({"c1": "demonstrated" if "blue" in answer.lower() else "error"}, quote)
    if prompt.startswith("With 32 candidates"):
        if "not sure" in answer:
            return judged({"c1": "not_shown"}, quote)
        return judged({"c1": "demonstrated"}, quote)
    if prompt.startswith("A sorted list"):
        return judged({"c1": "demonstrated", "c2": "demonstrated", "c3": "demonstrated"}, quote)
    connection_error = {"c1": "demonstrated", "c2": "demonstrated", "c3": "error"}
    if "misread" in answer:
        return judged(connection_error, quote, misread_criterion_keys=["c3"])
    return judged(
        connection_error,
        quote,
        hypotheses=[
            hypothesis("h1", ["c3"], "practice repeated halving"),
            hypothesis("h2", ["c3"], "explain why the count of halvings is the exponent"),
        ],
        question=question(["c3"], demonstrated=("teach", "h2"), error=("teach", "h1")),
    )


def reassess(user: str) -> dict[str, Any]:
    answer = user.split("<answer>\n", 1)[1].split("\n</answer>", 1)[0]
    quote = answer[: min(len(answer), 12)]
    if "keep" in user.split("<learner_disputes_it>", 1)[1]:
        earlier = user.split("<earlier_judgment>\n", 1)[1].split("\nInterpretation:", 1)[0]
        outcomes: dict[str, str] = {}
        for line in earlier.splitlines():
            key, rest = line.split(": ", 1)
            outcomes[key] = rest.split(" — ", 1)[0]
        return judged(outcomes, quote)
    return judged({"c1": "demonstrated", "c2": "demonstrated", "c3": "demonstrated"}, quote)


def draft(request: Any) -> dict[str, Any]:
    if "Notes on searching" in request.user:
        return notes_outline(request)
    if "Tarvi" in request.user:
        return vocab_outline()
    return outline()


class ScreenProvider:
    model = "scripted-ui-check"

    def __init__(self) -> None:
        self.parameters: dict[str, Any] = {}

    def complete(self, request: Any) -> ProviderResult:
        name = request.protocol["name"]
        output = {
            "draft-initial-outline": lambda: draft(request),
            "author-teaching": teaching,
            "author-variant": variant,
            "reassess-answer": lambda: reassess(request.user),
        }.get(name, lambda: assess(request.user))()
        parsed = OUTPUTS[name].model_validate(output)
        return ProviderResult(output=parsed, raw=json.dumps(output), model=self.model)


class DevClock:
    """The real clock plus an offset the UI check can move forward."""

    def __init__(self) -> None:
        self.offset = timedelta()

    def __call__(self) -> datetime:
        return datetime.now(UTC) + self.offset


def dev_app(data: Path) -> FastAPI:
    clock = DevClock()
    outer = FastAPI()

    @outer.post("/dev/clock")
    def advance(hours: float = 0, minutes: float = 0) -> dict[str, str]:
        clock.offset += timedelta(hours=hours, minutes=minutes)
        return {"now": utc(clock())}

    outer.mount("/", create_app(data, provider=ScreenProvider(), clock=clock))
    return outer


if __name__ == "__main__":
    data = Path(tempfile.mkdtemp(prefix="muninn-ui-"))
    uvicorn.run(dev_app(data), host="127.0.0.1", port=8766)
