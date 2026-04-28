"""Anthropic Glassbox example with a friendly no-key path."""

from __future__ import annotations

import os
from pathlib import Path

import glassbox


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set.")
        print("Set it, install the Anthropic SDK, then run this example again:")
        print("  export ANTHROPIC_API_KEY=...")
        print("  python3 -m pip install anthropic")
        print("  python3 examples/simple_anthropic_app.py")
        return 0

    db_path = Path("glassbox.db")
    try:
        from anthropic import Anthropic
    except ImportError:
        print("The Anthropic SDK is not installed.")
        print("Install it with: python3 -m pip install anthropic")
        return 1

    with glassbox.init(
        db_path=db_path,
        project_name="simple-anthropic-app",
        capture_anthropic=True,
    ):
        client = Anthropic()
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=80,
            messages=[
                {
                    "role": "user",
                    "content": "Say one sentence about why local debugging traces help.",
                }
            ],
        )
        print(response.content[0].text)

    print(f"Recorded run in {db_path}")
    print("Inspect it with:")
    print("  python3 -m glassbox view --db glassbox.db --port 4747")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
