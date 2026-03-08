# Repository Contributor Guide

This document summarizes contributor practices for the Stained Glass Odyssey Idle repository.

---

## Quick Start

- Run locally: `uv run main.py`
- UI code lives in `endless_idler/ui/`
- Preflight is required: read `.github/copilot-instructions.md` before any work
- Do not update `README.md`
- Keep changes focused and minimal

## Required Preflight and Run Log

All contributors must do the following for every run:

1. Read `.github/copilot-instructions.md` before starting.
2. Read `/tmp/agents-artifacts/agent-output.md` before work (and again before appending).
3. Append a short run entry to `/tmp/agents-artifacts/agent-output.md` after work.
4. Create `/tmp/agents-artifacts/agent-output.md` if it does not exist.
5. Use append-only writes (`>>`), never overwrite prior entries.

Required run-log fields:
- role
- files touched
- intent
- actions taken
- results
- blockers or follow-ups

## Where to Look for Guidance

- `.agents/`: contributor guidance and supporting docs
  - `modes/`: contributor mode documentation
  - `implementation/`: technical implementation notes
  - `instructions/`: process guidance
  - `lore/`, `notes/`, `planning/`, `review/`, `testing/`, `temp/`
- `.feedback/`: planning notes and priorities (read-only unless explicitly instructed)
- `.github/`: automation and agent configuration
- When entering any folder, check for a local `AGENTS.md` and follow the most specific one.

## Development Basics

- Use `uv` for Python commands. Avoid `python` or `pip` directly.
- Use `bun` for Node/React tooling.
- Run `uv sync --group ci` once at the start of a work session before lint/type/test commands.
- Standard validation flow:
  - `uv run ruff check .`
  - `uv run basedpyright`
  - `uv run pytest -q` (or targeted tests when appropriate)
- Verification-first: confirm current behavior before changing code; verify fix behavior after changes.
- No broad fallback behavior unless explicitly required.
- No backward-compatibility shims unless explicitly required.
- Prefer code and docstrings over long-lived documentation artifacts.
- Do not update `README.md`.
- Keep I/O and long-running work async-friendly where applicable.

### Python Style

- Place each import on its own line.
- Sort imports within each group from shortest to longest.
- Insert a blank line between standard library, third-party, and project imports.
- Avoid inline imports.
- Put `from ... import ...` after `import ...` statements.

## UI Theme Architecture (Mandatory)

- All persistent Qt styling must live in `endless_idler/ui/theme/`.
- Theme ownership rule: one reusable widget class per theme module in `endless_idler/ui/theme/`.
- Theme assembly must be explicit through `endless_idler/ui/theme/registry.py` imports.
- Every new themable `objectName` or style-driving property must ship with a selector in the owning theme module.
- When changing a style-driving property at runtime, repolish (`unpolish/polish/update`).

### Prohibited UI Patterns

- Do not add persistent inline `setStyleSheet(...)` styling.
- Do not add `!important` style overrides for normal UI components.
- Do not add monolithic theme files or persistent styles outside `endless_idler/ui/theme/`.
- Do not use soft-compliance placeholders such as:
  - `TODO: update standards later`
  - `follow-up agent will fix theme`
  - `temporary standards exception`

### Review Gates (Fail Conditions)

- Missing theme module for a new reusable widget class.
- Missing registry wiring for a new theme module.
- Missing selector coverage for a new themable `objectName` or dynamic property.
- Any new persistent inline widget stylesheet.

## File Size and Readability

- Soft max: ~500 lines per file.
- Hard max: 1000 lines per file.
- Split monolithic modules as they approach the soft limit.
- Keep code readable and organized.

## Commit Workflow

1. Review local changes (`git status`, `git diff`).
2. Create a descriptive commit with `[TYPE]` prefix (for example `[FEAT]`, `[FIX]`, `[DOCS]`, `[REFACTOR]`).
3. Confirm a clean working tree after committing.
4. Do not push unless explicitly requested.

## Contributor Modes

Read the relevant mode guide in `.agents/modes/` before starting work:

- `MANAGER.md`
- `CODER.md`
- `REVIEWER.md`
- `AUDITOR.md`
- `STORYTELLER.md`

Mode selection rule: if a request starts with a mode name, use that mode unless explicitly told otherwise.

## Game-Specific Guidelines

Stained Glass Odyssey Idle is an idle/incremental game in the shared Stained Glass universe.

  - Maintain idle progression systems.
  - Keep visual style consistent with stained glass aesthetics.
  - Prefer code and docstrings for documentation; keep notes minimal and scoped.
  - Verify game balance and progression impacts.
  - Ensure character assets follow project art guidelines.
  - Gameplay progression must not use hard caps; only soft caps are allowed and only when explicitly requested.
