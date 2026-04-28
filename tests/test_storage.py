from __future__ import annotations


def test_create_run_writes_readable_running_run(storage) -> None:
    run_id = storage.create_run(project_name="demo-app", tags=["local", "phase-1"])

    run = storage.get_run(run_id)

    assert run["id"] == run_id
    assert run["project_name"] == "demo-app"
    assert run["status"] == "running"
    assert run["runtime_language"] == "python"
    assert run["ended_at"] is None
    assert run["tags"] == ["local", "phase-1"]


def test_complete_run_marks_run_completed(storage) -> None:
    run_id = storage.create_run(project_name="demo-app")

    storage.complete_run(run_id)

    run = storage.get_run(run_id)
    assert run["status"] == "completed"
    assert run["ended_at"] is not None


def test_fail_run_marks_run_failed(storage) -> None:
    run_id = storage.create_run(project_name="demo-app")

    storage.fail_run(run_id)

    run = storage.get_run(run_id)
    assert run["status"] == "failed"
    assert run["ended_at"] is not None


def test_insert_child_events_preserves_parent_relationship(storage) -> None:
    run_id = storage.create_run(project_name="demo-app")
    parent_id = storage.insert_event(run_id, event_type="function", name="parent")
    child_id = storage.insert_event(
        run_id,
        event_type="log",
        name="child",
        parent_id=parent_id,
        status="completed",
        data={"answer": 42},
    )

    events = storage.list_events(run_id)

    assert [event["id"] for event in events] == [parent_id, child_id]
    assert events[1]["parent_id"] == parent_id
    assert events[1]["data"] == {"answer": 42}
    assert events[1]["status"] == "completed"


def test_insert_ai_call_details(storage) -> None:
    run_id = storage.create_run(project_name="demo-app")
    event_id = storage.insert_event(run_id, event_type="ai_call", name="openai.chat")

    storage.insert_ai_call(
        event_id,
        provider="openai",
        model="gpt-test",
        messages=[{"role": "user", "content": "Hello"}],
        response_text="Hi",
        input_tokens=5,
        output_tokens=7,
        cost_usd=0.0012,
    )

    ai_call = storage.get_ai_call(event_id)

    assert ai_call["event_id"] == event_id
    assert ai_call["provider"] == "openai"
    assert ai_call["model"] == "gpt-test"
    assert ai_call["messages"] == [{"role": "user", "content": "Hello"}]
    assert ai_call["response_text"] == "Hi"
    assert ai_call["input_tokens"] == 5
    assert ai_call["output_tokens"] == 7
    assert ai_call["cost_usd"] == 0.0012
