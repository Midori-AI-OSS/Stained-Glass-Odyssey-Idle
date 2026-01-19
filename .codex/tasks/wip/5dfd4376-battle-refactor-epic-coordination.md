# Epic: Battle System Refactor - Task Coordination

## Overview
This document tracks the battle system refactor that introduces onsite/offsite rows, shape-rendered foes, wave spawning, atk_speed timing, and wave-only overflow scaling while keeping existing combat math unchanged.

## Task Organization

### Phase 1: Foundation - Timing System (Priority: High)
These tasks establish the new tick-based timing system.

1. **3b475c11-rename-speed-stat-to-atk_speed.md**
   - Rename `spd` to `atk_speed` throughout codebase
   - Update baselines: players=1, foes=2
   - Status: Ready for Coder

2. **d210c1ad-implement-tick-based-action-timing.md**
   - Implement tick-based action intervals (500 ticks per action at atk_speed=1)
   - 10x slower action rate for offsite characters
   - Status: Blocked by #1
   - Dependencies: 3b475c11

3. **a7dfe25e-add-atk_speed-rebirth-scaling.md**
   - Add small atk_speed buffs from rebirth progression
   - Controlled scaling to prevent runaway rates
   - Status: Blocked by #2
   - Dependencies: d210c1ad

### Phase 2: Visual Foundation - Layout (Priority: High)
These tasks change the battle layout and establish shape rendering.

4. **e4c0bb06-refactor-battle-layout-to-horizontal-rows.md**
   - Change to horizontal onsite/offsite rows
   - Reuse existing character containers
   - Status: Ready for Coder (independent)

5. **ea22d177-create-shape-palette-system.md**
   - Create 25 shape templates with geometry definitions
   - Define fill behaviors and properties
   - Status: Ready for Coder (independent)

6. **3d3ed165-implement-foe-shape-selection-logic.md**
   - Deterministic shape selection based on foe stats
   - Same stats → same shape
   - Status: Blocked by #5
   - Dependencies: ea22d177

7. **bf034219-implement-shape-rendering-with-health-fill.md**
   - Render foes as shapes with color and health fill
   - Remove old foe visual system
   - Status: Blocked by #5, #6
   - Dependencies: ea22d177, 3d3ed165

### Phase 3: Battle Flow - Movement and Waves (Priority: High)
These tasks implement foe spawning, movement, and wave mechanics.

8. **8fd957a1-implement-foe-spawning-and-movement.md**
   - Spawn at top, move downward, engage at line
   - Smooth animation and combat trigger
   - Status: Blocked by #7
   - Dependencies: bf034219

9. **0dcdf834-implement-wave-spawning-system.md**
   - Wave triggers: 30s timer OR zero foes
   - Basic wave spawning (no scaling yet)
   - Status: Blocked by #8
   - Dependencies: 8fd957a1

10. **70c89728-implement-wave-spawn-count-time-scaling.md**
    - Scale spawn count by survival time
    - Formula: 1 + 0.15*floor(t/25) + 0.05*floor(t/30)
    - Status: Blocked by #9
    - Dependencies: 0dcdf834

11. **44ea3aa4-implement-foe-cap-and-wave-overflow-scaling.md**
    - Cap at 100 foes
    - Wave-only buff for blocked spawns (1.01 per block)
    - Status: Blocked by #10
    - Dependencies: 70c89728

12. **3aa5ebc3-implement-wave-index-difficulty-ramp.md**
    - Per-wave difficulty: 1.0005^wave_index
    - Persistent within battle, resets on new battle
    - Status: Blocked by #11
    - Dependencies: 44ea3aa4

### Phase 4: Rewards and Penalties (Priority: Medium-Low)
These tasks implement coin rewards and defeat mechanics.

13. **3b475c12-implement-coin-rewards-per-foe-kill.md**
    - Coins per kill: 1 × foe_level
    - Status: Blocked by #8 (needs foes to kill)
    - Dependencies: 8fd957a1

14. **3b475c13-implement-survival-idle-exp-multiplier.md**
    - Idle exp multiplier grows with survival time
    - Resets per battle
    - Status: Ready for Coder (independent)

15. **3b475c14-implement-run-health-loss-on-defeat.md**
    - Run health loss on defeat (5-95%, decreasing with survival)
    - Identify correct run health variable
    - Status: Ready for Coder (independent)

## Dependencies Visualization

```
Timing Chain:
3b475c11 → d210c1ad → a7dfe25e

Visual Chain:
e4c0bb06 (independent, parallel)
ea22d177 → 3d3ed165 → bf034219

Battle Flow Chain:
bf034219 → 8fd957a1 → 0dcdf834 → 70c89728 → 44ea3aa4 → 3aa5ebc3

Rewards Chain:
8fd957a1 → 3b475c12
(independent: 3b475c13, 3b475c14)
```

## Suggested Implementation Order

### Sprint 1: Foundations
1. 3b475c11 (rename to atk_speed)
2. e4c0bb06 (layout refactor) - parallel with #1
3. ea22d177 (shape palette) - parallel with #1-2
4. d210c1ad (tick timing)

### Sprint 2: Visual System
5. 3d3ed165 (shape selection)
6. bf034219 (shape rendering)
7. a7dfe25e (atk_speed scaling)

### Sprint 3: Battle Flow
8. 8fd957a1 (spawning & movement)
9. 0dcdf834 (wave system)
10. 70c89728 (time scaling)

### Sprint 4: Advanced Mechanics
11. 44ea3aa4 (foe cap & overflow)
12. 3aa5ebc3 (wave difficulty)
13. 3b475c12 (coin rewards)

### Sprint 5: Polish
14. 3b475c13 (idle exp)
15. 3b475c14 (run health loss)

## Key Principles (From Original Spec)
- **Keep existing combat math unchanged** (damage, healing, crit, targeting, etc.)
- Only change: layout, rendering, spawning, timing
- Foes remain characters under the hood (stats from existing system)
- Do not expose raw formulas to player
- All acceptance criteria must be met per task

## Notes for Coders
- Each task is self-contained and minimal
- Dependencies are clearly marked
- Test against acceptance criteria before moving to review
- Reference original spec for detailed requirements
- Use existing systems wherever possible (build_foes, combat calculation, etc.)

## Status Legend
- Ready for Coder: No dependencies, can start immediately
- Blocked by: Waiting on another task to complete
- In Progress: Being worked on by a Coder
- In Review: Awaiting Auditor review
- Complete: Merged and closed

---

**Created:** 2025-01-19 (Task Master)
**Last Updated:** 2025-01-19
