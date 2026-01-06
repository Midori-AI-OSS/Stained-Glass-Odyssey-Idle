"""User settings and preferences management."""

from __future__ import annotations

import json
import logging
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SettingsSave:
    """User preferences and settings."""

    # Tutorial
    tutorial_completed: bool = False
    tutorial_skipped: bool = False
    first_launch: bool = True

    # UI Preferences (future expansion)
    show_tooltips: bool = True
    tooltip_delay_ms: int = 500

    # Audio (future)
    audio_enabled: bool = True
    audio_volume: float = 0.8
    music_volume: float = 0.6
    sfx_volume: float = 0.8

    # Accessibility (future)
    reduced_motion: bool = False
    high_contrast: bool = False


def _default_settings_path() -> Path:
    """Default settings path with game namespace.
    
    Returns:
        Path to settings.json in game-specific subfolder.
        
    Priority:
        1. Environment variable: ENDLESS_IDLER_SETTINGS_PATH
        2. Game subfolder: ~/.midoriai/stained-glass-odyssey/settings.json
    """
    # Check environment override first
    override = os.environ.get("ENDLESS_IDLER_SETTINGS_PATH", "").strip()
    if override:
        return Path(override).expanduser()
    
    # New game-specific location
    return Path.home() / ".midoriai" / "stained-glass-odyssey" / "settings.json"


def _legacy_settings_path() -> Path:
    """Legacy settings path for backward compatibility."""
    return Path.home() / ".midoriai" / "settings.json"


def _migrate_settings_if_needed(new_path: Path) -> None:
    """Migrate settings from legacy location to new location.
    
    Args:
        new_path: Target path in game-specific subfolder
    """
    # Skip if new path already exists
    if new_path.exists():
        return
    
    legacy_path = _legacy_settings_path()
    
    # Skip if legacy path doesn't exist
    if not legacy_path.exists():
        return
    
    try:
        # Ensure new directory exists
        new_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy legacy file to new location
        shutil.copy2(legacy_path, new_path)
        
        logger.info(f"Migrated settings from {legacy_path} to {new_path}")
        
        # Keep legacy file for safety (can be removed in future version)
        
    except (OSError, IOError) as e:
        # Migration failed, but don't crash - new path will use defaults
        logger.warning(f"Failed to migrate settings from {legacy_path} to {new_path}: {e}")


class SettingsManager:
    """Manages user settings persistence."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or _default_settings_path()

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> SettingsSave:
        """Load settings, returning defaults if file doesn't exist."""
        # Attempt migration from legacy path
        _migrate_settings_if_needed(self._path)
        
        try:
            raw = self._path.read_text(encoding="utf-8")
            data = json.loads(raw)

            if not isinstance(data, dict):
                return SettingsSave()

            # Filter to only known fields to avoid errors
            valid_fields = {k: v for k, v in data.items() if k in SettingsSave.__dataclass_fields__}
            return SettingsSave(**valid_fields)

        except FileNotFoundError:
            # First time running, return defaults
            return SettingsSave()
        except (json.JSONDecodeError, TypeError, OSError):
            # Corrupted file, return defaults
            return SettingsSave()

    def save(self, settings: SettingsSave) -> None:
        """Persist settings to disk."""
        try:
            # Ensure directory exists
            self._path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dict
            data = {
                "tutorial_completed": settings.tutorial_completed,
                "tutorial_skipped": settings.tutorial_skipped,
                "first_launch": settings.first_launch,
                "show_tooltips": settings.show_tooltips,
                "tooltip_delay_ms": settings.tooltip_delay_ms,
                "audio_enabled": settings.audio_enabled,
                "audio_volume": settings.audio_volume,
                "music_volume": settings.music_volume,
                "sfx_volume": settings.sfx_volume,
                "reduced_motion": settings.reduced_motion,
                "high_contrast": settings.high_contrast,
            }

            # Write atomically using temporary file
            tmp = self._path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            tmp.replace(self._path)

        except OSError:
            # Failed to save, but don't crash the app
            pass

    def should_show_tutorial(self, settings: SettingsSave) -> bool:
        """Determine if tutorial should be shown."""
        return settings.first_launch and not settings.tutorial_completed and not settings.tutorial_skipped

    def mark_tutorial_completed(self, settings: SettingsSave) -> SettingsSave:
        """Mark tutorial as completed."""
        settings.tutorial_completed = True
        settings.first_launch = False
        return settings

    def mark_tutorial_skipped(self, settings: SettingsSave) -> SettingsSave:
        """Mark tutorial as skipped."""
        settings.tutorial_skipped = True
        settings.first_launch = False
        return settings
