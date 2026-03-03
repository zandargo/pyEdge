"""Centralized Qt stylesheet for the pyEdge main window."""

APP_STYLESHEET = """
/* Global font rendering optimization for anti-aliasing */
* {
    outline: none;
}

QLabel, QPushButton, QToolButton {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
}

QWidget#root {
    background: transparent;
}
QFrame#windowFrame {
    background-color: qlineargradient(
        x1: 0,
        y1: 0,
        x2: 1,
        y2: 1,
        stop: 0 #0a111a,
        stop: 0.55 #111827,
        stop: 1 #091019
    );
    border: 1px solid rgba(255, 255, 255, 20);
    border-radius: 16px;
}
QFrame#titleBar {
    background-color: rgba(7, 11, 18, 220);
    border-bottom: 1px solid rgba(255, 255, 255, 18);
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
}
QLabel#windowTitle {
    color: #cfd7e6;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.4px;
}
/* Fluent Design window control buttons */
QToolButton#minBtn,
QToolButton#maxBtn,
QToolButton#closeBtn {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 0px;
}
QToolButton#minBtn:hover,
QToolButton#maxBtn:hover {
    background-color: rgba(255, 255, 255, 0.08);
}
QToolButton#minBtn:pressed,
QToolButton#maxBtn:pressed {
    background-color: rgba(255, 255, 255, 0.12);
}
QToolButton#closeBtn:hover {
    background-color: rgba(255, 76, 56, 0.9);
}
QToolButton#closeBtn:pressed {
    background-color: rgba(255, 56, 40, 1.0);
}
/* Support for qfluentwidgets ToolButton styling */
ToolButton#minBtn,
ToolButton#maxBtn,
ToolButton#closeBtn {
    border-radius: 6px;
}
ToolButton#closeBtn:hover {
    background-color: rgba(255, 76, 56, 0.9);
}
QFrame#navPanel {
    background-color: rgba(14, 20, 30, 220);
    border: 1px solid rgba(255, 255, 255, 20);
    border-radius: 14px;
}
QLabel#navTitle {
    color: #e7eefb;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.3px;
}
QLabel#navSubtitle {
    color: #9fb0cb;
    font-size: 14px;
    letter-spacing: 0.2px;
}
QLabel#docCount {
    color: #7cb6ff;
    font-size: 13px;
    font-weight: 700;
}
QListWidget#docList {
    background-color: rgba(255, 255, 255, 8);
    border: 1px solid rgba(255, 255, 255, 16);
    border-radius: 10px;
    color: #d9e3f6;
    padding: 4px;
    outline: none;
}
QListWidget#docList::item {
    border-radius: 8px;
    padding: 8px;
    margin: 2px;
}
QListWidget#docList::item:selected {
    background-color: rgba(45, 140, 255, 70);
    color: #ffffff;
}
QListWidget#docList::item:selected:active,
QListWidget#docList::item:selected:!active {
    color: #ffffff;
}
QScrollBar:vertical {
    background: rgba(255, 255, 255, 8);
    width: 12px;
    margin: 6px 2px 6px 2px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: rgba(124, 182, 255, 170);
    min-height: 28px;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(124, 182, 255, 220);
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
    background: transparent;
}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
}
QScrollBar:horizontal {
    background: rgba(255, 255, 255, 8);
    height: 12px;
    margin: 2px 6px 2px 6px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal {
    background: rgba(124, 182, 255, 170);
    min-width: 28px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal:hover {
    background: rgba(124, 182, 255, 220);
}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
    background: transparent;
}
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: transparent;
}
QFrame#mainPanel {
    background-color: rgba(18, 24, 34, 220);
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 14px;
}
QLabel#mainTitle {
    color: #eef4ff;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 0.2px;
}
QLabel#connection {
    font-size: 14px;
    font-weight: 600;
    padding: 8px 12px;
    border-radius: 10px;
    color: #8da0bf;
    background-color: rgba(255, 255, 255, 8);
    border: 1px solid rgba(255, 255, 255, 14);
    letter-spacing: 0.1px;
}
QFrame#docPage,
QFrame#emptyPage {
    background-color: rgba(8, 12, 20, 150);
    border: 1px solid rgba(255, 255, 255, 16);
    border-radius: 12px;
}
QLabel#pageTitle {
    color: #f2f7ff;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 0.2px;
}
QLabel#pageSubtitle {
    color: #a2b2cd;
    font-size: 14px;
    margin-bottom: 8px;
    letter-spacing: 0.1px;
}
QLabel#metaKey {
    color: #89a0c4;
    font-size: 13px;
    font-weight: 700;
}
QLabel#customPropsTitle {
    color: #d6e7ff;
    font-size: 16px;
    font-weight: 700;
}
QLabel#metaValue {
    color: #dde8ff;
    font-size: 14px;
    font-weight: 600;
    background-color: rgba(255, 255, 255, 8);
    border: 1px solid rgba(255, 255, 255, 14);
    border-radius: 8px;
    padding: 8px;
}
QLineEdit#customValueEditor,
QDateEdit#customValueEditor,
QDoubleSpinBox#customValueEditor {
    color: #dde8ff;
    background-color: rgba(255, 255, 255, 76);
    border: 1px solid rgba(183, 213, 255, 110);
    border-radius: 8px;
    padding: 6px 8px;
}
QLineEdit#customValueEditor:disabled,
QDateEdit#customValueEditor:disabled,
QDoubleSpinBox#customValueEditor:disabled {
    color: #9ba9c0;
    background-color: rgba(255, 255, 255, 16);
}
QCheckBox#customValueEditor {
    color: #dde8ff;
}
QCheckBox#customValueEditor:disabled {
    color: #9ba9c0;
}
QScrollArea#customPropsScroll {
    background: transparent;
    border: none;
}
QScrollArea#customPropsScroll > QWidget > QWidget {
    background: transparent;
}
QPushButton#primaryButton {
    border-radius: 10px;
    background-color: #2d8cff;
}
QPushButton#primaryButton:hover {
    background-color: #58a4ff;
}
QPushButton#secondaryButton {
    border-radius: 10px;
    background-color: rgba(255, 255, 255, 14);
    color: #d9e2f2;
    border: 1px solid rgba(255, 255, 255, 20);
}
QPushButton#secondaryButton:hover {
    background-color: rgba(255, 255, 255, 22);
}
QPushButton#secondaryButton:disabled {
    color: rgba(217, 226, 242, 120);
    background-color: rgba(255, 255, 255, 8);
    border-color: rgba(255, 255, 255, 14);
}
QWidget#tabBarContainer {
    background-color: rgba(7, 11, 18, 200);
    border-bottom: 1px solid rgba(255, 255, 255, 14);
}
QPushButton#tabButton {
    background: transparent;
    border: none;
    border-bottom: 3px solid transparent;
    color: #7a90b0;
    font-size: 14px;
    font-weight: 600;
    padding: 0px 22px;
    border-radius: 0px;
    letter-spacing: 0.2px;
}
QPushButton#tabButton:checked {
    color: #e8f0ff;
    border-bottom: 3px solid #2d8cff;
}
QPushButton#tabButton:hover:!checked {
    color: #b0c4de;
    background-color: rgba(255, 255, 255, 6);
}
QPushButton#utilNavButton {
    text-align: left;
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid transparent;
    background-color: rgba(45, 140, 255, 55);
    color: #e8f0ff;
    font-size: 14px;
    font-weight: 600;
}
QPushButton#utilNavButton:checked {
    background-color: rgba(45, 140, 255, 80);
    border: 1px solid rgba(45, 140, 255, 120);
    color: #ffffff;
}
QPushButton#utilNavButton:hover:!checked {
    background-color: rgba(255, 255, 255, 12);
    border: 1px solid rgba(255, 255, 255, 16);
    color: #d0dcf5;
}

/* ── Printing panel ────────────────────────────────────────────────────── */
QFrame#printCard {
    background-color: rgba(10, 16, 26, 200);
    border: 1px solid rgba(255, 255, 255, 16);
    border-radius: 12px;
}
QLabel#printSectionLabel {
    color: #c4d4f0;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.3px;
}
QLabel#printFieldLabel {
    color: #7a91b8;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
QComboBox#printCombo {
    color: #dde8ff;
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(183, 213, 255, 60);
    border-radius: 8px;
    padding: 0px 10px;
    selection-background-color: rgba(45, 140, 255, 70);
}
QComboBox#printCombo:hover {
    border-color: rgba(183, 213, 255, 110);
    background-color: rgba(255, 255, 255, 14);
}
QComboBox#printCombo::drop-down {
    border: none;
    width: 22px;
}
QComboBox#printCombo QAbstractItemView {
    background-color: #101824;
    border: 1px solid rgba(255, 255, 255, 18);
    border-radius: 8px;
    color: #dde8ff;
    selection-background-color: rgba(45, 140, 255, 80);
    padding: 4px;
    outline: none;
}
QLineEdit#printInput {
    color: #dde8ff;
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(183, 213, 255, 60);
    border-radius: 8px;
    padding: 0px 10px;
}
QLineEdit#printInput:hover {
    border-color: rgba(183, 213, 255, 100);
    background-color: rgba(255, 255, 255, 14);
}
QLineEdit#printInput:focus {
    border-color: rgba(45, 140, 255, 180);
    background-color: rgba(255, 255, 255, 12);
}
QSpinBox#printSpin {
    color: #dde8ff;
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(183, 213, 255, 60);
    border-radius: 8px;
    padding: 0px 6px;
}
QSpinBox#printSpin:hover {
    border-color: rgba(183, 213, 255, 100);
}
QSpinBox#printSpin:focus {
    border-color: rgba(45, 140, 255, 180);
}
QSpinBox#printSpin::up-button,
QSpinBox#printSpin::down-button {
    background: transparent;
    border: none;
    width: 16px;
}
QPushButton#printSearchBtn {
    background-color: rgba(45, 140, 255, 150);
    color: #ffffff;
    border: 1px solid rgba(45, 140, 255, 190);
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
}
QPushButton#printSearchBtn:hover {
    background-color: rgba(45, 140, 255, 210);
}
QPushButton#printSearchBtn:disabled {
    background-color: rgba(45, 140, 255, 50);
    color: rgba(255, 255, 255, 90);
    border-color: rgba(45, 140, 255, 70);
}
QPushButton#printSecondaryBtn {
    background-color: rgba(45, 140, 255, 120);
    color: #ffffff;
    border: 1px solid rgba(45, 140, 255, 160);
    border-radius: 7px;
    font-size: 13px;
    font-weight: 600;
    padding: 2px 10px;
}
QPushButton#printSecondaryBtn:hover {
    background-color: rgba(45, 140, 255, 180);
    color: #ffffff;
}
QPushButton#printBtn {
    background-color: #7db8ff;
    color: #ffffff;
    border: 1px solid rgba(45, 140, 255, 200);
    border-radius: 10px;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.3px;
    padding-right: 6px;
}
QPushButton#printBtn:hover {
    background-color: #a5ceff;
}
QPushButton#printBtn:disabled {
    background-color: rgba(45, 140, 255, 55);
    color: rgba(255, 255, 255, 90);
    border-color: rgba(45, 140, 255, 80);
}
QListWidget#printResults {
    background-color: rgba(255, 255, 255, 6);
    border: 1px solid rgba(255, 255, 255, 14);
    border-radius: 10px;
    color: #d9e3f6;
    padding: 4px;
    outline: none;
}
QListWidget#printResults::item {
    border-radius: 7px;
    padding: 7px 8px;
    margin: 2px;
    color: #d9e3f6;
}
QListWidget#printResults::item:hover:!selected {
    background-color: rgba(255, 255, 255, 8);
    color: #d9e3f6;
}
QListWidget#printResults::item:selected,
QListWidget#printResults::item:selected:active,
QListWidget#printResults::item:selected:!active {
    background-color: rgba(45, 140, 255, 80);
    border: 1px solid rgba(45, 140, 255, 140);
    color: #ffffff;
    font-weight: 700;
}
QFrame#printDeepBar {
    background-color: rgba(234, 179, 8, 16);
    border: 1px solid rgba(234, 179, 8, 45);
    border-radius: 10px;
}
QLabel#printDeepIcon {
    color: #eab308;
    font-size: 16px;
}
QLabel#printDeepMsg {
    color: #c9b86c;
    font-size: 14px;
}
QLabel#printStatus {
    color: #7a91b8;
    font-size: 14px;
}
"""
