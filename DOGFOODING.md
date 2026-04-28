# Dogfooding Notes

## 2026-04-28 Phase 9

### What Worked

- The no-key example creates a complete local run with tracked functions, a custom log, and a tag.
- `python3 -m glassbox runs --db glassbox.db` gives a quick terminal confirmation that capture worked.
- `python3 -m glassbox view --db glassbox.db --port 4747` serves the packaged viewer without a separate Node process.
- Missing API keys for AI examples are handled before SDK imports or network calls.
- The post-alpha context manager keeps short scripts readable and closes runs automatically.

### What Was Confusing

- AI examples need separate SDK installs, which is reasonable for V1 but needs very plain README guidance.
- The viewer and CLI both read `glassbox.db`, so examples should always print the exact view command they expect users to run.

### Missing V1 Polish

- `glassbox view` could show a clearer empty state if the database path is wrong.
- The viewer should eventually expose copyable install/run commands for the selected example.
