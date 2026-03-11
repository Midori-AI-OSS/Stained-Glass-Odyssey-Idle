from __future__ import annotations


_CARD_SELECTORS = (
    "QFrame#onsiteCharacterCard",
    "QFrame#idleOffsiteCard",
)

_SOLID_BACKGROUNDS: dict[str, str] = {
    "generic": "rgba(255, 255, 255, 10)",
    "fire": "rgba(255, 90, 40, 60)",
    "ice": "rgba(80, 200, 255, 60)",
    "lightning": "rgba(255, 220, 0, 55)",
    "wind": "rgba(80, 230, 170, 60)",
    "water": "rgba(60, 130, 255, 60)",
    "nature": "rgba(80, 200, 120, 60)",
    "arcane": "rgba(255, 80, 200, 60)",
    "dark": "rgba(75, 45, 100, 60)",
    "light": "rgba(255, 220, 120, 60)",
    "physical": "rgba(180, 180, 190, 60)",
}


def _selector_list(*suffixes: str) -> str:
    selectors: list[str] = []
    for selector in _CARD_SELECTORS:
        for suffix in suffixes:
            selectors.append(f"{selector}{suffix}")
    return ",\n".join(selectors)


def _base_rules() -> str:
    selectors = _selector_list("")
    return (
        f"{selectors} {{\n"
        "    border: 1px solid rgba(255, 255, 255, 18);\n"
        f"    background-color: {_SOLID_BACKGROUNDS['generic']};\n"
        "}"
    )


def _single_type_rules() -> list[str]:
    rules: list[str] = []
    for element_id, color in _SOLID_BACKGROUNDS.items():
        if element_id == "generic":
            continue
        selectors = _selector_list(f'[elementId="{element_id}"]')
        rules.append(f"{selectors} {{ background-color: {color}; }}")
    return rules


def _dual_type_rules() -> list[str]:
    rules: list[str] = []
    dual_ids = tuple(
        element_id for element_id in _SOLID_BACKGROUNDS if element_id != "generic"
    )
    for first in dual_ids:
        for second in dual_ids:
            if first == second:
                continue
            selectors = _selector_list(f'[dualElementIds="{first},{second}"]')
            gradient = (
                "qlineargradient("
                "x1: 0, y1: 0, x2: 1, y2: 1, "
                f"stop: 0 {_SOLID_BACKGROUNDS[first]}, "
                f"stop: 1 {_SOLID_BACKGROUNDS[second]}"
                ")"
            )
            rules.append(f"{selectors} {{ background-color: {gradient}; }}")
    return rules


STYLESHEET = "\n\n".join(
    [_base_rules(), *_single_type_rules(), *_dual_type_rules()]
).strip()
