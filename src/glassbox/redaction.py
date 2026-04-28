"""Default sensitive-data redaction and truncation."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

REDACTED = "[REDACTED]"
TRUNCATED_SUFFIX = "...[truncated]"
DEFAULT_MAX_STRING_LENGTH = 500

SECRET_KEY_PATTERN = re.compile(r"(key|token|secret|password)", re.IGNORECASE)
API_KEY_PATTERNS = (
    re.compile(r"\bsk-(?:proj-|ant-api\d*-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{30,}\b"),
)


def redact_value(value: Any, *, max_string_length: int = DEFAULT_MAX_STRING_LENGTH) -> Any:
    """Return a JSON-serializable value with obvious secrets removed."""
    return _redact_value(value, max_string_length=max_string_length, parent_key=None)


def _redact_value(value: Any, *, max_string_length: int, parent_key: str | None) -> Any:
    if parent_key is not None and SECRET_KEY_PATTERN.search(parent_key):
        return REDACTED

    if value is None or isinstance(value, bool | int | float):
        return value

    if isinstance(value, str):
        return _redact_string(value, max_string_length=max_string_length)

    if isinstance(value, Mapping):
        return {
            str(key): _redact_value(
                nested_value,
                max_string_length=max_string_length,
                parent_key=str(key),
            )
            for key, nested_value in value.items()
        }

    if isinstance(value, tuple):
        return [
            _redact_value(item, max_string_length=max_string_length, parent_key=None)
            for item in value
        ]

    if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray):
        return [
            _redact_value(item, max_string_length=max_string_length, parent_key=None)
            for item in value
        ]

    return _redact_string(repr(value), max_string_length=max_string_length)


def _redact_string(value: str, *, max_string_length: int) -> str:
    if any(pattern.search(value) for pattern in API_KEY_PATTERNS):
        return REDACTED
    if len(value) <= max_string_length:
        return value
    return f"{value[:max_string_length]}{TRUNCATED_SUFFIX}"
