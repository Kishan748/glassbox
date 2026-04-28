from __future__ import annotations

from glassbox.pricing import estimate_cost_usd


def test_known_model_pricing_returns_input_and_output_cost() -> None:
    cost = estimate_cost_usd("gpt-4o-mini", input_tokens=1_000_000, output_tokens=500_000)

    assert cost == 0.45


def test_unknown_model_returns_none_without_failing() -> None:
    assert estimate_cost_usd("unknown-model", input_tokens=100, output_tokens=200) is None
