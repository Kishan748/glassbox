from __future__ import annotations

import sqlite3
import sys

import glassbox
import glassbox.context as runtime_context
from glassbox.context import reset_context_for_tests


def setup_function() -> None:
    reset_context_for_tests()


def teardown_function() -> None:
    reset_context_for_tests()


def test_init_creates_running_run(temp_db_path) -> None:
    context = glassbox.init(db_path=temp_db_path, project_name="demo-app")

    run = context.storage.get_run(context.run_id)

    assert run["project_name"] == "demo-app"
    assert run["status"] == "running"
    assert run["cwd"] is not None


def test_init_twice_reuses_active_context(temp_db_path) -> None:
    first = glassbox.init(db_path=temp_db_path, project_name="demo-app")
    second = glassbox.init(db_path=temp_db_path, project_name="demo-app")

    with sqlite3.connect(temp_db_path) as connection:
        run_count = connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0]

    assert second is first
    assert run_count == 1


def test_context_close_completes_run(temp_db_path) -> None:
    context = glassbox.init(db_path=temp_db_path, project_name="demo-app")

    context.close()

    run = context.storage.get_run(context.run_id)
    assert run["status"] == "completed"
    assert run["ended_at"] is not None


def test_excepthook_marks_active_run_failed(temp_db_path, monkeypatch) -> None:
    context = glassbox.init(db_path=temp_db_path, project_name="demo-app")
    monkeypatch.setattr(runtime_context, "_previous_excepthook", lambda *_args: None)

    exc = RuntimeError("crash")
    sys.excepthook(type(exc), exc, None)

    run = context.storage.get_run(context.run_id)
    assert run["status"] == "failed"
    assert run["ended_at"] is not None
