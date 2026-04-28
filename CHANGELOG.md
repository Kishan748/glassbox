# Changelog

All notable changes to Glassbox will be documented in this file.

The format is based on Keep a Changelog, and this project follows semantic
versioning once public releases begin.

## Unreleased

### Added

- Added Playwright browser smoke coverage for the viewer run-inspection and
  copy-debug-prompt path.
- Added `glassbox demo` to create a deterministic local sample run with fake AI
  prompt and response data for first-run viewer testing.
- Added copyable selected-event debug prompts for pasting Glassbox context into
  coding assistants.
- Added selectable viewer event rows with an event detail panel for captured
  data, source location, errors, and AI-call prompts/responses.
- Added context manager support for `glassbox.init()` so short scripts can mark
  runs completed or failed without an explicit `context.close()`.

### Changed

- Expanded `glassbox doctor` with database-path and packaged-viewer asset
  sanity checks.
- Improved viewer empty states for missing databases and empty or wrong
  database paths.
- Clarified README guidance for tracked function data versus real AI-call
  prompt and response capture.

## 0.1.0-alpha.1 - 2026-04-28

### Added

- Created the initial project foundation for Glassbox V1.
- Added planning documents for the V1-V3 roadmap and professional V1 build.
- Added minimal Python package, CLI entry point, tests, and CI configuration.
- Added SQLite storage, runtime tracking, redaction, AI SDK capture, CLI run
  inspection/export, FastAPI viewer backend, and Vite React viewer frontend.
- Added `glassbox view` to serve the packaged viewer and local API.
- Added tracked, OpenAI, and Anthropic examples plus dogfooding notes.
