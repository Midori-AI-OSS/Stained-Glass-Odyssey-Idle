from PySide6.QtWidgets import QApplication

_STAINED_GLASS_STYLESHEET = """
QFrame#mainMenuPanel {
    background-color: rgba(20, 30, 60, 130);
    border: 1px solid rgba(255, 255, 255, 28);
    border-radius: 0px;
}

QPushButton[stainedMenu="true"] {
    background-color: rgba(255, 255, 255, 26);
    border: none;
    border-radius: 0px;
    padding: 10px 14px;
    color: rgba(255, 255, 255, 235);
    font-size: 14px;
    text-align: left;
}

QPushButton[stainedMenu="true"]:hover {
    background-color: rgba(120, 180, 255, 56);
}

QPushButton[stainedMenu="true"]:pressed {
    background-color: rgba(80, 140, 220, 72);
}

QPushButton[stainedMenu="true"]:disabled {
    background-color: rgba(255, 255, 255, 14);
    color: rgba(255, 255, 255, 120);
}

QPushButton#partyBackButton {
    background-color: rgba(255, 255, 255, 20);
    border: 1px solid rgba(255, 255, 255, 28);
    border-radius: 0px;
    padding: 8px 12px;
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
    text-align: left;
}

QPushButton#partyBackButton:hover {
    background-color: rgba(120, 180, 255, 56);
}

QPushButton#partyBackButton:pressed {
    background-color: rgba(80, 140, 220, 72);
}

QPushButton#partyShopButton {
    background-color: rgba(255, 255, 255, 20);
    border: 1px solid rgba(255, 255, 255, 28);
    border-radius: 0px;
    padding: 8px 16px;
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
}

QPushButton#partyShopButton:hover {
    background-color: rgba(120, 180, 255, 56);
}

QPushButton#partyShopButton:checked {
    background-color: rgba(120, 180, 255, 56);
    border: 1px solid rgba(170, 220, 255, 140);
}

QPushButton#partyResetButton {
    background-color: rgba(255, 255, 255, 16);
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 0px;
    padding: 8px 16px;
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
}

QPushButton#partyResetButton:hover {
    background-color: rgba(255, 80, 80, 44);
}

QFrame#partyHpHeader {
    background-color: rgba(20, 30, 60, 120);
    border: 1px solid rgba(255, 255, 255, 22);
}

QLabel#partyHpHeaderLabel {
    color: rgba(255, 255, 255, 210);
    font-size: 12px;
    font-weight: 700;
}

QProgressBar#partyHpHeaderBar {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
    color: rgba(255, 255, 255, 220);
    font-size: 10px;
    text-align: center;
    height: 14px;
}

QProgressBar#partyHpHeaderBar::chunk {
    background-color: rgba(46, 204, 113, 165);
}

QPushButton#partyRerollButton {
    background-color: rgba(255, 255, 255, 16);
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 0px;
    padding: 6px 14px;
    color: rgba(255, 255, 255, 235);
    font-size: 12px;
}

QPushButton#partyRerollButton:hover {
    background-color: rgba(120, 180, 255, 44);
}

QWidget#partyBuilderScreen {
    background-color: rgba(0, 0, 0, 170);
}

QFrame#characterBar {
    background-color: rgba(20, 30, 60, 120);
    border: 1px solid rgba(255, 255, 255, 24);
}

QFrame#standbyBarContainer {
    background-color: rgba(30, 55, 105, 140);
    border: 1px solid rgba(255, 255, 255, 26);
}

QFrame#standbyPartyLevelTile {
    background-color: rgba(35, 70, 135, 170);
    border: 1px solid rgba(255, 255, 255, 30);
}

QFrame#standbyPartyLevelTile:hover {
    background-color: rgba(45, 90, 170, 195);
    border: 1px solid rgba(170, 220, 255, 90);
}

QFrame#fightBar {
    background-color: rgba(255, 59, 120, 150);
    border: 1px solid rgba(255, 120, 160, 120);
}

QFrame#idleBar {
    background-color: rgba(70, 140, 255, 120);
    border: 1px solid rgba(170, 220, 255, 120);
}

QFrame#groupFxPlane[tone="light"] {
    background-color: rgba(120, 185, 255, 30);
    border: 1px solid rgba(210, 235, 255, 45);
}

QFrame#rewardsPlane[tone="dark"] {
    background-color: rgba(25, 45, 100, 45);
    border: 1px solid rgba(170, 220, 255, 38);
}

QLabel#fightBarLabel {
    color: rgba(255, 255, 255, 235);
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}

QLabel#idleBarLabel {
    color: rgba(255, 255, 255, 235);
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}

QLabel#standbyPartyLevelTitle {
    color: rgba(255, 255, 255, 220);
    font-size: 12px;
}

QLabel#standbyPartyLevelValue {
    color: rgba(255, 255, 255, 240);
    font-size: 18px;
    font-weight: 700;
}

QLabel#standbyPartyLevelCost {
    color: rgba(255, 255, 255, 210);
    font-size: 12px;
}

QFrame#characterTile {
    background-color: rgba(255, 255, 255, 18);
    border: 1px solid rgba(255, 255, 255, 24);
}

QFrame#characterTileInner {
    background-color: rgba(0, 0, 0, 25);
    border: 2px solid rgba(255, 255, 255, 18);
}

QFrame#characterTileInner[starRank="1"] { border: 2px solid #808080; }
QFrame#characterTileInner[starRank="2"] { border: 2px solid #1E90FF; }
QFrame#characterTileInner[starRank="3"] { border: 2px solid #228B22; }
QFrame#characterTileInner[starRank="4"] { border: 2px solid #800080; }
QFrame#characterTileInner[starRank="5"] { border: 2px solid #FF3B30; }
QFrame#characterTileInner[starRank="6"] { border: 2px solid #FFD700; }

QLabel#shopSlotPlaceholder {
    color: rgba(255, 255, 255, 120);
    font-size: 12px;
}

QLabel#stackBadge {
    background-color: rgba(10, 14, 26, 210);
    border: 1px solid rgba(255, 255, 255, 42);
    color: rgba(255, 255, 255, 235);
    font-size: 11px;
    padding: 0px 4px;
}

QLabel#shopStackableBadge {
    background-color: rgba(10, 14, 26, 210);
    border: 1px solid rgba(255, 255, 255, 42);
    color: #FFD700;
    font-size: 12px;
    padding: 0px 4px;
}

QFrame#placementBadge {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(70, 110, 185, 55),
        stop: 1 rgba(10, 14, 26, 225)
    );
    border: 1px solid rgba(255, 255, 255, 60);
}

QFrame#placementSquare {
    background-color: rgba(0, 0, 0, 0);
    border: 1px solid rgba(255, 255, 255, 120);
}

QFrame#placementSquare[filled="true"] {
    background-color: rgba(255, 255, 255, 190);
    border: 1px solid rgba(255, 255, 255, 200);
}

QLabel#characterTileName {
    color: rgba(255, 255, 255, 235);
    font-size: 12px;
}

QFrame#dropSlot {
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(255, 255, 255, 20);
}

QFrame#dropSlotInner {
    background-color: rgba(0, 0, 0, 22);
    border: 2px solid rgba(255, 255, 255, 18);
}

QFrame#dropSlotInner[starRank="1"] { border: 2px solid #808080; }
QFrame#dropSlotInner[starRank="2"] { border: 2px solid #1E90FF; }
QFrame#dropSlotInner[starRank="3"] { border: 2px solid #228B22; }
QFrame#dropSlotInner[starRank="4"] { border: 2px solid #800080; }
QFrame#dropSlotInner[starRank="5"] { border: 2px solid #FF3B30; }
QFrame#dropSlotInner[starRank="6"] { border: 2px solid #FFD700; }

QLabel#dropSlotLabel {
    color: rgba(255, 255, 255, 220);
    font-size: 12px;
}

QFrame#sellZone {
    background-color: transparent;
    border: 2px solid transparent;
}

QFrame#sellZone[active="true"] {
    background-color: rgba(255, 59, 48, 38);
    border: 2px solid #FF3B30;
}

QLabel#sellZoneLabel {
    color: rgba(255, 255, 255, 235);
    font-size: 14px;
}

QLabel#tokenLabel {
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
}

QFrame#standbyShopTile {
    background-color: rgba(10, 20, 60, 200);
    border: 1px solid rgba(255, 255, 255, 34);
}

QFrame#standbyShopTile:hover {
    background-color: rgba(20, 40, 90, 220);
    border: 1px solid rgba(170, 220, 255, 120);
}

QFrame#standbyShopTile[open="true"] {
    background-color: rgba(20, 40, 90, 235);
    border: 1px solid rgba(170, 220, 255, 160);
}

QLabel#standbyShopTokens {
    color: rgba(255, 255, 255, 235);
    font-size: 16px;
    font-weight: 700;
}

QLabel#standbyShopLabel {
    color: rgba(255, 255, 255, 220);
    font-size: 13px;
}

QFrame#stainedTooltipPanel {
    background-color: rgba(10, 14, 26, 210);
    border: 1px solid rgba(255, 255, 255, 60);
}

QLabel#stainedTooltipContent {
    color: rgba(255, 255, 255, 235);
    font-size: 12px;
}

QToolTip {
    background-color: rgba(10, 14, 26, 238);
    color: rgba(255, 255, 255, 235);
    border: 1px solid rgba(255, 255, 255, 52);
    padding: 8px 10px;
    font-size: 12px;
}

QWidget#battleScreen {
    background-color: rgba(0, 0, 0, 180);
}

QPushButton#battleBackButton {
    background-color: rgba(255, 255, 255, 16);
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 0px;
    padding: 8px 16px;
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
}

QPushButton#battleBackButton:hover {
    background-color: rgba(120, 180, 255, 44);
}

QLabel#battleTitle {
    color: rgba(255, 255, 255, 240);
    font-size: 18px;
    font-weight: 700;
}

QLabel#battleStatus {
    color: rgba(255, 255, 255, 210);
    font-size: 12px;
}

QFrame#battleArena {
    background-color: rgba(10, 14, 26, 140);
    border: 1px solid rgba(255, 255, 255, 18);
}

QFrame#battleCombatantCard {
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(255, 255, 255, 18);
}

QLabel#battleCombatantName {
    color: rgba(255, 255, 255, 235);
    font-size: 12px;
    font-weight: 700;
}

QLabel#battleCombatantName[battleVariant="onsite"] {
    font-size: 13px;
}

QLabel#battleCombatantName[battleVariant="offsite"] {
    font-size: 10px;
}

QLabel#battleCombatantDetails {
    color: rgba(255, 255, 255, 170);
    font-size: 11px;
}

QProgressBar#battleHpBar {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
    color: rgba(255, 255, 255, 220);
    font-size: 10px;
    text-align: center;
    height: 14px;
}

QProgressBar#battleHpBar[battleVariant="onsite"] {
    height: 16px;
    font-size: 11px;
}

QProgressBar#battleHpBar[battleVariant="offsite"] {
    height: 10px;
    font-size: 9px;
}

QProgressBar#battleHpBar::chunk {
    background-color: rgba(46, 204, 113, 165);
}

QProgressBar#battleExpBar {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
    color: rgba(255, 255, 255, 210);
    font-size: 10px;
    text-align: center;
    height: 12px;
}

QProgressBar#battleExpBar[battleVariant="onsite"] {
    height: 13px;
    font-size: 10px;
}

QProgressBar#battleExpBar[battleVariant="offsite"] {
    height: 9px;
    font-size: 9px;
}

QProgressBar#battleExpBar::chunk {
    background-color: rgba(52, 152, 219, 170);
}

QPushButton#battleToggleStatBars {
    background-color: rgba(255, 255, 255, 14);
    border: 1px solid rgba(255, 255, 255, 20);
    border-radius: 0px;
    padding: 6px 10px;
    color: rgba(255, 255, 255, 230);
    font-size: 12px;
}

QPushButton#battleToggleStatBars:hover {
    background-color: rgba(120, 180, 255, 44);
}

QPushButton#battleToggleStatBars:checked {
    background-color: rgba(120, 180, 255, 32);
}

QFrame#battleCombatantStatBars {
    background-color: rgba(0, 0, 0, 18);
    border: 1px solid rgba(255, 255, 255, 14);
}

QLabel#battleStatLabel {
    color: rgba(255, 255, 255, 185);
    font-size: 9px;
    font-weight: 700;
}

QProgressBar#battleStatBar {
    background-color: rgba(0, 0, 0, 40);
    border: 1px solid rgba(255, 255, 255, 18);
    height: 10px;
}

QProgressBar#battleStatBar::chunk {
    background-color: rgba(155, 89, 182, 165);
}

QProgressBar#battleStatBar[statKey="atk"]::chunk {
    background-color: rgba(231, 76, 60, 170);
}

QProgressBar#battleStatBar[statKey="defense"]::chunk {
    background-color: rgba(52, 152, 219, 175);
}

QProgressBar#battleStatBar[statKey="spd"]::chunk {
    background-color: rgba(46, 204, 113, 175);
}

QProgressBar#battleStatBar[statKey="crit_rate"]::chunk {
    background-color: rgba(241, 196, 15, 185);
}

QProgressBar#battleStatBar[statKey="dodge_odds"]::chunk {
    background-color: rgba(26, 188, 156, 175);
}

QProgressBar#battleStatBar[statKey="regain"]::chunk {
    background-color: rgba(155, 89, 182, 175);
}

QProgressBar#battleStatBar[statKey="mitigation"]::chunk {
    background-color: rgba(149, 165, 166, 175);
}

QFrame#battleOffsiteStrip {
    background-color: rgba(20, 30, 60, 90);
    border: 1px solid rgba(255, 255, 255, 18);
}

QLabel#battleOffsiteTitle {
    color: rgba(255, 255, 255, 200);
    font-size: 11px;
    font-weight: 700;
}

QWidget#idleScreen {
    background-color: rgba(0, 0, 0, 180);
}

QFrame#idleArena {
    background-color: rgba(10, 14, 26, 140);
    border: 1px solid rgba(255, 255, 255, 18);
}

QFrame#idleCharacterCard {
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(255, 255, 255, 18);
}

QFrame#idleOffsiteCard {
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(255, 255, 255, 18);
}

QLabel#idlePortrait {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
}

QLabel#idleOffsitePortrait {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
}

QLabel#idleCharName {
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
    font-weight: 700;
}

QLabel#idleOffsiteName {
    color: rgba(255, 255, 255, 235);
    font-size: 12px;
    font-weight: 700;
}

QLabel#idleStackPlus {
    color: rgba(255, 255, 255, 170);
    font-size: 11px;
    font-weight: 700;
}

QLabel#idleCharLevel,
QLabel#idleCharStack {
    color: rgba(255, 255, 255, 170);
    font-size: 11px;
}

QLabel#idleExpLabel,
QLabel#idleHpLabel {
    color: rgba(255, 255, 255, 200);
    font-size: 10px;
}

QLabel#idleTickLabel {
    color: rgba(255, 255, 255, 210);
    font-size: 12px;
}

QProgressBar#idleExpBar {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
    color: rgba(255, 255, 255, 220);
    font-size: 10px;
    text-align: center;
}

QProgressBar#idleExpBar::chunk {
    background-color: rgba(241, 196, 15, 175);
}

QProgressBar#idleHpBar {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
    color: rgba(255, 255, 255, 220);
    font-size: 10px;
    text-align: center;
}

QProgressBar#idleHpBar::chunk {
    background-color: rgba(46, 204, 113, 165);
}

QFrame#idleModsPanel {
    background-color: rgba(20, 30, 60, 120);
    border: 1px solid rgba(255, 255, 255, 18);
}

QLabel#idleModsTitle,
QLabel#idleRRTitle {
    color: rgba(255, 255, 255, 235);
    font-size: 14px;
    font-weight: 700;
}

QLabel#idleModsHelp {
    color: rgba(255, 255, 255, 160);
    font-size: 10px;
}

QPushButton#idleSharedExpButton {
    background-color: rgba(255, 255, 255, 20);
    border: 1px solid rgba(255, 255, 255, 28);
    border-radius: 0px;
    padding: 8px 12px;
    color: rgba(255, 255, 255, 235);
    font-size: 12px;
}

QPushButton#idleSharedExpButton:hover {
    background-color: rgba(120, 180, 255, 56);
}

QPushButton#idleSharedExpButton:checked {
    background-color: rgba(46, 204, 113, 90);
    border: 1px solid rgba(46, 204, 113, 140);
}

QCheckBox#idleRRToggle {
    color: rgba(255, 255, 255, 220);
    font-size: 11px;
}

QSpinBox#idleRRLevel {
    background-color: rgba(255, 255, 255, 16);
    border: 1px solid rgba(255, 255, 255, 22);
    color: rgba(255, 255, 255, 235);
    font-size: 11px;
    padding: 4px;
}
""".strip()


def apply_stained_glass_theme(app: QApplication) -> None:
    app.setStyleSheet(_STAINED_GLASS_STYLESHEET)
