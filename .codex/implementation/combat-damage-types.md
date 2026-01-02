# Combat: Damage-Type Mechanics (Battle)

This document describes the per-damage-type mechanics applied during battle simulation.

## Where It Lives

- Battle step loop: `endless_idler/ui/battle/screen.py`
- Damage-type mechanics helpers: `endless_idler/ui/battle/mechanics.py`
- Core damage calculation: `endless_idler/ui/battle/sim.py` (`calculate_damage`)

## Core Concepts

- Battles alternate actions between the party and foes; each side selects an attacker weighted by `spd`.
- “Onsite” refers to active combatants in the battle arena.
- “Offsite” refers to the party’s reserve combatants displayed in the battle UI (they do not attack directly).
- Most damage-type mechanics are applied at the start of the attacker’s action and may modify the attacker’s next attack.
- HP reductions from effects are clamped so the affected combatant cannot drop below **20% of max HP**.

## Damage-Type Rules

### Dark

- On the dark attacker’s action, they reduce allied HP:
  - Onsite allies: **5% of max HP**
  - Offsite allies: **15% of max HP**
  - Both reductions clamp at **20% remaining HP**.
- For each point of HP removed across all affected allies, the dark attacker’s next attack gains:
  - **+0.01% damage per 1 HP removed** (`1.0 + 0.0001 * removed_hp`)

### Light

- On the light attacker’s action, they may heal allies instead of attacking.
- Healing “power” is based on the attacker’s `atk`:
  - Base heal = **5% of atk**
- Single-target heal:
  - 1 target at full base heal
  - If the target is offsite: **2× base heal**
- AOE heal:
  - Heals all wounded allies
  - Per-target heal = `base_heal / number_of_targets`
  - If a target is offsite: **2× per-target heal**
- If a light attacker heals, they **do not attack** on that action.

### Fire

- On the fire attacker’s action, they self-bleed to buff their next attack.
- Bleed amount scales with how many turns the combatant has taken:
  - Bleed fraction per action = `0.05% * turns_taken` (i.e. `0.0005 * turns_taken`)
  - Capped at **50% of max HP per action**
  - Clamped at **20% remaining HP**
- For each point of HP removed, the fire attacker’s next attack gains:
  - **+5% damage per 1 HP removed** (`1.0 + 0.05 * removed_hp`)

### Wind

- Wind attackers always attack **all living enemies**.
- Each target takes **1/N** of the attacker’s computed damage, where `N` is the number of targets hit.

### Lightning

- Lightning attackers perform **5 attacks** against a single target on their action.

### Ice

- Ice combatants act more slowly:
  - They require two selections to attack: first selection “charges”, second selection attacks.
- Ice combatants take reduced incoming damage via the shared damage reduction system:
  - `calculate_damage` applies the defender’s `damage_reduction_passes` to the defense mitigation step.
  - Ice defaults to **2 passes** unless overridden by the character plugin.

