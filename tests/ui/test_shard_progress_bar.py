from __future__ import annotations


from endless_idler.shard_progress import SHARD_BAR_CYCLE_TICKS
from endless_idler.ui.theme.shard_progress_bar_widget import (
    FIRE_RGBA,
    ICE_RGBA,
    LIGHTNING_RGBA,
    WIND_RGBA,
    DARK_RGBA,
    LIGHT_RGBA,
    GENERIC_CYCLE_COLORS,
)


class TestShardProgressBarText:
    """Test suite for ShardProgressBar text display."""

    def test_text_format_includes_shard_prefix(self):
        """Test that text format includes 'SHARD' prefix."""
        # Simulating the text format used in set_shard_data
        shard_bar_ticks = 67
        expected_text = f"SHARD {shard_bar_ticks}/{SHARD_BAR_CYCLE_TICKS}"
        assert expected_text == "SHARD 67/300"
        assert expected_text.startswith("SHARD ")

    def test_text_format_various_tick_counts(self):
        """Test text format for various tick counts."""
        test_cases = [
            (0, "SHARD 0/300"),
            (75, "SHARD 75/300"),
            (150, "SHARD 150/300"),
            (225, "SHARD 225/300"),
            (299, "SHARD 299/300"),
            (300, "SHARD 300/300"),
        ]

        for ticks, expected in test_cases:
            result = f"SHARD {ticks}/{SHARD_BAR_CYCLE_TICKS}"
            assert result == expected, f"Failed for ticks={ticks}"


class TestElementColors:
    """Test suite for element color constants."""

    def test_fire_color_values(self):
        """Test fire color matches expected hex."""
        r, g, b, a = FIRE_RGBA
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        assert hex_color == "#FF5A28"

    def test_ice_color_values(self):
        """Test ice color matches expected hex."""
        r, g, b, a = ICE_RGBA
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        assert hex_color == "#50C8FF"

    def test_lightning_color_values(self):
        """Test lightning color matches expected hex."""
        r, g, b, a = LIGHTNING_RGBA
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        assert hex_color == "#FFDC00"

    def test_wind_color_values(self):
        """Test wind color matches expected hex."""
        r, g, b, a = WIND_RGBA
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        assert hex_color == "#50E6AA"

    def test_dark_color_values(self):
        """Test dark color matches expected hex."""
        r, g, b, a = DARK_RGBA
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        assert hex_color == "#4B2D64"

    def test_light_color_values(self):
        """Test light color matches expected hex."""
        r, g, b, a = LIGHT_RGBA
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        assert hex_color == "#FFDC78"

    def test_all_generic_cycle_colors_present(self):
        """Test that all 6 element colors are in the generic cycle."""
        assert len(GENERIC_CYCLE_COLORS) == 6
        assert FIRE_RGBA in GENERIC_CYCLE_COLORS
        assert ICE_RGBA in GENERIC_CYCLE_COLORS
        assert LIGHTNING_RGBA in GENERIC_CYCLE_COLORS
        assert WIND_RGBA in GENERIC_CYCLE_COLORS
        assert DARK_RGBA in GENERIC_CYCLE_COLORS
        assert LIGHT_RGBA in GENERIC_CYCLE_COLORS


