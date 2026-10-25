"""Serve the app with a scripted model for checking the UI without an API key.

``uv run python -m tests.dev_server`` then paste ``tests.drafts.SOURCE`` as material.
The scripted assessor quotes the answer's first words; it checks screens and flows,
never judgment quality. The larger task always shows a connection error with two
possible causes, so the clarification → teaching → fresh check flow can be walked.
Words in an answer pick other paths: "misread" (a supported misread of the task) and,
on the clarification, "not sure" (the concern ends still uncertain).
"""

import json
import tempfile
from pathlib import Path
from typing import Any

import uvicorn

from muninn.web import create_app
from muninn.workflows import OUTPUTS, ProviderResult
from tests.drafts import hypothesis, outline, question, teaching, variant


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


class ScreenProvider:
    model = "scripted-ui-check"

    def __init__(self) -> None:
        self.parameters: dict[str, Any] = {}

    def complete(self, request: Any) -> ProviderResult:
        name = request.protocol["name"]
        output = {
            "draft-initial-outline": outline,
            "author-teaching": teaching,
            "author-variant": variant,
        }.get(name, lambda: assess(request.user))()
        parsed = OUTPUTS[name].model_validate(output)
        return ProviderResult(output=parsed, raw=json.dumps(output), model=self.model)


if __name__ == "__main__":
    data = Path(tempfile.mkdtemp(prefix="muninn-ui-"))
    uvicorn.run(create_app(data, provider=ScreenProvider()), host="127.0.0.1", port=8766)
