from __future__ import annotations

from pathlib import Path


def test_lucide_icon_assets_are_present() -> None:
    icons_dir = Path(__file__).resolve().parent.parent / "endless_idler" / "assets" / "icons" / "lucide"
    assert icons_dir.exists()

    svg_files = sorted(path for path in icons_dir.glob("*.svg"))
    assert len(svg_files) >= 800

    required = [
        "audio-lines.svg",
        "audio-waveform.svg",
        "settings.svg",
        "house.svg",
    ]
    for name in required:
        assert (icons_dir / name).exists()
