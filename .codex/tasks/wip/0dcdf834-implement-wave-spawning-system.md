# Task: Implement wave spawning system

## Priority
High - Core battle flow

## Category
Feature

## Description
Implement wave-based foe spawning with two trigger conditions: 30-second timer or zero foes alive.

## Requirements
1. Wave trigger conditions (either triggers spawn):
   - **Timer**: 30 seconds since last wave spawn
   - **Clear**: Zero foes alive

2. Wave tracking:
   - Track time since last wave spawn
   - Track current foe count
   - Spawn new wave when either condition is met
   - Reset timer after spawning

3. Implementation:
   - Add wave spawn timer to battle state
   - Check conditions in battle update loop
   - When triggered, spawn new wave of foes
   - Do NOT delay spawning if both conditions are met

4. Spawn count:
   - Use existing baseline spawn count from game
   - Do NOT implement scaling yet (that's a separate task)
   - Log wave spawn events for debugging

## Acceptance Criteria
- [ ] New wave spawns after 30 seconds
- [ ] New wave spawns when foes reach zero
- [ ] Timer resets after wave spawn
- [ ] Both conditions work independently
- [ ] Existing spawn logic is reused
- [ ] Wave spawns are logged or visible

## Dependencies
- Requires: 8fd957a1-implement-foe-spawning-and-movement.md

## Testing
- Start battle, wait 30 seconds, verify new wave spawns
- Kill all foes before 30 seconds, verify immediate new wave
- Verify timer resets after each wave
- Verify waves spawn continuously

## Notes
- This task establishes the wave system foundation
- Scaling and overflow handling come in separate tasks
- Keep spawn count simple for now (baseline only)
