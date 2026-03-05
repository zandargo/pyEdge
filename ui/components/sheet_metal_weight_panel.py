"""Sheet Metal Weight calculator panel."""

from __future__ import annotations

import json
import locale
from pathlib import Path
from typing import Optional, Type

from PyQt5.QtCore import QEvent, QPoint, Qt, QTimer
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QButtonGroup,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QStackedWidget,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

# ── Data source ───────────────────────────────────────────────────────────────

_DATA_PATH = Path(__file__).parent.parent.parent / "ref" / "sheet_metal_weight.json"
_DATA: dict = json.loads(_DATA_PATH.read_text(encoding="utf-8"))

_MATERIAL_KEYS: list[str] = list(_DATA["materials"].keys())
_DEFAULTS: dict = _DATA["defaults"]


# ── Panel widget ──────────────────────────────────────────────────────────────

class SheetMetalWeightPanel(QFrame):
    """Sheet Metal Weight calculator panel."""

    def __init__(self, SubtitleLabel: Type, BodyLabel: Type, parent=None):
        super().__init__(parent)
        self.setObjectName("mainPanel")

        self._dxf_path: str = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        # ── Header ─────────────────────────────────────────────────────────
        self._title_lbl = SubtitleLabel()
        self._title_lbl.setObjectName("mainTitle")
        self._subtitle_lbl = BodyLabel()
        self._subtitle_lbl.setObjectName("pageSubtitle")
        self._subtitle_lbl.setWordWrap(True)
        root.addWidget(self._title_lbl)
        root.addSpacing(2)
        root.addWidget(self._subtitle_lbl)
        root.addSpacing(22)

        # ── Input card ──────────────────────────────────────────────────────
        input_card = QFrame()
        input_card.setObjectName("printCard")
        input_inner = QVBoxLayout(input_card)
        input_inner.setContentsMargins(20, 16, 20, 18)
        input_inner.setSpacing(14)

        self._params_lbl = QLabel()
        self._params_lbl.setObjectName("printSectionLabel")
        input_inner.addWidget(self._params_lbl)

        # Row 1: Material + Density
        row1 = _transparent_row()
        row1_layout = QHBoxLayout(row1)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(16)

        mat_col = _col()
        self._mat_lbl = _field_label("")
        mat_col.addWidget(self._mat_lbl)
        self.material_combo = QComboBox()
        self.material_combo.setObjectName("gasCombo")
        self.material_combo.setMinimumHeight(36)
        for key in _MATERIAL_KEYS:
            self.material_combo.addItem("", key)
        mat_col.addWidget(self.material_combo)

        density_col = _col()
        self._density_lbl = _field_label("")
        density_col.addWidget(self._density_lbl)
        self.density_spin = QDoubleSpinBox()
        self.density_spin.setObjectName("smwSpin")
        self.density_spin.setMinimumHeight(36)
        self.density_spin.setRange(100.0, 25000.0)
        self.density_spin.setDecimals(0)
        self.density_spin.setSingleStep(10.0)
        self.density_spin.setSuffix(" kg/m³")
        density_col.addWidget(self.density_spin)

        row1_layout.addLayout(mat_col, 3)
        row1_layout.addLayout(density_col, 2)
        input_inner.addWidget(row1)

        # Thickness list
        self._thick_lbl = _field_label("")
        input_inner.addWidget(self._thick_lbl)

        self.thickness_list = QListWidget()
        self.thickness_list.setObjectName("smwThickList")
        self.thickness_list.setSelectionMode(QAbstractItemView.SingleSelection)
        # Show ~5 rows; each row ~32 px + 2 px margin + header/border
        self.thickness_list.setFixedHeight(168)
        self.thickness_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        input_inner.addWidget(self.thickness_list)

        root.addWidget(input_card)
        root.addSpacing(12)

        # ── Area card ───────────────────────────────────────────────────────
        area_card = QFrame()
        area_card.setObjectName("printCard")
        area_inner = QVBoxLayout(area_card)
        area_inner.setContentsMargins(20, 16, 20, 18)
        area_inner.setSpacing(12)

        self._area_lbl = QLabel()
        self._area_lbl.setObjectName("printSectionLabel")
        area_inner.addWidget(self._area_lbl)

        # Radio buttons
        radio_row = _transparent_row()
        radio_row_layout = QHBoxLayout(radio_row)
        radio_row_layout.setContentsMargins(0, 0, 0, 0)
        radio_row_layout.setSpacing(20)

        self.radio_manual = QRadioButton()
        self.radio_manual.setObjectName("smwRadio")
        self.radio_manual.setChecked(True)

        self.radio_dxf = QRadioButton()
        self.radio_dxf.setObjectName("smwRadio")

        self._area_btn_group = QButtonGroup(self)
        self._area_btn_group.addButton(self.radio_manual, 0)
        self._area_btn_group.addButton(self.radio_dxf, 1)

        radio_row_layout.addWidget(self.radio_manual)
        radio_row_layout.addWidget(self.radio_dxf)
        radio_row_layout.addStretch(1)
        area_inner.addWidget(radio_row)

        # Stacked area input (0 = manual, 1 = dxf)
        self._area_stack = QStackedWidget()
        self._area_stack.setStyleSheet("background: transparent;")

        # Page 0 – Manual (width × height)
        manual_page = QWidget()
        manual_page.setStyleSheet("background: transparent;")
        manual_layout = QHBoxLayout(manual_page)
        manual_layout.setContentsMargins(0, 0, 0, 0)
        manual_layout.setSpacing(16)

        width_col = _col()
        self._width_lbl = _field_label("")
        width_col.addWidget(self._width_lbl)
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setObjectName("smwSpin")
        self.width_spin.setMinimumHeight(36)
        self.width_spin.setRange(1.0, 99999.0)
        self.width_spin.setDecimals(1)
        self.width_spin.setSingleStep(100.0)
        self.width_spin.setSuffix(" mm")
        self.width_spin.setValue(_DEFAULTS["width_mm"])
        width_col.addWidget(self.width_spin)

        height_col = _col()
        self._height_lbl = _field_label("")
        height_col.addWidget(self._height_lbl)
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setObjectName("smwSpin")
        self.height_spin.setMinimumHeight(36)
        self.height_spin.setRange(1.0, 99999.0)
        self.height_spin.setDecimals(1)
        self.height_spin.setSingleStep(100.0)
        self.height_spin.setSuffix(" mm")
        self.height_spin.setValue(_DEFAULTS["height_mm"])
        height_col.addWidget(self.height_spin)

        manual_layout.addLayout(width_col, 1)
        manual_layout.addLayout(height_col, 1)
        self._area_stack.addWidget(manual_page)

        # Page 1 – DXF file picker
        dxf_page = QWidget()
        dxf_page.setStyleSheet("background: transparent;")
        dxf_layout = QVBoxLayout(dxf_page)
        dxf_layout.setContentsMargins(0, 0, 0, 0)
        dxf_layout.setSpacing(6)

        self._dxf_coming_soon_lbl = QLabel()
        self._dxf_coming_soon_lbl.setObjectName("smwComingSoon")
        dxf_layout.addWidget(self._dxf_coming_soon_lbl)

        dxf_row = QWidget()
        dxf_row.setStyleSheet("background: transparent;")
        dxf_row_layout = QHBoxLayout(dxf_row)
        dxf_row_layout.setContentsMargins(0, 0, 0, 0)
        dxf_row_layout.setSpacing(10)

        self.dxf_path_edit = QLineEdit()
        self.dxf_path_edit.setObjectName("smwDxfInput")
        self.dxf_path_edit.setReadOnly(True)
        self.dxf_path_edit.setMinimumHeight(36)
        self.dxf_path_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.dxf_browse_btn = QPushButton()
        self.dxf_browse_btn.setObjectName("smwBrowseBtn")
        self.dxf_browse_btn.setMinimumHeight(36)
        self.dxf_browse_btn.setMinimumWidth(100)
        self.dxf_browse_btn.clicked.connect(self._browse_dxf)

        dxf_row_layout.addWidget(self.dxf_path_edit, 1)
        dxf_row_layout.addWidget(self.dxf_browse_btn)
        dxf_layout.addWidget(dxf_row)
        self._area_stack.addWidget(dxf_page)

        area_inner.addWidget(self._area_stack)
        root.addWidget(area_card)
        root.addSpacing(12)

        # ── Result card ─────────────────────────────────────────────────────
        self.result_card = QFrame()
        self.result_card.setObjectName("smwResultCard")
        self.result_card.setVisible(False)
        result_inner = QVBoxLayout(self.result_card)
        result_inner.setContentsMargins(20, 16, 20, 18)
        result_inner.setSpacing(10)

        self._result_lbl = QLabel()
        self._result_lbl.setObjectName("printSectionLabel")
        result_inner.addWidget(self._result_lbl)

        result_values_row = _transparent_row()
        result_values_layout = QHBoxLayout(result_values_row)
        result_values_layout.setContentsMargins(0, 0, 0, 0)
        result_values_layout.setSpacing(12)

        self._area_result_card = _ResultTile(self)
        self._area_result_key = _result_key_label("")
        self._area_result_val = _result_val_label("—")
        self._area_result_card.layout().addWidget(self._area_result_key)
        self._area_result_card.layout().addWidget(self._area_result_val)

        self._weight_result_card = _ResultTile(self)
        self._weight_result_key = _result_key_label("")
        self._weight_result_val = _result_val_label("—")
        self._weight_result_card.layout().addWidget(self._weight_result_key)
        self._weight_result_card.layout().addWidget(self._weight_result_val)

        self._density_area_result_card = _ResultTile(self)
        self._density_area_result_key = _result_key_label("")
        self._density_area_result_val = _result_val_label("—")
        self._density_area_result_card.layout().addWidget(self._density_area_result_key)
        self._density_area_result_card.layout().addWidget(self._density_area_result_val)

        result_values_layout.addWidget(self._area_result_card, 1)
        result_values_layout.addWidget(self._weight_result_card, 1)
        result_values_layout.addWidget(self._density_area_result_card, 1)

        result_inner.addWidget(result_values_row)
        root.addWidget(self.result_card)
        root.addStretch(1)

        # ── Connections ─────────────────────────────────────────────────────
        self.material_combo.currentIndexChanged.connect(self._on_material_changed)
        self.density_spin.valueChanged.connect(self._calculate)
        self.thickness_list.currentRowChanged.connect(self._calculate)
        self.width_spin.valueChanged.connect(self._calculate)
        self.height_spin.valueChanged.connect(self._calculate)
        self._area_btn_group.buttonClicked.connect(self._on_area_mode_changed)

        self.retranslateUi()

        # Trigger initial population
        self._on_material_changed(0)

    # ── i18n ─────────────────────────────────────────────────────────────────

    def retranslateUi(self) -> None:
        self._title_lbl.setText(self.tr("Sheet Metal Weight"))
        self._subtitle_lbl.setText(
            self.tr("Select material, thickness and area to calculate the sheet metal weight.")
        )
        self._params_lbl.setText(self.tr("Material & Thickness"))
        self._mat_lbl.setText(self.tr("Material"))
        self._density_lbl.setText(self.tr("Density"))
        self._thick_lbl.setText(self.tr("Thickness (mm)"))
        self._area_lbl.setText(self.tr("Area"))
        self.radio_manual.setText(self.tr("Manual (Width × Height)"))
        self.radio_dxf.setText(self.tr("DXF File"))
        self._dxf_coming_soon_lbl.setText(self.tr("Coming soon…"))
        self._width_lbl.setText(self.tr("Width"))
        self._height_lbl.setText(self.tr("Height"))
        self.dxf_browse_btn.setText(self.tr("Browse…"))
        self.dxf_path_edit.setPlaceholderText(self.tr("No file selected"))
        self._result_lbl.setText(self.tr("Results"))
        self._area_result_key.setText(self.tr("Area"))
        self._weight_result_key.setText(self.tr("Weight"))
        self._density_area_result_key.setText(self.tr("kg / m²"))

        # Material combo labels
        _labels = {
            "stainless_steel": self.tr("Stainless Steel"),
            "carbon_steel": self.tr("Carbon Steel"),
            "galvanized_steel": self.tr("Galvanized Steel"),
            "aluminum": self.tr("Aluminum"),
            "other": self.tr("Other"),
        }
        for i, key in enumerate(_MATERIAL_KEYS):
            self.material_combo.setItemText(i, _labels.get(key, key))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_material_changed(self, _index: int) -> None:
        mat_key = self.material_combo.currentData()
        if not mat_key:
            return
        mat_data = _DATA["materials"][mat_key]

        # Update density (block signals to avoid double calculation)
        self.density_spin.blockSignals(True)
        self.density_spin.setValue(mat_data["density_kg_m3"])
        self.density_spin.blockSignals(False)

        # Repopulate thickness list
        self.thickness_list.blockSignals(True)
        self.thickness_list.clear()
        for t in mat_data["thickness_mm"]:
            item = QListWidgetItem(f"{t:g} mm")
            item.setData(Qt.UserRole, t)
            item.setTextAlignment(Qt.AlignCenter)
            self.thickness_list.addItem(item)
        self.thickness_list.blockSignals(False)

        # Select the first item by default
        if self.thickness_list.count() > 0:
            self.thickness_list.setCurrentRow(0)
        else:
            self._calculate()

    def _on_area_mode_changed(self) -> None:
        mode = self._area_btn_group.checkedId()
        self._area_stack.setCurrentIndex(mode)
        if mode == 0:
            self._calculate()
        else:
            # DXF area not yet implemented – hide result until file is selected
            if not self._dxf_path:
                self.result_card.setVisible(False)

    def _browse_dxf(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Open DXF File"),
            "",
            self.tr("DXF Files (*.dxf);;All Files (*)"),
        )
        if path:
            self._dxf_path = path
            self.dxf_path_edit.setText(path)
            # DXF area calculation will be implemented later
            self.result_card.setVisible(False)

    # ── Calculation ───────────────────────────────────────────────────────────

    def _calculate(self) -> None:
        # Thickness
        current_item = self.thickness_list.currentItem()
        if current_item is None:
            self.result_card.setVisible(False)
            return
        thickness_mm: float = current_item.data(Qt.UserRole)

        density = self.density_spin.value()  # kg/m³

        # Area (only manual supported now)
        mode = self._area_btn_group.checkedId()
        if mode == 1:
            # DXF – not yet implemented
            self.result_card.setVisible(False)
            return

        width_m = self.width_spin.value() / 1000.0
        height_m = self.height_spin.value() / 1000.0
        area_m2 = width_m * height_m

        thickness_m = thickness_mm / 1000.0
        volume_m3 = area_m2 * thickness_m
        weight_kg = volume_m3 * density
        kg_per_m2 = thickness_m * density  # kg/m² for this thickness

        self._area_result_val.setText(f"{area_m2:.2f} m²")
        self._weight_result_val.setText(f"{weight_kg:.2f} kg")
        self._density_area_result_val.setText(f"{kg_per_m2:.2f} kg/m²")

        self._area_result_card.set_value(area_m2)
        self._weight_result_card.set_value(weight_kg)
        self._density_area_result_card.set_value(kg_per_m2)

        self.result_card.setVisible(True)


