"""Centralized Qt stylesheet for the pyEdge main window."""

APP_STYLESHEET = """
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
QFrame#windowFrame[maximized="true"] {
    border-radius: 0px;
}
QFrame#titleBar {
    background-color: rgba(7, 11, 18, 220);
    border-bottom: 1px solid rgba(255, 255, 255, 18);
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
}
QFrame#windowFrame[maximized="true"] QFrame#titleBar {
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
}
QLabel#windowTitle {
    color: #cfd7e6;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.4px;
}
QToolButton#minBtn,
QToolButton#maxBtn {
    color: #ffffff;
    background-color: transparent;
    border: none;
    border-radius: 8px;
    font-weight: 700;
    font-family: "Segoe UI";
}
QToolButton#minBtn {
    font-size: 18px;
    padding-bottom: 3px;
}
QToolButton#maxBtn {
    font-size: 14px;
}
QToolButton#minBtn:hover,
QToolButton#maxBtn:hover {
    background-color: rgba(255, 255, 255, 16);
}
QToolButton#closeBtn {
    color: #ffffff;
    background-color: transparent;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 700;
    font-family: "Segoe UI";
}
QToolButton#closeBtn:hover {
    background-color: rgba(235, 77, 75, 220);
}
QFrame#navPanel {
    background-color: rgba(14, 20, 30, 220);
    border: 1px solid rgba(255, 255, 255, 20);
    border-radius: 14px;
}
QLabel#navTitle {
    color: #e7eefb;
    font-size: 18px;
    font-weight: 700;
}
QLabel#navSubtitle {
    color: #9fb0cb;
    font-size: 13px;
}
QLabel#docCount {
    color: #7cb6ff;
    font-size: 12px;
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
    font-size: 24px;
    font-weight: 700;
}
QLabel#connection {
    font-size: 13px;
    font-weight: 600;
    padding: 8px 12px;
    border-radius: 10px;
    color: #8da0bf;
    background-color: rgba(255, 255, 255, 8);
    border: 1px solid rgba(255, 255, 255, 14);
}
QFrame#docPage,
QFrame#emptyPage {
    background-color: rgba(8, 12, 20, 150);
    border: 1px solid rgba(255, 255, 255, 16);
    border-radius: 12px;
}
QLabel#pageTitle {
    color: #f2f7ff;
    font-size: 20px;
    font-weight: 700;
}
QLabel#pageSubtitle {
    color: #a2b2cd;
    font-size: 13px;
    margin-bottom: 8px;
}
QLabel#metaKey {
    color: #89a0c4;
    font-size: 12px;
    font-weight: 700;
}
QLabel#customPropsTitle {
    color: #d6e7ff;
    font-size: 15px;
    font-weight: 700;
}
QLabel#metaValue {
    color: #dde8ff;
    font-size: 13px;
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
"""
