"""SQLite schema management for Glassbox."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_VERSION = 1

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT NOT NULL,
    runtime_language TEXT NOT NULL,
    runtime_version TEXT,
    os TEXT,
    cwd TEXT,
    total_cost_usd REAL DEFAULT 0,
    total_input_tokens INTEGER DEFAULT 0,
    total_output_tokens INTEGER DEFAULT 0,
    duration_ms INTEGER,
    tags TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(id),
    parent_id TEXT REFERENCES events(id),
    event_type TEXT NOT NULL,
    name TEXT NOT NULL,
    started_at TEXT NOT NULL,
    duration_ms INTEGER,
    status TEXT NOT NULL,
    error_message TEXT,
    file_path TEXT,
    line_number INTEGER,
    data_json TEXT
);

CREATE TABLE IF NOT EXISTS ai_calls (
    event_id TEXT PRIMARY KEY REFERENCES events(id),
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    temperature REAL,
    max_tokens INTEGER,
    system_prompt TEXT,
    messages_json TEXT NOT NULL,
    response_text TEXT,
    stop_reason TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd REAL
);

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);
"""


def migrate(db_path: str | Path) -> None:
    """Create or migrate a Glassbox SQLite database to the current schema."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA_SQL)
        current_version = connection.execute(
            "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
        ).fetchone()

        if current_version is None:
            connection.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (SCHEMA_VERSION,),
            )
            return

        if current_version[0] != SCHEMA_VERSION:
            raise RuntimeError(
                f"Unsupported Glassbox schema version {current_version[0]}; "
                f"expected {SCHEMA_VERSION}."
            )
