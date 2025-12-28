# Audit Documentation

This folder contains comprehensive audit reports and quality assurance findings.

## Purpose

The `.codex/audit/` folder holds detailed audit reports created by contributors in Auditor Mode. These reports document comprehensive code, documentation, and process reviews.

## Guidelines

- **Auditor Mode Only**: Only contributors in Auditor Mode should create files in this folder
- Use random hash prefixes for filenames: `abcd1234-audit-summary.audit.md`
- Generate the hash with: `openssl rand -hex 4`
- Reserve this folder for in-depth reports that require a persistent home
- Routine task checks should be recorded in the task file itself

## When to Create Audit Reports

Create audit reports in this folder when:
- Conducting multi-day investigations
- Tracking findings across multiple tasks or releases
- Documenting systemic issues that span multiple areas
- Creating historical audit records

For routine task checks, update the originating task file instead of creating a separate audit report.

## Audit Report Format

```markdown
# Audit: [Area/Topic]

## Date
YYYY-MM-DD

## Auditor
[Your name/identifier]

## Scope
What was audited (systems, code areas, documentation, etc.)

## Methodology
How the audit was conducted

## Findings

### Critical Issues
- Issue 1: Description, impact, and reproduction steps
- Issue 2: Description, impact, and reproduction steps

### Important Issues
- Issue 1: Description and recommendations
- Issue 2: Description and recommendations

### Minor Issues
- Issue 1: Description
- Issue 2: Description

### Positive Observations
- What's working well
- Best practices observed

## Recommendations
1. Recommendation 1: Detailed action items
2. Recommendation 2: Detailed action items

## Follow-up Actions
- List of tasks created or issues filed
- Responsible parties
- Target completion dates

## Conclusion
Summary of overall findings and priority of recommendations
```

## Relationship to Tasks and Reviews

- **Tasks** (`.codex/tasks/`): Day-to-day work items
- **Reviews** (`.codex/review/`): Documentation audit findings
- **Audits** (`.codex/audit/`): Comprehensive quality assurance reports

Audit findings may result in:
- New tasks in `.codex/tasks/`
- Documentation updates
- Process improvements
- Follow-up audits

## Archiving

Keep audit reports for historical reference even after issues are resolved. They provide valuable context for future work and help track quality trends over time.
