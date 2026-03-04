"""Laser Cutting Gas calculator panel."""

from __future__ import annotations

from typing import Type

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


# ── Gas selection algorithm ──────────────────────────────────────────────────

def select_assist_gas(
    material: str,
    thickness_mm: float,
    edge_quality: str,
    post_process: str,
    cost_priority: bool,
) -> tuple[str, str]:
    """Return (gas_key, reason) based on the industrial selection algorithm."""

    avoid_oxygen = post_process in ("welding", "painting")

    if material == "carbon_steel":
        if thickness_mm > 12:
            if avoid_oxygen:
                return "nitrogen", (
                    "Thick carbon steel normally requires oxygen, but welding/painting "
                    "requires oxide-free edges — nitrogen selected."
                )
            return "oxygen", (
                "Heavy carbon steel (> 12 mm): oxygen provides the exothermic energy "
                "needed for a full-depth cut."
            )
        if thickness_mm <= 3:
            if avoid_oxygen and cost_priority:
                return "compressed_air", (
                    "Thin sheet with post-processing and cost priority: "
                    "compressed air avoids oxidation at minimal cost."
                )
            if edge_quality == "high":
                return "nitrogen", (
                    "Thin carbon steel with high edge-quality requirement: "
                    "nitrogen prevents surface oxidation."
                )
            if cost_priority:
                return "compressed_air", (
                    "Thin carbon steel with cost priority: compressed air reduces "
                    "gas cost by up to 80 %."
                )
            return "compressed_air", (
                "Thin carbon steel (≤ 3 mm): compressed air gives acceptable "
                "quality at low cost."
            )
        # 3 < thickness ≤ 12
        if avoid_oxygen:
            return "nitrogen", (
                "Carbon steel with post-processing: oxygen avoided to keep "
                "edges oxide-free for welding/painting."
            )
        return "oxygen", (
            "Carbon steel (3 – 12 mm): oxygen boosts effective cutting power "
            "through exothermic reaction."
        )

    if material == "stainless_steel":
        if cost_priority and thickness_mm <= 3 and not avoid_oxygen:
            return "compressed_air", (
                "Thin stainless steel with cost priority: compressed air "
                "(≈ 78 % N₂) provides reasonable edge quality at lower cost."
            )
        return "nitrogen", (
            "Stainless steel: nitrogen prevents surface oxidation and delivers "
            "clean, weld-ready edges."
        )

    if material == "galvanized_steel":
        if thickness_mm <= 3:
            return "compressed_air", (
                "Thin galvanized steel: compressed air dilutes zinc fumes and "
                "keeps operating costs low."
            )
        return "nitrogen", (
            "Thick galvanized steel (> 3 mm): nitrogen reduces zinc-oxide "
            "fume generation and maintains edge quality."
        )

    if material == "aluminum":
        if thickness_mm > 6:
            return "nitrogen", (
                "Thick aluminum (> 6 mm): high-pressure nitrogen prevents "
                "oxide buildup and supports the melt ejection."
            )
        return "nitrogen", (
            "Aluminum: nitrogen avoids aluminum-oxide formation and keeps "
            "edges clean and burr-free."
        )

    return "nitrogen", "Default: nitrogen selected as the safest inert option."


# ── Gas color constants ──────────────────────────────────────────────────────

_GAS_COLORS = {
    "oxygen": "#ff6b6b",
    "nitrogen": "#4fc3f7",
    "compressed_air": "#81c784",
}


# ── Panel widget ─────────────────────────────────────────────────────────────

