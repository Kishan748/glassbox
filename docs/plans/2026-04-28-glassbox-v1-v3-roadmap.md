# Glassbox V1-V3 Roadmap

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Turn the Glassbox PRD into a practical staged roadmap that starts with a useful local product, then grows toward the full comprehension layer for vibe-coded apps.

**Architecture:** Glassbox should start as a local-first Python package with a SQLite event store and a browser viewer. The first version should capture true runtime facts before attempting broad static understanding or replay. Later versions can add richer static analysis, maps, prompt experimentation, JavaScript support, and share/export workflows.

**Tech Stack:** Python 3.10+, SQLite, FastAPI, React/Next.js or Vite React, TypeScript, React Flow, Tailwind, pytest, Playwright for viewer smoke tests.

---

## Executive Summary

Glassbox is practical, but the current PRD is too large for a first release. The right starting point is not "understand every app perfectly." The right starting point is:

> Show a vibe coder what their AI-built app actually did, what prompts were sent, what responses came back, what it cost, where it happened, and what to copy into their AI tool when something breaks.

That is the smallest trustworthy product.

The product should be built in three major versions:

- **V1: Runtime Glassbox** - capture AI calls, tracked functions, errors, costs, and runs.
- **V2: Code Comprehension Glassbox** - add static analysis, file/function browsing, dependency understanding, and a first System Map.
- **V3: Confidence Glassbox** - add prompt playground, run comparison, safety scan, exports, snapshots, and JavaScript/TypeScript support.

The non-negotiable principle: build around facts first. Inferred descriptions, maps, and AI explanations should always be marked as inferred.

---

## Product Wedge

### Target User

Primary user:

- A non-expert builder using Claude Code, Cursor, ChatGPT, Replit, Lovable, Bolt, or similar tools.
- Has working apps they do not fully understand.
- Needs to debug, explain, trust, and safely modify those apps.

Secondary user:

- An engineer prototyping AI-heavy apps who wants local observability without setting up Langfuse, Datadog, OpenTelemetry, or hosted infrastructure.

### Core Promise

"See what your AI-built app did, in plain English, on your own machine."

### First Magic Moment

The first magic moment should happen within 5 minutes:

1. User installs Glassbox.
2. Adds `import glassbox; glassbox.init()` to a Python script.
3. Runs their app.
4. Runs `glassbox view`.
5. Sees a timeline of function steps and AI calls, including prompts, responses, errors, duration, token use, and cost.

Do not make the first magic moment depend on perfect static analysis.

---

## V1: Runtime Glassbox

### Goal

Make Glassbox immediately useful for Python AI apps by capturing real runs, AI calls, manually tracked functions, errors, and costs.

### User Outcome

The user can answer:

- What happened when my app ran?
- Which AI calls did it make?
- What exact prompt did it send?
- What response came back?
- What failed?
- What did it cost?
- Where in my code did that happen?
- What should I paste into Claude Code to fix this?

### Scope

Build Python only.

Include:

- Python package: `glassbox`
- `glassbox.init()`
- `@glassbox.track`
- `glassbox.log`
- `glassbox.tag`
- SQLite schema and migrations
- Capture Anthropic and OpenAI calls
- Capture errors from tracked functions
- Store prompt, response, model, latency, token counts, and estimated cost
- CLI commands:
  - `glassbox runs`
  - `glassbox view`
  - `glassbox doctor`
- Browser viewer:
  - Runs list
  - Run detail tree
  - AI call detail
  - Prompt/response copy buttons
  - Cost summary
  - Error detail
  - Copy-as-prompt for debugging

Exclude:

- JavaScript/TypeScript
- full static analysis
- System Map
- branch tracking
- replay
- snapshots
- Ask Glassbox chat
- semantic search
- full auto-instrumentation

### Why This Comes First

This version captures facts. It avoids the hardest trust problem: inferred maps that may be wrong.

