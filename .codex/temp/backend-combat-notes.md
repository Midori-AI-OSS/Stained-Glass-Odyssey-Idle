# Backend Combat Notes (code-only)

Source snapshot:
- Repo: `https://github.com/Midori-AI-OSS/Stained-Glass-Odyssey-Endless`
- Clone: `/tmp/stained-glass-odyssey-endless-20251228-141028`
- Commit: `a93ac2d44806cc94b49f265ba76809705a8a91af`

This note summarizes how combat works based on backend Python code only (no docs).

## High-Level Flow

Battle entrypoint:
- `backend/autofighter/rooms/battle/core.py`: `BattleRoom.resolve()` sets up battle state then calls `run_battle()`.
- `backend/autofighter/rooms/battle/engine.py`: `run_battle()` runs the async loop, pushes progress updates, and resolves rewards/state at the end.

Setup:
- `backend/autofighter/rooms/battle/setup.py`: `setup_battle()`:
  - Resets summons (`SummonManager.reset_all()`).
  - Builds foes (via `autofighter/rooms/utils._build_foes()` → `FoeFactory.build_encounter()`).
  - Applies rank-based passive substitutions for foes (`apply_rank_passives()`).
  - Scales foe stats per room (`_scale_stats()` → `FoeFactory.scale_stats()`).
  - Deep-copies party members for combat (`copy.deepcopy`) and applies cards + relics (`apply_cards`, `apply_relics`).
  - Attaches an `EffectManager` to each combatant (players and foes).
  - Creates a visual/UI `ActionQueue` (includes a synthetic `turn_counter` entity).
  - Marks battle active (`set_battle_active(True)`), used to ignore late damage tasks.

Main loop:
- `backend/autofighter/rooms/battle/turn_loop/orchestrator.py`: `run_turn_loop()`:
  - Initializes context (`initialize_turn_loop()`), then alternates:
    - `execute_player_phase(context)`
    - `execute_foe_phase(context)`
    - `cleanup_after_round(context)` (prunes dead foes)
  - Stops when either side has no living members.

## Turn Structure and Ordering

Phases (important nuance):
- The *actual* execution order is deterministic: players act (in party order) then foes act (in current foe list order).
  - Player: `backend/autofighter/rooms/battle/turn_loop/player_turn.py`: `execute_player_phase()`
  - Foe: `backend/autofighter/rooms/battle/turn_loop/foe_turn.py`: `execute_foe_phase()`
- SPD/action-gauge is primarily used for:
  - UI “action queue” snapshots (`backend/autofighter/action_queue.py`)
  - Advancing the “turn counter” used by enrage (`context.turn`), via `dispatch_turn_end_snapshot()`:
    - `backend/autofighter/rooms/battle/turn_loop/turn_end.py`
    - `backend/autofighter/rooms/battle/turns.py`

Action points and extra turns:
- Each combatant has `actions_per_turn` and `action_points`.
- If `action_points <= 0`, it is reset to `actions_per_turn` and emits `extra_turn` events for each extra point beyond 1.
  - This drives `_EXTRA_TURNS` (a global per-entity counter) and the UI action queue bonus turns:
    - `backend/autofighter/rooms/battle/pacing.py`

Effect ticking happens *per acting combatant action*:
- At the start of each actor’s action iteration, their `EffectManager.tick(target_effect_manager)` runs:
  - Player: `player_turn.py` calls `await member_effect.tick(target_manager)`
  - Foe: `foe_turn.py` calls `await foe_manager.tick(target_effect)`
- `EffectManager.tick()` processes, in order:
  - HoTs → DoTs → stat modifiers → passives (turn-end/tick style passives)
  - Emits `status_phase_start` / `status_phase_end` events to the bus for UI pacing.
  - `backend/autofighter/effects.py`

Regain heal cadence:
- `Stats.maybe_regain(turn)` heals on *even* turn values.
- The value passed is `context.action_turn` (a global “action index”), not `context.turn`.
  - So regain happens every 2nd action across the entire battle, not “every 2 turns per character”.
  - `backend/autofighter/stats.py`

Target selection:
- Player attacks pick a living foe weighted by `foe.aggro`:
  - `backend/autofighter/rooms/battle/targeting.py`: `select_aggro_target()`
- Foes pick a living party member weighted by `member.aggro`:
  - `backend/autofighter/rooms/battle/turn_loop/foe_turn.py`: `_select_target()`

## Actions (Basic, Special, Ultimate)

Action plugin system:
- The turn loop prefers `plugins.actions` via a shared `ActionRegistry`.
  - `backend/autofighter/rooms/battle/turn_loop/initialization.py`: `get_action_registry()`; fallback registers `BasicAttackAction` only.
  - `backend/plugins/actions/registry.py`: registry / cooldown management.
  - `backend/plugins/actions/context.py`: `BattleContext` wrappers for `apply_damage`, `apply_healing`, resource spending, etc.

Normal/basic attack:
- Player and foe turns both attempt `normal.basic_attack` via the action registry.
- If the action plugin call fails, the loop falls back to a hardcoded attack:
  - calls `prepare_action_attack_metadata(actor)` (for metadata fields)
  - then `target.apply_damage(actor.atk, attacker=actor, action_name=...)`
  - emits `hit_landed` and triggers passive hooks when damage > 0
  - tries to apply a DoT through the target `EffectManager.maybe_inflict_dot()`
  - Player fallback: `backend/autofighter/rooms/battle/turn_loop/player_turn.py`
  - Foe fallback: `backend/autofighter/rooms/battle/turn_loop/foe_turn.py`

