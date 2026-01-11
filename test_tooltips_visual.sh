#!/bin/bash
# Visual QA Testing Script for Tooltips
# Uses xdotool to interact with the running application

DISPLAY=:1
export DISPLAY

SCREENSHOT_DIR="/tmp/agents-artifacts"
COUNTER=3

echo "=== Visual QA Testing: Tooltips ==="
echo "Testing both StainedGlassTooltip and QToolTip across all screens"
echo ""

# Function to take a screenshot
take_screenshot() {
    local name="$1"
    local filename="${COUNTER}-${name}.png"
    import -window root "${SCREENSHOT_DIR}/${filename}"
    echo "✓ Captured: ${filename}"
    ((COUNTER++))
    sleep 0.5
}

# Function to move mouse and hover
hover_at() {
    local x="$1"
    local y="$2"
    local desc="$3"
    echo "  Hovering at ($x, $y) - $desc"
    xdotool mousemove "$x" "$y"
    sleep 1.5  # Wait for tooltip to appear
}

# Function to click at coordinates
click_at() {
    local x="$1"
    local y="$2"
    local desc="$3"
    echo "  Clicking at ($x, $y) - $desc"
    xdotool mousemove "$x" "$y"
    sleep 0.3
    xdotool click 1
    sleep 0.8
}

# Get window ID of the application
WINDOW_ID=$(xdotool search --name "Stained Glass Odyssey Idle" | head -1)
if [ -z "$WINDOW_ID" ]; then
    echo "✗ Application window not found!"
    exit 1
fi

echo "Found application window: $WINDOW_ID"
echo ""

# Activate the window
xdotool windowactivate "$WINDOW_ID"
sleep 1

# Get window geometry
eval $(xdotool getwindowgeometry --shell "$WINDOW_ID")
echo "Window geometry: ${WIDTH}x${HEIGHT} at position (${X}, ${Y})"
echo ""

# Calculate center and common positions
CENTER_X=$((X + WIDTH / 2))
CENTER_Y=$((Y + HEIGHT / 2))
TOP_Y=$((Y + 100))
BOTTOM_Y=$((Y + HEIGHT - 100))
LEFT_X=$((X + 100))
RIGHT_X=$((X + WIDTH - 100))

# === TEST 1: Main Menu (if present) ===
echo "=== Test 1: Main Menu / Initial Screen ==="
take_screenshot "initial-screen"

# Try to click "Play" or "Start" button to enter game
click_at "$CENTER_X" "$CENTER_Y" "Start/Play button"
take_screenshot "after-start-click"
sleep 1

# === TEST 2: Party Builder Screen ===
echo ""
echo "=== Test 2: Party Builder Screen ==="
take_screenshot "party-builder-overview"

# Test character tiles (StainedGlassTooltip)
echo "Testing character tiles with StainedGlassTooltip..."

# Hover over left area where party slots typically are
hover_at "$LEFT_X" "$TOP_Y" "Top-left party slot"
take_screenshot "party-slot-topleft-tooltip"

hover_at "$LEFT_X" "$CENTER_Y" "Middle-left party slot"
take_screenshot "party-slot-midleft-tooltip"

hover_at "$LEFT_X" "$BOTTOM_Y" "Bottom-left party slot"
take_screenshot "party-slot-botleft-tooltip"

# Test standby/shop area (right side)
hover_at "$RIGHT_X" "$TOP_Y" "Top-right shop tile"
take_screenshot "shop-tile-topright-tooltip"

hover_at "$RIGHT_X" "$CENTER_Y" "Middle-right shop tile"
take_screenshot "shop-tile-midright-tooltip"

# Test QToolTip elements (party bar elements, buttons)
echo "Testing QToolTip elements in Party Builder..."

# Move to top bar area
hover_at "$CENTER_X" "$TOP_Y" "Top bar element"
take_screenshot "party-bar-top-tooltip"

