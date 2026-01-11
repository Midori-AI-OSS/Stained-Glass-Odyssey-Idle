# Verify Stack Merge Animation Separation

## Description
Confirm that stack merge animations (`MergeFxOverlay` and `MergeArrow`) are completely separate from battle screen animations (`LineOverlay`). This ensures we can safely modify one without affecting the other.

## Requirements
- Review `MergeFxOverlay` class in `/endless_idler/ui/party_builder_merge_fx.py`
- Review `MergeArrow` class in `/endless_idler/ui/party_builder_merge_fx.py`
- Trace usage of `MergeFxOverlay` in `/endless_idler/ui/party_builder.py`
- Verify there's no shared code or inheritance between battle and merge animations
- Confirm different parent widgets/contexts for the two animation systems

## Acceptance Criteria
- [x] Confirmed `MergeFxOverlay` is only used in party builder (not battle)
- [x] Confirmed `LineOverlay` is only used in battle (not party builder)
- [x] Verified no shared base classes or common rendering code
- [x] Documented the isolation boundary between the two systems

## Notes
This verification is critical to ensure we don't accidentally break stack merge animations when removing battle lines/arrows. These should be completely independent systems.

Do NOT make any code changes in this task - this is verification only.

## Status Updates
- 2025-01-11: Task created by Task Master
- 2025-01-11: Verification completed. Documentation created at `.codex/implementation/battle-vs-merge-animation-separation.md`. Confirmed complete isolation between systems.
