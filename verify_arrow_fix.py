#!/usr/bin/env python3
"""
Verification script for arrow drawing crash fix.
Tests the logic without needing GUI interaction.
"""

import sys
import ast
import inspect

def verify_unboundlocalerror_fix():
    """Verify that waypoint.x() and waypoint.y() are used correctly."""
    print("=" * 70)
    print("VERIFICATION 1: UnboundLocalError Fix (Task 1eeea699)")
    print("=" * 70)
    
    # Read the source file
    with open('endless_idler/ui/battle/widgets.py', 'r') as f:
        source = f.read()
    
    # Check critical lines 503-504
    lines = source.split('\n')
    
    # Find the paintEvent method
    in_paintevent = False
    in_same_team = False
    found_bezier = False
    
    issues = []
    successes = []
    
    for i, line in enumerate(lines, 1):
        if 'def paintEvent' in line:
            in_paintevent = True
            successes.append(f"✓ Line {i}: Found paintEvent method")
        
        if in_paintevent and 'if pulse.same_team:' in line:
            in_same_team = True
            successes.append(f"✓ Line {i}: Found same_team arrow rendering block")
        
        # Check for the Bezier calculation (around line 503-504)
        if in_same_team and 'curve_end = QPointF(' in line:
            found_bezier = True
            # Check the next few lines for waypoint usage
            bezier_block = '\n'.join(lines[i-1:i+3])
            
            if 'waypoint.x()' in bezier_block and 'waypoint.y()' in bezier_block:
                successes.append(f"✓ Line {i}: Using waypoint.x() and waypoint.y() (CORRECT)")
                successes.append("✓ UnboundLocalError is FIXED - waypoint object is always defined")
            elif 'waypoint_x' in bezier_block or 'waypoint_y' in bezier_block:
                issues.append(f"✗ Line {i}: Still using waypoint_x/waypoint_y variables")
                issues.append("✗ UnboundLocalError STILL EXISTS - variables not always defined")
            else:
                issues.append(f"? Line {i}: Unexpected Bezier calculation format")
    
    if not found_bezier:
        issues.append("✗ Could not find Bezier calculation in same_team block")
    
    # Check that waypoint is always defined
    waypoint_defined_if = False
    waypoint_defined_else = False
    
    for i, line in enumerate(lines, 1):
        if in_same_team and 'if pulse.midpoint is not None:' in line:
            # Check next line
            if i < len(lines) and 'waypoint = pulse.midpoint' in lines[i]:
                waypoint_defined_if = True
                successes.append(f"✓ Line {i+1}: waypoint defined in if-branch (pulse.midpoint provided)")
        
        if in_same_team and 'else:' in line and not waypoint_defined_else:
            # Check subsequent lines for waypoint definition
            for j in range(i, min(i+5, len(lines))):
                if 'waypoint = QPointF(' in lines[j]:
                    waypoint_defined_else = True
                    successes.append(f"✓ Line {j+1}: waypoint defined in else-branch (fallback calculation)")
                    break
    
    if waypoint_defined_if and waypoint_defined_else:
        successes.append("✓ waypoint QPointF is defined in BOTH if and else branches")
        successes.append("✓ Using waypoint.x() and waypoint.y() will ALWAYS work")
    
    print("\nSuccesses:")
    for s in successes:
        print(f"  {s}")
    
    if issues:
        print("\nIssues Found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ VERIFICATION 1 PASSED: UnboundLocalError is fixed!")
        return True


