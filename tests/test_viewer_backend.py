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


def test_run_events_include_ai_call_detail(temp_db_path) -> None:
    storage = Storage(temp_db_path)
    run_id = storage.create_run(project_name="demo-app")
    event_id = storage.insert_event(
        run_id,
        event_type="ai_call",
        name="openai.chat.completions.create",
        status="completed",
    )
    storage.insert_ai_call(
        event_id,
        provider="openai",
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}],
        response_text="Hi",
        input_tokens=10,
        output_tokens=5,
        cost_usd=0.001,
    )
    storage.close()
    client = TestClient(create_app(db_path=temp_db_path))

    response = client.get(f"/api/runs/{run_id}/events")

    assert response.status_code == 200
    event = response.json()["events"][0]
    assert event["ai_call"]["provider"] == "openai"
    assert event["ai_call"]["messages"] == [{"role": "user", "content": "Hello"}]


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


def test_viewer_static_assets_are_served(tmp_path, temp_db_path) -> None:
    static_dir = tmp_path / "static"
    assets_dir = static_dir / "assets"
    assets_dir.mkdir(parents=True)
    (static_dir / "index.html").write_text(
        '<div id="root"></div><script src="/assets/app.js"></script>',
        encoding="utf-8",
    )
    (assets_dir / "app.js").write_text("console.log('glassbox')", encoding="utf-8")
    client = TestClient(create_app(db_path=temp_db_path, static_dir=static_dir))

    index_response = client.get("/")
    asset_response = client.get("/assets/app.js")
    frontend_route_response = client.get("/runs")

    assert index_response.status_code == 200
    assert '<div id="root"></div>' in index_response.text
    assert asset_response.status_code == 200
    assert "console.log" in asset_response.text
    assert frontend_route_response.status_code == 200
    assert '<div id="root"></div>' in frontend_route_response.text


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
