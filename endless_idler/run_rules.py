from __future__ import annotations

import time

from endless_idler.save import RunSave


PARTY_HP_LOSS_DAMAGE_PER_FIGHT = 15
PARTY_HP_LOSS_HEAL = 2
PARTY_HP_WIN_HEAL = 4

IDLE_PARTY_HP_HEAL_AMOUNT = 1
IDLE_PARTY_HP_HEAL_INTERVAL_SECONDS = 15 * 60


def clamp_party_hp(save: RunSave) -> None:
    save.party_hp_max = max(1, int(save.party_hp_max))
    save.party_hp_current = max(0, int(save.party_hp_current))
    save.party_hp_current = min(save.party_hp_current, save.party_hp_max)


def apply_battle_result(save: RunSave, *, victory: bool) -> bool:
    """Returns True if the run should be force-reset."""
    clamp_party_hp(save)
    fight_number = max(1, int(save.fight_number))

    if victory:
        save.party_hp_current = min(save.party_hp_max, save.party_hp_current + PARTY_HP_WIN_HEAL)
        save.fight_number = fight_number + 1
        return False

    damage = PARTY_HP_LOSS_DAMAGE_PER_FIGHT * fight_number
    save.party_hp_current = max(0, save.party_hp_current - damage)
    if save.party_hp_current <= 0:
        return True

    save.party_hp_current = min(save.party_hp_max, save.party_hp_current + PARTY_HP_LOSS_HEAL)
    return False


def apply_idle_party_heal(save: RunSave, *, now: float | None = None) -> int:
    clamp_party_hp(save)
    if save.party_hp_current <= 0:
        return 0
    if save.party_hp_current >= save.party_hp_max:
        return 0

    now = float(time.time() if now is None else now)
    last = float(max(0.0, save.party_hp_last_idle_heal_at))
    if last <= 0.0:
        save.party_hp_last_idle_heal_at = now
        return 0

    elapsed = now - last
    if elapsed < IDLE_PARTY_HP_HEAL_INTERVAL_SECONDS:
        return 0

    ticks = int(elapsed // IDLE_PARTY_HP_HEAL_INTERVAL_SECONDS)
    healed = min(
        IDLE_PARTY_HP_HEAL_AMOUNT * ticks,
        max(0, int(save.party_hp_max - save.party_hp_current)),
    )

    if healed <= 0:
        save.party_hp_last_idle_heal_at = now
        return 0

    save.party_hp_current = min(save.party_hp_max, save.party_hp_current + healed)
    save.party_hp_last_idle_heal_at = last + ticks * IDLE_PARTY_HP_HEAL_INTERVAL_SECONDS
    return healed


def start_idle_heal_timer(save: RunSave, *, now: float | None = None) -> None:
    now = float(time.time() if now is None else now)
    save.party_hp_last_idle_heal_at = now
