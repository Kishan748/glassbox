# Glassbox V1 Professional Build Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build Glassbox V1 as a professional-grade local product, not as a loosely vibe-coded prototype.

**Architecture:** V1 is a Python-first local runtime recorder. It captures tracked function calls and AI SDK calls into SQLite, then serves a local browser viewer for inspecting runs, prompts, responses, errors, timings, and costs.

**Tech Stack:** Python 3.10+, SQLite, FastAPI, TypeScript, React, Vite or Next.js, Tailwind, pytest, ruff, mypy or pyright, Playwright, GitHub Actions.

---

## Product Standard

Glassbox V1 should feel like a small, serious product from day one.

This means:

- clear scope
- boring architecture
- repeatable setup
- automated tests
- clean error handling
- predictable CLI behavior
- documented decisions
- no mystery state
- no hidden network calls
- no unreviewed sensitive-data handling
- no "we will fix it later" core flows

The product may be small. It should not be sloppy.

---

## V1 Product Definition

### One-Sentence Product

Glassbox V1 is a local flight recorder for Python AI apps.

### Primary User Job

Help a vibe coder understand what happened during an app run:

- what functions ran
- what AI calls were made
- what prompts were sent
- what responses came back
- what failed
- what it cost
- where it happened in code
- what to copy into an AI coding tool to debug it

### V1 Non-Goals

Do not build these in V1:

- JavaScript/TypeScript package
- static analyzer
- System Map
- branch-level tracking
- full run replay
- single-call replay
- Ask Glassbox chat
- snapshots
- hosted backend
- accounts
- telemetry
- semantic search
- automatic code modification

---

## Engineering Principles

### 1. Facts Before Inference

V1 stores facts only:

- run started
- run ended
- function entered
- function returned
- function raised an error
- AI call started
- AI call returned
- AI call raised an error

No V1 feature should depend on guessing what the app "means."

### 2. Local-First By Construction

All data stays in:

```text
./glassbox.db
```

No telemetry. No hosted services. No background daemon.

### 3. Explicit Sensitive Data Handling

V1 will capture prompts, responses, function args, and errors. These can contain secrets.

Therefore:

- redaction is on by default
- API keys are never stored
- common secret patterns are redacted
- large values are truncated
- exports are explicit
- README clearly warns what is captured

### 4. Small Public API

The V1 user API should be tiny:

```python
import glassbox

glassbox.init()

@glassbox.track
def my_function():
    ...

glassbox.log("thing_happened", {"count": 3})
glassbox.tag("experiment-a")
```

Everything else is internal until proven necessary.

### 5. Test The Contract

SQLite schema is the contract between capture, CLI, backend, and viewer.

Any schema change requires:

- migration
- schema version bump
- storage tests
- backend fixture test
- viewer fixture compatibility check

---

## Repository Structure

Start with one repository and one Python package.

```text
glassbox/
  README.md
  LICENSE
  CHANGELOG.md
  DECISIONS.md
  pyproject.toml
  .gitignore
  .github/
    workflows/
      ci.yml
  src/
    glassbox/
      __init__.py
      cli.py
      capture/
        __init__.py
        anthropic.py
        openai.py
      config.py
      context.py
      decorators.py
      errors.py
      pricing.py
      pricing.json
      redaction.py
      schema.py
      storage.py
      viewer_backend.py
  viewer/
    package.json
    tsconfig.json
    vite.config.ts
    src/
      main.tsx
      App.tsx
      api/
      components/
      pages/
      styles.css
  tests/
    conftest.py
    fixtures/
    test_storage.py
    test_schema.py
    test_decorators.py
    test_redaction.py
    test_capture_openai.py
    test_capture_anthropic.py
    test_cli.py
    test_viewer_backend.py
  examples/
    simple_tracked_app.py
    simple_openai_app.py
    simple_anthropic_app.py
```

Use Vite React for V1 unless there is a strong reason for Next.js. It is simpler to build, bundle, and serve locally.

---

## Quality Gates

Every phase must pass these gates before moving forward:

1. Unit tests pass.
2. Type/lint checks pass.
3. Example app still works.
4. CLI help output is valid.
5. No known secret is stored unredacted in test fixtures.
6. `DECISIONS.md` is updated for any architectural decision.
7. README is updated when user-facing behavior changes.

Recommended local command:

```bash
ruff check .
pytest
```

Once viewer exists:

```bash
cd viewer && npm run lint && npm run build
pytest
```

---

## Phase 0: Professional Project Setup

### Objective

Create a clean, reproducible project foundation.

### Deliverables

- Python package installs locally.
- CLI command exists.
- Tests run in CI.
- Formatting/linting configured.
- Decision log exists.

### Tasks

#### Task 0.1: Create Repository Foundation

