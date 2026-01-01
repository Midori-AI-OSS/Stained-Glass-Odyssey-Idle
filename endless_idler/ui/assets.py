from pathlib import Path

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def asset_path(*parts: str) -> str:
    return str(_ASSETS_DIR.joinpath(*parts))
