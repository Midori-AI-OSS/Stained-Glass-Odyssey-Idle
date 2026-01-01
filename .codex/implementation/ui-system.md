# UI System

## Main menu theme

The PySide6 UI uses a stained-glass inspired theme for the main menu:

- Theme entrypoint: `endless_idler/ui/theme.py` (`apply_stained_glass_theme`)
- Main menu widgets: `endless_idler/ui/main_menu.py`
- Background image: `endless_idler/assets/backgrounds/main_menu_cityscape.png`

## Battle screen (prototype)

- Battle screen widget: `endless_idler/ui/battle/screen.py` (`BattleScreenWidget`)
- Launched from the party builder "Fight" bar and returns to the party builder when the battle ends.
- Onsite character cards use the shared onsite card widget (see below).
- Party targets for foe turns are weighted by the party members' `aggro` stat.

## Idle screen

- Idle screen widget: `endless_idler/ui/idle/screen.py` (`IdleScreenWidget`)
- Per-character EXP bars show current EXP and the current gain rate as `+X.XX/s` (computed from the live idle state)
- Character cards show a `Rebirth` button at level 50+ (triggers `IdleGameState.rebirth_character`).
- Onsite character cards use the shared onsite card widget (see below).

## Party Builder screen

- Party Builder widget: `endless_idler/ui/party_builder.py` (`PartyBuilderWidget`)
- Run buff display: `endless_idler/ui/party_builder_rewards_plane.py` (`RewardsPlane`) only shows when the run has an active bonus/penalty.
- Shop EXP drip: while Party Builder is visible, party characters gain scaled Idle EXP (`SHOP_IDLE_EXP_SCALE`) without consuming run buff duration.

## Onsite character cards (shared)

Both Battle and Idle use a standardized onsite character layout and controls:

- Onsite card widgets: `endless_idler/ui/onsite/card.py` (`BattleOnsiteCharacterCard`, `IdleOnsiteCharacterCard`)
- Stat bars: `endless_idler/ui/onsite/stat_bars.py` (`StatBarsPanel`)
- Per-card stats UI: each onsite card has an `👁` button which opens a small popup containing stat bars.

## Party HP (shared run stat)

- Party HP UI: `endless_idler/ui/party_hp_bar.py` (`PartyHpHeader`) is shown in Party Builder, Battle, and Idle.
- Party HP rules + idle regen: `endless_idler/run_rules.py`.
- Party HP persistence + fight number: `endless_idler/save.py` (`RunSave`).