For vibe coders, seeing the actual prompt and response history is already high value. It also creates the data foundation for every later feature.

### V1 Success Criteria

Glassbox V1 is successful when:

- A user can install it and see a captured run in under 5 minutes.
- It works on a small real Python AI app.
- It captures Anthropic and OpenAI calls reliably.
- The viewer makes prompts, responses, errors, and costs easy to inspect.
- The user can copy a useful debugging prompt from any failed run.

### V1 Build Order

#### Phase 1: Repo and Package Skeleton

Create:

- `glassbox-py/pyproject.toml`
- `glassbox-py/src/glassbox/__init__.py`
- `glassbox-py/src/glassbox/cli.py`
- `glassbox-py/src/glassbox/schema.py`
- `glassbox-py/src/glassbox/storage.py`
- `glassbox-py/tests/`

Deliverable:

- `pip install -e ./glassbox-py` works.
- `glassbox doctor` prints environment diagnostics.

#### Phase 2: SQLite Event Store

Create the minimum schema:

- `runs`
- `events`
- `ai_calls`
- `schema_version`

Deliverable:

- Starting and ending a run writes to SQLite.
- Failed runs are marked failed.

#### Phase 3: Python Runtime API

Implement:

- `glassbox.init()`
- `@glassbox.track`
- `glassbox.log`
- `glassbox.tag`

Deliverable:

- A test script can capture nested tracked function calls.

#### Phase 4: AI SDK Capture

Implement:

- Anthropic sync capture
- OpenAI sync capture
- cost calculation from bundled pricing JSON
- prompt/response redaction and truncation

Deliverable:

- Fake SDK tests prove rows are written into `events` and `ai_calls`.

#### Phase 5: CLI Runs View

Implement:

- `glassbox runs`
- `glassbox export --run <id>`

Deliverable:

- User can inspect run summaries from the terminal.

#### Phase 6: Viewer Backend

Implement FastAPI endpoints:

- `GET /api/runs`
- `GET /api/runs/{id}`
- `GET /api/runs/{id}/events`
- `GET /api/events/{id}`
- `GET /api/stats`

Deliverable:

- Backend reads SQLite and returns run data.

#### Phase 7: Viewer Frontend

Implement:

- app shell
- side nav
- run list
- run detail tree
- AI call detail panel
- error detail panel
- copy buttons

Deliverable:

- `glassbox view` opens a local browser UI for real captured runs.

#### Phase 8: V1 Polish

Implement:

- first-run empty state
- sample demo script
- README quickstart
- better redaction defaults
- install sanity checks

Deliverable:

- A new user can get to the first magic moment without help.

---

## V2: Code Comprehension Glassbox

### Goal

Help users understand what their codebase is, not just what happened during a run.

### User Outcome

The user can answer:

- What files are in my app?
- What does each file do?
- What functions exist?
- Which functions ran and which did not?
- Which files call which other files?
- Which env vars and dependencies does this app use?
- Where did this AI call come from?

### Scope

Include:

- Static analyzer for Python
- File inventory
- Function inventory
- Import/call graph
- Dependency extraction
- Env var extraction
- Basic safety scan
- Code Browse view
- Function detail view
- Dependency view
- Keyword search
- `glassbox context` to generate `CONTEXT.md`
- First System Map generated from static structure plus runtime events

Exclude:

- JavaScript/TypeScript static analysis
- deep data-flow analysis
- branch-level runtime stats
- perfect call graph
- semantic search
- full prompt playground
- full run replay

### Why This Comes Second

By V2, Glassbox has real run data. Static analysis can now be grounded in what actually happened.

Instead of saying "this app probably works like this," Glassbox can say:

- "This function exists and ran 37 times."
- "This function exists but has not run yet."
- "This file contains the function that made this AI call."

That is much more trustworthy.

### V2 Success Criteria

Glassbox V2 is successful when:

