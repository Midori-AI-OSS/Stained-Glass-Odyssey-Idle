# Task: Implement survival idle exp multiplier

## Priority
Low - Enhancement mechanic

## Category
Feature

## Description
Increase idle experience gain multiplier as the party survives in battle. Longer survival means faster idle progression.

## Requirements
1. Multiplier tracking:
   - Track `idle_exp_mult` per battle (starts at 1.0)
   - Every 1 second the party is alive:
     ```
     idle_exp_mult *= 1.00001
     ```

2. Reset condition:
   - Reset `idle_exp_mult` to 1.0 when a new battle starts
   - Multiplier does NOT persist between battles

3. Application:
   - Apply multiplier to idle-mode experience gain
   - Identify existing idle exp calculation
   - Multiply idle exp by `idle_exp_mult`

4. Examples:
   - 0 seconds: idle_exp_mult = 1.0
   - 60 seconds: idle_exp_mult ≈ 1.0006
   - 600 seconds (10 min): idle_exp_mult ≈ 1.006
   - 3600 seconds (1 hour): idle_exp_mult ≈ 1.0366

5. No UI formula display:
   - Do not show raw multiplier formula to player
   - May show current multiplier value (e.g., "Idle XP: 1.05x")

## Acceptance Criteria
- [ ] idle_exp_mult starts at 1.0 on new battle
- [ ] Multiplier increases by 1.00001 every second
- [ ] Multiplier resets to 1.0 on new battle
- [ ] Idle exp gain uses this multiplier
- [ ] At 60 seconds, multiplier is approximately 1.0006
- [ ] No raw formula shown to player

## Dependencies
- None (can be implemented independently)

## Testing
- Start battle, wait 60 seconds, check idle_exp_mult ≈ 1.0006
- Verify idle exp gain increases over time
- Start new battle, verify multiplier resets to 1.0
- Let battle run for 10 minutes, verify continued growth

## Notes
- Very slow growth per second (0.01%)
- Encourages longer survival runs
- Compounds over time but resets per battle
