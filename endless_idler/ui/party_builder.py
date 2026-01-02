from __future__ import annotations

import random

from PySide6.QtCore import QPropertyAnimation
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.combat.party_stats import apply_offsite_stat_share
from endless_idler.combat.party_stats import build_scaled_character_stats
from endless_idler.combat.stats import Stats
from endless_idler.progression import record_character_death
from endless_idler.save import (
    BAR_SLOTS,
    DEFAULT_CHARACTER_COST,
    OFFSITE_SLOTS,
    ONSITE_SLOTS,
    DEFAULT_SHOP_REROLL_COST,
    STANDBY_SLOTS,
    RunSave,
    SaveManager,
    new_run_save,
    sanitize_save_characters,
    next_party_level_up_cost,
)
from endless_idler.ui.party_builder_bar import CharacterBar
from endless_idler.ui.party_builder_fight_bar import FightBar
from endless_idler.ui.party_builder_idle_bar import IdleBar
from endless_idler.ui.party_builder_merge_fx import MergeFxOverlay
from endless_idler.ui.party_builder_party_level_tile import StandbyPartyLevelTile
from endless_idler.ui.party_builder_planes import PulsingPlane
from endless_idler.ui.party_builder_rewards_plane import RewardsPlane
from endless_idler.ui.party_builder_sell import SellZone
from endless_idler.ui.party_builder_shop_tile import StandbyShopTile
from endless_idler.ui.party_builder_slot import DropSlot
from endless_idler.ui.party_hp_bar import PartyHpHeader
from endless_idler.ui.idle.idle_state import IDLE_TICK_INTERVAL_SECONDS
from endless_idler.ui.idle.idle_state import IdleGameState


SHOP_HIGH_STAR_THRESHOLD = 6
SHOP_HIGH_STAR_WEIGHT_MULTIPLIER = 1e-4
SHOP_DUPLICATE_WEIGHT_BASE = 0.05
SHOP_IDLE_EXP_SCALE = 0.0001


class PartyBuilderWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Party Builder")
        self.resize(1280, 820)

        self.setCentralWidget(PartyBuilderWidget())


