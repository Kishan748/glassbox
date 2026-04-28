"""Capture sync Anthropic messages calls."""

from __future__ import annotations

import functools
import importlib
import time
from typing import Any

from glassbox.context import get_current_context
from glassbox.pricing import estimate_cost_usd
from glassbox.redaction import redact_value

PROVIDER = "anthropic"
EVENT_NAME = "anthropic.messages.create"


def install_capture() -> bool:
    """Install Anthropic capture if the sync SDK resource is importable."""
    try:
        module = importlib.import_module("anthropic.resources.messages")
    except ImportError:
        return False

    messages_class = getattr(module, "Messages", None)
    if messages_class is None or not hasattr(messages_class, "create"):
        return False

    original = messages_class.create
    if getattr(original, "_glassbox_provider", None) == PROVIDER:
        return True

    @functools.wraps(original)
    def wrapped_create(self, *args: Any, **kwargs: Any) -> Any:
        context = get_current_context()
        if context is None or not context.config.capture_anthropic:
            return original(self, *args, **kwargs)

        event_id = context.start_event(
            event_type="ai_call",
            name=EVENT_NAME,
            data=_request_data(kwargs),
        )
        started = time.perf_counter()
        try:
            response = original(self, *args, **kwargs)
        except Exception as exc:
            context.fail_event(
                event_id,
                duration_ms=_duration_ms(started),
                error_message=str(exc),
                data=_request_data(kwargs),
            )
            raise

        model = _get(response, "model") or kwargs.get("model") or "unknown"
        input_tokens = _get(_get(response, "usage"), "input_tokens")
        output_tokens = _get(_get(response, "usage"), "output_tokens")
        response_text = _extract_response_text(response)
        context.storage.insert_ai_call(
            event_id,
            provider=PROVIDER,
            model=str(model),
            temperature=kwargs.get("temperature"),
            max_tokens=kwargs.get("max_tokens"),
            system_prompt=redact_value(kwargs.get("system")) if kwargs.get("system") else None,
            messages=redact_value(kwargs.get("messages") or []),
            response_text=redact_value(response_text) if response_text is not None else None,
            stop_reason=_as_optional_string(_get(response, "stop_reason")),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=estimate_cost_usd(
                str(model),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            ),
        )
        context.complete_event(
            event_id,
            duration_ms=_duration_ms(started),
            data={"provider": PROVIDER, "model": str(model)},
        )
        return response

    wrapped_create._glassbox_provider = PROVIDER  # type: ignore[attr-defined]
    messages_class.create = wrapped_create
    return True


def _request_data(kwargs: dict[str, Any]) -> dict[str, Any]:
    return redact_value(
        {
            "provider": PROVIDER,
            "model": kwargs.get("model"),
            "messages": kwargs.get("messages") or [],
            "system": kwargs.get("system"),
        }
    )


def _extract_response_text(response: Any) -> str | None:
    content_items = _get(response, "content") or []
    text_parts = []
    for item in content_items:
        text = _get(item, "text")
        if text is not None:
            text_parts.append(str(text))
    if not text_parts:
        return None
    return "\n".join(text_parts)


def _duration_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


def _as_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _get(value: Any, name: str) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name, None)
