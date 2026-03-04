from __future__ import annotations

import json

from pathlib import Path

from endless_idler.save import RunSave
from endless_idler.save import SaveManager
from endless_idler.settings import AppSettings
from endless_idler.settings import AppSettingsManager


def test_default_settings_path_uses_stainedlgassodysseyidle_folder(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("ENDLESS_IDLER_SETTINGS_PATH", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    manager = AppSettingsManager()
    assert (
        manager.path
        == tmp_path / ".midoriai" / "stainedlgassodysseyidle" / "settings.json"
    )


def test_load_invalid_fields_normalizes_settings(monkeypatch, tmp_path: Path) -> None:
    settings_path = tmp_path / "settings.json"
    monkeypatch.setenv("ENDLESS_IDLER_SETTINGS_PATH", str(settings_path))

    raw_payload = {
        "radio_enabled": "yes",
        "radio_autostart": 1,
        "radio_channel": "ALL",
        "radio_quality": "ultra",
        "radio_volume": "101",
        "radio_loudness_boost_enabled": "true",
        "radio_loudness_boost_factor": "99.9",
    }
    settings_path.write_text(json.dumps(raw_payload), encoding="utf-8")

    loaded = AppSettingsManager().load()
    assert loaded.radio_enabled is True
    assert loaded.radio_autostart is True
    assert loaded.radio_channel == ""
    assert loaded.radio_quality == "medium"
    assert loaded.radio_volume == 100
    assert loaded.radio_loudness_boost_enabled is True
    assert loaded.radio_loudness_boost_factor == 5.0


def test_malformed_json_returns_defaults(monkeypatch, tmp_path: Path) -> None:
    settings_path = tmp_path / "settings.json"
    monkeypatch.setenv("ENDLESS_IDLER_SETTINGS_PATH", str(settings_path))
    settings_path.write_text("{not-json", encoding="utf-8")

    loaded = AppSettingsManager().load()
    assert loaded == AppSettings()


def test_save_rewrites_normalized_payload(monkeypatch, tmp_path: Path) -> None:
    settings_path = tmp_path / "settings.json"
    monkeypatch.setenv("ENDLESS_IDLER_SETTINGS_PATH", str(settings_path))

    manager = AppSettingsManager()
    manager.save(
        AppSettings.from_mapping(
            {
                "radio_enabled": True,
                "radio_autostart": True,
                "radio_channel": " all ",
                "radio_quality": "HIGH",
                "radio_volume": -4,
                "radio_loudness_boost_enabled": True,
                "radio_loudness_boost_factor": 0.13,
            }
        )
    )

    payload = json.loads(settings_path.read_text(encoding="utf-8"))
    assert payload == {
        "radio_enabled": True,
        "radio_autostart": True,
        "radio_channel": "",
        "radio_quality": "high",
        "radio_volume": 0,
        "radio_loudness_boost_enabled": True,
        "radio_loudness_boost_factor": 0.15,
    }


def test_run_save_writes_do_not_modify_settings_file(monkeypatch, tmp_path: Path) -> None:
    save_path = tmp_path / "idlesave.json"
    settings_path = tmp_path / "settings.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))
    monkeypatch.setenv("ENDLESS_IDLER_SETTINGS_PATH", str(settings_path))

    settings_manager = AppSettingsManager()
    settings_manager.save(
        AppSettings.from_mapping(
            {
                "radio_enabled": True,
                "radio_autostart": False,
                "radio_channel": "lofi",
                "radio_quality": "medium",
                "radio_volume": 64,
                "radio_loudness_boost_enabled": True,
                "radio_loudness_boost_factor": 2.2,
            }
        )
    )
    before = settings_path.read_text(encoding="utf-8")

    save_manager = SaveManager()
    save_manager.save(RunSave())

    after = settings_path.read_text(encoding="utf-8")
    assert before == after
