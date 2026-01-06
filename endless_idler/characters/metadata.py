"""AST-based metadata extraction for character plugins.

This module inspects character plugin source files without importing them.
The character modules are copied from another project and may have unmet
dependencies at runtime.
"""

from __future__ import annotations

import ast

from pathlib import Path

from endless_idler.characters.ast_damage_type import extract_damage_type_id
from endless_idler.combat.damage_types import normalize_damage_type_id


DEFAULT_BASE_STATS: dict[str, float] = {
    "max_hp": 1000.0,
    "atk": 200.0,
    "defense": 200.0,
    "crit_rate": 0.05,
    "crit_damage": 2.0,
    "effect_hit_rate": 1.0,
    "mitigation": 1.0,
    "regain": 100.0,
    "dodge_odds": 0.05,
    "effect_resistance": 0.05,
    "vitality": 1.0,
    "spd": 2.0,
}

_BASE_STAT_KEYS = frozenset(DEFAULT_BASE_STATS.keys())
_PLACEMENTS = ("onsite", "offsite", "both")


def extract_character_metadata(
    path: Path,
) -> tuple[str, str, int, str, str, bool, dict[str, float], float | None, int | None, list[str]]:
    char_id = path.stem
    display_name = _derive_display_name(char_id)
    stars = 1
    placement = "both"
    damage_type_id = "generic"
    damage_type_random = False
    base_stats: dict[str, float] = dict(DEFAULT_BASE_STATS)
    base_aggro: float | None = None
    damage_reduction_passes: int | None = None
    passives: list[str] = []

    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return (
            "",
            "",
            stars,
            placement,
            damage_type_id,
            damage_type_random,
            base_stats,
            base_aggro,
            damage_reduction_passes,
            passives,
        )

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return (
            "",
            "",
            stars,
            placement,
            damage_type_id,
            damage_type_random,
            base_stats,
            base_aggro,
            damage_reduction_passes,
        )

    module_placement = _extract_from_module(tree)
    if module_placement:
        placement = module_placement

    found_character = False
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        found_id, found_name, found_stars, found_placement = _extract_from_classdef(node)
        found_damage_type, found_damage_random = _extract_damage_type_from_classdef(node)
        stat_overrides, found_base_aggro, found_damage_reduction_passes = _extract_stat_overrides_from_classdef(node)
        if found_id or found_name:
            found_character = True
        if found_id:
            char_id = found_id
        if found_name:
            display_name = found_name
        if found_stars is not None:
            stars = found_stars
        if found_placement:
            placement = found_placement
        if found_damage_type or found_damage_random:
            if found_damage_type:
                damage_type_id = found_damage_type
            damage_type_random = found_damage_random
        if stat_overrides:
            for key, value in stat_overrides.items():
                base_stats[key] = value
        if found_base_aggro is not None:
            base_aggro = found_base_aggro
        if found_damage_reduction_passes is not None:
            damage_reduction_passes = found_damage_reduction_passes
        if found_id or found_name:
            break

    if not found_character:
        return (
            "",
            "",
            stars,
            placement,
            damage_type_id,
            damage_type_random,
            base_stats,
            base_aggro,
            damage_reduction_passes,
        )

    if not display_name:
        display_name = _derive_display_name(char_id)

    sanitized_base_stats = _sanitize_base_stats(base_stats)
    return (
        char_id,
        display_name,
        _sanitize_stars(stars),
        _sanitize_placement(placement),
        _sanitize_damage_type(damage_type_id),
        bool(damage_type_random),
        sanitized_base_stats,
        base_aggro,
        damage_reduction_passes,
    )


def _extract_from_module(tree: ast.Module) -> str | None:
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == "placement":
                    return _const_str(stmt.value)
        elif isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Name) and stmt.target.id == "placement":
                return _const_str(stmt.value)
    return None


def _extract_from_classdef(node: ast.ClassDef) -> tuple[str | None, str | None, int | None, str | None]:
    char_id: str | None = None
    display_name: str | None = None
    stars: int | None = None
    placement: str | None = None

    for stmt in node.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    if target.id == "id":
                        char_id = _const_str(stmt.value)
                    elif target.id == "name":
                        display_name = _const_str(stmt.value)
                    elif target.id in {"gacha_rarity", "rarity", "stars"}:
                        stars = _const_int(stmt.value)
                    elif target.id == "placement":
                        placement = _const_str(stmt.value)
        elif isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Name):
                if stmt.target.id == "id":
                    char_id = _const_str(stmt.value)
                elif stmt.target.id == "name":
                    display_name = _const_str(stmt.value)
                elif stmt.target.id in {"gacha_rarity", "rarity", "stars"}:
                    stars = _const_int(stmt.value)
                elif stmt.target.id == "placement":
                    placement = _const_str(stmt.value)

    return char_id, display_name, stars, placement


def _extract_damage_type_from_classdef(node: ast.ClassDef) -> tuple[str | None, bool]:
    for stmt in node.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == "damage_type":
                    return extract_damage_type_id(stmt.value)
        elif isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Name) and stmt.target.id == "damage_type":
                return extract_damage_type_id(stmt.value)
    return None, False


def _extract_stat_overrides_from_classdef(
    node: ast.ClassDef,
) -> tuple[dict[str, float], float | None, int | None]:
    base_stats: dict[str, float] = {}
    base_aggro: float | None = None
    damage_reduction_passes: int | None = None

    for stmt in node.body:
        if not isinstance(stmt, ast.FunctionDef) or stmt.name != "__post_init__":
            continue
        for inner in stmt.body:
            if isinstance(inner, ast.Expr) and isinstance(inner.value, ast.Call):
                call = inner.value
                if (
                    isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Name)
                    and call.func.value.id == "self"
                    and call.func.attr == "set_base_stat"
                    and len(call.args) >= 2
                ):
                    stat_name = _const_str(call.args[0])
                    stat_value = _const_float(call.args[1])
                    if stat_name and stat_name in _BASE_STAT_KEYS and stat_value is not None:
                        base_stats[stat_name] = stat_value
                        continue

            if isinstance(inner, ast.Assign) and len(inner.targets) == 1:
                target = inner.targets[0]
                if (
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "self"
                ):
                    if target.attr == "base_aggro":
                        base_aggro_value = _const_float(inner.value)
                        if base_aggro_value is not None:
                            base_aggro = base_aggro_value
                    elif target.attr == "damage_reduction_passes":
                        passes_value = _const_int(inner.value)
                        if passes_value is not None:
                            damage_reduction_passes = passes_value

        break

    return base_stats, base_aggro, damage_reduction_passes


def _const_str(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _const_int(node: ast.AST | None) -> int | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    return None


def _const_float(node: ast.AST | None) -> float | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    return None


def _derive_display_name(char_id: str) -> str:
    return " ".join(part.capitalize() for part in char_id.split("_"))


def _sanitize_stars(stars: int) -> int:
    if stars <= 0:
        return 1
    if stars > 7:
        return 7
    return stars


def _sanitize_placement(placement: str) -> str:
    value = placement.strip().lower()
    return value if value in _PLACEMENTS else "both"


def _sanitize_damage_type(value: str) -> str:
    return normalize_damage_type_id(value)


def _sanitize_base_stats(base_stats: dict[str, float]) -> dict[str, float]:
    sanitized: dict[str, float] = dict(DEFAULT_BASE_STATS)
    for key, raw in base_stats.items():
        if key not in _BASE_STAT_KEYS:
            continue
        try:
            value = float(raw)
        except (TypeError, ValueError):
            continue
        sanitized[key] = value
    return sanitized
