from __future__ import annotations

from PySide6.QtWidgets import QApplication

from endless_idler.ui.settings import SettingsPage


def test_settings_page_save_pane_emits_management_signals() -> None:
    _ = QApplication.instance() or QApplication([])

    page = SettingsPage()
    signals = {
        "save_now": 0,
        "backup": 0,
        "reset": 0,
    }

    page.save_now_requested.connect(lambda: signals.__setitem__("save_now", signals["save_now"] + 1))
    page.save_backup_requested.connect(lambda: signals.__setitem__("backup", signals["backup"] + 1))
    page.save_reset_requested.connect(lambda: signals.__setitem__("reset", signals["reset"] + 1))

    page._save_now_button.click()
    page._save_backup_button.click()
    page._save_reset_button.click()

    assert "save" in page._pane_index_by_key
    assert signals == {"save_now": 1, "backup": 1, "reset": 1}


def test_settings_page_set_save_path_is_display_only() -> None:
    _ = QApplication.instance() or QApplication([])

    page = SettingsPage()
    emitted: list[dict[str, object]] = []
    page.settings_changed.connect(emitted.append)

    page.set_save_path("/tmp/idlesave.json")

    assert page._save_path_value.text() == "/tmp/idlesave.json"
    assert emitted == []
