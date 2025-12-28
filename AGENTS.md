# Repository Contributor Guide

This document summarizes common development practices for the Stained Glass Odyssey Idle game repository.

---


## Where to Look for Guidance

- **`.feedback/`**: Task lists and priorities. *Read only*—never edit directly unless you are the Task Master.
- **`.codex/`**:
  - `instructions/`: Contributor mode docs, process notes, and service-specific instructions. Place all new and updated process documentation here, following the structure and naming conventions. See examples in this folder.
  - `implementation/`: Technical implementation notes and documentation. Keep these in sync with code changes.
  - `modes/`: Contributor mode documentation defining roles and responsibilities.
  - `tasks/`: Organized task folders (wip, review, taskmaster) for work items.
  - Other subfolders: For planning, notes, and prototyping.
- **Never edit files in `.codex/audit/` unless you are in Auditor mode.**
- **`.github/`**: Workflow guidelines, agent configurations, and automation scripts.
- When entering any folder, check for a `AGENTS.md` file in that folder and read it before starting any work there.

---

## Development Basics

- Use [`uv`](https://github.com/astral-sh/uv) for Python environments and running code. Avoid `python` or `pip` directly.
- Use [`bun`](https://bun.sh/) for Node/React tooling instead of `npm` or `yarn`.
- Split large modules into smaller ones when practical and keep documentation in `.codex/implementation/` in sync with code.
- Ensure code is asynchronous-friendly: avoid blocking the event loop, use async/await for I/O and long-running tasks, and keep work off the main loop.
- Any test running longer than 15 seconds is automatically aborted in local development. GitHub Actions CI has no timeout limits.
- For Python style:
   - Place each import on its own line.
   - Sort imports within each group (standard library, third-party, project modules) from shortest to longest.
   - Insert a blank line between each import grouping (standard library, third-party, project modules).
   - Avoid inline imports.
   - For `from ... import ...` statements, group them after all `import ...` statements, and format each on its own line, sorted shortest to longest, with a blank line before the group. Example:

     ```python
     import os
     import time
     import logging
     import threading

     from datetime import datetime
     from rich.console import Console
     ```

## File Size and Readability (Repository-wide Rule)

- Aim for ~300 lines or fewer per file.
- Split monolithic modules into smaller units when they grow beyond this threshold.
- Keep code well commented and organized for readability.

---

## Commit and Pull Request Workflow

Follow this checklist whenever you are ready to publish work:

1. Stage and review your changes locally (`git status`, `git diff`) before committing.
2. Create a descriptive commit that begins with the appropriate `[TYPE]` prefix (e.g., `[FEAT]`, `[FIX]`, `[DOCS]`, `[REFACTOR]`).
3. Verify the working tree is clean after committing—`git status` must show **no pending changes**.
4. If you did not modify the repository, do **not** commit or create a pull request.

These steps apply to **all** contributor modes.

---

## Task Organization System

Tasks are organized by status into three main folders in `.codex/tasks/`:

### Status Folders

- **`wip/`** - Work In Progress: Tasks actively being developed by coders. When complete and ready for review, move to the corresponding subfolder in `review/`.
- **`review/`** - Ready for Review: Tasks awaiting auditor review. After review, move to `taskmaster/` if approved, or back to `wip/` with feedback if changes are needed.
- **`taskmaster/`** - Task Master Review: Tasks fully audited and awaiting final Task Master sign-off. The Task Master can either close the task (delete the file) or request additional changes (move back to `wip/`).

### Workflow

1. **Task Creation**: Task Master creates new tasks in the appropriate category subfolder within `wip/`
2. **Development**: Coders work on tasks in `wip/` and move them to `review/` when complete
3. **Auditing**: Auditors review tasks in `review/` and move them to `taskmaster/` if approved, or back to `wip/` if changes are needed
4. **Completion**: Task Master reviews tasks in `taskmaster/` and closes them when satisfied

---

## Contributor Modes

The repository supports several contributor modes to clarify expectations and best practices for different types of contributions:

> **MANDATORY: All contributors must read their mode's documentation in `.codex/modes/` before starting any work. Failure to do so may result in removal from the repository.**

**Mode selection rule:** When a request begins with the name of a mode (e.g., "Manager", "Coder", "Reviewer"), treat that as the required mode for the task unless explicitly told otherwise. Switch to that mode's instructions before continuing.

**All contributors should regularly review and keep their mode cheat sheet in `.codex/notes/` up to date.**
Refer to your mode's cheat sheet for quick reminders and update it as needed.

- **Task Master Mode** (`.codex/modes/TASKMASTER.md`)
- **Manager Mode** (`.codex/modes/MANAGER.md`)
- **Coder Mode** (`.codex/modes/CODER.md`)
- **Reviewer Mode** (`.codex/modes/REVIEWER.md`)
- **Auditor Mode** (`.codex/modes/AUDITOR.md`)
- **Storyteller Mode** (`.codex/modes/STORYTELLER.md`)

You must refer to the relevant mode guide in `.codex/modes/` before starting work, and follow the documentation structure and conventions described there.

---

## Game-Specific Guidelines

Stained Glass Odyssey Idle is an idle/incremental game featuring characters from the shared Stained Glass universe. When contributing:

- Maintain the idle game mechanics and incremental progression systems
- Keep the visual style consistent with the stained glass aesthetic
- Document all game mechanics, progression systems, and character implementations in `.codex/implementation/`
- Test game balance and progression carefully
- Ensure all character artwork and assets follow the project's art guidelines
