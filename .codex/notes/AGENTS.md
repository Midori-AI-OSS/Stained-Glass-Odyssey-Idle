# Personal Contributor Notes

This folder is for personal contributor notes and cheat sheets.

## Purpose

The `.codex/notes/` folder is a workspace for contributors to keep their own notes, reminders, and quick reference guides. This is particularly useful for maintaining mode-specific cheat sheets and personal development notes.

## What to Store Here

- **Mode Cheat Sheets**: Quick reference guides for your contributor mode(s)
- **Personal TODO Lists**: Your own task tracking and reminders
- **Learning Notes**: Notes from documentation or code exploration
- **Command References**: Frequently used commands and shortcuts
- **Troubleshooting Notes**: Solutions to problems you've encountered

## Organization

Each contributor should create their own files, preferably with their name or identifier to avoid conflicts:
```
username-coder-cheatsheet.md
username-notes.md
username-commands.md
```

## Note Privacy

- These notes are committed to the repository and visible to all contributors
- Do not include sensitive information like passwords or API keys
- Keep notes professional and focused on development

## Example Cheat Sheet Format

```markdown
# [Your Name] - Coder Mode Cheat Sheet

## Quick Commands
- Build: `./build.sh`
- Test: `./run-tests.sh`
- Lint: `ruff check . --fix`

## Common Tasks
- Starting a new task: Check `.codex/tasks/wip/`
- Submitting for review: Move task to `.codex/tasks/review/`

## Personal Reminders
- Always run tests before committing
- Update documentation when changing code
- Follow the commit message format

## Useful References
- Game mechanics: `.codex/implementation/game-mechanics.md`
- Code style: `AGENTS.md`
```
