# Task: Fix Tooltip Issues from QA (If Needed)

**Status**: Work In Progress  
**Priority**: Medium  
**Category**: UI/Tooltips/Bug Fix  
**Task ID**: 6c9d6121

## Objective

Address any issues, bugs, or improvements identified during the tooltip visual QA testing (task 10422986). This task may not be needed if QA passes without issues.

## Background

This is a contingency task for addressing problems found during QA. It should only be activated if the QA task (10422986) identifies issues that need fixing.

## Scope

This task covers fixes for:
- Visual artifacts or rendering issues
- Text readability problems
- Layout or positioning bugs
- Inconsistencies between tooltip types
- Performance issues (flicker, jitter)
- Edge cases or context-specific problems

## Process

1. **Review QA Findings**: Read `.codex/tasks/wip/10422986-tooltip-qa-findings.md`
2. **Prioritize Issues**: Sort by severity (Critical > High > Medium > Low)
3. **Fix Critical Issues First**: Address blocking problems immediately
4. **Iterate on High/Medium Issues**: Make adjustments as needed
5. **Re-test After Fixes**: Verify fixes don't introduce new problems
6. **Document Changes**: Update implementation notes

## Common Issues & Solutions

### Issue: Text Unreadable
**Solutions:**
- Increase background alpha slightly (e.g., from 35 to 45)
- Add text shadow: `text-shadow: 1px 1px 2px rgba(0, 0, 0, 180);`
- Increase text color alpha (e.g., from 235 to 250)
- Add a subtle dark gradient behind text area

### Issue: Tooltip Too Transparent
**Solutions:**
- Increase background alpha value
- Add a subtle darker tint to the background color
- Increase border opacity/brightness
- Add a subtle backdrop layer (semi-transparent solid)

### Issue: Element Tint Not Visible (StainedGlassTooltip)
**Solutions:**
- Increase element tint alpha in `_apply_element_tint()`
- Adjust tint color brightness/saturation
- Add a subtle glow effect with the element color

### Issue: Visual Artifacts or Rectangle Outlines
**Solutions:**
- Ensure `WA_TranslucentBackground` attribute is set
- Check for conflicting stylesheets
- Verify no solid color is bleeding through
- Adjust widget composition or layering

### Issue: Tooltips Clip Off-Screen
**Solutions:**
- Review positioning logic in `show_near_cursor()`
- Add additional boundary checks
- Reduce tooltip size if too large
- Adjust offset values

### Issue: Flicker or Jitter
**Solutions:**
- Add debounce to hover events
- Reduce update frequency in `_refresh_background()`
- Check for rapid show/hide cycles
- Optimize rendering performance

### Issue: Inconsistent Appearance Between Tooltip Types
**Solutions:**
- Match alpha values between StainedGlassTooltip and QToolTip
- Use similar tint colors
- Align border radius and border styling
- Ensure similar padding and text styles

## Implementation Approach

1. Create separate sub-tasks if there are multiple unrelated issues
2. Fix one issue at a time and re-test
3. Commit fixes incrementally with descriptive messages
4. Update QA findings document with fix status
5. Request re-testing after all fixes are complete

## Acceptance Criteria

- [ ] All critical issues are resolved
- [ ] All high-priority issues are resolved
- [ ] Medium and low-priority issues are resolved or deferred
- [ ] Fixes are tested and verified
- [ ] No new issues introduced by fixes
- [ ] Code changes are documented
- [ ] QA findings document is updated with fix status
- [ ] Ready for Auditor review

## Testing After Fixes

- [ ] Re-test all affected tooltip locations
- [ ] Verify fixes don't break working tooltips
- [ ] Check for performance regressions
- [ ] Confirm visual consistency maintained
- [ ] Test edge cases and unusual contexts

## Notes

- This task may not be needed if QA passes cleanly
- If QA identifies only minor issues, they may be fixed directly in QA task
- Critical issues should be fixed immediately before moving to review
- Document all changes in commit messages and implementation notes
- Consider creating a follow-up polish task for non-blocking improvements

## Related Files

- `endless_idler/ui/tooltip.py` - StainedGlassTooltip implementation
- `endless_idler/ui/theme.py` - QToolTip stylesheet
- `.codex/tasks/wip/10422986-tooltip-qa-findings.md` - QA results

## Estimated Effort

Variable (30 minutes to 3 hours depending on issues found)

## Dependencies

- Requires completion of task `10422986-visual-qa-tooltip-styling.md`
- May require iteration with Auditor feedback
- Should be completed before moving tasks to review status