- `glassbox analyze` works on a real Python project.
- The viewer shows files, functions, dependencies, and env vars.
- Users can click from a runtime AI call to the source function/file.
- `CONTEXT.md` is useful enough to paste into Claude Code.
- The first System Map gives a helpful high-level picture without pretending to be perfect.

### V2 Build Order

#### Phase 1: Python Static Analyzer

Implement:

- project file discovery
- `.gitignore` awareness
- Python `ast` parsing
- file hashes
- source file table
- source function table

Deliverable:

- `glassbox analyze` populates static tables.

#### Phase 2: Code Relationships

Implement:

- imports
- local function calls where easy to resolve
- external calls
- env var references
- dependency manifests

Deliverable:

- Viewer can show file/function relationships.

#### Phase 3: Browse UI

Implement:

- file tree
- file detail
- function list
- function detail
- link runtime events to source locations

Deliverable:

- User can browse their analyzed app in the UI.

#### Phase 4: Context Export

Implement:

- `glassbox context`
- project summary
- key files
- key functions
- recent runs
- recent errors
- AI calls summary
- dependencies and env vars

Deliverable:

- Generated `CONTEXT.md` improves a fresh Claude Code session.

#### Phase 5: First System Map

Implement:

- graph synthesis from files, functions, AI calls, external touchpoints, and outputs
- React Flow visualization
- node detail panel
- "inferred" labels

Deliverable:

- User can understand the app shape visually.

#### Phase 6: Safety Scan Lite

Implement:

- hardcoded secret patterns
- HTTP URLs
- dangerous calls like `eval` and `exec`
- committed `.env` warning
- TODO/HACK scan

Deliverable:

- User gets actionable findings with copy-as-prompt buttons.

---

## V3: Confidence Glassbox

### Goal

Help users compare behavior, experiment safely, share context, and support more app types.

### User Outcome

The user can answer:

- Why did this run behave differently?
- Can I try a prompt change without editing code?
- What changed since the last good run?
- Can I share a safe snapshot of what my app does?
- Can I use this with TypeScript apps?

### Scope

Include:

- Prompt catalog
- Prompt Playground for single AI-call replay
- Run comparison
- Golden runs
- Prompt history
- Shareable HTML export
- Snapshot system
- JavaScript/TypeScript runtime capture
- JavaScript/TypeScript static analysis
- Semantic search
- Ask Glassbox chat

Exclude Until Later:

- production monitoring
- hosted SaaS
- multi-user teams
- RBAC
- OpenTelemetry export
- automatic code modifications

### Why This Comes Third

These are powerful features, but they depend on trust and good underlying data.

Prompt Playground, replay, snapshots, and Ask Glassbox are only useful once Glassbox already has reliable run capture, source links, and enough static context.

### V3 Success Criteria

Glassbox V3 is successful when:

- User can replay a single AI call with edited parameters.
- User can compare two runs and understand meaningful differences.
- User can mark a run as golden.
- User can export safe context for another person.
- User can use Glassbox on a basic Node/TypeScript AI app.

### V3 Build Order

#### Phase 1: Prompt Catalog

Implement:

- prompt fingerprinting
- prompt templates
- model/cost aggregation
- prompt detail page

Deliverable:

- User can see which prompts are used most often and cost most.

#### Phase 2: Single AI-Call Replay

Implement:

- replay endpoint
- editable model/messages/system prompt fields
- streaming response
- replay result stored in SQLite

Deliverable:

- User can experiment with a past AI call safely.

#### Phase 3: Run Comparison

Implement:

- compare two runs
- highlight differences in steps, prompts, models, costs, outputs, and errors
- plain-language summary

Deliverable:

- User can understand why a run differed from a known-good run.

#### Phase 4: Share Export

Implement:

- static HTML export
- redaction controls
- include/exclude prompts and responses
- include/exclude source snippets

Deliverable:

- User can share a read-only version safely.

#### Phase 5: Snapshots

Implement:

- opt-in source snapshots
- snapshot list
- diff two snapshots
- restore with explicit preview

