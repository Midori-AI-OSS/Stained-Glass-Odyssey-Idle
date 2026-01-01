"""AST helpers for damage-type metadata extraction."""

from __future__ import annotations

import ast


def extract_damage_type_id(node: ast.AST | None) -> tuple[str | None, bool]:
    if node is None:
        return None, False

    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "field"
    ):
        default_factory = _keyword_value(node, "default_factory")
        if default_factory is not None:
            return _damage_type_from_factory(default_factory)
        default_value = _keyword_value(node, "default")
        if default_value is not None:
            return extract_damage_type_id(default_value)

    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "load_damage_type":
            if not node.args:
                return None, False
            resolved, is_random = extract_damage_type_id(node.args[0])
            if is_random:
                return None, True
            return resolved, False
        if isinstance(node.func, ast.Name) and node.func.id == "choice":
            return _damage_type_from_choice(node)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "choice":
            return _damage_type_from_choice(node)
        if isinstance(node.func, ast.Name) and node.func.id == "random_damage_type":
            return None, True

    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value, False

    if isinstance(node, ast.Name):
        return node.id, False

    if isinstance(node, ast.Attribute):
        return node.attr, False

    return None, False


def _damage_type_from_choice(node: ast.Call) -> tuple[str | None, bool]:
    if not node.args:
        return None, True

    source = node.args[0]
    if isinstance(source, ast.Name) and source.id == "ALL_DAMAGE_TYPES":
        return None, True

    if isinstance(source, ast.Attribute) and source.attr == "ALL_DAMAGE_TYPES":
        return None, True

    if isinstance(source, (ast.List, ast.Tuple)):
        values: list[str] = []
        for item in source.elts:
            if isinstance(item, ast.Constant) and isinstance(item.value, str):
                values.append(item.value)
            else:
                return None, True
        if len(values) >= 2:
            return " / ".join(values), False
        if values:
            return values[0], False

    return None, True


def _damage_type_from_factory(node: ast.AST) -> tuple[str | None, bool]:
    if isinstance(node, ast.Name):
        if node.id == "random_damage_type":
            return None, True
        return node.id, False

    if isinstance(node, ast.Lambda):
        return extract_damage_type_id(node.body)

    if isinstance(node, ast.Call):
        return extract_damage_type_id(node)

    return None, False


def _keyword_value(call: ast.Call, key: str) -> ast.AST | None:
    for keyword in call.keywords:
        if keyword.arg == key:
            return keyword.value
    return None
