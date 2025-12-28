# Task Organization

This folder contains organized tasks for the Stained Glass Odyssey Idle project.

## Folder Structure

Tasks are organized by status:

### `wip/` - Work In Progress
Tasks that are actively being developed by coders. When complete and ready for review, move to the `review/` folder.

### `review/` - Ready for Review
Tasks that are complete and awaiting auditor review. After review:
- If approved, move to the `taskmaster/` folder
- If changes are needed, move back to `wip/` with feedback

### `taskmaster/` - Task Master Review
Tasks that have been fully audited and are awaiting final Task Master sign-off. The Task Master can either:
- Close the task as complete (delete the task file)
- Request additional changes (move back to `wip/` with clarifications)

## Task File Format

Task files should be named with a random hash prefix followed by a descriptive title:
```
1234abcd-task-title.md
```

Generate the hash with:
```bash
openssl rand -hex 4
```

## Task File Template

```markdown
# Task Title

## Description
Clear description of what needs to be done.

## Requirements
- Specific requirement 1
- Specific requirement 2
- Specific requirement 3

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Notes
Any additional context or considerations.

## Status Updates
- YYYY-MM-DD: Status update or note
```

## Workflow

1. **Task Creation**: Task Master creates new tasks in `wip/`
2. **Development**: Coders work on tasks in `wip/` and move them to `review/` when complete
3. **Auditing**: Auditors review tasks in `review/` and move them to `taskmaster/` if approved, or back to `wip/` if changes are needed
4. **Completion**: Task Master reviews tasks in `taskmaster/` and closes them when satisfied