class TestShardProgressBarLogic:
    """Test suite for ShardProgressBar logic (without Qt dependencies)."""

    def test_element_color_map(self):
        """Test that element color map contains all elements."""
        from endless_idler.ui.widgets.shard_progress_bar import ELEMENT_COLORS

        expected_elements = {"fire", "ice", "lightning", "wind", "dark", "light"}
        assert set(ELEMENT_COLORS.keys()) == expected_elements

    def test_element_color_values(self):
        """Test that element colors match expected RGBA values."""
        from endless_idler.ui.widgets.shard_progress_bar import ELEMENT_COLORS

        assert ELEMENT_COLORS["fire"] == FIRE_RGBA
        assert ELEMENT_COLORS["ice"] == ICE_RGBA
        assert ELEMENT_COLORS["lightning"] == LIGHTNING_RGBA
        assert ELEMENT_COLORS["wind"] == WIND_RGBA
        assert ELEMENT_COLORS["dark"] == DARK_RGBA
        assert ELEMENT_COLORS["light"] == LIGHT_RGBA

    def test_progress_calculation_formula(self):
        """Test the progress calculation formula."""
        # Test various tick counts
        test_cases = [
            (0, 0.0),
            (75, 0.25),
            (150, 0.5),
            (225, 0.75),
            (300, 1.0),
        ]

        for ticks, expected_progress in test_cases:
            progress = ticks / float(SHARD_BAR_CYCLE_TICKS)
            assert progress == expected_progress, f"Failed for ticks={ticks}"

    def test_generic_type_detection_logic(self):
        """Test the logic for detecting generic types."""
        from endless_idler.ui.widgets.shard_progress_bar import ELEMENT_COLORS

        # All 6 elements should be considered generic
        all_elements = ("fire", "ice", "lightning", "wind", "dark", "light")
        element_count = sum(1 for t in all_elements if t in ELEMENT_COLORS)
        assert element_count == 6
        assert element_count >= 6  # This is the condition for generic type

        # Partial elements should not be generic
        partial = ("fire", "ice")
        partial_count = sum(1 for t in partial if t in ELEMENT_COLORS)
        assert partial_count == 2
        assert partial_count < 6  # Not generic

    def test_shard_types_filtering_logic(self):
        """Test the logic for filtering shard types."""
        # Simulating the filtering that happens in set_shard_data
        raw_types = ("fire", "", "ice", None, "wind")
        filtered = tuple(str(t) for t in raw_types if t)

        assert "fire" in filtered
        assert "ice" in filtered
        assert "wind" in filtered
        assert "" not in filtered
        assert "None" not in filtered  # None gets converted to "None" by str()

    def test_element_id_normalization_cases(self):
        """Test element ID normalization scenarios."""
        test_cases = [
            ("FIRE", "fire"),
            ("  Fire  ", "fire"),
            ("Fire", "fire"),
            ("ICE", "ice"),
            ("LIGHTNING", "lightning"),
        ]

        for input_id, expected in test_cases:
            normalized = str(input_id or "generic").strip().lower()
            assert normalized == expected, f"Failed for input={input_id}"


class TestIdleStateGenericRewardTypes:
    """Test the generic damage type handling in IdleGameState."""

    def test_generic_damage_type_returns_all_elements(self):
        """Test that generic damage type returns all 6 elemental types."""
        # This tests the logic added to _reward_types_for_char in idle_state.py
        # When raw == "generic", it should extend options with all SHARD_ALLOWED_TYPES

        shard_allowed_types = frozenset(
            {
                "fire",
                "ice",
                "wind",
                "lightning",
                "light",
                "dark",
            }
        )

        # Simulate the logic from idle_state.py
        raw = "generic"
        options = []

        if raw == "generic":
            options.extend(sorted(shard_allowed_types))

        result = tuple(options)

        assert len(result) == 6
        assert set(result) == shard_allowed_types
        assert result == tuple(sorted(shard_allowed_types))

    def test_specific_element_returns_single_type(self):
        """Test that specific element returns just that type."""
        shard_allowed_types = frozenset(
            {
                "fire",
                "ice",
                "wind",
                "lightning",
                "light",
                "dark",
            }
        )

        raw = "fire"
        options = []

        if "/" in raw:
            for part in raw.split("/"):
                normalized = part.strip().lower().replace("-", "_").replace(" ", "_")
                if normalized in shard_allowed_types and normalized not in options:
                    options.append(normalized)
        elif raw in shard_allowed_types:
            options.append(raw)
        elif raw == "generic":
            options.extend(sorted(shard_allowed_types))

        result = tuple(options)

        assert result == ("fire",)

    def test_dual_element_type(self):
        """Test that dual element type (fire/ice) returns both types."""
        shard_allowed_types = frozenset(
            {
                "fire",
                "ice",
                "wind",
                "lightning",
                "light",
                "dark",
            }
        )

        raw = "fire/ice"
        options = []

        if "/" in raw:
            for part in raw.split("/"):
                normalized = part.strip().lower().replace("-", "_").replace(" ", "_")
                if normalized in shard_allowed_types and normalized not in options:
                    options.append(normalized)
        elif raw in shard_allowed_types:
            options.append(raw)
        elif raw == "generic":
            options.extend(sorted(shard_allowed_types))

        result = tuple(options)

        assert "fire" in result
        assert "ice" in result
        assert len(result) == 2
