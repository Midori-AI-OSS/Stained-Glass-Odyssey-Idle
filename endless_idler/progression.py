from __future__ import annotations

from endless_idler.characters.metadata import DEFAULT_BASE_STATS
from endless_idler.save import RunSave

DEATH_STAT_BONUS_RATE = 0.0001  # 0.01%
DEATH_STAT_EXCLUDED_KEYS = frozenset(
    {
        "exp",
        "exp_gain",
        "exp_multiplier",
        "mitigation",
        "passive_pot",
        "req_multiplier",
        "vitality",
    }
)


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

    apply_death_stat_bonus(stats)


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
