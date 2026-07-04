---
applyTo: '**'
---

**Operational Directives: All Environments Protocol**

**Note:** Always read and follow the nearest applicable `AGENTS.md` (repo root plus any folder-local `AGENTS.md`). When instructions conflict, the most specific `AGENTS.md` takes precedence.

1. **Preflight Environment Check (Required):**
   - If on Windows/WSL, stop and recommend switching to Linux.
   - Detect whether execution is inside a container before relying on `/etc/os-release` alone.
   - PixelArch container is the permissive environment.
   - Any non-PixelArch environment is high risk.

2. **Execution Rules (Environment-Gated):**
   - PixelArch container: full command access is allowed for repo work.
   - High-risk environments: ask for explicit approval before side-effectful actions.

3. **Local Rules Discovery (Required):**
   - Before editing any file, locate applicable `AGENTS.md` files in scope.
   - Follow most specific instructions first.

4. **Tooling + Network:**
   - Use repo-approved tooling: `uv` for Python, `bun` for Node.
   - In PixelArch permissive mode, dependency installs are allowed.
   - In high-risk environments, ask before installs or system changes.

5. **Change Documentation Protocol:**
   - Upon completing a change, provide a concise commit message recommendation in markdown code fences.

6. **Planning/Notes Review Protocol:**
   - At the start, middle, and end of complex work, review `.agents/implementation/` and `.agents/instructions/` for relevant guidance.
   - Keep updates minimal and only when needed for correctness.

7. **Temp Files + Cleanup Protocol:**
   - Write temporary artifacts and screenshots to `/tmp/agents-artifacts/` unless explicitly instructed otherwise.
   - Do not add temporary outputs to git.

8. **Compliance Reporting Protocol:**
   - Include a short compliance section only for PR descriptions/reviews or when explicitly requested.

---

## Repository Overview

Stained Glass Odyssey Idle is an idle/incremental game featuring characters from the shared Stained Glass universe.

### Directory Structure
- `.agents/` - Contributor guides and process documentation
  - `modes/` - Contributor mode documentation
  - `instructions/` - Process notes and guidelines
  - `implementation/` - Technical documentation
  - `lore/`, `notes/`, `planning/`, `review/`, `testing/`, `temp/`
- `.github/` - Workflows and agent configurations
- `.feedback/` - Planning notes and priorities (read-only unless instructed)

## Required Startup Rules

- Read `.github/copilot-instructions.md` before starting work.
- Read `/tmp/agents-artifacts/agent-output.md` before work and again before appending.
- Append a run summary to `/tmp/agents-artifacts/agent-output.md` after each run.
- Create `/tmp/agents-artifacts/agent-output.md` if missing.

Required run-log fields:
- role
- files touched
- intent
- actions taken
- results
- blockers/follow-ups

## Contributor Modes

Mandatory: read the required mode guide in `.agents/modes/` before work.

Available modes:
- `MANAGER.md`
- `CODER.md`
- `REVIEWER.md`
- `AUDITOR.md`
- `STORYTELLER.md`

Mode selection rule: if a request begins with a mode name, use that mode unless explicitly told otherwise.

## Instruction Conflict Resolver (GitHub vs Direct Messages)

When instructions conflict, apply this algorithm after higher-priority system/developer/platform rules:

1. Collect candidate instructions with immutable IDs.
2. Compute `effective_timestamp_utc` from metadata only:
   - GitHub: `updated_at`, fallback `created_at`
   - Direct message: server `received_at`
3. Compare normalized UTC timestamps (`YYYY-MM-DDTHH:MM:SSZ`): newest wins.
4. If equal, apply tie-breakers in order:
   - valid `SUPERSEDES` block
   - GitHub source
   - higher immutable ID
5. If timestamps differ by <= 60 seconds and no valid `SUPERSEDES` exists, request clarification before acting.
6. Log the decision in the response:
   - `Applied: <source> <id> @ <UTC>; Superseded: <source> <id>.`

## Development Standards

- Use `uv` for Python and `bun` for Node.
- Do not update `README.md`.
- Verification-first: confirm current behavior before changes; verify after changes.
- No broad fallback behavior unless explicitly requested.
- No compatibility shims unless explicitly requested.
- Keep logs/docs minimal unless required for debugging or crash prevention.

### Python Style
- One import per line.
- Group and sort imports by standard/third-party/project.
- Avoid inline imports.
- Place `from ... import ...` statements after `import ...` statements.

### File Size
- Soft max ~500 lines per file.
- Hard max 1000 lines per file.

## Testing Standards

- Do not add or build tests unless explicitly requested.
- When requested, run tests via `uv run pytest`.
- Prefer targeted tests during iteration.

## UI Rules

Persistent Qt styles must live in `endless_idler/ui/theme/`.
Do not add persistent inline `setStyleSheet(...)` or monolithic theme files outside the theme module structure.
