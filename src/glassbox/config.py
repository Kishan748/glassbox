"""Runtime configuration for Glassbox."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GlassboxConfig:
    db_path: Path
    project_name: str
    capture_openai: bool
    capture_anthropic: bool


def build_config(
    *,
    db_path: str | Path = "glassbox.db",
    project_name: str | None = None,
    capture_openai: bool = False,
    capture_anthropic: bool = False,
) -> GlassboxConfig:
    path = Path(db_path)
    return GlassboxConfig(
        db_path=path,
        project_name=project_name or Path.cwd().name,
        capture_openai=capture_openai,
        capture_anthropic=capture_anthropic,
    )
