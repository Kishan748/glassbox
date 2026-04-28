from __future__ import annotations

from fastapi.testclient import TestClient

from glassbox.storage import Storage
from glassbox.viewer_backend import create_app


def test_stats_returns_run_and_event_counts(temp_db_path) -> None:
    run_id, _parent_id, _child_id = _create_run_with_events(temp_db_path)
    assert run_id
    client = TestClient(create_app(db_path=temp_db_path))

    response = client.get("/api/stats")

    assert response.status_code == 200
    assert response.json() == {
        "database_exists": True,
        "setup_required": False,
        "run_count": 1,
        "event_count": 2,
        "ai_call_count": 0,
    }


def test_runs_returns_recent_runs(temp_db_path) -> None:
    run_id, _parent_id, _child_id = _create_run_with_events(temp_db_path)
    client = TestClient(create_app(db_path=temp_db_path))

    response = client.get("/api/runs")

    assert response.status_code == 200
    assert response.json()["runs"][0]["id"] == run_id
    assert response.json()["runs"][0]["project_name"] == "demo-app"


def test_run_detail_returns_one_run(temp_db_path) -> None:
    run_id, _parent_id, _child_id = _create_run_with_events(temp_db_path)
    client = TestClient(create_app(db_path=temp_db_path))

    response = client.get(f"/api/runs/{run_id}")

    assert response.status_code == 200
    assert response.json()["run"]["id"] == run_id


def test_run_events_returns_event_tree(temp_db_path) -> None:
    run_id, parent_id, child_id = _create_run_with_events(temp_db_path)
    client = TestClient(create_app(db_path=temp_db_path))

    response = client.get(f"/api/runs/{run_id}/events")

    assert response.status_code == 200
    events = response.json()["events"]
    assert events[0]["id"] == parent_id
    assert events[0]["children"][0]["id"] == child_id


def test_missing_database_returns_friendly_setup_state(temp_db_path) -> None:
    client = TestClient(create_app(db_path=temp_db_path))

    response = client.get("/api/stats")

    assert response.status_code == 200
    assert response.json() == {
        "database_exists": False,
        "setup_required": True,
        "run_count": 0,
        "event_count": 0,
        "ai_call_count": 0,
    }


def test_missing_run_returns_404_with_useful_message(temp_db_path) -> None:
    _create_run_with_events(temp_db_path)
    client = TestClient(create_app(db_path=temp_db_path))

    response = client.get("/api/runs/missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "Run not found: missing"


def _create_run_with_events(temp_db_path):
    storage = Storage(temp_db_path)
    run_id = storage.create_run(project_name="demo-app")
    parent_id = storage.insert_event(
        run_id,
        event_type="function",
        name="parent",
        status="completed",
    )
    child_id = storage.insert_event(
        run_id,
        event_type="log",
        name="child",
        parent_id=parent_id,
        status="completed",
        data={"count": 3},
    )
    storage.complete_run(run_id)
    storage.close()
    return run_id, parent_id, child_id
