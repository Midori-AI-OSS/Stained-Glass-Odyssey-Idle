# UI System

## Main menu theme

The PySide6 UI uses a stained-glass inspired theme for the main menu:

- Theme entrypoint: `endless_idler/ui/theme.py` (`apply_stained_glass_theme`)
- Main menu widgets: `endless_idler/ui/main_menu.py`
- Background image: `endless_idler/assets/backgrounds/main_menu_cityscape.png`

## Battle screen (prototype)

- Battle screen widget: `endless_idler/ui/battle/screen.py` (`BattleScreenWidget`)
- Launched from the party builder "Fight" bar and returns to the party builder when the battle ends.
