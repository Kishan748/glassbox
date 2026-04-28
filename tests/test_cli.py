from __future__ import annotations

import json

import pytest

from glassbox.cli import main
from glassbox.storage import Storage


def test_cli_help(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    captured = capsys.readouterr()

    assert exc_info.value.code == 0
    assert "Local flight recorder" in captured.out


def test_doctor_outputs_diagnostics(capsys) -> None:
    result = main(["doctor"])

    captured = capsys.readouterr()

    assert result == 0
    assert "Glassbox diagnostics" in captured.out
    assert "python:" in captured.out


def test_doctor_outputs_cwd_db_path_and_sdk_availability(capsys, temp_db_path) -> None:
    result = main(["doctor", "--db", str(temp_db_path)])

    captured = capsys.readouterr()

    assert result == 0
    assert f"database: {temp_db_path}" in captured.out
    assert "cwd:" in captured.out
    assert "openai sdk:" in captured.out
    assert "anthropic sdk:" in captured.out


def test_runs_lists_recent_runs(capsys, temp_db_path) -> None:
    storage = Storage(temp_db_path)
    run_id = storage.create_run(project_name="demo-app", tags=["local"])
    storage.complete_run(run_id)
    storage.close()

    result = main(["runs", "--db", str(temp_db_path)])

    captured = capsys.readouterr()
    assert result == 0
    assert run_id in captured.out
    assert "demo-app" in captured.out
    assert "completed" in captured.out


def test_runs_empty_database_is_friendly(capsys, temp_db_path) -> None:
    result = main(["runs", "--db", str(temp_db_path)])

    captured = capsys.readouterr()
    assert result == 0
    assert "No runs found" in captured.out


def test_export_prints_json_for_run_and_events(capsys, temp_db_path) -> None:
    storage = Storage(temp_db_path)
    run_id = storage.create_run(project_name="demo-app")
    event_id = storage.insert_event(
        run_id,
        event_type="log",
        name="thing_happened",
        status="completed",
        data={"count": 3},
    )
    storage.complete_run(run_id)
    storage.close()

    result = main(["export", "--db", str(temp_db_path), "--run", run_id])

    captured = capsys.readouterr()
    exported = json.loads(captured.out)
    assert result == 0
    assert exported["run"]["id"] == run_id
    assert exported["events"][0]["id"] == event_id
    assert exported["events"][0]["data"] == {"count": 3}
