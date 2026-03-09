"""BlessingPlugin dataclass definition."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


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