class CalculatorsPanel(QFrame):
    """Laser Cutting Gas calculator panel."""

    def __init__(self, SubtitleLabel: Type, BodyLabel: Type, parent=None):
        super().__init__(parent)
        self.setObjectName("mainPanel")

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        # Header
        self._title_lbl = SubtitleLabel()
        self._title_lbl.setObjectName("mainTitle")
        self._subtitle_lbl = BodyLabel()
        self._subtitle_lbl.setObjectName("pageSubtitle")
        self._subtitle_lbl.setWordWrap(True)
        root.addWidget(self._title_lbl)
        root.addSpacing(2)
        root.addWidget(self._subtitle_lbl)
        root.addSpacing(22)

        # ── Input card ───────────────────────────────────────────────────────
        input_card = QFrame()
        input_card.setObjectName("printCard")
        input_inner = QVBoxLayout(input_card)
        input_inner.setContentsMargins(20, 16, 20, 18)
        input_inner.setSpacing(12)

        self._params_lbl = QLabel()
        self._params_lbl.setObjectName("printSectionLabel")
        input_inner.addWidget(self._params_lbl)

        # Row 1: material + thickness
        row1 = _row_widget()
        row1_layout = QHBoxLayout(row1)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(16)

        mat_col = _col()
        self._mat_lbl = _field_label_widget("")
        mat_col.addWidget(self._mat_lbl)
        self.material_combo = QComboBox()
        self.material_combo.setObjectName("gasCombo")
        self.material_combo.setMinimumHeight(36)
        for internal_key in ("carbon_steel", "stainless_steel", "galvanized_steel", "aluminum"):
            self.material_combo.addItem("", internal_key)
        mat_col.addWidget(self.material_combo)

        thick_col = _col()
        self._thick_lbl = _field_label_widget("")
        thick_col.addWidget(self._thick_lbl)
        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setObjectName("gasSpin")
        self.thickness_spin.setMinimumHeight(36)
        self.thickness_spin.setRange(0.1, 200.0)
        self.thickness_spin.setDecimals(1)
        self.thickness_spin.setSingleStep(0.5)
        self.thickness_spin.setValue(3.0)
        self.thickness_spin.setSuffix(" mm")
        thick_col.addWidget(self.thickness_spin)

        row1_layout.addLayout(mat_col, 2)
        row1_layout.addLayout(thick_col, 1)
        input_inner.addWidget(row1)

        # Row 2: edge quality + post process
        row2 = _row_widget()
        row2_layout = QHBoxLayout(row2)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(16)

        eq_col = _col()
        self._eq_lbl = _field_label_widget("")
        eq_col.addWidget(self._eq_lbl)
        self.edge_combo = QComboBox()
        self.edge_combo.setObjectName("gasCombo")
        self.edge_combo.setMinimumHeight(36)
        for internal_key in ("high", "medium", "low"):
            self.edge_combo.addItem("", internal_key)
        eq_col.addWidget(self.edge_combo)

        pp_col = _col()
        self._pp_lbl = _field_label_widget("")
        pp_col.addWidget(self._pp_lbl)
        self.post_combo = QComboBox()
        self.post_combo.setObjectName("gasCombo")
        self.post_combo.setMinimumHeight(36)
        for internal_key in ("none", "welding", "painting"):
            self.post_combo.addItem("", internal_key)
        pp_col.addWidget(self.post_combo)

        row2_layout.addLayout(eq_col, 1)
        row2_layout.addLayout(pp_col, 1)
        input_inner.addWidget(row2)

        # Row 3: cost priority checkbox + calculate button
        row3 = _row_widget()
        row3_layout = QHBoxLayout(row3)
        row3_layout.setContentsMargins(0, 0, 0, 0)
        row3_layout.setSpacing(16)

        self.cost_check = QCheckBox()
        self.cost_check.setObjectName("gasCheck")
        row3_layout.addWidget(self.cost_check)
        row3_layout.addStretch(1)

        self.calc_btn = QPushButton()
        self.calc_btn.setObjectName("gasCalcBtn")
        self.calc_btn.setMinimumHeight(38)
        self.calc_btn.setMinimumWidth(120)
        self.calc_btn.clicked.connect(self._calculate)
        row3_layout.addWidget(self.calc_btn)

        input_inner.addWidget(row3)
        root.addWidget(input_card)
        root.addSpacing(14)

        # ── Result card ──────────────────────────────────────────────────────
        self.result_card = QFrame()
        self.result_card.setObjectName("gasResultCard")
        self.result_card.setVisible(False)
        result_inner = QVBoxLayout(self.result_card)
        result_inner.setContentsMargins(20, 18, 20, 18)
        result_inner.setSpacing(10)

        self._result_header = QLabel()
        self._result_header.setObjectName("printSectionLabel")
        result_inner.addWidget(self._result_header)

        self.gas_name_label = QLabel("")
        self.gas_name_label.setObjectName("gasResultName")
        result_inner.addWidget(self.gas_name_label)

        self.gas_desc_label = QLabel("")
        self.gas_desc_label.setObjectName("gasResultDesc")
        self.gas_desc_label.setWordWrap(True)
        result_inner.addWidget(self.gas_desc_label)

        separator = QFrame()
        separator.setObjectName("gasSeparator")
        separator.setFrameShape(QFrame.HLine)
        result_inner.addWidget(separator)

        self._reason_header = QLabel()
        self._reason_header.setObjectName("gasReasonHeader")
        result_inner.addWidget(self._reason_header)

        self.reason_label = QLabel("")
        self.reason_label.setObjectName("gasReason")
        self.reason_label.setWordWrap(True)
        result_inner.addWidget(self.reason_label)

        root.addWidget(self.result_card)
        root.addStretch(1)

        self.retranslateUi()
        # Trigger once so result shows immediately on first view.
        self._calculate()

    # ── i18n ─────────────────────────────────────────────────────────────────

    def retranslateUi(self) -> None:
        self._title_lbl.setText(self.tr("Laser Cutting Gas"))
        self._subtitle_lbl.setText(
            self.tr("Select material and cutting parameters to get the recommended assist gas.")
        )
        self._params_lbl.setText(self.tr("Parameters"))
        self._mat_lbl.setText(self.tr("Material"))
        self._thick_lbl.setText(self.tr("Thickness (mm)"))
        self._eq_lbl.setText(self.tr("Edge Quality"))
        self._pp_lbl.setText(self.tr("Post-Process"))
        self.cost_check.setText(self.tr("Prioritize cost reduction"))
        self.calc_btn.setText(self.tr("Calculate"))
        self._result_header.setText(self.tr("Recommended Gas"))
        self._reason_header.setText(self.tr("Reasoning"))

        # Update combo item texts while preserving internal data.
        for i, text in enumerate([self.tr("Carbon Steel"), self.tr("Stainless Steel"),
                                   self.tr("Galvanized Steel"), self.tr("Aluminum")]):
            self.material_combo.setItemText(i, text)
        for i, text in enumerate([self.tr("High"), self.tr("Medium"), self.tr("Low")]):
            self.edge_combo.setItemText(i, text)
        for i, text in enumerate([self.tr("None"), self.tr("Welding"), self.tr("Painting")]):
            self.post_combo.setItemText(i, text)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _gas_display_name(self, gas_key: str) -> str:
        """Return translated gas display name."""
        if gas_key == "oxygen":
            return self.tr("O₂ — Oxygen")
        elif gas_key == "nitrogen":
            return self.tr("N₂ — Nitrogen")
        elif gas_key == "compressed_air":
            return self.tr("Compressed Air")
        return ""

    def _gas_description(self, gas_key: str) -> str:
        """Return translated gas description."""
        if gas_key == "oxygen":
            return self.tr(
                "Reacts exothermically with the metal, greatly increasing effective cutting power. "
                "Best for thick carbon steel. Leaves an oxide layer on edges."
            )
        elif gas_key == "nitrogen":
            return self.tr(
                "Inert gas — prevents oxidation and delivers clean, bright edges. "
                "Required for stainless steel, aluminum, and parts that will be welded or painted."
            )
        elif gas_key == "compressed_air":
            return self.tr(
                "Economical blend (≈ 78 % N₂ + 21 % O₂). Intermediate quality at significantly "
                "lower cost than pure gases. Suitable for thin sheets and non-critical edges."
            )
        return ""

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _calculate(self) -> None:
        # Internal keys are stored as item data — translation-safe.
        material = self.material_combo.currentData()
        thickness = self.thickness_spin.value()
        edge_quality = self.edge_combo.currentData()
        post_process = self.post_combo.currentData()
        cost_priority = self.cost_check.isChecked()

        if not material or not edge_quality or not post_process:
            return

        gas_key, reason = select_assist_gas(
            material, thickness, edge_quality, post_process, cost_priority
        )

        gas_display = self._gas_display_name(gas_key)
        gas_color = _GAS_COLORS[gas_key]
        gas_desc = self._gas_description(gas_key)

        self.gas_name_label.setText(gas_display)
        self.gas_name_label.setStyleSheet(
            f"color: {gas_color}; font-size: 22px; font-weight: 700; letter-spacing: 0.3px;"
        )
        self.gas_desc_label.setText(gas_desc)
        self.reason_label.setText(self.tr(reason))
        self.result_card.setVisible(True)


# ── Layout helpers ────────────────────────────────────────────────────────────

def _row_widget() -> QWidget:
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    return w


def _col() -> QVBoxLayout:
    lay = QVBoxLayout()
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(4)
    return lay


def _field_label_widget(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("printFieldLabel")
    return lbl
