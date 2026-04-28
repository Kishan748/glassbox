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
    print("Glassbox diagnostics")
    print(f"  glassbox: {get_version()}")
    print(f"  python: {platform.python_version()}")
    print(f"  executable: {sys.executable}")
    print(f"  platform: {platform.platform()}")
    print(f"  cwd: {Path.cwd()}")
    print(f"  database: {Path(_args.db)}")
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


def _port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return probe.connect_ex((host, port)) != 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return int(args.func(args))
