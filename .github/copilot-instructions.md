# Stained Glass Odyssey Idle Development Instructions

**ALWAYS follow these instructions first**. Only search for additional information or run exploration commands if the information here is incomplete or contradicted by actual behavior.

## Repository Overview

Stained Glass Odyssey Idle is an idle/incremental game featuring characters from the shared Stained Glass universe. The game is designed to provide engaging idle gameplay with character progression, resource management, and story elements.

### Directory Structure
- `.codex/` - Documentation and contributor guides
  - `modes/` - Contributor mode documentation
  - `instructions/` - Process notes and guidelines
  - `implementation/` - Technical documentation
  - `tasks/` - Organized task tracking (wip, review, taskmaster)
  - `notes/` - Personal contributor notes
- `.github/` - GitHub workflows and agent configurations
- `.feedback/` - Planning notes and priorities (read-only)

## Required Tools Installation

**CRITICAL**: Always use `uv` for Python and `bun` for Node.js. Never use `pip` or `npm` directly as they are slower and not compatible with the repository's tooling.

### Installing Required Tools

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install bun (JavaScript runtime and package manager)
curl -fsSL https://bun.sh/install | bash
```

## Development Workflow

### 1. Bootstrap and Test the Repository

**MANDATORY**: Always run the full test suite first to understand the current state:

```bash
# Run all tests (if test suite exists)
# TODO: Add test commands once test infrastructure is set up
```

### 2. Building the Application

```bash
# TODO: Add build commands once build infrastructure is set up
```

### 3. Running the Application

```bash
# TODO: Add run commands once application is developed
```

## Contributor Modes

This repository uses a structured contributor mode system. **MANDATORY: All contributors must read their mode's documentation in `.codex/modes/` before starting any work.**

Available modes:
- **Task Master Mode** (`.codex/modes/TASKMASTER.md`) - Task planning and coordination
- **Manager Mode** (`.codex/modes/MANAGER.md`) - Team coordination and process management
- **Coder Mode** (`.codex/modes/CODER.md`) - Code implementation and development
- **Reviewer Mode** (`.codex/modes/REVIEWER.md`) - Code review and feedback
- **Auditor Mode** (`.codex/modes/AUDITOR.md`) - Quality assurance and compliance
- **Storyteller Mode** (`.codex/modes/STORYTELLER.md`) - Narrative and content creation

**Mode selection rule:** When a request begins with the name of a mode, treat that as the required mode for the task unless explicitly told otherwise.

## Task Organization

Tasks are organized in `.codex/tasks/` with three status folders:
- **`wip/`** - Work in progress
- **`review/`** - Ready for review
- **`taskmaster/`** - Awaiting final approval

## Commit and Pull Request Workflow

1. Stage and review your changes locally (`git status`, `git diff`)
2. Create a descriptive commit with appropriate `[TYPE]` prefix (e.g., `[FEAT]`, `[FIX]`, `[DOCS]`)
3. Verify the working tree is clean after committing
4. Create a pull request if there are committed changes

## Code Style Guidelines

### Python Style
- Place each import on its own line
- Sort imports within each group (standard library, third-party, project modules) from shortest to longest
- Insert a blank line between each import grouping
- Avoid inline imports
- For `from ... import ...` statements, group them after all `import ...` statements

Example:
```python
import os
import time
import logging

from datetime import datetime
from rich.console import Console
```

### File Size
- Aim for ~300 lines or fewer per file
- Split monolithic modules into smaller units when they grow beyond this threshold
- Keep code well commented and organized for readability

## Game-Specific Guidelines

### Idle Game Mechanics
- Maintain incremental progression systems
- Balance resource generation and consumption
- Test progression pacing carefully
- Document all game mechanics in `.codex/implementation/`

### Character System
- Keep character implementations consistent with the shared Stained Glass universe
- Document character abilities and progression in `.codex/implementation/`
- Maintain visual consistency with the stained glass aesthetic

### Asset Management
- Follow project art guidelines for all visual assets
- Document asset requirements and specifications
- Keep asset references organized and accessible

## Documentation Standards

- Keep `.codex/implementation/` in sync with code changes
- Update `.codex/instructions/` when processes change
- Document game mechanics, character systems, and progression in detail
- Use markdown format for all documentation

## Testing Standards

- Write tests for all new features
- Maintain high test coverage
- Run targeted tests during development
- Ensure all tests pass before submitting for review

## Best Practices

- Use async/await for I/O and long-running tasks
- Avoid blocking the event loop
- Keep modules focused and under 300 lines
- Write clear, descriptive commit messages
- Break large changes into smaller, reviewable commits
- Self-review code before submitting for review

## Getting Help

- Check `.codex/modes/` for role-specific guidance
- Review `.codex/implementation/` for technical documentation
- Consult `.codex/instructions/` for process guidelines
- Read `AGENTS.md` in any directory before working in it
