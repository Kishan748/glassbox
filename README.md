# Glassbox

Glassbox is a local flight recorder for Python AI apps. V1 focuses on capturing real runtime facts: runs, tracked function calls, AI calls, prompts, responses, errors, timings, and costs.

## Current Status

This repository is in Phase 2: Runtime API.

## Development Quickstart

```bash
python3 -m pip install -e .
python3 -m glassbox --help
pytest
```

Phase 2 includes the internal SQLite schema, storage layer, and small public
runtime API used by later AI capture, CLI, and viewer features.

## Runtime API

```python
import glassbox

glassbox.init()

@glassbox.track
def my_function():
    return "captured"

glassbox.log("thing_happened", {"count": 3})
glassbox.tag("experiment-a")
```

## Principles

- Local-first: data stays on the user's machine.
- Facts before inference: V1 records what happened before trying to explain what it means.
- Small public API: keep the first user experience simple.
- Privacy-aware by default: captured data must be redacted and handled deliberately.

See the planning docs in `docs/plans/`.
