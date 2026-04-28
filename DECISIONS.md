# Decisions

This file records important product and engineering decisions.

## 2026-04-28: Build Python V1 First

Glassbox starts as a Python-first local runtime recorder. JavaScript and
TypeScript support are intentionally deferred until the core product value is
proven with Python AI apps.

## 2026-04-28: Use Runtime Facts Before Static Inference

V1 records factual runtime data first: runs, tracked function calls, AI calls,
errors, timings, and costs. Static analysis, inferred descriptions, and System
Map features are deferred to V2.

## 2026-04-28: Use Standard Library CLI For Phase 0

The initial CLI uses `argparse` from the Python standard library to keep the
foundation dependency-light. A richer CLI framework can be considered later if
the command surface grows enough to justify it.

## 2026-04-28: Use Idempotent SQLite Schema Migrations

The local event store is created through an explicit schema migration function
with a `schema_version` table. Phase 1 starts at schema version 1 and treats the
SQLite schema as the contract between storage, capture, CLI, backend, and
viewer code.

## 2026-04-28: Use A Single Active Runtime Context

Phase 2 uses one active process-local runtime context for `glassbox.init()`.
Nested tracked function calls use `contextvars` to preserve parent-child event
relationships without passing context objects through user code.

## 2026-04-28: Redact Before Function Data Reaches Storage

Phase 3 applies redaction and truncation before captured function arguments,
keyword arguments, and return values are written into SQLite. The first pass
uses deterministic local rules for common API-key patterns and secret-like
mapping keys rather than making any network calls or inference requests.

## 2026-04-28: Make AI SDK Capture Explicitly Opt-In

Phase 4 installs OpenAI and Anthropic sync capture adapters only when
`glassbox.init(capture_openai=True, capture_anthropic=True)` requests them.
This keeps imports graceful when SDKs are missing and avoids surprising method
patching for users who only want tracked functions and custom logs.

## 2026-04-28: Keep CLI Export As Plain JSON

Phase 5 exports a run as deterministic JSON containing the run, events, and AI
call rows. This keeps the first export format scriptable and easy to inspect
before the browser viewer exists.

## 2026-04-28: Expose Viewer Data Through A Small FastAPI App

Phase 6 uses FastAPI for the local viewer backend and keeps API responses close
to the SQLite contract: runs, event trees, and aggregate stats. Missing
databases return a setup state instead of creating hidden state.

## 2026-04-28: Use Vite React For The Local Viewer

Phase 7 uses a Vite React TypeScript app for the browser viewer. The frontend
stays as a separate `viewer/` build until Phase 8 wires `glassbox view` and
static asset serving into the Python package.