# ── Layout helpers ─────────────────────────────────────────────────────────────

def _transparent_row() -> QWidget:
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    return w


def _col() -> QVBoxLayout:
    lay = QVBoxLayout()
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(4)
    return lay


def _field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("printFieldLabel")
    return lbl


class _ResultTile(QFrame):
    """Clickable result tile — copies numeric value to clipboard on click."""

    def __init__(self, panel: "SheetMetalWeightPanel"):
        super().__init__(panel)
        self._panel = panel
        self._value: Optional[float] = None
        self.setObjectName("smwResultTile")
        self.setCursor(Qt.PointingHandCursor)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(4)
        lay.setAlignment(Qt.AlignCenter)

    def set_value(self, value: float) -> None:
        self._value = value

    def _show_tooltip(self) -> None:
        if self._value is None:
            return
        tooltip_text = self._panel.tr("Value copied to clipboard")
        pos = self.mapToGlobal(QPoint(self.width() // 2, -8))
        QToolTip.showText(pos, tooltip_text, self, self.rect(), 2000)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._value is not None:
            # Format with system decimal separator
            dec_sep = locale.localeconv().get("decimal_point", ".")
            text = f"{self._value:.2f}".replace(".", dec_sep)
            QApplication.clipboard().setText(text)
            self._pending_tooltip = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton and getattr(self, "_pending_tooltip", False):
            self._pending_tooltip = False
            # Defer past the release so Qt doesn't kill the tooltip immediately
            QTimer.singleShot(0, self._show_tooltip)


def _result_key_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("smwResultKey")
    lbl.setAlignment(Qt.AlignCenter)
    return lbl


def _result_val_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("smwResultVal")
    lbl.setAlignment(Qt.AlignCenter)
    return lbl
