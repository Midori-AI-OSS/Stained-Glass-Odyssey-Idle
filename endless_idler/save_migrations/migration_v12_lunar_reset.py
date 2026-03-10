from __future__ import annotations

from endless_idler.save_migrations.base import MigratableSave
from endless_idler.save_migrations.base import SaveMigration


def _reset_legacy_lunar_progress(save: MigratableSave) -> None:
    if save.version >= 12:
        return

    lunar = save.blessings.get("lunar_blessing")
    if not isinstance(lunar, dict):
        return

    lunar["steps"] = 0
    lunar["total_minutes"] = 0
    lunar["last_tick_time"] = 0.0
    lunar["step_start_time"] = 0.0


migration = SaveMigration(
    migration_id="v12_lunar_legacy_reset",
    order=1200,
    migrate=_reset_legacy_lunar_progress,
)
