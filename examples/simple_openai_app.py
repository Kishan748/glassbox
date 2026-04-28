"""OpenAI Glassbox example with a friendly no-key path."""

from __future__ import annotations

import os
from pathlib import Path

import glassbox


def main() -> int:
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set.")
        print("Set it, install the OpenAI SDK, then run this example again:")
        print("  export OPENAI_API_KEY=...")
        print("  python3 -m pip install openai")
        print("  python3 examples/simple_openai_app.py")
        return 0

    db_path = Path("glassbox.db")
    try:
        from openai import OpenAI
    except ImportError:
        print("The OpenAI SDK is not installed.")
        print("Install it with: python3 -m pip install openai")
        return 1

    with glassbox.init(
        db_path=db_path,
        project_name="simple-openai-app",
        capture_openai=True,
    ):
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": "Say one sentence about why local debugging traces help.",
                }
            ],
            max_tokens=80,
        )
        print(response.choices[0].message.content)

    print(f"Recorded run in {db_path}")
    print("Inspect it with:")
    print("  python3 -m glassbox view --db glassbox.db --port 4747")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