Deliverable:

- User can roll back accidental AI-generated code changes.

#### Phase 6: JavaScript/TypeScript Runtime Capture

Implement:

- npm package
- `init`, `track`, `log`, `tag`
- OpenAI and Anthropic capture
- same SQLite schema

Deliverable:

- Same viewer works for Node/TypeScript apps.

#### Phase 7: JavaScript/TypeScript Static Analyzer

Implement:

- Tree-sitter parsing
- source files/functions/calls
- dependency and env extraction

Deliverable:

- JS/TS apps get Browse and System Map support.

#### Phase 8: Ask Glassbox

Implement:

- local chat drawer
- query recent runs and static tables
- citations to files, functions, runs, and events

Deliverable:

- User can ask plain-language questions about their app.

---

## Recommended Starting Point

Start with a narrow V1 repository, not the full monorepo.

Recommended initial structure:

```text
glassbox/
  README.md
  LICENSE
  pyproject.toml
  src/
    glassbox/
      __init__.py
      cli.py
      capture.py
      decorators.py
      pricing.py
      pricing.json
      redaction.py
      schema.py
      storage.py
      viewer_backend.py
  viewer/
    package.json
    src/
  tests/
    test_storage.py
    test_decorators.py
    test_capture_openai.py
    test_capture_anthropic.py
  examples/
    simple_openai_app.py
    simple_anthropic_app.py
```

Avoid starting with separate `glassbox-py`, `glassbox-js`, `viewer`, and `shared` packages. That monorepo shape is correct later, but it slows down the first useful release.

Start with one Python package and one embedded viewer.

---

## Key Product Decisions

### Decision 1: Python First

Python is the fastest route to a real MVP because:

- many vibe-coded AI apps are Python
- Python has easy monkey-patching
- FastAPI and SQLite are straightforward
- static analysis via `ast` is built in

JavaScript/TypeScript should wait until the product proves value.

### Decision 2: Manual Function Tracking First

Use `@glassbox.track` before auto-instrumentation.

Reason:

- it is predictable
- it avoids noisy traces
- it gives users control
- it builds trust

Auto-instrumentation can come later as an advanced mode.

### Decision 3: Runtime Facts Before Inferred Maps

V1 should avoid pretending to understand everything.

Facts:

- this run happened
- this function ran
- this AI call happened
- this prompt was sent
- this response came back
- this error occurred
- this cost was estimated

Inferences:

- this function means X
- this file is responsible for Y
- this branch is important
- this map explains the whole app

Inferences are useful later, but facts should ship first.

### Decision 4: Single AI-Call Replay Before Full Run Replay

Full run replay is hard because real apps use files, APIs, databases, randomness, clocks, and side effects.

Single AI-call replay is much more practical and still valuable.

Build that first.

### Decision 5: `CONTEXT.md` Is a Killer Feature

The context export may be one of the most useful features for vibe coders.

It directly supports the common workflow:

> "I need to paste my app context into Claude Code and ask it to fix something."

This should ship in V2, possibly earlier.

---

## Major Risks

### Risk 1: Overpromising Zero Config

"Zero config" is a great aspiration but dangerous as a strict promise.

Mitigation:

- V1 requires one import and optional decorators.
- Say "minimal setup" until the product earns "zero config."

### Risk 2: Noisy Function Capture

Capturing every function can overwhelm users.

Mitigation:

- V1 uses manual `@track`.
- Later auto-capture should default to important entry points and AI-related call paths only.

### Risk 3: Incorrect System Maps

Bad maps destroy trust.

Mitigation:

- Ground maps in captured runtime data.
- Mark inferred edges.
- Let the user hide low-confidence nodes.

### Risk 4: Sensitive Data Exposure

Glassbox stores prompts, responses, function args, and errors locally. That can include secrets or customer data.

Mitigation:

- strong default redaction
- local-only messaging
- clear warnings
- redaction tests
- export review screens before sharing

