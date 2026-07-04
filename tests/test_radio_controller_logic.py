from __future__ import annotations

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


def test_probe_returns_false_when_audio_output_init_raises(
    monkeypatch,
    tmp_path,
) -> None:
    class _BrokenAudioOutput:
        def __init__(self) -> None:
            raise OSError("boom")

    monkeypatch.setattr(controller_module, "QAudioOutput", _BrokenAudioOutput)
    monkeypatch.setattr(controller_module, "QMediaPlayer", object)
    socket_path = tmp_path / "pipewire-0"
    socket_path.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        RadioController,
        "_pipewire_socket_path",
        staticmethod(lambda: socket_path),
    )
    assert RadioController.probe_qt_multimedia_available() is False


def test_probe_returns_false_when_player_init_raises(monkeypatch, tmp_path) -> None:
    class _AudioOutput:
        def deleteLater(self) -> None:
            return

    class _BrokenPlayer:
        def __init__(self) -> None:
            raise RuntimeError("boom")

    monkeypatch.setattr(controller_module, "QAudioOutput", _AudioOutput)
    monkeypatch.setattr(controller_module, "QMediaPlayer", _BrokenPlayer)
    socket_path = tmp_path / "pipewire-0"
    socket_path.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        RadioController,
        "_pipewire_socket_path",
        staticmethod(lambda: socket_path),
    )
    assert RadioController.probe_qt_multimedia_available() is False


def test_probe_returns_true_when_multimedia_probe_succeeds(monkeypatch, tmp_path) -> None:
    class _AudioOutput:
        def __init__(self) -> None:
            self.deleted = False

        def deleteLater(self) -> None:
            self.deleted = True

    class _Player:
        def __init__(self) -> None:
            self.audio = None
            self.deleted = False

        def setAudioOutput(self, audio) -> None:
            self.audio = audio

        def deleteLater(self) -> None:
            self.deleted = True

    monkeypatch.setattr(controller_module, "QAudioOutput", _AudioOutput)
    monkeypatch.setattr(controller_module, "QMediaPlayer", _Player)
    socket_path = tmp_path / "pipewire-0"
    socket_path.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        RadioController,
        "_pipewire_socket_path",
        staticmethod(lambda: socket_path),
    )
    assert RadioController.probe_qt_multimedia_available() is True
