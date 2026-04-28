from __future__ import annotations

from glassbox.redaction import REDACTED, redact_value


def test_api_key_like_strings_are_redacted() -> None:
    assert redact_value("sk-proj-abcdefghijklmnopqrstuvwxyz123456") == REDACTED
    assert redact_value("sk-ant-api03-abcdefghijklmnopqrstuvwxyz123456") == REDACTED


def test_secret_like_mapping_keys_are_redacted() -> None:
    value = {
        "OPENAI_API_KEY": "sk-proj-abcdefghijklmnopqrstuvwxyz123456",
        "refresh_token": "abc123",
        "databasePassword": "correct-horse-battery-staple",
        "safe": "visible",
    }

    redacted = redact_value(value)

    assert redacted == {
        "OPENAI_API_KEY": REDACTED,
        "refresh_token": REDACTED,
        "databasePassword": REDACTED,
        "safe": "visible",
    }


def test_long_strings_are_truncated() -> None:
    value = "x" * 700

    redacted = redact_value(value, max_string_length=80)

    assert redacted.endswith("...[truncated]")
    assert len(redacted) < len(value)


def test_nested_dicts_lists_and_tuples_are_handled() -> None:
    value = {
        "items": [
            {"name": "safe", "token": "secret"},
            ("visible", {"api_secret": "hidden"}),
        ],
    }

    redacted = redact_value(value)

    assert redacted == {
        "items": [
            {"name": "safe", "token": REDACTED},
            ["visible", {"api_secret": REDACTED}],
        ],
    }
