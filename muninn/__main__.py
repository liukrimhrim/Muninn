"""Run the local learning app: ``uv run python -m muninn [--data DIR] [--port N]``."""

import argparse
from pathlib import Path

import uvicorn

from muninn.web import create_app


def main() -> None:
    """Serve one learner's library on localhost."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data", help="directory holding the library store")
    parser.add_argument("--port", type=int, default=8770)
    args = parser.parse_args()
    uvicorn.run(create_app(Path(args.data)), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
