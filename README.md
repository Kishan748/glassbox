# Glassbox

Glassbox is a local flight recorder for Python AI apps. V1 focuses on capturing real runtime facts: runs, tracked function calls, AI calls, prompts, responses, errors, timings, and costs.

## Current Status

This repository is in Phase 6: Viewer backend.

## Development Quickstart

```bash
python3 -m pip install -e .
python3 -m glassbox --help
python3 -m glassbox doctor
python3 -m glassbox runs --db glassbox.db
python3 -m glassbox export --db glassbox.db --run <run_id>
pytest
```

Phase 6 includes the internal SQLite schema, storage layer, small public
runtime API, default redaction/truncation, bundled model pricing, opt-in sync
OpenAI/Anthropic SDK capture, and terminal commands for diagnostics, runs, and
JSON export. It also includes a FastAPI backend for the future local viewer.

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

AI SDK capture is opt-in:

```python
glassbox.init(capture_openai=True, capture_anthropic=True)
```

Glassbox stores local runtime data in SQLite. Captured function arguments and
return values are redacted and truncated by default, but prompts, responses,
arguments, and errors can still contain sensitive information. Treat
`glassbox.db` as local application data and review exports before sharing them.

## Principles

- Local-first: data stays on the user's machine.
- Facts before inference: V1 records what happened before trying to explain what it means.
- Small public API: keep the first user experience simple.
- Privacy-aware by default: captured data must be redacted and handled deliberately.

See the planning docs in `docs/plans/`.
