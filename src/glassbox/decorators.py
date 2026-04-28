"""Runtime decorators for capturing sync function calls."""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from glassbox.context import get_current_context

P = ParamSpec("P")
R = TypeVar("R")

MAX_CAPTURE_CHARS = 500


def track(func: Callable[P, R]) -> Callable[P, R]:
    """Capture a sync function call when a Glassbox context is active."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        context = get_current_context()
        if context is None:
            return func(*args, **kwargs)

        data = {
            "args": [_capture_value(arg) for arg in args],
            "kwargs": {key: _capture_value(value) for key, value in kwargs.items()},
        }
        event_id = context.start_event(
            event_type="function",
            name=func.__name__,
            data=data,
        )
        token = context.push_event(event_id)
        started = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            duration_ms = _duration_ms(started)
            context.fail_event(
                event_id,
                duration_ms=duration_ms,
                error_message=str(exc),
                data=data,
            )
            raise
        else:
            duration_ms = _duration_ms(started)
            data["return_value"] = _capture_value(result)
            context.complete_event(event_id, duration_ms=duration_ms, data=data)
            return result
        finally:
            context.reset_event_stack(token)

    return wrapper


def _duration_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


def _capture_value(value: object) -> str:
    captured = repr(value)
    if len(captured) <= MAX_CAPTURE_CHARS:
        return captured
    return f"{captured[:MAX_CAPTURE_CHARS]}..."