### Risk 5: Packaging Complexity

Bundling Python backend plus web frontend can become a tax.

Mitigation:

- start with a simple viewer build path
- avoid supporting PyPI and npm until Python product is proven
- keep the backend API small

---

## What Not To Build First

Do not start with:

- full System Map
- JS/TS support
- branch runtime tracking
- data-flow diagrams
- semantic search
- Ask Glassbox chat
- snapshots
- full replay
- model-cost optimization suggestions
- beautiful six-area dashboard

Those features are appealing, but they are not the first wedge.

---

## Suggested Milestones

### Milestone A: Local Run Recorder

Time estimate: 3-5 days.

User can:

- install package locally
- call `glassbox.init()`
- use `@glassbox.track`
- run an example app
- inspect captured rows in SQLite

### Milestone B: AI Call Recorder

Time estimate: 4-7 days.

User can:

- capture OpenAI and Anthropic calls
- see prompts/responses/costs in SQLite
- run `glassbox runs`

### Milestone C: First Browser Viewer

Time estimate: 1-2 weeks.

User can:

- run `glassbox view`
- inspect runs in browser
- click into AI calls
- copy prompts/responses/errors

### Milestone D: Useful Alpha

Time estimate: 3-5 weeks total.

User can:

- use Glassbox on a real Python project
- understand runs
- debug errors faster
- share screenshots

### Milestone E: Comprehension Beta

Time estimate: 8-12 weeks total.

User can:

- run static analysis
- browse files/functions/dependencies
- export `CONTEXT.md`
- see a first System Map

---

## Immediate Next Actions

1. Create a new `glassbox` repository.
2. Build only the Python V1 package first.
3. Write one tiny example app that calls Anthropic or OpenAI.
4. Implement SQLite run/event storage.
5. Implement `@glassbox.track`.
6. Implement AI SDK capture.
7. Build `glassbox runs`.
8. Build the smallest browser viewer.
9. Dogfood it on one of Kishan's real projects.
10. Only then decide how much of the System Map belongs in V2.

---

## V1 Definition of Done

V1 is done when a user can:

1. Install Glassbox locally.
2. Add `import glassbox; glassbox.init()`.
3. Add `@glassbox.track` to important functions.
4. Run a Python AI app normally.
5. Run `glassbox view`.
6. See all captured runs.
7. Open a run and inspect each step.
8. Open an AI call and see prompt, response, model, latency, tokens, and cost.
9. Open an error and copy a clean prompt for Claude Code.
10. Trust that all stored data is local.

---

## V2 Definition of Done

V2 is done when a user can:

1. Run `glassbox analyze`.
2. Browse files and functions.
3. See which functions ran and which did not.
4. See dependencies and env vars.
5. Click from a run event to source code context.
6. Generate a useful `CONTEXT.md`.
7. See a basic System Map grounded in real runtime data.

---

## V3 Definition of Done

V3 is done when a user can:

1. See a prompt catalog.
2. Replay and tweak a single AI call.
3. Compare two runs.
4. Mark golden runs.
5. Export a safe HTML snapshot.
6. Use snapshots to restore code.
7. Use Glassbox on Node/TypeScript apps.
8. Ask plain-language questions with citations.

---

## Recommended Positioning

Use this positioning early:

> Glassbox is a local flight recorder for AI-built apps.

Then, once V2 lands:

> Glassbox is a local comprehension layer for AI-built apps.

Avoid leading with:

> Full observability platform.

That sounds too engineer-heavy and invites comparison with mature tools.

---

## Final Recommendation

Build V1 as a narrow, trustworthy runtime recorder.

Make it excellent at:

- capturing AI calls
- showing prompts and responses
- explaining errors
- showing costs
- creating copyable debug context

Then use real dogfooding to decide how much of the static analyzer and System Map should exist in V2.

The full PRD is a compelling north star. The practical starting product is much smaller:

> A local, beautiful, plain-English run viewer for Python AI apps.

