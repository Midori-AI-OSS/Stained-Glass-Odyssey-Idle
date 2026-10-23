from __future__ import annotations

import html

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QLabel, QWidget

from endless_idler.combat.stats import Stats


MIME_TYPE = "application/x-endless-idler-character"

STAR_COLORS: dict[int, str] = {
    1: "#808080",
    2: "#1E90FF",
    3: "#228B22",
    4: "#800080",
    5: "#FF3B30",
    6: "#FFD700",
    7: "#00FFD1",
}

TOOLTIP_LABEL_COLOR = "rgba(255, 255, 255, 170)"
TOOLTIP_VALUE_COLOR = "rgba(255, 255, 255, 235)"
MISMATCH_TOOLTIP_VALUE_COLOR = "rgba(255, 148, 176, 245)"
TINY_EXP_PER_SECOND_THRESHOLD = 0.005


def set_pixmap(
    label: QLabel,
    path: Path | None,
    *,
    size: int,
    placeholder: str | None = None,
) -> None:
    pixmap = QPixmap(str(path)) if path else QPixmap()
    if pixmap.isNull():
        if placeholder:
            label.setPixmap(_placeholder_pixmap(placeholder, size=size))
        else:
            label.clear()
        return
    label.setPixmap(
        pixmap.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    )


def derive_display_name(char_id: str) -> str:
    return " ".join(part.capitalize() for part in char_id.split("_"))


def format_idle_exp_rate_suffix(gain_per_second: float) -> str:
    gain = float(gain_per_second)
    if gain <= 0.0:
        return ""
    if gain < TINY_EXP_PER_SECOND_THRESHOLD:
        return " ~0.00/s"
    return f" +{gain:.2f}/s"


def sanitize_stars(stars: int) -> int:
    if stars <= 0:
        return 1
    if stars > 7:
        return 7
    return stars


def apply_star_rank_visuals(widget: QWidget, stars: int) -> None:
    stars = sanitize_stars(stars)
    widget.setProperty("starRank", stars)
    widget.setGraphicsEffect(_make_glow(widget, stars))
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def clear_star_rank_visuals(widget: QWidget) -> None:
    widget.setProperty("starRank", None)
    widget.setGraphicsEffect(None)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def _make_glow(widget: QWidget, stars: int) -> QGraphicsDropShadowEffect:
    glow = QGraphicsDropShadowEffect(widget)
    glow.setBlurRadius(20)
    glow.setOffset(0, 0)
    glow.setColor(QColor(STAR_COLORS.get(stars, "#708090")))
    return glow


def _placeholder_pixmap(text: str, *, size: int) -> QPixmap:
    initials = _initials(text)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.fillRect(pixmap.rect(), Qt.GlobalColor.darkGray)
    painter.setPen(Qt.GlobalColor.white)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, initials)
    painter.end()
    return pixmap


def _initials(text: str) -> str:
    parts = [part for part in text.replace("_", " ").split(" ") if part]
    if not parts:
        return "?"
    return "".join(part[0].upper() for part in parts[:2])


