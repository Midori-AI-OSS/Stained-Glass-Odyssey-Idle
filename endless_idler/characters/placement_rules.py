from __future__ import annotations


VALID_PLACEMENTS = frozenset({"onsite", "offsite", "both"})
ONSITE_PLACEMENTS = frozenset({"onsite", "both"})
OFFSITE_PLACEMENTS = frozenset({"offsite", "both"})

MISPLACED_EXP_MULTIPLIER = 0.25
MISPLACED_STAT_MULTIPLIER = 0.05


def normalize_placement(value: object) -> str:
    placement = str(value or "").strip().lower()
    if placement in VALID_PLACEMENTS:
        return placement
    return "both"


def lane_allows_placement(*, lane: str, placement: object) -> bool:
    lane_key = str(lane or "").strip().lower()
    placement_key = normalize_placement(placement)
    if lane_key == "onsite":
        return placement_key in ONSITE_PLACEMENTS
    if lane_key == "offsite":
        return placement_key in OFFSITE_PLACEMENTS
    return True


def plugin_lane_mismatch(*, lane: str, plugin: object | None) -> bool:
    lane_key = str(lane or "").strip().lower()
    if lane_key not in {"onsite", "offsite"}:
        return False
    placement = getattr(plugin, "placement", "both") if plugin is not None else "both"
    return not lane_allows_placement(lane=lane_key, placement=placement)
