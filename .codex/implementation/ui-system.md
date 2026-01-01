# UI System

## Main menu theme

The PySide6 UI uses a stained-glass inspired theme for the main menu:

- Theme entrypoint: `endless_idler/ui/theme.py` (`apply_stained_glass_theme`)
- Main menu widgets: `endless_idler/ui/main_menu.py`
- Background image: `endless_idler/assets/backgrounds/main_menu_cityscape.png`

## Battle screen (prototype)

- Battle screen widget: `endless_idler/ui/battle/screen.py` (`BattleScreenWidget`)
- Launched from the party builder "Fight" bar and returns to the party builder when the battle ends.

## Idle screen

- Idle screen widget: `endless_idler/ui/idle/screen.py` (`IdleScreenWidget`)
- Per-character EXP bars show current EXP and the current gain rate as `+X.XX/s` (computed from the live idle state)
- Character cards show a `Rebirth` button at level 50+ (triggers `IdleGameState.rebirth_character`).

## Party HP (shared run stat)

- Party HP UI: `endless_idler/ui/party_hp_bar.py` (`PartyHpHeader`) is shown in Party Builder, Battle, and Idle.
- Party HP rules + idle regen: `endless_idler/run_rules.py`.
- Party HP persistence + fight number: `endless_idler/save.py` (`RunSave`).
