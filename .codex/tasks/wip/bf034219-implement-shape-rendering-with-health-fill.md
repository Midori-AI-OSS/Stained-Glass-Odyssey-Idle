# Task: Implement shape rendering with health fill

## Priority
High - Visual representation of foes

## Category
Feature

## Description
Implement rendering of foe shapes with color (damage type) and health-based fill. Replace old foe visual system.

## Requirements
1. Create a new widget for shape-based foe rendering (e.g., `ShapeFoeWidget`)

2. Shape rendering features:
   - Draw shape geometry from selected template
   - Apply color based on damage type
   - Show foe name label (generated character name)
   - Implement health-based fill visualization

3. Health fill visualization:
   - Fill ratio = current_hp / max_hp
   - Visual "unfill" as health decreases
   - Use fill_direction from shape template
   - Smooth visual updates as health changes
   - Examples:
     - 100% health: fully filled
     - 50% health: half filled
     - 0% health: empty/outline only

4. Color encoding:
   - Use existing `color_for_damage_type_id` function
   - Apply color to shape fill
   - Consider outline/border for readability

5. Remove old foe visual system:
   - Identify and remove old foe card/portrait rendering
   - Keep the underlying `build_foes` logic (stats generation)

## Acceptance Criteria
- [x] Foes render as shapes, not portraits
- [x] Shape displays foe name (generated character name)
- [x] Shape color matches foe damage type
- [x] Shape fill reflects health ratio (full at 100%, empty at 0%)
- [x] Fill updates smoothly as health changes
- [x] Old foe visual system is removed
- [x] Foe stats generation (build_foes) remains unchanged

## Dependencies
- Requires: ea22d177-create-shape-palette-system.md ✅
- Requires: 3d3ed165-implement-foe-shape-selection-logic.md ✅

## Testing
- Spawn foe at full health, verify full fill
- Damage foe to 50%, verify half fill
- Damage foe to near 0%, verify nearly empty
- Verify different damage types show different colors
- Verify foe name displays correctly

## Notes
- Performance is important; shapes will be drawn frequently
- Consider using QPainter clipping for fill effect
- Smooth interpolation may require animation/update loop

---

## 🔴 AUDIT FEEDBACK - MUST ADDRESS BEFORE RE-SUBMISSION

**Status:** RETURNED TO WIP  
**Auditor:** Auditor Mode  
**Date:** 2024-01-21

### Implementation Quality: ✅ EXCELLENT
The code is **production-ready** - clean, well-tested, follows all coding standards. All acceptance criteria met. Great work!

### Process Issues: ❌ WORKFLOW VIOLATIONS
The following process violations must be corrected:

#### 1. ❌ COMMIT CHANGES FIRST
**Problem:** Uncommitted changes detected in git status
- New file: `endless_idler/ui/battle/shape_foe_widget.py`
- Modified: `endless_idler/ui/battle/screen.py`
- Task file moved but not committed

**Required Action:**
```bash
git add endless_idler/ui/battle/shape_foe_widget.py
git add endless_idler/ui/battle/screen.py
git commit -m "[FEAT] Implement shape-based foe rendering with health fill"
git status  # Must show "nothing to commit, working tree clean"
```

#### 2. ❌ MANUAL GUI VERIFICATION REQUIRED
**Problem:** No evidence of visual testing. This is a **visual feature** that must be manually verified.

**Required Action:** Launch the application and verify:
- [ ] Shapes render correctly (not broken/invisible)
- [ ] Health fill works (test at 100%, 50%, 10% health)
- [ ] Different damage types show different colors
- [ ] Names display under shapes
- [ ] Shapes update smoothly when health changes
- [ ] All three fill directions work (bottom_up, left_right, center_out)

Document verification in completion notes with specific observations.

#### 3. ℹ️ WORKFLOW CLARIFICATION
**Note:** Tasks should move: `wip/` → `review/` → `taskmaster/` (not to `done/`)
- After fixing above issues, move to `review/` folder
- Auditor will then review and move to `taskmaster/` if approved

---

### What to Do Next

1. ✅ **Commit your changes** (see command above)
2. ✅ **Run manual GUI test** (launch app, verify rendering)
3. ✅ **Document verification** in COMPLETION_NOTES
4. ✅ **Move task to `.codex/tasks/review/`** (not done/)
5. ✅ **Commit the task move** with `[DOCS]` prefix

Once completed, the auditor will review and approve for taskmaster.

---

**Full audit report available at:** `.codex/tasks/done/AUDIT_REPORT_bf034219.md`
