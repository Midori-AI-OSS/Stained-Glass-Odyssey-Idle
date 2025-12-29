from __future__ import annotations

import random

from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtCore import QPropertyAnimation
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.save import BAR_SLOTS
from endless_idler.save import DEFAULT_CHARACTER_COST
from endless_idler.save import DEFAULT_RUN_TOKENS
from endless_idler.save import OFFSITE_SLOTS
from endless_idler.save import ONSITE_SLOTS
from endless_idler.save import STANDBY_SLOTS
from endless_idler.save import RunSave
from endless_idler.save import SaveManager
from endless_idler.save import next_party_level_up_cost
from endless_idler.ui.party_builder_bar import CharacterBar
from endless_idler.ui.party_builder_fight_bar import FightBar
from endless_idler.ui.party_builder_planes import PulsingPlane
from endless_idler.ui.party_builder_party_level_tile import StandbyPartyLevelTile
from endless_idler.ui.party_builder_shop_tile import StandbyShopTile
from endless_idler.ui.party_builder_slot import DropSlot
from endless_idler.ui.party_builder_sell import SellZone


class PartyBuilderWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Party Builder")
        self.resize(1280, 820)

        self.setCentralWidget(PartyBuilderWidget())


class PartyBuilderWidget(QWidget):
    back_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("partyBuilderScreen")

        self._rng = random.Random()
        self._root_layout: QVBoxLayout | None = None
        self._plugins = discover_character_plugins()
        self._plugin_by_id = {plugin.char_id: plugin for plugin in self._plugins}
        self._save_manager = SaveManager()
        self._save = self._save_manager.load() or self._new_run_save()
        self._save_manager.save(self._save)
        self._slots_by_id: dict[str, DropSlot] = {}
        self._shop_open = False
        self._sell_zones: list[SellZone] = []
        self._shop_tile: StandbyShopTile | None = None
        self._party_level_tile: StandbyPartyLevelTile | None = None

        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)
        self.setLayout(root)
        self._root_layout = root

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)
        root.addLayout(header)

        back = QPushButton("Back")
        back.setObjectName("partyBackButton")
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.clicked.connect(self.back_requested.emit)
        header.addWidget(back, 0, Qt.AlignmentFlag.AlignLeft)

        header.addStretch(1)

        reset = QPushButton("Reset")
        reset.setObjectName("partyResetButton")
        reset.setCursor(Qt.CursorShape.PointingHandCursor)
        reset.clicked.connect(self._reset_run)
        header.addWidget(reset, 0, Qt.AlignmentFlag.AlignRight)

        self._char_bar: CharacterBar | None = None
        self._token_label: QLabel | None = None
        self._token_opacity: QGraphicsOpacityEffect | None = None
        self._token_pulse_anim: QPropertyAnimation | None = None
        self._maybe_build_char_bar()

        root.addWidget(self._make_planes_row())

        root.addStretch(1)

        grid = QVBoxLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)
        root.addLayout(grid)

        grid.addLayout(self._make_onsite_row())
        grid.addLayout(self._make_row("Offsite", count=OFFSITE_SLOTS, center=True))
        grid.addWidget(self._make_fight_and_standby_area(), 0, Qt.AlignmentFlag.AlignHCenter)

        self._refresh_tokens()
        self._load_slots_from_save()

    def _maybe_build_char_bar(self) -> None:
        if not self._shop_open:
            return

        bar = CharacterBar(
            char_ids=self._save.bar,
            plugins_by_id=self._plugin_by_id,
            rng=self._rng,
            on_reroll=self._reroll_shop,
            get_stack_count=self._get_stack_count,
            character_cost=DEFAULT_CHARACTER_COST,
            can_afford=self._can_afford,
            on_insufficient_funds=self._pulse_tokens,
        )

        bar.destroyed.connect(self._on_char_bar_destroyed)
        self._char_bar = bar
        if self._root_layout is not None:
            self._root_layout.insertWidget(1, bar, 0, Qt.AlignmentFlag.AlignHCenter)

    def _on_char_bar_destroyed(self) -> None:
        self._char_bar = None
        self._shop_open = False
        if self._shop_tile is not None:
            self._shop_tile.set_open(False)

    def _set_shop_open(self, open_: bool) -> None:
        self._shop_open = open_
        if self._shop_tile is not None:
            self._shop_tile.set_open(open_)

        if self._char_bar is not None and self._root_layout is not None:
            bar = self._char_bar
            self._root_layout.removeWidget(self._char_bar)
            self._char_bar.hide()
            self._char_bar.setParent(None)
            bar.deleteLater()

        self._char_bar = None

        if open_:
            self._maybe_build_char_bar()

    def _new_run_save(self) -> RunSave:
        bar: list[str | None] = [None] * BAR_SLOTS
        if self._plugins:
            count = min(BAR_SLOTS, len(self._plugins))
            chosen = [plugin.char_id for plugin in self._rng.sample(self._plugins, k=count)]
            bar[: len(chosen)] = chosen

        return RunSave(tokens=DEFAULT_RUN_TOKENS, bar=bar)

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
                allow_stacking=allow_stacking,
                show_stack_badge=show_stack_badge,
            )
            self._slots_by_id[slot_id] = slot
            row.addWidget(slot)

        row.addStretch(1)

        return row

    def _make_planes_row(self) -> QWidget:
        wrapper = QWidget()
        row = QHBoxLayout()
        row.setContentsMargins(14, 0, 14, 0)
        row.setSpacing(26)
        wrapper.setLayout(row)

        row.addWidget(PulsingPlane(object_name="groupFxPlane", tone="light"))
        row.addStretch(1)
        row.addWidget(PulsingPlane(object_name="rewardsPlane", tone="dark"))
        return wrapper

    def _make_fight_and_standby_area(self) -> QWidget:
        wrapper = QWidget()
        wrapper_layout = QVBoxLayout()
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(12)
        wrapper.setLayout(wrapper_layout)

        fight_row = QHBoxLayout()
        fight_row.setContentsMargins(0, 0, 14, 0)
        fight_row.setSpacing(0)
        fight_row.addStretch(1)
        fight_row.addWidget(FightBar())
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

    def _sell_character(self, char_id: str) -> None:
        stacks = self._save.stacks.get(char_id, 1)
        self._save.tokens += DEFAULT_CHARACTER_COST * max(1, int(stacks))
        self._save.stacks.pop(char_id, None)
        self._refresh_tokens()
        self._save_manager.save(self._save)

    def _set_sell_zones_active(self, active: bool) -> None:
        for zone in self._sell_zones:
            zone.set_active(active)

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

        self._save = self._new_run_save()
        self._save_manager.save(self._save)

        self._set_sell_zones_active(False)
        self._refresh_tokens()
        self._refresh_party_level()
        self._load_slots_from_save()
        if self._char_bar is not None:
            self._char_bar.set_char_ids(self._save.bar)

    def _reroll_shop(self) -> None:
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

        duplicates = max(0, int(offered_counts.get(char_id, 0)))
        duplicate_weight = 0.25**duplicates

        return stack_weight * duplicate_weight

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

        self._apply_auto_merges()
        self._refresh_standby_slots()
        self._save_manager.save(self._save)
        if self._char_bar is not None:
            self._char_bar.refresh_stack_badges()

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

    def _refresh_party_level(self) -> None:
        if self._party_level_tile is None:
            return
        self._party_level_tile.set_level(self._save.party_level)
        self._party_level_tile.set_cost(self._save.party_level_up_cost)
