"""Runtime configuration for Glassbox."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GlassboxConfig:
    db_path: Path
    project_name: str


def build_config(
    *,
    db_path: str | Path = "glassbox.db",
    project_name: str | None = None,
) -> GlassboxConfig:
    path = Path(db_path)
    return GlassboxConfig(
        db_path=path,
        project_name=project_name or Path.cwd().name,
    )
