# Glassbox

Glassbox is a local flight recorder for Python AI apps. V1 focuses on capturing real runtime facts: runs, tracked function calls, AI calls, prompts, responses, errors, timings, and costs.

## Current Status

This repository is in Phase 0: professional project setup.

## Development Quickstart

```bash
python3 -m pip install -e .
python3 -m glassbox --help
pytest
```

## Principles

- Local-first: data stays on the user's machine.
- Facts before inference: V1 records what happened before trying to explain what it means.
- Small public API: keep the first user experience simple.
- Privacy-aware by default: captured data must be redacted and handled deliberately.

See the planning docs in `docs/plans/`.
