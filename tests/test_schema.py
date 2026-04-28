from __future__ import annotations

import sqlite3

from glassbox.schema import SCHEMA_VERSION, migrate


def test_migrate_creates_schema_version_1(temp_db_path) -> None:
    migrate(temp_db_path)

    with sqlite3.connect(temp_db_path) as connection:
        version = connection.execute("SELECT version FROM schema_version").fetchone()
        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert version == (SCHEMA_VERSION,)
    assert {"runs", "events", "ai_calls", "schema_version"} <= table_names


def test_migrate_is_idempotent(temp_db_path) -> None:
    migrate(temp_db_path)
    migrate(temp_db_path)

    with sqlite3.connect(temp_db_path) as connection:
        versions = connection.execute("SELECT version FROM schema_version").fetchall()

    assert versions == [(SCHEMA_VERSION,)]
