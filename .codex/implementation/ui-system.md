# UI System

## Main menu theme

The PySide6 UI uses a stained-glass inspired theme for the main menu:

- Theme entrypoint: `endless_idler/ui/theme.py` (`apply_stained_glass_theme`)
- Main menu widgets: `endless_idler/ui/main_menu.py`
- Background image: `endless_idler/assets/backgrounds/main_menu_cityscape.png`

## Icons

The Endless Autofighter menu uses the Lucide icon pack. This project downloads Lucide SVGs at runtime and caches them locally (no Lucide files are checked in):

- Runtime helper: `endless_idler/ui/icons.py` (`lucide_icon`, `lucide_service`)
- Cache location: `QStandardPaths.CacheLocation` under a `lucide/` subfolder

The Lucide license text is also downloaded on first use and stored alongside the cached icons, without committing a dedicated license file in this repo.
