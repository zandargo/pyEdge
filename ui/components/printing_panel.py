"""Printing utility panel – search and batch-print Solid Edge draft files."""

from __future__ import annotations

import os
from typing import List, Type

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class PrintingPanel(QFrame):
    """Right-side panel for searching and printing Solid Edge draft files."""

    search_requested = pyqtSignal(str, str)          # code, drive
    deep_search_requested = pyqtSignal(str, str)     # code, drive
    print_requested = pyqtSignal(list, str, int, str, str) # files, printer, copies, property_name, property_value

    def __init__(self, SubtitleLabel: Type, BodyLabel: Type, parent=None):
        super().__init__(parent)
        self.setObjectName("mainPanel")

        self._last_code: str = ""
        self._last_drive: str = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────────
        title = SubtitleLabel("Printing")
        title.setObjectName("mainTitle")
        subtitle = BodyLabel("Search and print Solid Edge draft documents.")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        root.addWidget(title)
        root.addSpacing(2)
        root.addWidget(subtitle)
        root.addSpacing(22)

        # ── Configuration card ───────────────────────────────────────────────
        config_card = QFrame()
        config_card.setObjectName("printCard")
        config_inner = QVBoxLayout(config_card)
        config_inner.setContentsMargins(18, 14, 18, 16)
        config_inner.setSpacing(10)

        config_section = QLabel("Configuration")
        config_section.setObjectName("printSectionLabel")
        config_inner.addWidget(config_section)

        config_row = QWidget()
        config_row.setStyleSheet("background: transparent;")
        config_row_layout = QHBoxLayout(config_row)
        config_row_layout.setContentsMargins(0, 0, 0, 0)
        config_row_layout.setSpacing(16)

        printer_col = self._col()
        self._field_label("Printer", printer_col)
        self.printer_combo = QComboBox()
        self.printer_combo.setObjectName("printCombo")
        self.printer_combo.setMinimumHeight(36)
        self.printer_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        printer_col.addWidget(self.printer_combo)

        drive_col = self._col()
        self._field_label("Drive", drive_col)
        self.drive_combo = QComboBox()
        self.drive_combo.setObjectName("printCombo")
        self.drive_combo.setMinimumHeight(36)
        self.drive_combo.setFixedWidth(90)
        drive_col.addWidget(self.drive_combo)

        config_row_layout.addLayout(printer_col, 1)
        config_row_layout.addLayout(drive_col)
        config_inner.addWidget(config_row)
        root.addWidget(config_card)
        root.addSpacing(12)

        # ── Search card ──────────────────────────────────────────────────────
        search_card = QFrame()
        search_card.setObjectName("printCard")
        search_inner = QVBoxLayout(search_card)
        search_inner.setContentsMargins(18, 14, 18, 16)
        search_inner.setSpacing(10)

        search_section = QLabel("Search")
        search_section.setObjectName("printSectionLabel")
        search_inner.addWidget(search_section)

        search_row = QWidget()
        search_row.setStyleSheet("background: transparent;")
        search_row_layout = QHBoxLayout(search_row)
        search_row_layout.setContentsMargins(0, 0, 0, 0)
        search_row_layout.setSpacing(14)

        code_col = self._col()
        self._field_label("File Code", code_col)
        self.code_input = QLineEdit()
        self.code_input.setObjectName("printInput")
        self.code_input.setPlaceholderText("001-0001  or  001-0001-A1")
        self.code_input.setMinimumHeight(36)
        self.code_input.returnPressed.connect(self._on_search)
        code_col.addWidget(self.code_input)

        prop_col = self._col()
        self._field_label("SE Property", prop_col)
        self.prop_input = QLineEdit()
        self.prop_input.setObjectName("printInput")
        self.prop_input.setText("Quantidade")
        self.prop_input.setMinimumHeight(36)
        prop_col.addWidget(self.prop_input)

        prop_value_col = self._col()
        self._field_label("Property Value", prop_value_col)
        self.prop_value_input = QLineEdit()
        self.prop_value_input.setObjectName("printInput")
        self.prop_value_input.setPlaceholderText("e.g. 3")
        self.prop_value_input.setMinimumHeight(36)
        prop_value_col.addWidget(self.prop_value_input)

        search_btn_col = self._col()
        search_btn_col.addSpacing(22)  # align button baseline with inputs
        self.search_btn = QPushButton("Search")
        self.search_btn.setObjectName("printSearchBtn")
        self.search_btn.setMinimumHeight(36)
        self.search_btn.setMinimumWidth(88)
        self.search_btn.clicked.connect(self._on_search)
        search_btn_col.addWidget(self.search_btn)

        search_row_layout.addLayout(code_col, 2)
        search_row_layout.addLayout(prop_col, 2)
        search_row_layout.addLayout(prop_value_col, 1)
        search_row_layout.addLayout(search_btn_col)
        search_inner.addWidget(search_row)
        root.addWidget(search_card)
        root.addSpacing(12)

        # ── Results card ─────────────────────────────────────────────────────
        results_card = QFrame()
        results_card.setObjectName("printCard")
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(18, 14, 18, 16)
        results_layout.setSpacing(8)

        results_header = QWidget()
        results_header.setStyleSheet("background: transparent;")
        results_header_layout = QHBoxLayout(results_header)
        results_header_layout.setContentsMargins(0, 0, 0, 0)
        results_header_layout.setSpacing(10)

        self.results_label = QLabel("Found files")
        self.results_label.setObjectName("printSectionLabel")
        results_header_layout.addWidget(self.results_label)
        results_header_layout.addStretch(1)

        results_layout.addWidget(results_header)

        self.results_list = QListWidget()
        self.results_list.setObjectName("printResults")
        self.results_list.setMinimumHeight(100)
        self.results_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.results_list.currentRowChanged.connect(lambda _: self._update_print_btn())
        results_layout.addWidget(self.results_list, 1)

        # Copies row below file list
        copies_row = QWidget()
        copies_row.setStyleSheet("background: transparent;")
        copies_row_layout = QHBoxLayout(copies_row)
        copies_row_layout.setContentsMargins(0, 6, 0, 0)
        copies_row_layout.setSpacing(10)

        copies_lbl = QLabel("Copies")
        copies_lbl.setObjectName("printFieldLabel")
        self.copies_spin = QSpinBox()
        self.copies_spin.setObjectName("printSpin")
        self.copies_spin.setRange(1, 999)
        self.copies_spin.setValue(1)
        self.copies_spin.setMinimumHeight(34)
        self.copies_spin.setFixedWidth(80)

        copies_row_layout.addWidget(copies_lbl)
        copies_row_layout.addWidget(self.copies_spin)
        copies_row_layout.addStretch(1)
        results_layout.addWidget(copies_row)

        # Deep-search prompt bar (hidden until an empty result)
        self.deep_bar = QFrame()
        self.deep_bar.setObjectName("printDeepBar")
        deep_layout = QHBoxLayout(self.deep_bar)
        deep_layout.setContentsMargins(14, 10, 14, 10)
        deep_layout.setSpacing(12)

        deep_icon = QLabel("⚠")
        deep_icon.setObjectName("printDeepIcon")
        self._deep_msg = BodyLabel("No files found in the preferred location.")
        self._deep_msg.setObjectName("printDeepMsg")
        self._deep_msg.setWordWrap(False)
        self.deep_btn = QPushButton("Search entire drive")
        self.deep_btn.setObjectName("printSecondaryBtn")
        self.deep_btn.setFixedHeight(30)
        self.deep_btn.clicked.connect(self._on_deep_search)

        deep_layout.addWidget(deep_icon)
        deep_layout.addWidget(self._deep_msg, 1)
        deep_layout.addWidget(self.deep_btn)
        self.deep_bar.setVisible(False)
        results_layout.addWidget(self.deep_bar)

        root.addWidget(results_card, 1)
        root.addSpacing(14)

        # ── Footer: status + print button ────────────────────────────────────
        footer = QWidget()
        footer.setStyleSheet("background: transparent;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(14)

        self.status_label = QLabel("")
        self.status_label.setObjectName("printStatus")

        self.print_btn = QPushButton("  Print")
        self.print_btn.setObjectName("printBtn")
        self.print_btn.setMinimumHeight(44)
        self.print_btn.setMinimumWidth(130)
        self.print_btn.setEnabled(False)
        self.print_btn.clicked.connect(self._on_print)

        footer_layout.addWidget(self.status_label, 1)
        footer_layout.addWidget(self.print_btn)
        root.addWidget(footer)

    # ── Private helpers ───────────────────────────────────────────────────

    @staticmethod
    def _col() -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(5)
        return col

    def _field_label(self, text: str, layout: QVBoxLayout) -> None:
        lbl = QLabel(text)
        lbl.setObjectName("printFieldLabel")
        layout.addWidget(lbl)

    def _selected_files(self) -> List[str]:
        item = self.results_list.currentItem()
        if item:
            return [item.data(Qt.UserRole)]
        return []

    def _update_print_btn(self) -> None:
        self.print_btn.setEnabled(bool(self._selected_files()))

    # ── Slots ─────────────────────────────────────────────────────────────

    def _on_search(self) -> None:
        code = self.code_input.text().strip()
        if not code:
            return
        drive = self.drive_combo.currentText()
        self._last_code = code
        self._last_drive = drive
        self.results_list.clear()
        self.deep_bar.setVisible(False)
        self.results_label.setText("Searching…")
        self.search_btn.setEnabled(False)
        self.print_btn.setEnabled(False)
        self.search_requested.emit(code, drive)

    def _on_deep_search(self) -> None:
        self.deep_bar.setVisible(False)
        self.results_label.setText("Searching entire drive…")
        self.search_btn.setEnabled(False)
        self.deep_search_requested.emit(self._last_code, self._last_drive)


    def _on_print(self) -> None:
        files = self._selected_files()
        if not files:
            return
        self.print_btn.setEnabled(False)
        self.set_status("info", "Sending to printer…")
        self.print_requested.emit(
            files,
            self.printer_combo.currentText(),
            self.copies_spin.value(),
            self.prop_input.text().strip(),
            self.prop_value_input.text().strip(),
        )

    # ── Public API ────────────────────────────────────────────────────────

    def populate_printers(self, printers: List[str]) -> None:
        self.printer_combo.clear()
        self.printer_combo.addItems(printers)

    def populate_drives(self, drives: List[str]) -> None:
        self.drive_combo.clear()
        self.drive_combo.addItems(drives)
        idx = self.drive_combo.findText("P:")
        if idx >= 0:
            self.drive_combo.setCurrentIndex(idx)

    def show_results(
        self,
        files: List[str],
        deep_available: bool = False,
        is_deep_search: bool = False,
    ) -> None:
        self.search_btn.setEnabled(True)
        self.results_list.clear()

        if not files:
            suffix = " across the entire drive." if is_deep_search else "."
            self.results_label.setText(f"No files found{suffix}")
            self.deep_bar.setVisible(deep_available)
            self.print_btn.setEnabled(False)
            return

        self.results_label.setText(f"Found files  ({len(files)})")
        self.deep_bar.setVisible(False)
        for path in files:
            item = QListWidgetItem(os.path.basename(path))
            item.setToolTip(path)
            item.setData(Qt.UserRole, path)
            self.results_list.addItem(item)

        if self.results_list.count():
            self.results_list.setCurrentRow(0)
        self._update_print_btn()

    def set_status(self, state: str, message: str) -> None:
        colors = {"info": "#9fb0cb", "success": "#34d399", "error": "#f87171"}
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {colors.get(state, '#9fb0cb')}; font-size: 13px;")

    def set_busy(self, busy: bool) -> None:
        self.search_btn.setEnabled(not busy)
        self.code_input.setEnabled(not busy)
        if not busy:
            self._update_print_btn()
