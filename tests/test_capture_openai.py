from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace

import pytest

import glassbox
from glassbox.context import reset_context_for_tests


class FakeOpenAICompletions:
    def create(self, **_kwargs):
        return SimpleNamespace(
            model="gpt-4o-mini",
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="Hello back"),
                    finish_reason="stop",
                )
            ],
            usage=SimpleNamespace(prompt_tokens=12, completion_tokens=8),
        )


class FailingOpenAICompletions:
    def create(self, **_kwargs):
        raise RuntimeError("openai exploded")


def setup_function() -> None:
    reset_context_for_tests()


def teardown_function() -> None:
    reset_context_for_tests()


def test_fake_openai_call_writes_event_and_ai_call(monkeypatch, temp_db_path) -> None:
    _install_fake_openai_module(monkeypatch, FakeOpenAICompletions)
    context = glassbox.init(
        db_path=temp_db_path,
        project_name="demo-app",
        capture_openai=True,
    )

    response = FakeOpenAICompletions().create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.2,
        max_tokens=64,
    )

    events = context.storage.list_events(context.run_id)
    ai_call = context.storage.get_ai_call(events[0]["id"])

    assert response.choices[0].message.content == "Hello back"
    assert events[0]["event_type"] == "ai_call"
    assert events[0]["status"] == "completed"
    assert ai_call["provider"] == "openai"
    assert ai_call["model"] == "gpt-4o-mini"
    assert ai_call["messages"] == [{"role": "user", "content": "Hello"}]
    assert ai_call["response_text"] == "Hello back"
    assert ai_call["input_tokens"] == 12
    assert ai_call["output_tokens"] == 8
    assert ai_call["cost_usd"] is not None


def test_fake_openai_errors_are_captured_and_reraised(monkeypatch, temp_db_path) -> None:
    _install_fake_openai_module(monkeypatch, FailingOpenAICompletions)
    context = glassbox.init(
        db_path=temp_db_path,
        project_name="demo-app",
        capture_openai=True,
    )

    with pytest.raises(RuntimeError, match="openai exploded"):
        FailingOpenAICompletions().create(model="gpt-4o-mini", messages=[])

    events = context.storage.list_events(context.run_id)
    assert events[0]["event_type"] == "ai_call"
    assert events[0]["status"] == "failed"
    assert events[0]["error_message"] == "openai exploded"


def test_openai_capture_can_be_disabled(monkeypatch, temp_db_path) -> None:
    _install_fake_openai_module(monkeypatch, FakeOpenAICompletions)
    context = glassbox.init(
        db_path=temp_db_path,
        project_name="demo-app",
        capture_openai=False,
    )

    FakeOpenAICompletions().create(model="gpt-4o-mini", messages=[])

    assert context.storage.list_events(context.run_id) == []


def test_glassbox_imports_when_openai_package_is_missing() -> None:
    import glassbox as imported_glassbox

    assert imported_glassbox.__version__ == "0.0.0"


def _install_fake_openai_module(monkeypatch, completions_class: type) -> None:
    module_name = "openai.resources.chat.completions.completions"
    module = ModuleType(module_name)
    module.Completions = completions_class
    monkeypatch.setitem(sys.modules, module_name, module)