Files:

- Create `README.md`
- Create `LICENSE`
- Create `CHANGELOG.md`
- Create `DECISIONS.md`
- Create `.gitignore`
- Create `pyproject.toml`

Acceptance criteria:

- `pip install -e .` works.
- `python -m glassbox --help` works.

#### Task 0.2: Configure Tooling

Configure:

- pytest
- ruff
- packaging metadata
- console script `glassbox`

Acceptance criteria:

- `ruff check .` passes.
- `pytest` passes.

#### Task 0.3: Add CI

Files:

- Create `.github/workflows/ci.yml`

Acceptance criteria:

- CI runs lint and tests on push/PR.

---

## Phase 1: SQLite Storage Core

### Objective

Create the durable local event store.

### Deliverables

- `glassbox.db` is created automatically.
- Schema migrations run safely.
- Runs and events can be inserted and read.

### Schema For V1

Start with the minimum schema:

```sql
CREATE TABLE runs (
    id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT NOT NULL,
    runtime_language TEXT NOT NULL,
    runtime_version TEXT,
    os TEXT,
    cwd TEXT,
    total_cost_usd REAL DEFAULT 0,
    total_input_tokens INTEGER DEFAULT 0,
    total_output_tokens INTEGER DEFAULT 0,
    duration_ms INTEGER,
    tags TEXT
);

CREATE TABLE events (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(id),
    parent_id TEXT REFERENCES events(id),
    event_type TEXT NOT NULL,
    name TEXT NOT NULL,
    started_at TEXT NOT NULL,
    duration_ms INTEGER,
    status TEXT NOT NULL,
    error_message TEXT,
    file_path TEXT,
    line_number INTEGER,
    data_json TEXT
);

CREATE TABLE ai_calls (
    event_id TEXT PRIMARY KEY REFERENCES events(id),
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    temperature REAL,
    max_tokens INTEGER,
    system_prompt TEXT,
    messages_json TEXT NOT NULL,
    response_text TEXT,
    stop_reason TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd REAL
);

CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY
);
```

### Tasks

#### Task 1.1: Implement Schema Migration

Files:

- Create `src/glassbox/schema.py`
- Create `tests/test_schema.py`

Acceptance criteria:

- New database gets schema version 1.
- Re-running migration is idempotent.

#### Task 1.2: Implement Storage Layer

Files:

- Create `src/glassbox/storage.py`
- Create `tests/test_storage.py`

Acceptance criteria:

- Can create a run.
- Can complete a run.
- Can fail a run.
- Can insert child events.
- Can insert AI call details.

#### Task 1.3: Add Database Fixture Tests

Files:

- Create `tests/conftest.py`

Acceptance criteria:

- Every storage test uses isolated temporary SQLite DB.

---

## Phase 2: Runtime API

### Objective

Expose the tiny public Python API.

### Deliverables

- `glassbox.init()` starts a run.
- run is closed on normal process exit.
- run is marked failed on unhandled exception where practical.
- `@glassbox.track` captures function calls.
- `glassbox.log` captures custom events.
- `glassbox.tag` adds run tags.

### Tasks

#### Task 2.1: Implement Init Context

Files:

- Modify `src/glassbox/__init__.py`
- Create `src/glassbox/context.py`
- Create `src/glassbox/config.py`

Acceptance criteria:

- Calling `glassbox.init(db_path=...)` creates a run.
- Calling it twice does not create duplicate active contexts.

#### Task 2.2: Implement Function Tracking

Files:

- Create `src/glassbox/decorators.py`
- Create `tests/test_decorators.py`

Acceptance criteria:

- Decorated sync function captures start/end/duration.
- Decorated function return value is captured in redacted/truncated form.
- Decorated function exception is captured and re-raised.
- Nested decorated functions preserve parent/child relationship.

#### Task 2.3: Implement Custom Logs And Tags

Files:

- Modify `src/glassbox/__init__.py`
- Modify `src/glassbox/context.py`
- Modify `tests/test_decorators.py`

Acceptance criteria:

- `glassbox.log("name", data)` writes a custom event.
- `glassbox.tag("x")` updates run tags without duplicates.

---

## Phase 3: Redaction And Data Safety

### Objective

Make sensitive-data handling deliberate before capturing AI calls.

### Deliverables

- Default redaction layer.
- Truncation layer.
- Tests for common secret patterns.

### Tasks

#### Task 3.1: Implement Redaction

Files:

- Create `src/glassbox/redaction.py`
- Create `tests/test_redaction.py`

Acceptance criteria:

- API-key-like strings are redacted.
- Env-var-looking keys containing `KEY`, `TOKEN`, `SECRET`, `PASSWORD` are redacted.
- Long strings are truncated.
- Nested dict/list structures are handled.

