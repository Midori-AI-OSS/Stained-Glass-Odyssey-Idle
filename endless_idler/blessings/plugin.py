"""BlessingPlugin dataclass definition."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from typing import Any


def _default_shimmer_formula(seconds_to_next: float) -> float:
    if seconds_to_next > 30:
        return 0.0
    if seconds_to_next <= 5:
        return 1.0
    return (30.0 - seconds_to_next) / 25.0


@dataclass(frozen=True, slots=True)
class BlessingPlugin:
    """A blessing plugin that provides idle progression bonuses.

    Blessings accumulate multipliers over time based on step intervals.
    The multiplier_formula is called with the current step count and returns
    the total multiplier to apply to idle gains.

    Attributes:
        blessing_id: Unique identifier for the blessing
        display_name: Human-readable name for the blessing
        description: Description of what the blessing does
        step_seconds: Interval between each step in seconds (e.g., 300.0 for 5 minutes)
        multiplier_formula: Callable that takes step count and returns multiplier
        max_steps: Optional maximum number of steps before capping
        target_damage_type: Damage type this blessing affects (fire, ice, wind, lightning, light, dark)
        is_unlocked: Whether the blessing is unlocked
        unlock_condition: Description of how to unlock the blessing
        is_persistent: Whether this blessing saves across sessions
        save_schema: Fields to save: {"steps": int, "unlocked": bool}
    """

    blessing_id: str
    display_name: str
    description: str
    step_seconds: float
    multiplier_formula: Callable[[int], float]
    max_steps: int | None = None
    target_damage_type: str | None = None
    is_unlocked: bool = True
    unlock_condition: str | None = None
    is_persistent: bool = True
    save_schema: dict[str, type] = field(default_factory=dict)
    tooltip_formatter: Callable[[int, dict[str, Any]], str] | None = None
    shimmer_formula: Callable[[float], float] | None = None

    def get_multiplier(self, steps: int) -> float:
        """Calculate the multiplier for a given step count.

        Args:
            steps: The current step count

        Returns:
            The multiplier value to apply to idle gains
        """
        if self.max_steps is not None:
            steps = min(steps, self.max_steps)
        return float(self.multiplier_formula(steps))

    def format_tooltip(self, steps: int, context: dict[str, Any]) -> str:
        """Generate tooltip HTML for this blessing.

        Args:
            steps: Current step count
            context: Dictionary containing:
                - save: RunSave instance (for persistent blessings)
                - runtime: {"steps", "progress", "countdown_seconds", "step_seconds"}

        Returns:
            HTML string for tooltip display
        """
        if self.tooltip_formatter is not None:
            return self.tooltip_formatter(steps, context)
        return self._default_tooltip(steps, context)

    def _default_tooltip(self, steps: int, context: dict[str, Any]) -> str:
        """Default tooltip for damage-type blessings."""
        runtime = context.get("runtime", {}) if isinstance(context, dict) else {}
        if not isinstance(runtime, dict):
            runtime = {}
        try:
            progress = float(runtime.get("progress", 0.0))
        except (TypeError, ValueError):
            progress = 0.0
        progress = max(0.0, min(1.0, progress))
        try:
            current_step = max(0, int(runtime.get("steps", steps)))
        except (TypeError, ValueError):
            current_step = max(0, int(steps))
        bonus_pct = (current_step * 0.0001) * 100
        return (
            f"<b>{self.display_name}</b><br>"
            f"EXP gain: <b>+{bonus_pct:.2f}%</b><br>"
            f"Progress: <b>{progress * 100.0:.1f}%</b>"
        )

    def get_shimmer_intensity(self, seconds_to_next: float) -> float:
        if self.shimmer_formula is not None:
            return float(self.shimmer_formula(seconds_to_next))
        return _default_shimmer_formula(seconds_to_next)
