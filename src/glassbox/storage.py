"""Durable SQLite storage for Glassbox runtime facts."""

from __future__ import annotations

import json
import platform
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from glassbox.schema import migrate


class Storage:
    """Small SQLite storage layer used by capture, CLI, and viewer code."""

    def __init__(self, db_path: str | Path = "glassbox.db") -> None:
        self.db_path = Path(db_path)
        migrate(self.db_path)
        self._connection = sqlite3.connect(self.db_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")

    def close(self) -> None:
        self._connection.close()

    def create_run(
        self,
        *,
        project_name: str,
        tags: list[str] | None = None,
        run_id: str | None = None,
        started_at: datetime | None = None,
        runtime_language: str = "python",
        runtime_version: str | None = None,
        os_name: str | None = None,
        cwd: str | None = None,
    ) -> str:
        run_id = run_id or self._new_id("run")
        self._connection.execute(
            """
            INSERT INTO runs (
                id,
                project_name,
                started_at,
                status,
                runtime_language,
                runtime_version,
                os,
                cwd,
                tags
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                project_name,
                self._format_time(started_at),
                "running",
                runtime_language,
                runtime_version or platform.python_version(),
                os_name or platform.platform(),
                cwd,
                self._to_json(tags or []),
            ),
        )
        self._connection.commit()
        return run_id

    def complete_run(self, run_id: str, *, ended_at: datetime | None = None) -> None:
        self._finish_run(run_id, status="completed", ended_at=ended_at)

    def fail_run(self, run_id: str, *, ended_at: datetime | None = None) -> None:
        self._finish_run(run_id, status="failed", ended_at=ended_at)

    def update_run_tags(self, run_id: str, tags: list[str]) -> None:
        self._connection.execute(
            "UPDATE runs SET tags = ? WHERE id = ?",
            (self._to_json(tags), run_id),
        )
        self._connection.commit()

    def get_run(self, run_id: str) -> dict[str, Any]:
        row = self._connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        if row is None:
            raise KeyError(f"Run not found: {run_id}")
        run = dict(row)
        run["tags"] = self._from_json(run["tags"], default=[])
        return run

    def insert_event(
        self,
        run_id: str,
        *,
        event_type: str,
        name: str,
        parent_id: str | None = None,
        event_id: str | None = None,
        started_at: datetime | None = None,
        duration_ms: int | None = None,
        status: str = "running",
        error_message: str | None = None,
        file_path: str | None = None,
        line_number: int | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        event_id = event_id or self._new_id("evt")
        self._connection.execute(
            """
            INSERT INTO events (
                id,
                run_id,
                parent_id,
                event_type,
                name,
                started_at,
                duration_ms,
                status,
                error_message,
                file_path,
                line_number,
                data_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                run_id,
                parent_id,
                event_type,
                name,
                self._format_time(started_at),
                duration_ms,
                status,
                error_message,
                file_path,
                line_number,
                self._to_json(data),
            ),
        )
        self._connection.commit()
        return event_id

    def list_events(self, run_id: str) -> list[dict[str, Any]]:
        rows = self._connection.execute(
            "SELECT * FROM events WHERE run_id = ? ORDER BY started_at, id",
            (run_id,),
        ).fetchall()
        return [self._event_from_row(row) for row in rows]

    def complete_event(
        self,
        event_id: str,
        *,
        duration_ms: int,
        data: dict[str, Any] | None = None,
    ) -> None:
        self._connection.execute(
            """
            UPDATE events
            SET duration_ms = ?, status = ?, data_json = ?
            WHERE id = ?
            """,
            (duration_ms, "completed", self._to_json(data), event_id),
        )
        self._connection.commit()

    def fail_event(
        self,
        event_id: str,
        *,
        duration_ms: int,
        error_message: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        self._connection.execute(
            """
            UPDATE events
            SET duration_ms = ?, status = ?, error_message = ?, data_json = ?
            WHERE id = ?
            """,
            (duration_ms, "failed", error_message, self._to_json(data), event_id),
        )
        self._connection.commit()

    def insert_ai_call(
        self,
        event_id: str,
        *,
        provider: str,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        response_text: str | None = None,
        stop_reason: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        cost_usd: float | None = None,
    ) -> None:
        self._connection.execute(
            """
            INSERT INTO ai_calls (
                event_id,
                provider,
                model,
                temperature,
                max_tokens,
                system_prompt,
                messages_json,
                response_text,
                stop_reason,
                input_tokens,
                output_tokens,
                cost_usd
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                provider,
                model,
                temperature,
                max_tokens,
                system_prompt,
                self._to_json(messages),
                response_text,
                stop_reason,
                input_tokens,
                output_tokens,
                cost_usd,
            ),
        )
        self._connection.commit()

    def get_ai_call(self, event_id: str) -> dict[str, Any]:
        row = self._connection.execute(
            "SELECT * FROM ai_calls WHERE event_id = ?",
            (event_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"AI call not found: {event_id}")
        ai_call = dict(row)
        ai_call["messages"] = self._from_json(ai_call.pop("messages_json"), default=[])
        return ai_call

    def _finish_run(
        self,
        run_id: str,
        *,
        status: str,
        ended_at: datetime | None = None,
    ) -> None:
        run = self.get_run(run_id)
        ended = ended_at or datetime.now(timezone.utc)
        started = datetime.fromisoformat(run["started_at"])
        duration_ms = int((ended - started).total_seconds() * 1000)
        self._connection.execute(
            """
            UPDATE runs
            SET ended_at = ?, status = ?, duration_ms = ?
            WHERE id = ?
            """,
            (ended.isoformat(), status, duration_ms, run_id),
        )
        self._connection.commit()

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex}"

    @staticmethod
    def _format_time(value: datetime | None) -> str:
        return (value or datetime.now(timezone.utc)).isoformat()

    @staticmethod
    def _to_json(value: Any) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _from_json(value: str | None, *, default: Any) -> Any:
        if value is None:
            return default
        return json.loads(value)

    def _event_from_row(self, row: sqlite3.Row) -> dict[str, Any]:
        event = dict(row)
        event["data"] = self._from_json(event.pop("data_json"), default={})
        return event
