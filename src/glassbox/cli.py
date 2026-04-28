"""Command-line interface for Glassbox."""

from __future__ import annotations

import argparse
import platform
import sys
from importlib import metadata


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
    doctor.set_defaults(func=run_doctor)

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
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return int(args.func(args))
