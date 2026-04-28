"""No-key Glassbox example: tracked functions, logs, and tags."""

from __future__ import annotations

from pathlib import Path

import glassbox


@glassbox.track
def build_prompt(topic: str) -> str:
    return f"Write one practical tip about {topic}."


@glassbox.track
def score_candidate(prompt: str) -> dict[str, int | str]:
    words = prompt.split()
    score = min(10, max(1, len(words)))
    return {"prompt": prompt, "score": score}


def main() -> int:
    db_path = Path("glassbox.db")
    context = glassbox.init(db_path=db_path, project_name="simple-tracked-app")
    try:
        glassbox.tag("example")
        prompt = build_prompt("local AI app debugging")
        candidate = score_candidate(prompt)
        glassbox.log("candidate_scored", candidate)
    finally:
        context.close()

    print(f"Recorded run in {db_path}")
    print("Inspect it with:")
    print("  python3 -m glassbox view --db glassbox.db --port 4747")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
