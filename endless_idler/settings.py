from __future__ import annotations

import json
import os

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QStandardPaths


QUALITY_VALUES = ("low", "medium", "high")
LOUDNESS_BOOST_MIN = 0.1
LOUDNESS_BOOST_MAX = 5.0
LOUDNESS_BOOST_STEP = 0.05
LOUDNESS_BOOST_DEFAULT = 2.2
VOLUME_DEFAULT = 70


def normalize_quality(value: object) -> str:
    raw = str(value or "medium").strip().lower()
    if raw not in QUALITY_VALUES:
        return "medium"
    return raw


def normalize_channel(value: object) -> str:
    raw = str(value or "").strip().lower()
    if raw == "all":
        return ""
    return raw


def clamp_volume(value: object) -> int:
    try:
        parsed = int(str(value).strip())
    except Exception:
        parsed = VOLUME_DEFAULT
    return max(0, min(100, parsed))


def normalize_loudness_boost_factor(value: object) -> float:
    try:
        parsed = float(str(value).strip())
    except Exception:
        parsed = LOUDNESS_BOOST_DEFAULT
    parsed = max(LOUDNESS_BOOST_MIN, min(LOUDNESS_BOOST_MAX, parsed))
    step_count = int(round((parsed - LOUDNESS_BOOST_MIN) / LOUDNESS_BOOST_STEP))
    snapped = LOUDNESS_BOOST_MIN + (step_count * LOUDNESS_BOOST_STEP)
    snapped = max(LOUDNESS_BOOST_MIN, min(LOUDNESS_BOOST_MAX, snapped))
    return round(snapped, 2)


@dataclass(slots=True)
class AppSettings:
    radio_enabled: bool = False
    radio_autostart: bool = False
    radio_channel: str = ""
    radio_quality: str = "medium"
    radio_volume: int = VOLUME_DEFAULT
    radio_loudness_boost_enabled: bool = False
    radio_loudness_boost_factor: float = LOUDNESS_BOOST_DEFAULT

    @classmethod
    def from_mapping(cls, values: Mapping[str, object] | None) -> AppSettings:
        values = values or {}
        return cls(
            radio_enabled=bool(values.get("radio_enabled") or False),
            radio_autostart=bool(values.get("radio_autostart") or False),
            radio_channel=normalize_channel(values.get("radio_channel")),
            radio_quality=normalize_quality(values.get("radio_quality")),
            radio_volume=clamp_volume(values.get("radio_volume")),
            radio_loudness_boost_enabled=bool(values.get("radio_loudness_boost_enabled") or False),
            radio_loudness_boost_factor=normalize_loudness_boost_factor(
                values.get("radio_loudness_boost_factor")
            ),
        )

    def as_dict(self) -> dict[str, object]:
        normalized = AppSettings.from_mapping(
            {
                "radio_enabled": self.radio_enabled,
                "radio_autostart": self.radio_autostart,
                "radio_channel": self.radio_channel,
                "radio_quality": self.radio_quality,
                "radio_volume": self.radio_volume,
                "radio_loudness_boost_enabled": self.radio_loudness_boost_enabled,
                "radio_loudness_boost_factor": self.radio_loudness_boost_factor,
            }
        )
        return {
            "radio_enabled": normalized.radio_enabled,
            "radio_autostart": normalized.radio_autostart,
            "radio_channel": normalized.radio_channel,
            "radio_quality": normalized.radio_quality,
            "radio_volume": normalized.radio_volume,
            "radio_loudness_boost_enabled": normalized.radio_loudness_boost_enabled,
            "radio_loudness_boost_factor": normalized.radio_loudness_boost_factor,
        }


class AppSettingsManager:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or _default_settings_path()

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> AppSettings:
        try:
            raw = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return AppSettings()
        except OSError:
            return AppSettings()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return AppSettings()

        if not isinstance(data, dict):
            return AppSettings()
        return AppSettings.from_mapping(data)

    def save(self, settings: AppSettings) -> None:
        payload = settings.as_dict()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        tmp_path.replace(self._path)


def _default_settings_path() -> Path:
    override = os.environ.get("ENDLESS_IDLER_SETTINGS_PATH", "").strip()
    if override:
        return Path(override).expanduser()

    home = Path.home()
    if home.exists():
        return home / ".midoriai" / "stainedlgassodysseyidle" / "settings.json"

    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if not base:
        base = str(Path.cwd())
    return Path(base) / "stainedlgassodysseyidle" / "settings.json"
