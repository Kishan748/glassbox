# Glassbox

Glassbox is a local flight recorder for Python AI apps. V1 focuses on capturing real runtime facts: runs, tracked function calls, AI calls, prompts, responses, errors, timings, and costs.

## Current Status

This repository is in post-alpha polish after `v0.1.0-alpha.1`.

## Quickstart

```bash
python3 -m pip install -e .
python3 examples/simple_tracked_app.py
python3 -m glassbox runs --db glassbox.db
python3 -m glassbox view --db glassbox.db --port 4747
```

Then open `http://127.0.0.1:4747/` if your browser did not open automatically.

To instrument your own Python code:

```python
import glassbox

@glassbox.track
def my_function():
    return "captured"

with glassbox.init(db_path="glassbox.db", project_name="my-app"):
    result = my_function()
    glassbox.log("thing_happened", {"result": result})
    glassbox.tag("local")
```

Useful local commands:

```bash
python3 -m glassbox doctor
python3 -m glassbox runs --db glassbox.db
python3 -m glassbox export --db glassbox.db --run <run_id>
python3 -m glassbox view --db glassbox.db --port 4747
```

Development checks:

```bash
pytest
cd viewer
npm install
npm test
npm run build
```

V1 alpha includes the internal SQLite schema, storage layer, small public
runtime API, default redaction/truncation, bundled model pricing, opt-in sync
OpenAI/Anthropic SDK capture, and terminal commands for diagnostics, runs, and
JSON export. It also includes a FastAPI backend and Vite React frontend for the
local viewer, `glassbox view` to launch it, and runnable examples.

## Runtime API

```python
import glassbox

@glassbox.track
def my_function():
    return "captured"

with glassbox.init():
    glassbox.log("thing_happened", {"count": 3})
    glassbox.tag("experiment-a")
    my_function()
```

Tracked functions are normal Python events. They can contain prompt-like return
values, but they are not model calls. To see real prompt/response details in
the AI-call panel, enable SDK capture and run an OpenAI or Anthropic request.

AI SDK capture is opt-in and sync-only in the alpha:

```python
import glassbox
from openai import OpenAI

client = OpenAI()

with glassbox.init(capture_openai=True):
    client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Explain Glassbox in one sentence."}],
    )
```

## Viewer Frontend

```bash
cd viewer
npm install
npm run dev
```

The frontend expects the Phase 6 API shape under `/api`. The CLI command that
serves the built viewer and starts the backend is:

```bash
python3 -m glassbox view --db glassbox.db --port 4747
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
