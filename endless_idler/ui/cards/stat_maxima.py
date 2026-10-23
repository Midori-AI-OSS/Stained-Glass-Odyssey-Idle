from __future__ import annotations

from dataclasses import dataclass

from endless_idler.combat.stats import Stats


@dataclass(frozen=True, slots=True)
class StatBarSpec:
    key: str
    label: str


STAT_BARS: tuple[StatBarSpec, ...] = (
    StatBarSpec(key="atk", label="Attack"),
    StatBarSpec(key="defense", label="Defense"),
    StatBarSpec(key="atk_speed", label="Atk Speed"),
    StatBarSpec(key="crit_mod", label="Crit Mod"),
    StatBarSpec(key="dodge_odds", label="Dodge"),
    StatBarSpec(key="regain", label="Regain"),
    StatBarSpec(key="mitigation", label="Mitigation"),
)


def compute_stat_maxima(stats_list: list[Stats]) -> dict[str, float]:
    maxima: dict[str, float] = {spec.key: 0.0 for spec in STAT_BARS}
    for stats in stats_list:
        maxima["atk"] = max(maxima["atk"], float(stats.atk))
        maxima["defense"] = max(maxima["defense"], float(stats.defense))
        maxima["atk_speed"] = max(maxima["atk_speed"], float(stats.atk_speed))
        maxima["crit_mod"] = max(maxima["crit_mod"], float(stats.crit_mod))
        maxima["dodge_odds"] = max(maxima["dodge_odds"], float(stats.dodge_odds))
        maxima["regain"] = max(maxima["regain"], float(stats.regain))
        maxima["mitigation"] = max(maxima["mitigation"], float(stats.mitigation))

    for key, value in list(maxima.items()):
        if value <= 0:
            maxima[key] = 1.0
    return maxima
