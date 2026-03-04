from __future__ import annotations

import subprocess

import endless_idler.ui.radio.controller as controller_module

from endless_idler.ui.radio.controller import RadioController


def test_quality_channel_volume_normalization() -> None:
    assert RadioController.normalize_quality("HIGH") == "high"
    assert RadioController.normalize_quality("ultra") == "medium"

    assert RadioController.normalize_channel("ALL") == ""
    assert RadioController.normalize_channel("  lofi ") == "lofi"

    assert RadioController.clamp_volume("97") == 97
    assert RadioController.clamp_volume("-10") == 0
    assert RadioController.clamp_volume("1000") == 100


def test_loudness_boost_factor_normalization() -> None:
    assert RadioController.normalize_loudness_boost_factor("0.13") == 0.15
    assert RadioController.normalize_loudness_boost_factor("900") == 5.0
    assert RadioController.normalize_loudness_boost_factor("bad") == 2.2


def test_reconnect_delay_schedule() -> None:
    assert RadioController._next_reconnect_delay_ms(RadioController, 1) == 500
    assert RadioController._next_reconnect_delay_ms(RadioController, 2) == 1000
    assert RadioController._next_reconnect_delay_ms(RadioController, 3) == 2000
    assert RadioController._next_reconnect_delay_ms(RadioController, 4) == 3000
    assert RadioController._next_reconnect_delay_ms(RadioController, 50) == 3000


def test_probe_returns_false_when_multimedia_import_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(controller_module, "QAudioOutput", None)
    monkeypatch.setattr(controller_module, "QMediaPlayer", None)

    assert RadioController.probe_qt_multimedia_available() is False


def test_probe_returns_false_when_subprocess_raises(monkeypatch) -> None:
    monkeypatch.setattr(controller_module, "QAudioOutput", object)
    monkeypatch.setattr(controller_module, "QMediaPlayer", object)

    def _raise(*args, **kwargs):
        del args
        del kwargs
        raise OSError("boom")

    monkeypatch.setattr(controller_module.subprocess, "run", _raise)
    assert RadioController.probe_qt_multimedia_available() is False


def test_probe_returns_false_on_nonzero_subprocess(monkeypatch) -> None:
    monkeypatch.setattr(controller_module, "QAudioOutput", object)
    monkeypatch.setattr(controller_module, "QMediaPlayer", object)

    result = subprocess.CompletedProcess(
        args=["python", "-c", "pass"],
        returncode=1,
        stdout="",
        stderr="probe failed",
    )
    monkeypatch.setattr(controller_module.subprocess, "run", lambda *a, **k: result)

    assert RadioController.probe_qt_multimedia_available() is False


def test_probe_returns_true_on_ok_subprocess(monkeypatch) -> None:
    monkeypatch.setattr(controller_module, "QAudioOutput", object)
    monkeypatch.setattr(controller_module, "QMediaPlayer", object)

    result = subprocess.CompletedProcess(
        args=["python", "-c", "pass"],
        returncode=0,
        stdout="ok\n",
        stderr="",
    )
    monkeypatch.setattr(controller_module.subprocess, "run", lambda *a, **k: result)

    assert RadioController.probe_qt_multimedia_available() is True
