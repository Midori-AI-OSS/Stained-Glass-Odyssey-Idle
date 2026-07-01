from __future__ import annotations

from endless_idler.save_migrations.base import MigratableSave
from endless_idler.save_migrations.base import SaveMigration


def _add_warp_fields(save: MigratableSave) -> None:
    if save.version >= 13:
        return

    setattr(save, "warp_pity", {})
    setattr(save, "warp_pull_total", {})
    setattr(save, "warp_last_rarity", {})
    setattr(save, "warp_character_obtained", {})
    save.version = 13


migration = SaveMigration(
    migration_id="v13_warp_fields",
    order=1300,
    migrate=_add_warp_fields,
)
