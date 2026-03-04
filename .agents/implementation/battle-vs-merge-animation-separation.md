# Battle vs Merge Animation System Separation

## Overview
This document verifies that the battle screen animation system (`LineOverlay`) and the party builder merge animation system (`MergeFxOverlay`, `MergeArrow`) are completely separate and independent.

## Battle Animation System

### Components
- **File**: `endless_idler/ui/battle/widgets.py`
- **Classes**:
  - `LinePulse` (dataclass, lines 29-42): Stores animation state
  - `LineOverlay` (lines 263-450+): Widget that renders attack/healing lines
  - `Arena` (lines 565-620+): Contains LineOverlay as `self._overlay`

### Usage
- **Used by**: `endless_idler/ui/battle/screen.py`
- **Call sites**: Lines 479, 557, 590, 648, 694, 702
- **Purpose**: Visual feedback for attacks, healing, and critical hits in battle

### Characteristics
- Renders straight attack lines and curved healing arrows
- Uses tick-based animation (30ms timer)
- Pulse duration: 220ms (normal), 440ms (wrong-way healing)
- Line widths: 3px (normal), 6px (critical)

## Party Builder Merge Animation System

### Components
- **File**: `endless_idler/ui/party_builder_merge_fx.py`
- **Classes**:
  - `MergeArrow` (lines 20-74): Widget that draws a single arrow
  - `MergeFxOverlay` (lines 76-164): Widget that orchestrates merge animations

### Usage
- **Used by**: `endless_idler/ui/party_builder.py`
- **Instantiation**: Line 160 (`merge_fx = MergeFxOverlay(self)`)
- **Purpose**: Visual feedback when characters are merged/stacked in party builder

### Characteristics
- Renders white arrows with arrowheads
- Uses QPropertyAnimation for fade-in/fade-out
- Animation duration: 520ms
- Includes dissolve effect for merged character sprites

## Verification Results

### ✅ No Shared Code
- `LineOverlay` and `MergeFxOverlay` are in completely different files
- No common base classes beyond QWidget
- No shared helper methods or utilities
- No imports between the two systems

### ✅ Different Parent Contexts
- `LineOverlay` is used in `Arena` (battle/widgets.py) → Battle Screen
- `MergeFxOverlay` is used in `PartyBuilderScreen` (party_builder.py) → Party Builder

### ✅ Different Animation Mechanisms
- Battle: Timer-based tick system with manual painting
- Merge: Qt's QPropertyAnimation with automatic rendering

### ✅ Different Visual Characteristics
- Battle: Colored elemental lines, varying widths, fading alpha
- Merge: White arrows with arrowheads, opacity animations

## Conclusion

**The two animation systems are completely isolated and independent.**

Modifications to `LineOverlay` (battle animations) will NOT affect `MergeFxOverlay` or `MergeArrow` (merge animations).

This means we can safely:
1. Add a configuration flag to disable battle animations
2. Modify `LineOverlay.paintEvent()` to skip rendering
3. Keep the tick mechanism for cleanup

**Without any risk of breaking stack merge animations in the party builder.**

## Related Tasks
- Task edc6b187: Verify stack merge animation separation (THIS DOCUMENT)
- Task 983ed6db: Analyze LineOverlay usage (COMPLETED)
- Task c27c66d4: Add config flag for battle animations (NEXT)
- Task 95f5b1c9: Implement conditional rendering (AFTER FLAG)
- Task 0bf94f2a: Test battle without animations (FINAL)
