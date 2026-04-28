from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from glassbox.storage import Storage

ROOT = Path(__file__).resolve().parents[1]


def _run_example(script_name: str, tmp_path: Path, env: dict[str, str] | None = None):
    run_env = os.environ.copy()
    run_env.pop("OPENAI_API_KEY", None)
    run_env.pop("ANTHROPIC_API_KEY", None)
    if env:
        run_env.update(env)

    return subprocess.run(
        [sys.executable, str(ROOT / "examples" / script_name)],
        cwd=tmp_path,
        env=run_env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_simple_tracked_app_creates_a_completed_run_without_api_keys(tmp_path: Path) -> None:
    result = _run_example("simple_tracked_app.py", tmp_path)

    assert result.returncode == 0, result.stderr
    assert "Recorded run in" in result.stdout
    assert "python3 -m glassbox view --db glassbox.db --port 4747" in result.stdout

    storage = Storage(tmp_path / "glassbox.db")
    try:
        runs = storage.list_runs()
        assert len(runs) == 1
        assert runs[0]["project_name"] == "simple-tracked-app"
        assert runs[0]["status"] == "completed"
        assert "example" in runs[0]["tags"]

        events = storage.list_events(runs[0]["id"])
        event_names = {event["name"] for event in events}
        assert {"build_prompt", "score_candidate", "candidate_scored"} <= event_names
    finally:
        storage.close()


def test_simple_openai_app_explains_missing_api_key(tmp_path: Path) -> None:
    result = _run_example("simple_openai_app.py", tmp_path)

    assert result.returncode == 0
    assert "OPENAI_API_KEY is not set" in result.stdout
    assert "export OPENAI_API_KEY=" in result.stdout
    assert not (tmp_path / "glassbox.db").exists()


def test_simple_anthropic_app_explains_missing_api_key(tmp_path: Path) -> None:
    result = _run_example("simple_anthropic_app.py", tmp_path)

    assert result.returncode == 0
    assert "ANTHROPIC_API_KEY is not set" in result.stdout
    assert "export ANTHROPIC_API_KEY=" in result.stdout
    assert not (tmp_path / "glassbox.db").exists()
