# Legacy UI Guardrails

This folder contains quarantined legacy UI code.

## Rules

- Never modify files in this folder during normal feature work.
- Read-only usage is allowed for reference when building new UI behavior.
- If behavior must be ported, implement it in active modules outside `ui/legacy`.
- Keep new runtime paths out of `ui/legacy`; active flows must continue to use current idle-first modules.

