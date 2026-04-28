"""FastAPI backend for the local Glassbox viewer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from glassbox.storage import Storage


def create_app(
    *,
    db_path: str | Path = "glassbox.db",
    static_dir: str | Path | None = None,
) -> FastAPI:
    db = Path(db_path)
    static_path = (
        Path(static_dir) if static_dir is not None else Path(__file__).parent / "viewer_static"
    )
    app = FastAPI(title="Glassbox Viewer API")

    @app.get("/api/stats")
    def stats() -> dict[str, int | bool]:
        if not db.exists():
            return _setup_state()

        storage = Storage(db)
        try:
            return {
                "database_exists": True,
                "setup_required": False,
                **storage.get_stats(),
            }
        finally:
            storage.close()

    @app.get("/api/runs")
    def runs() -> dict[str, Any]:
        if not db.exists():
            return {"setup_required": True, "runs": []}

        storage = Storage(db)
        try:
            return {"setup_required": False, "runs": storage.list_runs()}
        finally:
            storage.close()

    @app.get("/api/runs/{run_id}")
    def run_detail(run_id: str) -> dict[str, Any]:
        storage = _storage_or_404(db)
        try:
            return {"run": _get_run_or_404(storage, run_id)}
        finally:
            storage.close()

    @app.get("/api/runs/{run_id}/events")
    def run_events(run_id: str) -> dict[str, Any]:
        storage = _storage_or_404(db)
        try:
            _get_run_or_404(storage, run_id)
            return {
                "events": _build_event_tree(
                    storage.list_events(run_id),
                    storage.list_ai_calls_for_run(run_id),
                )
            }
        finally:
            storage.close()

    _mount_viewer_assets(app, static_path)
    return app


def _setup_state() -> dict[str, int | bool]:
    return {
        "database_exists": False,
        "setup_required": True,
        "run_count": 0,
        "event_count": 0,
        "ai_call_count": 0,
    }


def _storage_or_404(db: Path) -> Storage:
    if not db.exists():
        raise HTTPException(status_code=404, detail="Glassbox database not found")
    return Storage(db)


def _get_run_or_404(storage: Storage, run_id: str) -> dict[str, Any]:
    try:
        return storage.get_run(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}") from exc


def _build_event_tree(
    events: list[dict[str, Any]],
    ai_calls: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    ai_calls_by_event_id = {ai_call["event_id"]: ai_call for ai_call in ai_calls or []}
    by_id = {event["id"]: {**event, "children": []} for event in events}
    for event_id, ai_call in ai_calls_by_event_id.items():
        if event_id in by_id:
            by_id[event_id]["ai_call"] = ai_call
    roots = []
    for event in by_id.values():
        parent_id = event["parent_id"]
        if parent_id and parent_id in by_id:
            by_id[parent_id]["children"].append(event)
        else:
            roots.append(event)
    return roots


def _mount_viewer_assets(app: FastAPI, static_path: Path) -> None:
    index_path = static_path / "index.html"
    assets_path = static_path / "assets"
    if not index_path.exists():
        return

    if assets_path.exists():
        app.mount("/assets", StaticFiles(directory=assets_path), name="viewer-assets")

    @app.get("/", include_in_schema=False)
    def viewer_index() -> FileResponse:
        return FileResponse(index_path)

    @app.get("/{frontend_path:path}", include_in_schema=False)
    def viewer_route(frontend_path: str) -> FileResponse:
        if frontend_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(index_path)
