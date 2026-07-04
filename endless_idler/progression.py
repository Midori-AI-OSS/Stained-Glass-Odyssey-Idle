from __future__ import annotations

from endless_idler.characters.metadata import DEFAULT_BASE_STATS
from endless_idler.save import RunSave


DEATH_STAT_BONUS_RATE = 0.0001  # 0.01%
REBIRTH_LEVEL_THRESHOLD = 500
PROGRESSION_STAR_MULTIPLIERS: dict[int, float] = {
    5: 0.5,
    6: 1.0,
    7: 2.5,
}
DEATH_STAT_EXCLUDED_KEYS = frozenset(
    {
        "exp",
        "exp_gain",
        "exp_multiplier",
        "mitigation",
        "passive_modifier",
        "req_multiplier",
        "vitality",
    }
)


def validate_progression_stars(stars: int) -> int:
    try:
        value = int(stars)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid progression stars {stars!r}; expected one of 5, 6, 7."
        ) from exc
    if value not in PROGRESSION_STAR_MULTIPLIERS:
        raise ValueError(f"Invalid progression stars {value}; expected one of 5, 6, 7.")
    return value


def progression_star_multiplier(stars: int) -> float:
    return PROGRESSION_STAR_MULTIPLIERS[validate_progression_stars(stars)]


def calculate_rebirth_power(level: int) -> float:
    level = max(REBIRTH_LEVEL_THRESHOLD, int(level))
    return 1.0 + 0.15 * float(level - REBIRTH_LEVEL_THRESHOLD)


def calculate_rebirth_exp_mult_gain(*, power: float, stars: int) -> float:
    return (0.01 + (max(0.0, float(power)) * 0.000005)) * progression_star_multiplier(
        stars
    )


def calculate_rebirth_exp_tax(*, level: int, rebirth_power: float, stars: int) -> float:
    level_value = max(1, int(level))
    power = max(1.0, float(rebirth_power))
    if level_value < REBIRTH_LEVEL_THRESHOLD:
        return 1.0

    step_multiplier = 1.25 + (0.05 * power)
    steps = max(0, (level_value - REBIRTH_LEVEL_THRESHOLD) // 5)
    raw_tax = step_multiplier**steps
    if raw_tax <= 1.0:
        return 1.0

    effective_tax = 1.0 + ((raw_tax - 1.0) / (progression_star_multiplier(stars) + 1.0))
    return max(1.01, effective_tax)


def calculate_prestige_stat_gain_rate(prestige_count: int, stars: int) -> float:
    count = max(0, int(prestige_count))
    return 0.001 * (2.0**count) * progression_star_multiplier(stars)


def record_character_death(
    save: RunSave,
    *,
    char_id: str,
    base_stats_template: dict[str, float] | None = None,
) -> None:
    char_id = str(char_id or "").strip()
    if not char_id:
        return

    deaths = getattr(save, "character_deaths", None)
    if not isinstance(deaths, dict):
        deaths = {}
        save.character_deaths = deaths
    deaths[char_id] = max(0, int(deaths.get(char_id, 0))) + 1

    template = (
        base_stats_template
        if isinstance(base_stats_template, dict)
        else DEFAULT_BASE_STATS
    )
    stats = save.character_stats.get(char_id)
    if not isinstance(stats, dict):
        stats = dict(template)
        save.character_stats[char_id] = stats
    else:
        for key, value in template.items():
            if key not in stats and isinstance(value, (int, float)):
                stats[key] = float(value)

    initial_stats = getattr(save, "character_initial_stats", {}) or {}
    if not isinstance(initial_stats, dict):
        initial_stats = {}
        save.character_initial_stats = initial_stats
    initial_for_char = initial_stats.get(char_id)
    if not isinstance(initial_for_char, dict):
        initial_for_char = dict(template)
        initial_stats[char_id] = initial_for_char
    else:
        for key, value in template.items():
            if key not in initial_for_char and isinstance(value, (int, float)):
                initial_for_char[key] = float(value)

    apply_death_stat_bonus(stats)
    apply_death_stat_bonus(initial_for_char)


def apply_death_stat_bonus(stats: dict[str, float]) -> None:
    multiplier = 1.0 + float(DEATH_STAT_BONUS_RATE)
    for key, value in list(stats.items()):
        if key in DEATH_STAT_EXCLUDED_KEYS:
            continue
        if not isinstance(key, str):
            continue
        if not isinstance(value, (int, float)):
            continue
        stats[key] = float(value) * multiplier