class PartyBuilderWidget(QWidget):
    back_requested = Signal()
    fight_requested = Signal(object)
    idle_requested = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("partyBuilderScreen")

        self._rng = random.Random()
        self._root_layout: QVBoxLayout | None = None
        self._plugins = discover_character_plugins()
        self._plugin_by_id = {plugin.char_id: plugin for plugin in self._plugins}
        self._save_manager = SaveManager()
        self._save = sanitize_save_characters(
            save=self._save_manager.load() or self._new_run_save(),
            allowed_char_ids=set(self._plugin_by_id),
        )
        self._save_manager.save(self._save)
        self._slots_by_id: dict[str, DropSlot] = {}
        self._shop_open = False
        self._sell_zones: list[SellZone] = []
        self._drag_active = False
        self._party_dirty = False
        self._party_finalize_timer: QTimer | None = None
        self._shop_exp_state: IdleGameState | None = None
        self._shop_exp_signature: tuple[tuple[str, ...], tuple[str, ...], int] | None = None
        self._shop_exp_timer: QTimer | None = None
        self._shop_exp_ticks = 0
        self._shop_tile: StandbyShopTile | None = None
        self._party_level_tile: StandbyPartyLevelTile | None = None
        self._rewards_plane: RewardsPlane | None = None
        self._overlay_layout: QGridLayout | None = None
        self._shop_clearance: QWidget | None = None
        self._fight_bar: FightBar | None = None
        self._idle_bar: IdleBar | None = None
        self._party_hp_header: PartyHpHeader | None = None
        self._merge_fx: MergeFxOverlay | None = None

        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)
        self.setLayout(root)
        self._root_layout = root

        header = QGridLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setHorizontalSpacing(10)
        header.setVerticalSpacing(0)
        root.addLayout(header)

        back = QPushButton("Back")
        back.setObjectName("partyBackButton")
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.clicked.connect(self.back_requested.emit)
        header.addWidget(back, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        party_hp = PartyHpHeader()
        self._party_hp_header = party_hp
        header.addWidget(party_hp, 0, 1, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        header.setColumnStretch(1, 1)
        spacer = QWidget()
        spacer.setFixedWidth(back.sizeHint().width())
        spacer.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        header.addWidget(spacer, 0, 2, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._char_bar: CharacterBar | None = None
        self._token_label: QLabel | None = None
        self._token_opacity: QGraphicsOpacityEffect | None = None
        self._token_pulse_anim: QPropertyAnimation | None = None

        overlay_host = QWidget()
        overlay = QGridLayout()
        overlay.setContentsMargins(0, 0, 0, 0)
        overlay.setSpacing(0)
        overlay_host.setLayout(overlay)
        self._overlay_layout = overlay

        clearance = QWidget()
        clearance.setFixedHeight(0)
        clearance.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        clearance.setVisible(False)
        self._shop_clearance = clearance

        overlay.addWidget(self._make_main_area(), 0, 0)
        root.addWidget(overlay_host, 1)

        merge_fx = MergeFxOverlay(self)
        merge_fx.setGeometry(self.rect())
        merge_fx.hide()
        merge_fx.raise_()
        self._merge_fx = merge_fx

        finalize_timer = QTimer(self)
        finalize_timer.setSingleShot(True)
        finalize_timer.timeout.connect(self._finalize_party_changes)
        self._party_finalize_timer = finalize_timer

        shop_timer = QTimer(self)
        shop_timer.setInterval(int(max(1, IDLE_TICK_INTERVAL_SECONDS * 1000)))
        shop_timer.timeout.connect(self._shop_exp_tick)
        self._shop_exp_timer = shop_timer

        self._maybe_build_char_bar()

        self._refresh_tokens()
        self._load_slots_from_save()
        self._refresh_party_hp()
        self._refresh_rewards_plane()
        self._refresh_action_bars_state()

    def showEvent(self, event: object) -> None:
        if self._shop_exp_timer is not None and not self._shop_exp_timer.isActive():
            self._shop_exp_timer.start()
        try:
            super().showEvent(event)  # type: ignore[misc]
        except Exception:
            return

    def hideEvent(self, event: object) -> None:
        if self._shop_exp_timer is not None:
            self._shop_exp_timer.stop()
        self._save_shop_exp_state()
        try:
            super().hideEvent(event)  # type: ignore[misc]
        except Exception:
            return

    def resizeEvent(self, event: object) -> None:
        if self._merge_fx is not None:
            self._merge_fx.setGeometry(self.rect())
            self._merge_fx.raise_()
        try:
            super().resizeEvent(event)  # type: ignore[misc]
        except Exception:
            return

    def _maybe_build_char_bar(self) -> None:
        if not self._shop_open:
            return
        if self._char_bar is not None:
            return
        if self._overlay_layout is None:
            return

        bar = CharacterBar(
            char_ids=self._save.bar,
            plugins_by_id=self._plugin_by_id,
            rng=self._rng,
            on_reroll=self._reroll_shop,
            reroll_cost=DEFAULT_SHOP_REROLL_COST,
            get_stack_count=self._get_stack_count,
            character_cost=DEFAULT_CHARACTER_COST,
            can_afford=self._can_afford,
            on_insufficient_funds=self._pulse_tokens,
            get_tooltip_stats=self._tooltip_stats_for_character,
        )

        bar.destroyed.connect(self._on_char_bar_destroyed)
        self._char_bar = bar
        self._overlay_layout.addWidget(bar, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        if self._merge_fx is not None:
            self._merge_fx.raise_()
        self._set_shop_clearance_for_bar()

    def _on_char_bar_destroyed(self) -> None:
        self._char_bar = None
        self._shop_open = False
        self._set_shop_clearance_height(0)
        if self._shop_tile is not None:
            self._shop_tile.set_open(False)
        self._refresh_party_hp()

    def _set_shop_open(self, open_: bool) -> None:
        self._shop_open = open_
        if self._shop_tile is not None:
            self._shop_tile.set_open(open_)

        if self._char_bar is not None and self._overlay_layout is not None:
            bar = self._char_bar
            self._overlay_layout.removeWidget(bar)
            self._char_bar.hide()
            self._char_bar.setParent(None)
            bar.deleteLater()

        self._char_bar = None
        if not open_:
            self._set_shop_clearance_height(0)

        if open_:
            self._maybe_build_char_bar()
        self._refresh_party_hp()

    def _set_shop_clearance_height(self, height: int) -> None:
        if self._shop_clearance is None:
            return
        height = max(0, int(height))
        self._shop_clearance.setFixedHeight(height)
        self._shop_clearance.setVisible(height > 0)

    def _set_shop_clearance_for_bar(self) -> None:
        if self._char_bar is None:
            self._set_shop_clearance_height(0)
            return
        self._set_shop_clearance_height(self._char_bar.sizeHint().height() + 12)

    def _new_run_save(self) -> RunSave:
        return new_run_save(
            available_char_ids=[plugin.char_id for plugin in self._plugins],
            rng=self._rng,
        )

    def _make_onsite_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        left_sell = SellZone(on_sell=self._sell_character)
        right_sell = SellZone(on_sell=self._sell_character)
        self._sell_zones = [left_sell, right_sell]
        for zone in self._sell_zones:
            zone.set_active(False)

        row.addWidget(left_sell)
        row.addStretch(1)

        for index in range(ONSITE_SLOTS):
            slot_id = f"onsite_{index + 1}"
            slot = DropSlot(
                empty_label="OnSite",
                slot_id=slot_id,
                plugins_by_id=self._plugin_by_id,
                rng=self._rng,
                character_cost=DEFAULT_CHARACTER_COST,
                can_afford=self._can_afford,
                purchase_character=self._purchase_character,
                is_in_party=self._is_char_in_party,
                is_primary_stack_slot=self._is_primary_stack_slot,
                on_slot_changed=self._on_slot_changed,
                on_drag_active_changed=self._set_sell_zones_active,
                get_stack_count=self._get_stack_count,
                get_tooltip_stats=self._tooltip_stats_for_character,
                allow_stacking=True,
                show_stack_badge=True,
            )
            self._slots_by_id[slot_id] = slot
            row.addWidget(slot)

        row.addStretch(1)
        row.addWidget(right_sell)

        return row

    def _make_row(
        self,
        label: str,
        *,
        count: int,
        center: bool = False,
        allow_stacking: bool = True,
        show_stack_badge: bool = True,
    ) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        if center:
            row.addStretch(1)

        for index in range(count):
            slot_id = f"{label.lower()}_{index + 1}"
            slot = DropSlot(
                empty_label=label,
                slot_id=slot_id,
                plugins_by_id=self._plugin_by_id,
                rng=self._rng,
                character_cost=DEFAULT_CHARACTER_COST,
                can_afford=self._can_afford,
                purchase_character=self._purchase_character,
                is_in_party=self._is_char_in_party,
                is_primary_stack_slot=self._is_primary_stack_slot,
                on_slot_changed=self._on_slot_changed,
                on_drag_active_changed=self._set_sell_zones_active,
                get_stack_count=self._get_stack_count,
                get_tooltip_stats=self._tooltip_stats_for_character,
                allow_stacking=allow_stacking,
                show_stack_badge=show_stack_badge,
            )
            self._slots_by_id[slot_id] = slot
            row.addWidget(slot)

        row.addStretch(1)

        return row

    def _make_main_area(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        wrapper.setLayout(layout)

        if self._shop_clearance is not None:
            layout.addWidget(self._shop_clearance)

        block = QWidget()
        block_layout = QVBoxLayout()
        block_layout.setContentsMargins(0, 0, 0, 0)
        block_layout.setSpacing(12)
        block.setLayout(block_layout)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(18)
        top_row.addStretch(1)

        top_row.addWidget(PulsingPlane(object_name="groupFxPlane", tone="light"), 0, Qt.AlignmentFlag.AlignTop)

        party = QWidget()
        party.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        party_layout = QVBoxLayout()
        party_layout.setContentsMargins(0, 0, 0, 0)
        party_layout.setSpacing(12)
        party.setLayout(party_layout)
        party_layout.addLayout(self._make_onsite_row())
        party_layout.addLayout(self._make_row("Offsite", count=OFFSITE_SLOTS, center=True))
        top_row.addWidget(party, 0, Qt.AlignmentFlag.AlignTop)

        rewards = RewardsPlane()
        self._rewards_plane = rewards
        top_row.addWidget(rewards, 0, Qt.AlignmentFlag.AlignTop)
        top_row.addStretch(1)

        block_layout.addLayout(top_row)
        block_layout.addWidget(self._make_fight_and_standby_area(), 0, Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(block)
        return wrapper

    def _make_fight_and_standby_area(self) -> QWidget:
        wrapper = QWidget()
        wrapper_layout = QVBoxLayout()
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(12)
        wrapper.setLayout(wrapper_layout)

        fight_row = QHBoxLayout()
        fight_row.setContentsMargins(0, 0, 14, 0)
        fight_row.setSpacing(12)
        fight_row.addStretch(1)
        self._idle_bar = IdleBar()
        self._idle_bar.clicked.connect(self._request_idle)
        fight_row.addWidget(self._idle_bar)
        self._fight_bar = FightBar()
        self._fight_bar.clicked.connect(self._request_fight)
        fight_row.addWidget(self._fight_bar)
        wrapper_layout.addLayout(fight_row)

        wrapper_layout.addWidget(self._make_standby_row())
        return wrapper

    def _make_standby_row(self) -> QFrame:
        container = QFrame()
        container.setObjectName("standbyBarContainer")
        container.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        row = QHBoxLayout(container)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(10)

        self._party_level_tile = StandbyPartyLevelTile(
            level=self._save.party_level,
            cost=self._save.party_level_up_cost,
        )
        self._party_level_tile.level_requested.connect(self._attempt_party_level_up)
        row.addWidget(self._party_level_tile)

        for save_index in range(1, max(1, STANDBY_SLOTS - 1)):
            slot_id = f"standby_{save_index}"
            slot = DropSlot(
                empty_label="Standby",
                slot_id=slot_id,
                plugins_by_id=self._plugin_by_id,
                rng=self._rng,
                character_cost=DEFAULT_CHARACTER_COST,
                can_afford=self._can_afford,
                purchase_character=self._purchase_character,
                is_in_party=self._is_char_in_party,
                is_primary_stack_slot=self._is_primary_stack_slot,
                on_slot_changed=self._on_slot_changed,
                on_drag_active_changed=self._set_sell_zones_active,
                get_stack_count=self._get_stack_count,
                get_tooltip_stats=self._tooltip_stats_for_character,
                allow_stacking=False,
                show_stack_badge=True,
            )
            self._slots_by_id[slot_id] = slot
            row.addWidget(slot)

        self._shop_tile = StandbyShopTile(tokens=self._save.tokens, open_=self._shop_open)
        self._shop_tile.toggled.connect(self._set_shop_open)
        self._token_label = self._shop_tile.token_label
        row.addWidget(self._shop_tile)

        return container

    def _can_afford(self, cost: int) -> bool:
        return self._save.tokens >= cost

    def _is_char_in_party(self, char_id: str) -> bool:
        return char_id in {item for item in (self._save.onsite + self._save.offsite) if item}

    def _is_primary_stack_slot(self, slot_id: str, char_id: str) -> bool:
        prefix, index_raw = slot_id.split("_", 1)
        if prefix != "standby":
            return True

        if self._is_char_in_party(char_id):
            return False

        try:
            standby_index = int(index_raw)
        except ValueError:
            return False
        if standby_index <= 0 or standby_index >= max(1, len(self._save.standby) - 1):
            return False

        for first in self._iter_standby_indices():
            if self._save.standby[first] == char_id:
                return first == standby_index
        return False

    def _iter_standby_indices(self) -> range:
        return range(1, max(1, len(self._save.standby) - 1))

    def _attempt_party_level_up(self) -> None:
        cost = max(0, int(self._save.party_level_up_cost))
        if self._save.tokens < cost:
            self._pulse_tokens()
            return
        if cost <= 0:
            return

        self._save.tokens -= cost
        self._save.party_level = max(1, int(self._save.party_level)) + 1
        self._save.party_level_up_cost = next_party_level_up_cost(
            new_level=self._save.party_level,
            previous_cost=cost,
        )
        self._refresh_tokens()
        self._refresh_party_level()
        self._save_manager.save(self._save)

    def _purchase_character(self, char_id: str, destination: str, target_char_id: str | None) -> bool:
        if self._save.tokens < DEFAULT_CHARACTER_COST:
            return False
        if char_id not in self._save.bar:
            return False

        in_party = char_id in {item for item in (self._save.onsite + self._save.offsite) if item}
        destination = destination.strip().lower()

        if destination in {"onsite", "offsite"}:
            if target_char_id is None:
                if in_party:
                    return False
                self._save.stacks[char_id] = max(1, int(self._save.stacks.get(char_id, 1)))
            else:
                if target_char_id != char_id:
                    return False
                if not in_party:
                    return False
                if not self._add_copy_or_merge(char_id):
                    return False
        elif destination == "standby":
            if target_char_id is not None:
                return False
        else:
            return False

        self._save.tokens -= DEFAULT_CHARACTER_COST

        removed = False
        updated_bar: list[str | None] = []
        for item in self._save.bar:
            if not removed and item == char_id:
                updated_bar.append(None)
                removed = True
            else:
                updated_bar.append(item)
        self._save.bar = updated_bar

        self._refresh_tokens()
        self._apply_auto_merges()
        self._refresh_standby_slots()
        self._save_manager.save(self._save)
        if self._char_bar is not None:
            self._char_bar.refresh_stack_badges()
        return True

    def _add_copy_or_merge(self, char_id: str) -> bool:
        indices = [index for index in self._iter_standby_indices() if self._save.standby[index] == char_id]
        if indices:
            first = indices[0]
            self._play_merge_fx(char_id=char_id, standby_indices=[first])
            self._save.standby[first] = None
            slot = self._slots_by_id.get(f"standby_{first}")
            if slot:
                slot.load_char_id(None)
            self._save.stacks[char_id] = max(1, int(self._save.stacks.get(char_id, 1))) + 2
            self._refresh_party_slot(char_id)
            return True

        empty = self._first_empty_standby_index()
        if empty is None:
            return False
        self._save.standby[empty] = char_id
        slot = self._slots_by_id.get(f"standby_{empty}")
        if slot:
            slot.load_char_id(char_id)
        return True

    def _first_empty_standby_index(self) -> int | None:
        for index in self._iter_standby_indices():
            if not self._save.standby[index]:
                return index
        return None

    def _apply_auto_merges(self) -> None:
        party = [item for item in (self._save.onsite + self._save.offsite) if item]
        for char_id in sorted(set(party)):
            indices = [index for index in self._iter_standby_indices() if self._save.standby[index] == char_id]
            while len(indices) >= 2:
                first, second = indices[:2]
                self._play_merge_fx(char_id=char_id, standby_indices=[first, second])
                self._save.standby[first] = None
                self._save.standby[second] = None
                for idx in (first, second):
                    slot = self._slots_by_id.get(f"standby_{idx}")
                    if slot:
                        slot.load_char_id(None)
                self._save.stacks[char_id] = max(1, int(self._save.stacks.get(char_id, 1))) + 2
                self._refresh_party_slot(char_id)
                indices = [index for index in self._iter_standby_indices() if self._save.standby[index] == char_id]

        self._refresh_standby_slots()

    def _refresh_standby_slots(self) -> None:
        for index in self._iter_standby_indices():
            slot = self._slots_by_id.get(f"standby_{index}")
            if slot:
                slot.refresh_view()

    def _refresh_party_slot(self, char_id: str) -> None:
        if char_id in self._save.onsite:
            index = self._save.onsite.index(char_id)
            slot = self._slots_by_id.get(f"onsite_{index + 1}")
            if slot:
                slot.refresh_view()
            return

        if char_id in self._save.offsite:
            index = self._save.offsite.index(char_id)
            slot = self._slots_by_id.get(f"offsite_{index + 1}")
            if slot:
                slot.refresh_view()

    def _party_slot_for_char(self, char_id: str) -> DropSlot | None:
        if char_id in self._save.onsite:
            index = self._save.onsite.index(char_id)
            return self._slots_by_id.get(f"onsite_{index + 1}")
        if char_id in self._save.offsite:
            index = self._save.offsite.index(char_id)
            return self._slots_by_id.get(f"offsite_{index + 1}")
        return None

    def _play_merge_fx(self, *, char_id: str, standby_indices: list[int]) -> None:
        if self._merge_fx is None:
            return
        destination = self._party_slot_for_char(char_id)
        if destination is None:
            return

        sources: list[QWidget] = []
        for idx in standby_indices:
            slot = self._slots_by_id.get(f"standby_{idx}")
            if slot is not None:
                sources.append(slot)
        if not sources:
            return

        self._merge_fx.play_merge(sources=sources, destination=destination)

    def _sell_character(self, char_id: str) -> None:
        stacks = self._save.stacks.get(char_id, 1)
        self._save.tokens += DEFAULT_CHARACTER_COST * max(1, int(stacks))
        self._save.stacks.pop(char_id, None)
        self._refresh_tokens()
        self._save_manager.save(self._save)

    def _set_sell_zones_active(self, active: bool) -> None:
        self._drag_active = bool(active)
        for zone in self._sell_zones:
            zone.set_active(active)
        if not self._drag_active and self._party_dirty:
            self._schedule_party_finalize()

    def _pulse_tokens(self) -> None:
        if self._token_label is None:
            return
        if self._token_opacity is None:
            effect = QGraphicsOpacityEffect(self._token_label)
            effect.setOpacity(1.0)
            self._token_label.setGraphicsEffect(effect)
            self._token_opacity = effect

        if self._token_pulse_anim is None:
            anim = QPropertyAnimation(self._token_opacity, b"opacity", self)
            anim.setDuration(1400)
            anim.setLoopCount(2)
            anim.setKeyValueAt(0.0, 1.0)
            anim.setKeyValueAt(0.5, 0.25)
            anim.setKeyValueAt(1.0, 1.0)
            self._token_pulse_anim = anim

        self._token_pulse_anim.stop()
        self._token_pulse_anim.start()

    def _reset_run(self) -> None:
        result = QMessageBox.question(
            self,
            "Reset Run",
            "Reset tokens, party, stacks, and shop?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            return

        preserved_progress = dict(self._save.character_progress)
        preserved_stats = dict(self._save.character_stats)
        preserved_initial_stats = dict(getattr(self._save, "character_initial_stats", {}) or {})
        preserved_deaths = dict(getattr(self._save, "character_deaths", {}) or {})
        preserved_bonus = float(self._save.idle_exp_bonus_seconds)
        preserved_penalty = float(self._save.idle_exp_penalty_seconds)

        for char_id in sorted({item for item in (self._save.onsite + self._save.offsite) if item}):
            plugin = self._plugin_by_id.get(char_id)
            record_character_death(
                self._save,
                char_id=char_id,
                base_stats_template=getattr(plugin, "base_stats", None),
            )
        preserved_stats = dict(self._save.character_stats)
        preserved_initial_stats = dict(getattr(self._save, "character_initial_stats", {}) or {})
        preserved_deaths = dict(getattr(self._save, "character_deaths", {}) or {})

        self._save = self._new_run_save()
        self._save.character_progress = preserved_progress
        self._save.character_stats = preserved_stats
        self._save.character_initial_stats = preserved_initial_stats
        self._save.character_deaths = preserved_deaths
        self._save.idle_exp_bonus_seconds = preserved_bonus
        self._save.idle_exp_penalty_seconds = preserved_penalty
        self._save_manager.save(self._save)

        self._set_sell_zones_active(False)
        self._refresh_tokens()
        self._refresh_party_level()
        self._load_slots_from_save()
        self._refresh_action_bars_state()
        self._refresh_party_hp()
        self._refresh_rewards_plane()
        if self._char_bar is not None:
            self._char_bar.set_char_ids(self._save.bar)

    def _reroll_shop(self) -> None:
        reroll_cost = max(0, int(DEFAULT_SHOP_REROLL_COST))
        if reroll_cost > 0:
            if self._save.tokens < reroll_cost:
                self._pulse_tokens()
                return
            self._save.tokens -= reroll_cost

        party = [item for item in (self._save.onsite + self._save.offsite) if item]
        party_unique = sorted(set(party))
        filled = len(party_unique)
        fill_ratio = filled / float(ONSITE_SLOTS + OFFSITE_SLOTS)

        all_ids = [plugin.char_id for plugin in self._plugins]
        party_set = set(party_unique)
        non_party = [char_id for char_id in all_ids if char_id not in party_set]

        offers: list[str | None] = []
        offered_counts: dict[str, int] = {}
        for index in range(1, BAR_SLOTS + 1):
            offer = self._roll_shop_offer(index, fill_ratio, party_unique, non_party, offered_counts)
            offers.append(offer)
            if offer:
                offered_counts[offer] = offered_counts.get(offer, 0) + 1

        if len(offers) > 1:
            self._rng.shuffle(offers)

        self._save.bar = offers

        self._refresh_tokens()
        self._save_manager.save(self._save)
        if self._char_bar is not None:
            self._char_bar.set_char_ids(self._save.bar)

    def _roll_shop_offer(
        self,
        slot_index: int,
        fill_ratio: float,
        party: list[str],
        non_party: list[str],
        offered_counts: dict[str, int],
    ) -> str | None:
        if not party and not non_party:
            return None

        debuff_by_slot: dict[int, float] = {4: 1.0, 5: 2.5, 6: 5.0}
        base_boost = 1.15 if slot_index <= 3 else 1.0
        base_boost = base_boost / debuff_by_slot.get(slot_index, 1.0)
        p_party = max(0.0, min(0.6, fill_ratio * 0.65 * base_boost))

        prefer_party = bool(party) and (self._rng.random() < p_party)
        primary = party if prefer_party else non_party
        secondary = non_party if prefer_party else party

        pool = [char_id for char_id in primary if offered_counts.get(char_id, 0) <= 0]
        if not pool:
            pool = [char_id for char_id in secondary if offered_counts.get(char_id, 0) <= 0]
        if not pool:
            pool = primary if primary else secondary

        weights = [self._shop_offer_weight(char_id, offered_counts) for char_id in pool]
        return self._weighted_choice(pool, weights)

    def _shop_offer_weight(self, char_id: str, offered_counts: dict[str, int]) -> float:
        stacks = self._save.stacks.get(char_id, 1)
        extra = max(0, int(stacks) - 1)
        stack_weight = 1.0 / (1.0 + extra * 0.25)

        plugin = self._plugin_by_id.get(char_id)
        stars = 1 if plugin is None else int(getattr(plugin, "stars", 1) or 1)
        stars = max(1, stars)
        star_weight = SHOP_HIGH_STAR_WEIGHT_MULTIPLIER if stars >= SHOP_HIGH_STAR_THRESHOLD else 1.0

        duplicates = max(0, int(offered_counts.get(char_id, 0)))
        duplicate_weight = SHOP_DUPLICATE_WEIGHT_BASE**duplicates

        return stack_weight * star_weight * duplicate_weight

    def _weighted_choice(self, items: list[str], weights: list[float]) -> str | None:
        if not items:
            return None
        total = sum(max(0.0, float(w)) for w in weights)
        if total <= 0:
            return self._rng.choice(items)
        threshold = self._rng.random() * total
        running = 0.0
        for item, weight in zip(items, weights, strict=False):
            running += max(0.0, float(weight))
            if running >= threshold:
                return item
        return items[-1]

    def _get_stack_count(self, char_id: str) -> int:
        return max(0, int(self._save.stacks.get(char_id, 0)))

    def _tooltip_stats_for_character(self, char_id: str, context: str) -> Stats | None:
        char_id = str(char_id or "").strip()
        if not char_id:
            return None

        plugin = self._plugin_by_id.get(char_id)
        if plugin is None:
            return None

        party_level = max(1, int(getattr(self._save, "party_level", 1) or 1))
        stacks = max(1, int(self._save.stacks.get(char_id, 1)))
        stars = max(1, int(getattr(plugin, "stars", 1) or 1))

        stats = build_scaled_character_stats(
            plugin=plugin,
            party_level=party_level,
            stars=stars,
            stacks=stacks,
            progress=self._save.character_progress.get(char_id),
            saved_base_stats=self._save.character_stats.get(char_id),
        )

        if (context or "").strip().lower() != "onsite":
            return stats

        reserves = self._build_offsite_reserve_stats(party_level=party_level)
        apply_offsite_stat_share(party=[stats], reserves=reserves, share=0.10)
        return stats

    def _build_offsite_reserve_stats(self, *, party_level: int) -> list[Stats]:
        reserves: list[Stats] = []
        party_level = max(1, int(party_level))
        seen: set[str] = set()
        for char_id in [str(item) for item in self._save.offsite if item]:
            if len(reserves) >= 6:
                break
            if char_id in seen:
                continue
            seen.add(char_id)

            plugin = self._plugin_by_id.get(char_id)
            if plugin is None:
                continue

            stacks = max(1, int(self._save.stacks.get(char_id, 1)))
            stars = max(1, int(getattr(plugin, "stars", 1) or 1))
            reserves.append(
                build_scaled_character_stats(
                    plugin=plugin,
                    party_level=party_level,
                    stars=stars,
                    stacks=stacks,
                    progress=self._save.character_progress.get(char_id),
                    saved_base_stats=self._save.character_stats.get(char_id),
                )
            )
        return reserves

    def _on_slot_changed(self, slot_id: str, char_id: str | None) -> None:
        prefix, index_raw = slot_id.split("_", 1)
        try:
            index = int(index_raw) - 1
        except ValueError:
            return

        if prefix == "onsite" and 0 <= index < len(self._save.onsite):
            self._save.onsite[index] = char_id
        elif prefix == "offsite" and 0 <= index < len(self._save.offsite):
            self._save.offsite[index] = char_id
        elif prefix == "standby":
            try:
                standby_index = int(index_raw)
            except ValueError:
                return
            if standby_index <= 0 or standby_index >= max(1, len(self._save.standby) - 1):
                return
            self._save.standby[standby_index] = char_id
        else:
            return

        if char_id and prefix in {"onsite", "offsite"}:
            self._save.stacks[char_id] = max(1, int(self._save.stacks.get(char_id, 1)))

        self._party_dirty = True
        self._schedule_party_finalize()

    def _schedule_party_finalize(self) -> None:
        if self._party_finalize_timer is None:
            return
        self._party_finalize_timer.stop()
        self._party_finalize_timer.start(200)

    def _finalize_party_changes(self) -> None:
        if self._drag_active:
            self._schedule_party_finalize()
            return
        if not self._party_dirty:
            return

        self._party_dirty = False
        self._apply_auto_merges()
        self._refresh_standby_slots()
        self._save_manager.save(self._save)
        self._refresh_action_bars_state()
        self._refresh_party_hp()
        if self._char_bar is not None:
            self._char_bar.refresh_stack_badges()
        self._refresh_rewards_plane()
        self._shop_exp_signature = None

    def _shop_exp_tick(self) -> None:
        onsite = [item for item in self._save.onsite if item]
        offsite = [item for item in self._save.offsite if item]
        if not onsite:
            self._save_shop_exp_state()
            self._shop_exp_state = None
            self._shop_exp_signature = None
            self._shop_exp_ticks = 0
            return

        signature = (tuple(onsite), tuple(offsite), int(self._save.party_level))
        if self._shop_exp_state is None or self._shop_exp_signature != signature:
            self._shop_exp_state = IdleGameState(
                char_ids=list(onsite),
                offsite_ids=list(offsite),
                party_level=int(self._save.party_level),
                stacks=dict(self._save.stacks),
                plugins_by_id=self._plugin_by_id,
                rng=self._rng,
                progress_by_id=dict(self._save.character_progress),
                stats_by_id=dict(self._save.character_stats),
                initial_stats_by_id=dict(getattr(self._save, "character_initial_stats", {}) or {}),
                exp_bonus_seconds=float(self._save.idle_exp_bonus_seconds),
                exp_penalty_seconds=float(self._save.idle_exp_penalty_seconds),
                exp_gain_scale=SHOP_IDLE_EXP_SCALE,
                advance_run_buffs=False,
            )
            self._shop_exp_signature = signature
            self._shop_exp_ticks = 0

        self._shop_exp_state.process_tick()
        self._shop_exp_ticks += 1
        self._merge_shop_exp_exports()

        if IDLE_TICK_INTERVAL_SECONDS > 0 and self._shop_exp_ticks % int(max(1, round(5.0 / IDLE_TICK_INTERVAL_SECONDS))) == 0:
            self._save_shop_exp_state()

    def _merge_shop_exp_exports(self) -> None:
        if self._shop_exp_state is None:
            return

        progress = dict(self._save.character_progress)
        progress.update(self._shop_exp_state.export_progress())
        self._save.character_progress = progress

        stats = dict(self._save.character_stats)
        stats.update(self._shop_exp_state.export_character_stats())
        self._save.character_stats = stats

        initial_stats = dict(getattr(self._save, "character_initial_stats", {}) or {})
        initial_stats.update(self._shop_exp_state.export_initial_stats())
        self._save.character_initial_stats = initial_stats

    def _save_shop_exp_state(self) -> None:
        if self._shop_exp_state is None:
            return
        self._merge_shop_exp_exports()
        self._save_manager.save(self._save)

    def _load_slots_from_save(self) -> None:
        for index, char_id in enumerate(self._save.onsite):
            slot = self._slots_by_id.get(f"onsite_{index + 1}")
            if slot:
                slot.load_char_id(char_id)

        for index, char_id in enumerate(self._save.offsite):
            slot = self._slots_by_id.get(f"offsite_{index + 1}")
            if slot:
                slot.load_char_id(char_id)

        for index in self._iter_standby_indices():
            slot = self._slots_by_id.get(f"standby_{index}")
            if slot:
                slot.load_char_id(self._save.standby[index])

    def _refresh_tokens(self) -> None:
        if self._shop_tile is not None:
            self._shop_tile.set_tokens(self._save.tokens)

    def _refresh_party_hp(self) -> None:
        if self._party_hp_header is None:
            return
        self._party_hp_header.setVisible(True)
        self._party_hp_header.set_hp(
            current=int(getattr(self._save, "party_hp_current", 0)),
            max_hp=int(getattr(self._save, "party_hp_max", 0)),
        )

    def _refresh_rewards_plane(self) -> None:
        if self._rewards_plane is None:
            return
        self._rewards_plane.set_idle_exp_timers(
            bonus_seconds=float(getattr(self._save, "idle_exp_bonus_seconds", 0.0)),
            penalty_seconds=float(getattr(self._save, "idle_exp_penalty_seconds", 0.0)),
        )

    def _refresh_action_bars_state(self) -> None:
        has_onsite = any(item for item in self._save.onsite if item)
        if self._fight_bar is not None:
            self._fight_bar.set_active(has_onsite)
        if self._idle_bar is not None:
            self._idle_bar.set_active(has_onsite)

    def _refresh_party_level(self) -> None:
        if self._party_level_tile is None:
            return
        self._party_level_tile.set_level(self._save.party_level)
        self._party_level_tile.set_cost(self._save.party_level_up_cost)

    def _request_fight(self) -> None:
        onsite = [item for item in self._save.onsite if item]
        if not onsite:
            return

        payload = {
            "party_level": int(self._save.party_level),
            "onsite": list(self._save.onsite),
            "offsite": list(self._save.offsite),
            "stacks": dict(self._save.stacks),
        }
        self.fight_requested.emit(payload)

    def _request_idle(self) -> None:
        onsite = [item for item in self._save.onsite if item]
        if not onsite:
            return

        payload = {
            "party_level": int(self._save.party_level),
            "onsite": list(self._save.onsite),
            "offsite": list(self._save.offsite),
            "stacks": dict(self._save.stacks),
        }
        self.idle_requested.emit(payload)

    def reload_save(self) -> None:
        try:
            latest = self._save_manager.load() or self._save
        except Exception:
            return

        if self._shop_exp_state is not None:
            progress = dict(latest.character_progress)
            progress.update(self._shop_exp_state.export_progress())
            latest.character_progress = progress

            stats = dict(latest.character_stats)
            stats.update(self._shop_exp_state.export_character_stats())
            latest.character_stats = stats

            initial_stats = dict(getattr(latest, "character_initial_stats", {}) or {})
            initial_stats.update(self._shop_exp_state.export_initial_stats())
            latest.character_initial_stats = initial_stats

            self._save_manager.save(latest)

        latest = sanitize_save_characters(save=latest, allowed_char_ids=set(self._plugin_by_id))
        self._save_manager.save(latest)

        self._save = latest
        self._shop_exp_state = None
        self._shop_exp_signature = None
        self._refresh_tokens()
        self._refresh_party_level()
        self._refresh_action_bars_state()
        self._refresh_party_hp()
        self._refresh_rewards_plane()
