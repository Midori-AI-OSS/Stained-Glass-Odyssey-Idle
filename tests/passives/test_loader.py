from __future__ import annotations

from pathlib import Path

from endless_idler.passives.loader import load_passive_module


def _write_module(path: Path, source: str) -> None:
    path.write_text(source, encoding="utf-8")


def test_load_passive_module_returns_plugin_for_valid_module(tmp_path: Path) -> None:
    module_path = tmp_path / "valid_passive.py"
    _write_module(
        module_path,
        "\n".join(
            [
                "from endless_idler.passives.plugin import PassivePlugin",
                "",
                "passive = PassivePlugin(",
                '    passive_id="valid_passive",',
                '    display_name="Valid Passive",',
                '    description="Valid passive module for testing.",',
                '    save_schema={"count": int},',
                ")",
                "",
            ]
        ),
    )

    plugin = load_passive_module(module_path)

    assert plugin is not None
    assert plugin.passive_id == "valid_passive"
    assert plugin.display_name == "Valid Passive"
    assert plugin.save_schema == {"count": int}


def test_load_passive_module_returns_none_when_variable_missing(tmp_path: Path) -> None:
    module_path = tmp_path / "missing_variable.py"
    _write_module(module_path, "VALUE = 1\n")

    assert load_passive_module(module_path) is None


def test_load_passive_module_returns_none_when_variable_is_wrong_type(
    tmp_path: Path,
) -> None:
    module_path = tmp_path / "wrong_type.py"
    _write_module(module_path, 'passive = "not a plugin"\n')

    assert load_passive_module(module_path) is None


def test_load_passive_module_returns_none_for_import_failure(tmp_path: Path) -> None:
    module_path = tmp_path / "import_failure.py"
    _write_module(module_path, "import definitely_missing_module\n")

    assert load_passive_module(module_path) is None


def test_load_passive_module_returns_none_for_syntax_error(tmp_path: Path) -> None:
    module_path = tmp_path / "syntax_error.py"
    _write_module(module_path, "def broken(:\n    return None\n")

    assert load_passive_module(module_path) is None