#### Task 3.2: Apply Redaction To Function Capture

Files:

- Modify `src/glassbox/decorators.py`
- Modify `tests/test_decorators.py`

Acceptance criteria:

- Function args and return values are redacted before storage.

---

## Phase 4: AI SDK Capture

### Objective

Capture real AI calls reliably with provider-specific adapters.

### Deliverables

- OpenAI sync client capture.
- Anthropic sync client capture.
- cost estimation.
- graceful behavior when SDKs are not installed.

### Tasks

#### Task 4.1: Pricing Module

Files:

- Create `src/glassbox/pricing.py`
- Create `src/glassbox/pricing.json`
- Create tests in `tests/test_storage.py` or `tests/test_pricing.py`

Acceptance criteria:

- Known model pricing returns input/output cost.
- Unknown model returns `None` cost without failing.

#### Task 4.2: OpenAI Capture

Files:

- Create `src/glassbox/capture/openai.py`
- Create `tests/test_capture_openai.py`

Acceptance criteria:

- Fake OpenAI call writes one `events` row.
- Fake OpenAI call writes one `ai_calls` row.
- Errors are captured and re-raised.
- If OpenAI package is missing, Glassbox still imports.

#### Task 4.3: Anthropic Capture

Files:

- Create `src/glassbox/capture/anthropic.py`
- Create `tests/test_capture_anthropic.py`

Acceptance criteria:

- Fake Anthropic call writes one `events` row.
- Fake Anthropic call writes one `ai_calls` row.
- Errors are captured and re-raised.
- If Anthropic package is missing, Glassbox still imports.

#### Task 4.4: Wire Capture Into Init

Files:

- Modify `src/glassbox/context.py`
- Modify `src/glassbox/__init__.py`

Acceptance criteria:

- `glassbox.init(capture_openai=True, capture_anthropic=True)` installs adapters.
- Capture can be disabled.

---

## Phase 5: CLI

### Objective

Make Glassbox usable before the browser viewer exists.

### Deliverables

- `glassbox doctor`
- `glassbox runs`
- `glassbox export`

### Tasks

#### Task 5.1: CLI Skeleton

Files:

- Create `src/glassbox/cli.py`
- Create `tests/test_cli.py`

Acceptance criteria:

- `glassbox --help` works.
- `glassbox doctor` prints Python version, cwd, database path, and SDK availability.

#### Task 5.2: Runs Command

Files:

- Modify `src/glassbox/cli.py`
- Modify `tests/test_cli.py`

Acceptance criteria:

- `glassbox runs --db path/to/db` lists recent runs.
- Empty database gets a friendly message.

#### Task 5.3: Export Command

Files:

- Modify `src/glassbox/cli.py`
- Modify `tests/test_cli.py`

Acceptance criteria:

- `glassbox export --run <id>` prints JSON for a run and its events.

---

## Phase 6: Viewer Backend

### Objective

Expose the SQLite data through a small local API.

### Deliverables

- FastAPI app.
- JSON endpoints for runs, events, and stats.
- backend tests.

### Tasks

#### Task 6.1: Backend App

Files:

- Create `src/glassbox/viewer_backend.py`
- Create `tests/test_viewer_backend.py`

Acceptance criteria:

- `GET /api/stats` returns run count and event count.
- `GET /api/runs` returns recent runs.
- `GET /api/runs/{id}` returns one run.
- `GET /api/runs/{id}/events` returns event tree data.

#### Task 6.2: Backend Error Handling

Files:

- Modify `src/glassbox/viewer_backend.py`
- Modify `tests/test_viewer_backend.py`

Acceptance criteria:

- Missing database returns friendly setup state.
- Missing run returns 404 with useful message.

---

## Phase 7: Viewer Frontend

### Objective

Create the first useful browser UI.

### Deliverables

- local browser app
- run list
- run detail tree
- AI call detail
- error detail
- copy buttons

### UX Standard

The UI should be calm and operational, not a marketing page.

Avoid:

- oversized hero sections
- decorative cards inside cards
- jargon like "trace" or "span"
- unexplained blank states

Use plain labels:

- "Runs"
- "Steps"
- "AI call"
- "Prompt"
- "Response"
- "Cost"
- "Error"

### Tasks

#### Task 7.1: Viewer App Shell

Files:

- Create `viewer/package.json`
- Create `viewer/src/main.tsx`
- Create `viewer/src/App.tsx`
- Create `viewer/src/styles.css`

Acceptance criteria:

- `npm run build` succeeds.
- App shell has left nav and main content area.

#### Task 7.2: API Client

Files:

- Create `viewer/src/api/client.ts`
- Create `viewer/src/api/types.ts`

Acceptance criteria:

- Frontend types match backend responses.

