from __future__ import annotations

from endless_idler.save_migrations.base import MigratableSave
from endless_idler.save_migrations.base import SaveMigration


def _add_yolo_prefs(save: MigratableSave) -> None:
    if save.version >= 14:
        return

    setattr(save, "warp_yolo_preferences", [])
    save.version = 14


migration = SaveMigration(
    migration_id="v14_yolo_prefs",
    order=1400,
    migrate=_add_yolo_prefs,
)
