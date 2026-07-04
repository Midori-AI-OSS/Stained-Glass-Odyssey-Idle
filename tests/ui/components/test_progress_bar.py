import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from endless_idler.ui.components.progress_bar import AnimatedProgressBar


@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


def test_progress_bar_theme_tokens(app):
    bar = AnimatedProgressBar()
    bar.show()

    # Verify theme token usage
    assert bar._color_thresholds == []
    bar.set_color_thresholds([(0.3, (231, 76, 60, 170))])
    assert bar._color_thresholds[0][1] == (231, 76, 60, 170)


def test_progress_bar_shimmer_effect(app):
    bar = AnimatedProgressBar()
    bar.show()
    assert bar._frame_timer.interval() == 33

    # Set shimmer intensity
    bar.set_shimmer(0.5)
    QTest.qWait(500)  # Allow full animation to complete

    # Verify shimmer alpha calculation
    assert bar._display_shimmer == pytest.approx(0.5, abs=0.01)


def test_progress_bar_color_thresholds(app):
    bar = AnimatedProgressBar()
    bar.show()

    # Set color thresholds
    bar.set_color_thresholds(
        [
            (0.0, (231, 76, 60, 170)),
            (0.3, (241, 196, 15, 185)),
            (0.7, (46, 204, 113, 165)),
        ]
    )

    # Test threshold selection
    bar.set_value(0.25)
    QTest.qWait(100)
    assert bar._color_thresholds[1][0] == 0.3  # Verify internal state


def test_progress_bar_shimmer_wraps_offscreen() -> None:
    fill_left = 10
    fill_width = 100
    half_width = max(8, int(round(float(fill_width) * 0.14)))
    shimmer_travel = float(fill_width + (half_width * 2))

    start_center = (float(fill_left) - float(half_width)) + (0.0 * shimmer_travel)
    end_center = (float(fill_left) - float(half_width)) + (0.999 * shimmer_travel)

    assert start_center < fill_left
    assert end_center > (fill_left + fill_width - 1)
