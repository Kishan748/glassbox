"""Command-line interface for Glassbox."""

from __future__ import annotations

import argparse
import json
import platform
import socket
import sys
import webbrowser
from importlib import metadata, util
from pathlib import Path

import uvicorn

from glassbox.storage import Storage
from glassbox.viewer_backend import create_app


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="glassbox",
        description="Local flight recorder for Python AI apps.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"glassbox {get_version()}",
    )

    subparsers = parser.add_subparsers(dest="command")

    doctor = subparsers.add_parser("doctor", help="Show local Glassbox diagnostics.")
    doctor.add_argument("--db", default="glassbox.db", help="Path to the Glassbox SQLite DB.")
    doctor.set_defaults(func=run_doctor)

    runs = subparsers.add_parser("runs", help="List recent Glassbox runs.")
    runs.add_argument("--db", default="glassbox.db", help="Path to the Glassbox SQLite DB.")
    runs.add_argument("--limit", type=int, default=20, help="Maximum runs to show.")
    runs.set_defaults(func=run_runs)

    export = subparsers.add_parser("export", help="Export one run as JSON.")
    export.add_argument("--db", default="glassbox.db", help="Path to the Glassbox SQLite DB.")
    export.add_argument("--run", required=True, help="Run ID to export.")
    export.set_defaults(func=run_export)

    demo = subparsers.add_parser("demo", help="Create a local demo run with sample AI data.")
    demo.add_argument("--db", default="glassbox.db", help="Path to the Glassbox SQLite DB.")
    demo.set_defaults(func=run_demo)

    view = subparsers.add_parser("view", help="Start the local Glassbox viewer.")
    view.add_argument("--db", default="glassbox.db", help="Path to the Glassbox SQLite DB.")
    view.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    view.add_argument("--port", type=int, default=4747, help="Port for the local viewer.")
    view.set_defaults(func=run_view)

    return parser


def get_version() -> str:
    try:
        return metadata.version("glassbox")
    except metadata.PackageNotFoundError:
        return "0.0.0"


def run_doctor(_args: argparse.Namespace) -> int:
    db_path = Path(_args.db)
    print("Glassbox diagnostics")
    print(f"  glassbox: {get_version()}")
    print(f"  python: {platform.python_version()}")
    print(f"  executable: {sys.executable}")
    print(f"  platform: {platform.platform()}")
    print(f"  cwd: {Path.cwd()}")
    print(f"  database: {db_path}")
    print(f"  database status: {_database_status(db_path)}")
    print(f"  viewer assets: {_viewer_assets_status()}")
    print(f"  openai sdk: {_sdk_status('openai')}")
    print(f"  anthropic sdk: {_sdk_status('anthropic')}")
    return 0


def run_runs(args: argparse.Namespace) -> int:
    storage = Storage(args.db)
    try:
        runs = storage.list_runs(limit=args.limit)
    finally:
        storage.close()

    if not runs:
        print("No runs found.")
        return 0

    print("Run ID | Project | Status | Started | Duration ms")
    for run in runs:
        print(
            " | ".join(
                [
                    run["id"],
                    run["project_name"],
                    run["status"],
                    run["started_at"],
                    str(run["duration_ms"] or ""),
                ]
            )
        )
    return 0


def run_export(args: argparse.Namespace) -> int:
    storage = Storage(args.db)
    try:
        try:
            run = storage.get_run(args.run)
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        payload = {
            "run": run,
            "events": storage.list_events(args.run),
            "ai_calls": storage.list_ai_calls_for_run(args.run),
        }
    finally:
        storage.close()

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def run_demo(args: argparse.Namespace) -> int:
    storage = Storage(args.db)
    try:
        run_id = _create_demo_run(storage)
    finally:
        storage.close()

    print(f"Created demo run {run_id} in {Path(args.db)}")
    print("Inspect it with:")
    print(f"  python3 -m glassbox view --db {args.db} --port 4747")
    return 0


def run_view(args: argparse.Namespace) -> int:
    if not _port_available(args.host, args.port):
        print(
            f"Port {args.port} is already in use. Choose another port with --port.",
            file=sys.stderr,
        )
        return 1

    app = create_app(db_path=args.db)
    url = f"http://{args.host}:{args.port}/"
    print(f"Starting Glassbox viewer at {url}")
    webbrowser.open(url)
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return 0


def _sdk_status(package_name: str) -> str:
    return "available" if util.find_spec(package_name) is not None else "not installed"


def _database_status(db_path: Path) -> str:
    return "found" if db_path.exists() else "not found"


def _viewer_assets_status() -> str:
    static_path = Path(__file__).parent / "viewer_static"
    index_path = static_path / "index.html"
    assets_path = static_path / "assets"
    has_assets = assets_path.exists() and any(assets_path.iterdir())
    return "available" if index_path.exists() and has_assets else "missing"


def _port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return probe.connect_ex((host, port)) != 0


def _create_demo_run(storage: Storage) -> str:
    run_id = storage.create_run(project_name="glassbox-demo", tags=["demo", "local"])
    question_event_id = storage.insert_event(
        run_id,
        event_type="function",
        name="draft_question",
        duration_ms=12,
        status="completed",
        data={
            "args": ["local AI traces"],
            "return_value": "Explain why local AI traces help debugging.",
        },
    )
    ai_event_id = storage.insert_event(
        run_id,
        parent_id=question_event_id,
        event_type="ai_call",
        name="glassbox.demo.ai_call",
        duration_ms=328,
        status="completed",
        data={"provider": "demo", "model": "demo-local-model"},
    )
    storage.insert_ai_call(
        ai_event_id,
        provider="demo",
        model="demo-local-model",
        messages=[
            {
                "role": "user",
                "content": "Explain why local AI traces help debugging.",
            }
        ],
        response_text=(
            "Local AI traces show the exact prompt, response, timing, and surrounding "
            "function calls, so debugging starts from facts instead of guesses."
        ),
        stop_reason="stop",
        input_tokens=9,
        output_tokens=24,
        cost_usd=0.0,
    )
    storage.insert_event(
        run_id,
        parent_id=question_event_id,
        event_type="log",
        name="demo_summary",
        duration_ms=1,
        status="completed",
        data={
            "message": "This demo run is deterministic and never calls an external model.",
            "next_step": "Open the viewer and inspect the AI call.",
        },
    )
    storage.complete_run(run_id)
    return run_id


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return int(args.func(args))
