from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace

import pytest

import glassbox
from glassbox.context import reset_context_for_tests


class FakeAnthropicMessages:
    def create(self, **_kwargs):
        return SimpleNamespace(
            model="claude-3-5-haiku-latest",
            content=[SimpleNamespace(text="Hello from Claude")],
            stop_reason="end_turn",
            usage=SimpleNamespace(input_tokens=10, output_tokens=6),
        )


class FailingAnthropicMessages:
    def create(self, **_kwargs):
        raise RuntimeError("anthropic exploded")


def setup_function() -> None:
    reset_context_for_tests()


def teardown_function() -> None:
    reset_context_for_tests()


def test_fake_anthropic_call_writes_event_and_ai_call(monkeypatch, temp_db_path) -> None:
    _install_fake_anthropic_module(monkeypatch, FakeAnthropicMessages)
    context = glassbox.init(
        db_path=temp_db_path,
        project_name="demo-app",
        capture_anthropic=True,
    )

    response = FakeAnthropicMessages().create(
        model="claude-3-5-haiku-latest",
        messages=[{"role": "user", "content": "Hello"}],
        system="You are concise.",
        temperature=0.1,
        max_tokens=64,
    )

    events = context.storage.list_events(context.run_id)
    ai_call = context.storage.get_ai_call(events[0]["id"])

    assert response.content[0].text == "Hello from Claude"
    assert events[0]["event_type"] == "ai_call"
    assert events[0]["status"] == "completed"
    assert ai_call["provider"] == "anthropic"
    assert ai_call["model"] == "claude-3-5-haiku-latest"
    assert ai_call["messages"] == [{"role": "user", "content": "Hello"}]
    assert ai_call["response_text"] == "Hello from Claude"
    assert ai_call["input_tokens"] == 10
    assert ai_call["output_tokens"] == 6
    assert ai_call["cost_usd"] is not None


def test_fake_anthropic_errors_are_captured_and_reraised(monkeypatch, temp_db_path) -> None:
    _install_fake_anthropic_module(monkeypatch, FailingAnthropicMessages)
    context = glassbox.init(
        db_path=temp_db_path,
        project_name="demo-app",
        capture_anthropic=True,
    )

    with pytest.raises(RuntimeError, match="anthropic exploded"):
        FailingAnthropicMessages().create(model="claude-3-5-haiku-latest", messages=[])

    events = context.storage.list_events(context.run_id)
    assert events[0]["event_type"] == "ai_call"
    assert events[0]["status"] == "failed"
    assert events[0]["error_message"] == "anthropic exploded"


def test_anthropic_capture_can_be_disabled(monkeypatch, temp_db_path) -> None:
    _install_fake_anthropic_module(monkeypatch, FakeAnthropicMessages)
    context = glassbox.init(
        db_path=temp_db_path,
        project_name="demo-app",
        capture_anthropic=False,
    )

    FakeAnthropicMessages().create(model="claude-3-5-haiku-latest", messages=[])

    assert context.storage.list_events(context.run_id) == []


def test_glassbox_imports_when_anthropic_package_is_missing() -> None:
    import glassbox as imported_glassbox

    assert imported_glassbox.__version__ == "0.0.0"


def _install_fake_anthropic_module(monkeypatch, messages_class: type) -> None:
    module_name = "anthropic.resources.messages"
    module = ModuleType(module_name)
    module.Messages = messages_class
    monkeypatch.setitem(sys.modules, module_name, module)
