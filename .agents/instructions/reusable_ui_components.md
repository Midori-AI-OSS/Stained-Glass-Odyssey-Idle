# Reusable UI Components

## Animated Progress Bar
Use `AnimatedProgressBar` for all progress indicators in the application.

**When to use:**
- Any progress visualization (HP, EXP, cooldowns, loading, etc.)
- Status indicators that benefit from smooth animations
- Components requiring visual feedback for state changes

**Configuration options:**
- `set_value(progress)`: Set progress (0.0-1.0)
- `set_shimmer(intensity)`: Set shimmer effect (0.0-1.0)
- `set_reset_mode(active)`: Enable/disable reset animation
- `set_color_thresholds(thresholds)`: Configure progress-based color changes
- `set_gradient_colors(start, mid, end)`: Customize aurora gradient

**Best practices:**
- Use color thresholds for meaningful state changes
- Keep shimmer subtle (0.3-0.6) for most applications
- Use reset mode for temporary state indicators
- Prefer smooth transitions over instant changes
- Maintain consistent color scheme with game elements

**Examples:**

1. **Health Bar with Color Thresholds**:
```python
# Change color at specific thresholds
health_bar.set_color_thresholds([
    (0.0, (231, 76, 60, 170)),    # Red for 0-29% (critical)
    (0.3, (241, 196, 15, 185)),   # Yellow for 30-69% (low)
    (0.7, (46, 204, 113, 165)),   # Green for 70-100% (healthy)
])
```

2. **Experience Bar with Gradient**:
```python
# Smooth gradient transition
exp_bar.set_gradient_colors(
    start_color=(52, 152, 219, 170),    # Blue start
    mid_color=(155, 89, 182, 175),     # Purple middle
    end_color=(231, 76, 60, 170)       # Red end
)
```

3. **Cooldown Bar with Shimmer**:
```python
# Subtle shimmer effect
cooldown_bar.set_shimmer(0.4)
```

4. **Progress Bar with Reset Animation**:
```python
# Enable reset mode for temporary effects
progress_bar.set_reset_mode(True)
```

## Tooltip
Use `show_stained_tooltip()` for contextual information displays with glass-morphism styling.

**When to use:**
- Contextual information displays (item descriptions, stat explanations)
- Element-specific visual feedback (damage type indicators)
- Hover interactions requiring frosted glass effects

**Configuration options:**
- `show_stained_tooltip(owner, html, element_id)`: Display tooltip (element_id: `fire`/`ice`/`lightning`/`wind`/`dark`/`light`/`generic`)
- `hide_stained_tooltip()`: Clear active tooltip

**Best practices:**
- Prefer dynamic `element_id` from context (e.g., `stats.element_id`)
- Keep HTML content concise (1-3 lines)
- Always call `hide_stained_tooltip()` before new content
- Maintain screen-bound positioning (auto-handled by implementation)

**Examples:**

1. **Dynamic Element ID** (typical usage):
```python
show_stained_tooltip(self, self._tooltip_html, element_id=stats.element_id)
```

2. **Static Context** (simplified example):
```python
show_stained_tooltip(self, "<b>Fire Damage</b>", element_id="fire")
```