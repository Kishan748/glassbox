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
