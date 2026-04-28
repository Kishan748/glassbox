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
