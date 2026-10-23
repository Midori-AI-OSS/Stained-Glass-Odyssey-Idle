# Coder Mode

> **Note:** Prefer code and docstrings as the source of truth. Keep notes minimal and task-scoped in `/tmp/agents-artifacts/` when needed.

## Purpose

Coders implement, refactor, and fix code with a focus on correctness, maintainability, and clear verification.

## Guidelines

- Follow repository standards and applicable `AGENTS.md` files.
- Run mandatory preflight and run-log steps from root `AGENTS.md`.
- Verification-first: confirm current behavior before changing code, then verify the fix.
- Keep diffs focused; avoid unrelated refactors.
- Use `uv` for Python and `bun` for Node/React tooling.
- Do not update `README.md`.
- Do not add/build tests unless explicitly requested.
- Commit frequently with clear `[TYPE]` commit messages.

## Typical Actions

- Implement requested features or bug fixes.
- Refactor for readability/performance when in scope.
- Run targeted checks relevant to the change.
- Surface blockers quickly in the active GitHub thread.

## Communication

- Primary async communication is GitHub issues/PR threads.
- Direct Lead Developer/Programmer instructions are valid and follow repository precedence rules.
- Summarize changes and verification evidence in commits/PR updates.
