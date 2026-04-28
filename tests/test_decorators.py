from __future__ import annotations

import pytest

import glassbox
from glassbox.context import reset_context_for_tests


def setup_function() -> None:
    reset_context_for_tests()


def teardown_function() -> None:
    reset_context_for_tests()


def test_track_captures_sync_function_return_and_duration(temp_db_path) -> None:
    context = glassbox.init(db_path=temp_db_path, project_name="demo-app")

    @glassbox.track
    def compute() -> str:
        return "x" * 800

    result = compute()
    events = context.storage.list_events(context.run_id)

    assert result == "x" * 800
    assert len(events) == 1
    assert events[0]["event_type"] == "function"
    assert events[0]["name"] == "compute"
    assert events[0]["status"] == "completed"
    assert events[0]["duration_ms"] is not None
    assert len(events[0]["data"]["return_value"]) < 800


def test_track_redacts_function_args_kwargs_and_return_value(temp_db_path) -> None:
    context = glassbox.init(db_path=temp_db_path, project_name="demo-app")

    @glassbox.track
    def handle(payload: dict, *, api_key: str) -> dict:
        return {"token": api_key, "safe": payload["safe"]}

    handle(
        {"safe": "visible", "password": "correct-horse-battery-staple"},
        api_key="sk-proj-abcdefghijklmnopqrstuvwxyz123456",
    )

    events = context.storage.list_events(context.run_id)
    assert events[0]["data"]["args"] == [
        {"safe": "visible", "password": "[REDACTED]"}
    ]
    assert events[0]["data"]["kwargs"] == {"api_key": "[REDACTED]"}
    assert events[0]["data"]["return_value"] == {
        "token": "[REDACTED]",
        "safe": "visible",
    }


def test_track_captures_exception_and_reraises(temp_db_path) -> None:
    context = glassbox.init(db_path=temp_db_path, project_name="demo-app")

    @glassbox.track
    def explode() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        explode()

    events = context.storage.list_events(context.run_id)
    assert events[0]["status"] == "failed"
    assert events[0]["error_message"] == "boom"


def test_nested_tracked_functions_preserve_parent_child_relationship(temp_db_path) -> None:
    context = glassbox.init(db_path=temp_db_path, project_name="demo-app")

    @glassbox.track
    def outer() -> str:
        return inner()

    @glassbox.track
    def inner() -> str:
        return "done"

    assert outer() == "done"

    events = context.storage.list_events(context.run_id)
    outer_event = next(event for event in events if event["name"] == "outer")
    inner_event = next(event for event in events if event["name"] == "inner")
    assert inner_event["parent_id"] == outer_event["id"]


def test_log_writes_custom_event(temp_db_path) -> None:
    context = glassbox.init(db_path=temp_db_path, project_name="demo-app")

    glassbox.log("thing_happened", {"count": 3})

    events = context.storage.list_events(context.run_id)
    assert events[0]["event_type"] == "log"
    assert events[0]["name"] == "thing_happened"
    assert events[0]["status"] == "completed"
    assert events[0]["data"] == {"count": 3}


def test_tag_updates_run_tags_without_duplicates(temp_db_path) -> None:
    context = glassbox.init(db_path=temp_db_path, project_name="demo-app")

    glassbox.tag("experiment-a")
    glassbox.tag("experiment-a")
    glassbox.tag("local")

    run = context.storage.get_run(context.run_id)
    assert run["tags"] == ["experiment-a", "local"]
