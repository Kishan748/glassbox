"""Bundled model pricing helpers."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources


def estimate_cost_usd(
    model: str,
    *,
    input_tokens: int | None,
    output_tokens: int | None,
) -> float | None:
    pricing = _load_pricing().get(model)
    if pricing is None or input_tokens is None or output_tokens is None:
        return None

    input_cost = input_tokens * pricing["input_per_1m"] / 1_000_000
    output_cost = output_tokens * pricing["output_per_1m"] / 1_000_000
    return round(input_cost + output_cost, 12)


@lru_cache(maxsize=1)
def _load_pricing() -> dict[str, dict[str, float]]:
    with resources.files("glassbox").joinpath("pricing.json").open() as handle:
        return json.load(handle)
