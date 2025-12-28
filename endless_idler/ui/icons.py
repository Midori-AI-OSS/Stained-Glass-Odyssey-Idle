from __future__ import annotations

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from urllib.error import URLError
from urllib.request import urlopen

from PySide6.QtCore import QByteArray
from PySide6.QtCore import QObject
from PySide6.QtCore import QStandardPaths
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPixmap
from PySide6.QtSvg import QSvgRenderer


_LUCIDE_VERSION = "0.539.0"
_LUCIDE_ICON_URL = "https://raw.githubusercontent.com/lucide-icons/lucide/v{version}/icons/{name}.svg"


def _cache_root() -> Path:
    cache_root = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
    if not cache_root:
        cache_root = str(Path.home() / ".cache" / "stained-glass-odyssey-idle")
    return Path(cache_root) / "lucide"


def _icon_cache_path(name: str) -> Path:
    return _cache_root() / "icons" / f"{name}.svg"



def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _write_text(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def _download_text(url: str, timeout_s: float = 6.0) -> str:
    with urlopen(url, timeout=timeout_s) as response:
        return response.read().decode("utf-8")


class LucideIconService(QObject):
    svg_ready = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._executor = ThreadPoolExecutor(max_workers=6)
        self._pending: set[str] = set()

    def ensure_svg(self, name: str) -> None:
        cache_path = _icon_cache_path(name)
        if cache_path.exists() or name in self._pending:
            return
        self._pending.add(name)
        self._executor.submit(self._download_icon, name)

    def get_svg(self, name: str) -> str | None:
        return _read_text(_icon_cache_path(name))

    def _download_icon(self, name: str) -> None:
        try:
            url = _LUCIDE_ICON_URL.format(version=_LUCIDE_VERSION, name=name)
            svg = _download_text(url)
        except (OSError, URLError):
            self._pending.discard(name)
            return

        try:
            _write_text(_icon_cache_path(name), svg)
        except OSError:
            self._pending.discard(name)
            return

        self._pending.discard(name)
        self.svg_ready.emit(name)


_LUCIDE_SERVICE: LucideIconService | None = None


def lucide_service() -> LucideIconService:
    global _LUCIDE_SERVICE
    if _LUCIDE_SERVICE is None:
        _LUCIDE_SERVICE = LucideIconService()
    return _LUCIDE_SERVICE


@lru_cache(maxsize=512)
def lucide_icon(name: str, size: int = 20) -> QIcon:
    service = lucide_service()
    service.ensure_svg(name)

    svg = service.get_svg(name)
    if not svg:
        return QIcon()

    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    if not renderer.isValid():
        return QIcon()

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)