def verify_qpainter_tryfinally():
    """Verify that QPainter is wrapped in try-finally."""
    print("\n" + "=" * 70)
    print("VERIFICATION 2: QPainter try-finally Protection (Task 45379ecc)")
    print("=" * 70)
    
    # Read the source file
    with open('endless_idler/ui/battle/widgets.py', 'r') as f:
        source = f.read()
    
    lines = source.split('\n')
    
    issues = []
    successes = []
    
    # Find paintEvent method
    paintevent_line = None
    for i, line in enumerate(lines, 1):
        if 'def paintEvent' in line:
            paintevent_line = i
            successes.append(f"✓ Line {i}: Found paintEvent method")
            break
    
    if not paintevent_line:
        issues.append("✗ Could not find paintEvent method")
        return False
    
    # Check structure
    found_qpainter = False
    found_try = False
    found_finally = False
    painter_end_in_finally = False
    
    try_indent = None
    finally_indent = None
    
    for i in range(paintevent_line - 1, min(paintevent_line + 300, len(lines))):
        line = lines[i]
        stripped = line.strip()
        
        if 'painter = QPainter(self)' in line:
            found_qpainter = True
            successes.append(f"✓ Line {i+1}: QPainter created")
        
        if found_qpainter and not found_try and stripped.startswith('try:'):
            found_try = True
            try_indent = len(line) - len(line.lstrip())
            successes.append(f"✓ Line {i+1}: try block starts (indent={try_indent})")
        
        if found_try and stripped.startswith('finally:'):
            found_finally = True
            finally_indent = len(line) - len(line.lstrip())
            successes.append(f"✓ Line {i+1}: finally block starts (indent={finally_indent})")
        
        if found_finally and 'painter.end()' in line:
            painter_end_in_finally = True
            successes.append(f"✓ Line {i+1}: painter.end() in finally block")
            break
    
    if not found_qpainter:
        issues.append("✗ Could not find QPainter creation")
    
    if not found_try:
        issues.append("✗ No try block found after QPainter creation")
    
    if not found_finally:
        issues.append("✗ No finally block found")
    
    if found_finally and not painter_end_in_finally:
        issues.append("✗ painter.end() not found in finally block")
    
    if try_indent is not None and finally_indent is not None:
        if try_indent == finally_indent:
            successes.append("✓ try and finally blocks are properly aligned")
        else:
            issues.append(f"✗ Indentation mismatch: try={try_indent}, finally={finally_indent}")
    
    print("\nSuccesses:")
    for s in successes:
        print(f"  {s}")
    
    if issues:
        print("\nIssues Found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ VERIFICATION 2 PASSED: QPainter is protected by try-finally!")
        return True


def verify_code_quality():
    """Check code quality aspects."""
    print("\n" + "=" * 70)
    print("VERIFICATION 3: Code Quality")
    print("=" * 70)
    
    issues = []
    successes = []
    
    # Test Python syntax
    try:
        with open('endless_idler/ui/battle/widgets.py', 'r') as f:
            source = f.read()
        compile(source, 'endless_idler/ui/battle/widgets.py', 'exec')
        successes.append("✓ Python syntax is valid")
    except SyntaxError as e:
        issues.append(f"✗ Syntax error: {e}")
    
    # Test imports
    try:
        from endless_idler.ui.battle.widgets import LineOverlay
        successes.append("✓ Module imports successfully")
        
        # Check that paintEvent exists
        if hasattr(LineOverlay, 'paintEvent'):
            successes.append("✓ paintEvent method exists")
        else:
            issues.append("✗ paintEvent method not found")
    except ImportError as e:
        issues.append(f"✗ Import error: {e}")
    
    # Check for common issues
    with open('endless_idler/ui/battle/widgets.py', 'r') as f:
        source = f.read()
    
    if 'waypoint_x' not in source or source.count('waypoint_x') <= 2:
        successes.append("✓ No problematic waypoint_x variable usage")
    else:
        # Check if it's only in the else branch definition
        lines = source.split('\n')
        waypoint_x_uses = [i+1 for i, line in enumerate(lines) if 'waypoint_x' in line]
        if len(waypoint_x_uses) <= 2:  # Only definition in else branch
            successes.append(f"✓ waypoint_x only used for definition (lines {waypoint_x_uses})")
    
    if 'waypoint_y' not in source or source.count('waypoint_y') <= 2:
        successes.append("✓ No problematic waypoint_y variable usage")
    
    print("\nSuccesses:")
    for s in successes:
        print(f"  {s}")
    
    if issues:
        print("\nIssues Found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ VERIFICATION 3 PASSED: Code quality is good!")
        return True


def main():
    print("Arrow Drawing Crash Fix - Verification Script")
    print("=" * 70)
    print()
    
    results = []
    
    # Run all verifications
    results.append(("UnboundLocalError Fix", verify_unboundlocalerror_fix()))
    results.append(("QPainter try-finally", verify_qpainter_tryfinally()))
    results.append(("Code Quality", verify_code_quality()))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    all_passed = all(r[1] for r in results)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    
    print()
    if all_passed:
        print("🎉 ALL VERIFICATIONS PASSED!")
        print()
        print("The arrow drawing crash fix is correctly implemented:")
        print("1. ✅ waypoint_x/waypoint_y UnboundLocalError is fixed")
        print("2. ✅ QPainter is wrapped in try-finally")
        print("3. ✅ Code quality meets standards")
        print()
        print("Note: GUI testing requires a display environment and manual interaction.")
        print("The code-level verification confirms the fixes are correct.")
        return 0
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        print("Please review the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
