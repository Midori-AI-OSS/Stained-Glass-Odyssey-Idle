# Review Documentation

This folder contains review notes and findings from documentation audits.

## Purpose

The `.codex/review/` folder holds review notes created by contributors in Reviewer Mode. These notes document findings from documentation audits and identify areas that need updates.

## Guidelines

- **Reviewer Mode Only**: Only contributors in Reviewer Mode should create files in this folder
- Use random hash prefixes for filenames: `abcd1234-review-note.md`
- Generate the hash with: `openssl rand -hex 4`
- Each review note should be comprehensive and actionable

## Review Note Format

```markdown
# Review: [Area/Topic]

## Date
YYYY-MM-DD

## Reviewer
[Your name/identifier]

## Scope
What was reviewed (e.g., documentation in .codex/implementation/, AGENTS.md, etc.)

## Findings
- Finding 1: Description of issue or concern
- Finding 2: Description of issue or concern
- Finding 3: Description of issue or concern

## Recommendations
- Recommendation 1: Suggested action
- Recommendation 2: Suggested action

## Follow-up Tasks
List any tasks created in `.codex/tasks/taskmaster/` as a result of this review
```

## Relationship to Tasks

Significant findings from reviews should result in task files created in `.codex/tasks/taskmaster/` with the `TMT-` prefix, allowing the Task Master to prioritize and assign them.

## Archiving

When review findings have been fully addressed:
- Mark the review note with a resolution section
- Move it to an archive subdirectory if needed
- Keep the audit trail for future reference
