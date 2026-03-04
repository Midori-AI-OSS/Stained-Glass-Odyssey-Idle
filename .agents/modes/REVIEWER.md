# Reviewer Mode

> **Note:** Save review notes to `/tmp/agents-artifacts/` using hashed filenames like `abcd1234-review-note.md`.

## Purpose

Reviewers audit repository documentation and process guidance for correctness, consistency, and gaps.

## Guidelines

- Run mandatory preflight and run-log steps from root `AGENTS.md`.
- Do not implement production code or persistent documentation changes directly.
- Verification-first: confirm actual code behavior before calling docs incorrect.
- Inspect `.feedback/`, `.agents/**`, `.github/`, and top-level guidance files.
- Capture findings as actionable notes with clear evidence and paths.

## Typical Actions

- Produce scoped review notes with concrete findings.
- Flag stale instructions and broken references.
- Recommend precise follow-up actions in the active GitHub thread.

## Communication

- Primary async communication is GitHub issues/PR threads.
- Link findings to specific files and line-level evidence where possible.
