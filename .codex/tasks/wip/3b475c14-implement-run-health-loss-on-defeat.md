# Task: Implement run health loss on defeat

## Priority
Medium - Core defeat mechanic

## Category
Feature

## Description
On battle loss, reduce run health based on survival time. Longer survival means less health lost.

## Requirements
1. Identify run health:
   - **ACTION REQUIRED**: Before implementing, search the codebase for run health variable
   - Look in `endless_idler/save.py` for `RunSave` class definition
   - Search for "run.*health" or "health" in save-related files
   - Common patterns: `run_hp`, `health`, `current_health`, `hp`
   - **Do not proceed with implementation until variable is confirmed**

2. Loss formula:
   - Loss amount depends on survival time
   - Function must be:
     - Monotonic decreasing (longer survival → less loss)
     - Clamped: max 95% loss, min 5% loss (never below 0% total)
   - Example implementation:
     ```python
     survival_seconds = time_survived_in_battle
     # Linear scaling example:
     loss_percent = 95 - (survival_seconds / 10)  # -1% per 10 seconds
     loss_percent = max(5, min(95, loss_percent))  # clamp to [5, 95]
     
     new_run_health = run_health * (1 - loss_percent / 100)
     ```

3. Apply on loss:
   - Trigger when party is defeated (all onsite characters at 0 hp)
   - Calculate survival time from battle start to defeat
   - Apply loss formula
   - Update run health in save

4. Tuning:
   - **FINALIZE FORMULA**: The exact formula must be chosen before implementation
   - Formula MUST meet: monotonic decreasing, max 95%, min 5%
   - **Suggested concrete formula**: `loss_percent = max(5, min(95, 100 - (survival_seconds * 0.3)))`
     - At 10s: 97% loss (high penalty for quick defeat)
     - At 100s: 70% loss
     - At 300s: 10% loss
     - At 317s: 5% loss (minimum, floors here)
   - **Adjust coefficients if needed** but document the chosen formula in code comments

5. No formula display:
   - Do not show raw formula to player
   - May show "Run Health Lost: X%" message

## Acceptance Criteria
- [ ] Correct run health variable identified and used
- [ ] Loss formula is monotonic decreasing with survival time
- [ ] Maximum loss is 95% (when survival time is very short)
- [ ] Minimum loss is 5% (when survival time is very long)
- [ ] Loss never reduces run health below 0
- [ ] Loss applies on party defeat
- [ ] No raw formula shown to player

## Dependencies
- None (independent of wave/timing refactor)

## Testing
- Lose battle at 10 seconds, verify high loss (~90%+)
- Lose battle at 300 seconds, verify low loss (~5%)
- Verify run health cannot go below 0
- Verify loss is applied to persistent run health

## Notes
- Formula may need tuning based on typical survival times
- Consider logarithmic or exponential decay for smoother scaling
- Minimum 5% loss ensures defeat always has consequence
