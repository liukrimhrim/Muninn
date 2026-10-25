"""Serve the app with a scripted model for checking the UI without an API key.

``uv run python -m tests.dev_server`` then paste ``tests.drafts.SOURCE`` as material.
The scripted assessor marks every criterion shown, quoting the answer's first words;
it checks screens and flows, never judgment quality.
"""

import json
import tempfile
from pathlib import Path

import uvicorn

from muninn.web import create_app
from muninn.workflows import OUTPUTS, ProviderResult
from tests.drafts import outline


class ScreenProvider:
    model = "scripted-ui-check"

    def __init__(self):
        self.parameters = {}

    def complete(self, request):
        if request.protocol["name"] == "draft-initial-outline":
            output = outline()
        else:
            answer = request.user.split("<answer>\n", 1)[1].rsplit("\n</answer>", 1)[0]
            quote = answer[: min(len(answer), 12)]
            output = {
                "observations": [
                    {
                        "criterion_key": f"c{n}",
                        "outcome": "demonstrated",
                        "quotes": [quote],
                        "reason": "scripted",
                    }
                    for n in (1, 2, 3)
                ],
                "explanation": "Scripted feedback for checking the screens.",
                "next": {
                    "kind": "stop",
                    "criterion_keys": [],
                    "text": "Done.",
                    "reason": "scripted",
                },
            }
        parsed = OUTPUTS[request.protocol["name"]].model_validate(output)
        return ProviderResult(output=parsed, raw=json.dumps(output), model=self.model)


if __name__ == "__main__":
    data = Path(tempfile.mkdtemp(prefix="muninn-ui-"))
    uvicorn.run(create_app(data, provider=ScreenProvider()), host="127.0.0.1", port=8766)