Special abilities:
- Characters can declare `special_abilities = ["special.some.action.id", ...]`.
- During initialization these get registered per character id:
  - `backend/autofighter/rooms/battle/turn_loop/initialization.py`: `_register_special_abilities()`
- Player turns try to execute a special ability before basic attack:
  - `backend/autofighter/rooms/battle/turn_loop/player_turn.py`: `_try_special_ability()`

Ultimates:
- Ult charge increases after each action by `actions_per_turn`.
  - Player: `player_turn.py` (`member.add_ultimate_charge(member.actions_per_turn)`)
  - Foe: `foe_turn.py` (`acting_foe.add_ultimate_charge(acting_foe.actions_per_turn)`)
- If `ultimate_ready`:
  - Player tries an action-registry ultimate mapped by damage type id; otherwise falls back to `damage_type.ultimate(...)` if implemented.
    - `player_turn.py`: `_handle_ultimate()`
  - Foes call `damage_type.ultimate(...)` directly (no registry ultimate mapping).
    - `foe_turn.py`: `_handle_ultimate()`

Wind team synergy:
- After each player action, each ally calls `ally.handle_ally_action(actor)` which grants extra ultimate charge to Wind-aligned allies.
  - `backend/autofighter/stats.py`: `handle_ally_action()`

Multi-hit / spread:
- After basic attack, the player turn checks `damage_type.get_turn_spread()` and can run spread logic (notably for Wind) which applies additional scaled hits to other foes.
  - `backend/autofighter/rooms/battle/turn_loop/player_turn.py`: `_handle_wind_spread()`

Summons:
- After resolving an action, the loop:
  - adds newly created summons to the party, and
  - discovers/attaches foe summons into the foe list with new `EffectManager`s
  - then sends a progress update so the UI sees the new entities.
  - `player_turn.py` and `foe_turn.py` (both use `SummonManager`)

## Damage, Healing, and Status Effects

Damage application:
- Core API: `await target.apply_damage(amount, attacker=attacker, ...)`
  - `backend/autofighter/stats.py`: `Stats.apply_damage()`
  - Key steps:
    - If battle isn’t active or target already dead: ignore damage.
    - Dodge check uses *target* `dodge_odds`; emits `dodge` event.
    - Damage type hooks:
      - `attacker.damage_type.on_hit(attacker, target)` (only when `trigger_on_hit=True`)
      - crit: `random() < attacker.crit_rate` → multiply by `attacker.crit_damage`
      - `attacker.damage_type.on_damage(amount, attacker, target)`
    - Target-side hooks:
      - `target.damage_type.on_damage_taken(...)` and `on_party_damage_taken(...)`
      - optional “login theme” damage bonus/reduction maps
    - Mitigation formula (quadratic vs defense³ * vitality * mitigation), possibly repeated `damage_reduction_passes` times.
    - Global enrage multiplies damage taken via `get_enrage_percent()`.
    - Shields absorb before HP is reduced; records `last_shield_absorbed`, `last_overkill`, `last_damage_taken`.
    - Emits batched `damage_taken` / `damage_dealt` events; triggers passive hooks for damage taken.

Healing application:
- Core API: `await target.apply_healing(amount, healer=healer, ...)`
  - `backend/autofighter/stats.py`: `Stats.apply_healing()`
  - Scales by healer vitality and target vitality, then enrage reduces healing globally.
  - Optional overheal converts extra healing into shields with diminishing returns when `overheal_enabled` is true.

DoTs / HoTs:
- `EffectManager` tracks `dots`, `hots`, and `mods`:
  - `backend/autofighter/effects.py`
- DoT/HoT ticks emit events (`dot_tick`, `hot_tick`) then call `apply_damage` / `apply_healing`.
- DoT infliction is usually attempted after a hit: `EffectManager.maybe_inflict_dot(attacker, damage)`.

Passive processing:
- Two separate passive paths exist:
  1) `PassiveRegistry` (event-driven hooks called from the turn loop and from `Stats.apply_damage`)
     - `backend/autofighter/passives.py`
  2) `EffectManager._tick_passives()` (turn-end/tick-style passives processed as part of effect ticking)
     - `backend/autofighter/effects.py`

## Enrage

Enrage threshold:
- `compute_enrage_threshold(room)` chooses normal vs boss thresholds.
  - `backend/autofighter/rooms/battle/enrage.py`

Enrage update:
- Called during the player turn loop (`update_enrage_state(...)`) and controls:
  - global damage-taken multiplier (via `set_enrage_percent(1.35 * stacks)`)
  - a long-lived foe ATK multiplier buff (`atk_mult = 1 + 2.0 * stacks`) applied as a `StatModifier`
  - catastrophic damage if turn exceeds a high threshold
  - `backend/autofighter/rooms/battle/enrage.py`

Bleed:
- While enraged, every 10 enrage-stacks it adds stacking “Enrage Bleed” DoTs to both sides (party and foes) based on max HP.
  - `backend/autofighter/rooms/battle/enrage.py`

