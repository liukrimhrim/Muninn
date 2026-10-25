"""Run the local learning app: ``uv run python -m muninn [--data D] [--port N] [--provider P]``."""

import argparse
import os
from pathlib import Path

import uvicorn

from muninn.web import create_app
from muninn.workflows import choose_provider


def main() -> None:
    """Serve one learner's library on localhost."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data", help="directory holding the library store")
    parser.add_argument("--port", type=int, default=8770)
    parser.add_argument(
        "--provider",
        choices=["anthropic", "claude-code"],
        default=os.environ.get("MUNINN_PROVIDER"),
        help="model access: the Anthropic API (needs ANTHROPIC_API_KEY) or your Claude Code "
        "login (default: the API when a key is set, else Claude Code)",
    )
    args = parser.parse_args()
    provider = choose_provider(args.provider)
    print(f"model access: {type(provider).__name__} ({provider.model})")  # noqa: T201
    uvicorn.run(create_app(Path(args.data), provider=provider), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