# Test bottom controls
hover_at "$CENTER_X" "$BOTTOM_Y" "Bottom bar element"
take_screenshot "party-bar-bottom-tooltip"

# === TEST 3: Navigate to Battle Screen ===
echo ""
echo "=== Test 3: Battle Screen ==="

# Look for tabs or battle button
# Try clicking in tab area (typically top of window)
TAB_Y=$((Y + 50))
BATTLE_TAB_X=$((X + 200))

click_at "$BATTLE_TAB_X" "$TAB_Y" "Battle tab/button"
sleep 1
take_screenshot "battle-screen-overview"

# Test combatant cards (StainedGlassTooltip)
echo "Testing combatant cards with StainedGlassTooltip..."

# Hover over enemy/combatant positions
hover_at "$LEFT_X" "$TOP_Y" "Top combatant"
take_screenshot "battle-combatant-top-tooltip"

hover_at "$CENTER_X" "$CENTER_Y" "Center combatant"
take_screenshot "battle-combatant-center-tooltip"

hover_at "$RIGHT_X" "$TOP_Y" "Right combatant"
take_screenshot "battle-combatant-right-tooltip"

# Test QToolTip in battle (stat labels, status messages)
echo "Testing QToolTip in battle screen..."

# Bottom stats area
hover_at "$LEFT_X" "$BOTTOM_Y" "Battle stat label"
take_screenshot "battle-stat-tooltip"

# === TEST 4: Navigate to Idle/Onsite Screen ===
echo ""
echo "=== Test 4: Idle/Onsite Screen ==="

# Try clicking different tab
IDLE_TAB_X=$((X + 100))
click_at "$IDLE_TAB_X" "$TAB_Y" "Idle/Onsite tab"
sleep 1
take_screenshot "onsite-screen-overview"

# Test onsite cards (StainedGlassTooltip)
echo "Testing onsite character cards with StainedGlassTooltip..."

hover_at "$LEFT_X" "$CENTER_Y" "Left onsite card"
take_screenshot "onsite-card-left-tooltip"

hover_at "$CENTER_X" "$CENTER_Y" "Center onsite card"
take_screenshot "onsite-card-center-tooltip"

hover_at "$RIGHT_X" "$CENTER_Y" "Right onsite card"
take_screenshot "onsite-card-right-tooltip"

# Test QToolTip in onsite (stat bars, buttons)
echo "Testing QToolTip in onsite screen..."

hover_at "$CENTER_X" "$TOP_Y" "Onsite stat bar"
take_screenshot "onsite-statbar-tooltip"

hover_at "$CENTER_X" "$BOTTOM_Y" "Onsite button"
take_screenshot "onsite-button-tooltip"

# === TEST 5: Various Background Contexts ===
echo ""
echo "=== Test 5: Testing Tooltips Over Different Backgrounds ==="

# Navigate back to party builder
click_at "$((X + 50))" "$TAB_Y" "Party builder tab"
sleep 1

# Test tooltip over different background colors/elements
hover_at "$((X + WIDTH / 3))" "$((Y + HEIGHT / 3))" "Over light background"
take_screenshot "tooltip-light-bg"

hover_at "$((X + WIDTH * 2 / 3))" "$((Y + HEIGHT / 3))" "Over dark background"
take_screenshot "tooltip-dark-bg"

hover_at "$CENTER_X" "$((Y + HEIGHT * 2 / 3))" "Over bottom area"
take_screenshot "tooltip-bottom-area"

# === Final Overview ===
echo ""
echo "=== Test Complete ==="
take_screenshot "final-state"

echo ""
echo "Testing complete!"
echo "Total screenshots captured: $((COUNTER - 3))"
echo "Screenshots saved to: $SCREENSHOT_DIR"
echo ""
echo "Next steps:"
echo "1. Review all screenshots for visual quality"
echo "2. Check for tooltip visibility and readability"
echo "3. Document any issues found"
