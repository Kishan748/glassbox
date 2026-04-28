"""Glassbox public package interface."""

from __future__ import annotations

from pathlib import Path

from glassbox.context import RuntimeContext, init_context, log, tag
from glassbox.decorators import track

__version__ = "0.1.0a1"


def init(
    *,
    db_path: str | Path = "glassbox.db",
    project_name: str | None = None,
    capture_openai: bool = False,
    capture_anthropic: bool = False,
) -> RuntimeContext:
    return init_context(
        db_path=db_path,
        project_name=project_name,
        capture_openai=capture_openai,
        capture_anthropic=capture_anthropic,
    )


__all__ = ["__version__", "init", "log", "tag", "track"]