#### Task 7.3: Runs Page

Files:

- Create `viewer/src/pages/RunsPage.tsx`
- Create `viewer/src/components/RunList.tsx`
- Create `viewer/src/components/RunDetail.tsx`

Acceptance criteria:

- User can select a run.
- User can see duration, status, cost, and event count.

#### Task 7.4: AI Call Detail

Files:

- Create `viewer/src/components/AiCallDetail.tsx`

Acceptance criteria:

- User can see provider, model, prompt, response, latency, token count, and cost.
- User can copy prompt.
- User can copy response.

#### Task 7.5: Error Detail

Files:

- Create `viewer/src/components/ErrorDetail.tsx`

Acceptance criteria:

- User can see error message and source location.
- User can copy a clean debugging prompt.

---

## Phase 8: `glassbox view`

### Objective

Make the viewer launchable from the CLI.

### Deliverables

- `glassbox view`
- backend starts locally
- browser opens
- viewer build is served

### Tasks

#### Task 8.1: Serve Viewer Assets

Files:

- Modify `src/glassbox/viewer_backend.py`
- Modify packaging config in `pyproject.toml`

Acceptance criteria:

- Built viewer assets are included in package.
- FastAPI serves frontend routes.

#### Task 8.2: Implement View Command

Files:

- Modify `src/glassbox/cli.py`

Acceptance criteria:

- `glassbox view --db ./glassbox.db --port 4747` starts local server.
- If port is busy, the command explains how to choose another port.

---

## Phase 9: Examples And Dogfooding

### Objective

Prove V1 works on real usage, not just tests.

### Deliverables

- examples
- dogfood notes
- README quickstart

### Tasks

#### Task 9.1: Example Apps

Files:

- Create `examples/simple_tracked_app.py`
- Create `examples/simple_openai_app.py`
- Create `examples/simple_anthropic_app.py`

Acceptance criteria:

- Each example has instructions.
- Tracked example works without API keys.
- AI examples fail gracefully if API keys are missing.

#### Task 9.2: README Quickstart

Files:

- Modify `README.md`

Acceptance criteria:

- New user can install, instrument, run, and view without extra explanation.

#### Task 9.3: Dogfood On One Real Project

Files:

- Create `DOGFOODING.md`

Acceptance criteria:

- Document what worked.
- Document what confused the user.
- Document missing V1 polish.

---

## Phase 10: V1 Release Gate

### Objective

Decide whether V1 is ready to tag.

### Release Checklist

V1 can be released only if:

- `ruff check .` passes.
- `pytest` passes.
- viewer build passes.
- at least one no-key example works.
- at least one real AI-call example works with a real key.
- README quickstart has been followed on a clean machine or clean virtual environment.
- redaction tests pass.
- package can be installed locally.
- no test fixture contains real secrets.
- `CHANGELOG.md` has an entry.
- `DECISIONS.md` reflects current architecture.

### V1 Tag

Release as:

```text
v0.1.0-alpha.1
```

This should be framed as an alpha for friendly testers, not a public v1.0.

---

## Professional Team Habits

### Decision Log

Every important decision goes into `DECISIONS.md`.

Examples:

- why Python first
- why Vite vs Next.js
- why manual tracking first
- why SQLite schema shape changed
- why replay was excluded from V1

### Changelog

Every user-facing change goes into `CHANGELOG.md`.

Use sections:

- Added
- Changed
- Fixed
- Security

### Pull Request Standard

Even if working solo, use PR-sized chunks mentally:

- one phase or sub-phase per branch
- tests included
- docs updated
- screenshots for UI changes
- migration notes for schema changes

### Test Standard

Each behavior gets at least one test at the lowest useful level.

Do not over-test implementation details.

Must test:

- schema migration
- event insertion
- run lifecycle
- nested tracking
- exception tracking
- redaction
- AI capture adapters with fake clients
- CLI output
- backend endpoints

### Documentation Standard

Docs should explain:

- what is captured
- where data is stored
- how to disable capture
- how redaction works
- what remains local
- how to delete `glassbox.db`
- known limitations

---

## What "Professional" Means Here

Professional does not mean slow.

It means:

- every phase leaves the product working
- every risky behavior has a test
- every important decision is written down
- every user-facing command has a clear error path
- every data-capture feature treats privacy seriously
- every release can be reproduced

The goal is still to move quickly. The difference is that the product should get more trustworthy with every commit.

---

## Immediate Next Step

Create the actual `glassbox` repository and execute Phase 0 only.

Do not start AI capture first.
Do not start the viewer first.
Do not start the System Map.

Start with the boring foundation:

1. package installs
2. CLI opens
3. tests run
4. CI exists
5. decision log exists

That is how this becomes a company-grade product instead of a pile of clever code.