def build_character_stats_tooltip(
    *,
    name: str,
    stars: int | None = None,
    stacks: int | None = None,
    stackable: bool | None = None,
    stats: Stats | None = None,
    mismatch: bool = False,
    exp_multiplier_override: float | None = None,
) -> str:
    generated_stats = stats is None
    stats = stats or Stats()
    if exp_multiplier_override is None:
        exp_multiplier = float(stats.exp_multiplier)
    else:
        try:
            exp_multiplier = max(0.0, float(exp_multiplier_override))
        except (TypeError, ValueError):
            exp_multiplier = float(stats.exp_multiplier)
    stat_value_color = MISMATCH_TOOLTIP_VALUE_COLOR if mismatch else TOOLTIP_VALUE_COLOR

    safe_name = html.escape(name)
    safe_stars = sanitize_stars(int(stars)) if stars is not None else None
    star_color = STAR_COLORS.get(safe_stars or 1, "#708090")
    stars_text = ("★" * safe_stars) if safe_stars is not None else ""

    def stat_row(label: str, value: object, *, alt: bool) -> str:
        bg = "rgba(255, 255, 255, 0.04)" if alt else "transparent"
        return (
            "<tr style='background-color:"
            + bg
            + ";'>"
            + "<td style='padding:4px 10px; color: "
            + TOOLTIP_LABEL_COLOR
            + "; white-space: nowrap;'>"
            + html.escape(label)
            + "</td>"
            + "<td style='padding:4px 10px; color: "
            + stat_value_color
            + "; text-align: right; white-space: nowrap;'>"
            + html.escape(str(value))
            + "</td>"
            + "</tr>"
        )

    meta_bits: list[str] = [
        f"<span style='color: {TOOLTIP_LABEL_COLOR};'>Level</span> "
        f"<span style='color: {TOOLTIP_VALUE_COLOR};'><b>{stats.level}</b></span>",
        f"<span style='color: {TOOLTIP_LABEL_COLOR};'>Exp</span> "
        f"<span style='color: {TOOLTIP_VALUE_COLOR};'><b>{stats.exp}</b></span>",
        f"<span style='color: {TOOLTIP_LABEL_COLOR};'>Exp Mult</span> "
        f"<span style='color: {stat_value_color};'><b>{exp_multiplier:.2f}x</b></span>",
    ]

    if stacks is not None and int(stacks) > 1:
        meta_bits.append(
            f"<span style='color: {TOOLTIP_LABEL_COLOR};'>Stacks</span> "
            f"<span style='color: {TOOLTIP_VALUE_COLOR};'><b>x{int(stacks)}</b></span>"
        )
    if generated_stats and stacks is not None:
        stats.passive_modifier = 1.5 ** max(0, int(stacks) - 1)
    if stackable is True:
        meta_bits.append("<span style='color: #FFD700;'><b>Stackable</b></span>")

    stat_pairs: list[tuple[str, object]] = [
        ("HP", f"{stats.hp} / {stats.max_hp}"),
        ("ATK", stats.atk),
        ("Defense", stats.defense),
        ("Regain", stats.regain),
        ("Vitality", f"{stats.vitality:.2f}"),
        ("Mitigation", f"{stats.mitigation:.2f}"),
        ("Crit Mod", f"{stats.crit_mod:.0f}"),
        ("Effect Hit", f"{stats.effect_hit_rate:.2f}"),
        ("Effect Res", f"{stats.effect_resistance:.2f}"),
        ("Dodge", f"{stats.dodge_odds * 100:.1f}%"),
        ("Passive Modifier", f"{stats.passive_modifier:.2f}"),
        ("Aggro", f"{stats.aggro:.3f}"),
        ("Summon Slots", stats.summon_slot_capacity),
    ]

    stat_rows = "".join(
        stat_row(label, value, alt=index % 2 == 1)
        for index, (label, value) in enumerate(stat_pairs)
    )

    return (
        "<div style='min-width: 280px; max-width: 340px;'>"
        "<table style='width: 100%; border-collapse: collapse;'>"
        "<tr>"
        "<td colspan='2' style='padding: 8px 10px 6px 10px;'>"
        "<table style='width: 100%; border-collapse: collapse;'>"
        "<tr>"
        f"<td style='font-size: 13px; font-weight: 700; color: rgba(255, 255, 255, 240);'>{safe_name}</td>"
        f"<td style='font-size: 12px; font-weight: 700; text-align: right; color: {star_color};'>{html.escape(stars_text)}</td>"
        "</tr>"
        "</table>"
        "</td>"
        "</tr>"
        "<tr>"
        "<td colspan='2' style='padding: 0px 10px 8px 10px;'>"
        f"<span style='display: block; height: 2px; background-color: {star_color};'></span>"
        "<span style='display: block; padding-top: 6px; line-height: 1.35;'>"
        + " &nbsp;&nbsp; ".join(meta_bits)
        + "</span>"
        "</td>"
        "</tr>"
        "<tr>"
        "<td colspan='2' style='padding: 0px;'>"
        "<table style='width: 100%; border-collapse: collapse;'>"
        + stat_rows
        + "</table>"
        "</td>"
        "</tr>"
        "</table>"
        "</div>"
    )
