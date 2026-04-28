"""Runtime context for active Glassbox capture."""

from __future__ import annotations

import atexit
import sys
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType

from glassbox.config import GlassboxConfig, build_config
from glassbox.storage import Storage

_current_context: RuntimeContext | None = None
_event_stack: ContextVar[tuple[str, ...]] = ContextVar("glassbox_event_stack", default=())


@dataclass
class RuntimeContext:
    config: GlassboxConfig
    storage: Storage
    run_id: str
    _closed: bool = False

    @property
    def is_active(self) -> bool:
        return not self._closed

    @property
    def current_event_id(self) -> str | None:
        stack = _event_stack.get()
        if not stack:
            return None
        return stack[-1]

    def close(self) -> None:
        if self._closed:
            return
        self.storage.complete_run(self.run_id)
        self._closed = True

    def fail(self) -> None:
        if self._closed:
            return
        self.storage.fail_run(self.run_id)
        self._closed = True

    def start_event(self, *, event_type: str, name: str, data: dict | None = None) -> str:
        return self.storage.insert_event(
            self.run_id,
            event_type=event_type,
            name=name,
            parent_id=self.current_event_id,
            data=data,
        )

    def complete_event(
        self,
        event_id: str,
        *,
        duration_ms: int,
        data: dict | None = None,
    ) -> None:
        self.storage.complete_event(event_id, duration_ms=duration_ms, data=data)

    def fail_event(
        self,
        event_id: str,
        *,
        duration_ms: int,
        error_message: str,
        data: dict | None = None,
    ) -> None:
        self.storage.fail_event(
            event_id,
            duration_ms=duration_ms,
            error_message=error_message,
            data=data,
        )

    def push_event(self, event_id: str):
        stack = _event_stack.get()
        return _event_stack.set((*stack, event_id))

    def reset_event_stack(self, token) -> None:
        _event_stack.reset(token)

    def log(self, name: str, data: dict | None = None) -> str:
        return self.storage.insert_event(
            self.run_id,
            event_type="log",
            name=name,
            parent_id=self.current_event_id,
            status="completed",
            data=data,
        )

    def tag(self, tag_name: str) -> None:
        run = self.storage.get_run(self.run_id)
        tags = list(run["tags"])
        if tag_name not in tags:
            tags.append(tag_name)
            self.storage.update_run_tags(self.run_id, tags)


def init_context(
    *,
    db_path: str | Path = "glassbox.db",
    project_name: str | None = None,
    capture_openai: bool = False,
    capture_anthropic: bool = False,
) -> RuntimeContext:
    global _current_context

    if _current_context is not None and _current_context.is_active:
        return _current_context

    config = build_config(
        db_path=db_path,
        project_name=project_name,
        capture_openai=capture_openai,
        capture_anthropic=capture_anthropic,
    )
    storage = Storage(config.db_path)
    run_id = storage.create_run(
        project_name=config.project_name,
        cwd=str(Path.cwd()),
    )
    _current_context = RuntimeContext(config=config, storage=storage, run_id=run_id)
    if config.capture_openai:
        from glassbox.capture.openai import install_capture as install_openai_capture

        install_openai_capture()
    if config.capture_anthropic:
        from glassbox.capture.anthropic import install_capture as install_anthropic_capture

        install_anthropic_capture()
    atexit.register(_close_current_context)
    _install_excepthook()
    return _current_context


def get_current_context() -> RuntimeContext | None:
    if _current_context is None or not _current_context.is_active:
        return None
    return _current_context


def log(name: str, data: dict | None = None) -> str | None:
    context = get_current_context()
    if context is None:
        return None
    return context.log(name, data)


def tag(tag_name: str) -> None:
    context = get_current_context()
    if context is None:
        return
    context.tag(tag_name)


def reset_context_for_tests() -> None:
    global _current_context

    if _current_context is not None and _current_context.is_active:
        _current_context.close()
    _current_context = None
    _event_stack.set(())


def _close_current_context() -> None:
    context = get_current_context()
    if context is not None:
        context.close()


_previous_excepthook = sys.excepthook
_excepthook_installed = False


def _install_excepthook() -> None:
    global _excepthook_installed
    if _excepthook_installed:
        return
    sys.excepthook = _glassbox_excepthook
    _excepthook_installed = True


def _glassbox_excepthook(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    context = get_current_context()
    if context is not None:
        context.fail()
    _previous_excepthook(exc_type, exc_value, exc_traceback)
