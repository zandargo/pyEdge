"""Laser Cutting Gas calculator panel."""

from __future__ import annotations

from typing import Type

from PyQt5.QtCore import Qt
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


# ── Display helpers ──────────────────────────────────────────────────────────

_GAS_DISPLAY = {
    "oxygen": ("O₂ — Oxygen", "#ff6b6b"),
    "nitrogen": ("N₂ — Nitrogen", "#4fc3f7"),
    "compressed_air": ("Compressed Air", "#81c784"),
}

_GAS_DETAIL = {
    "oxygen": (
        "Reacts exothermically with the metal, greatly increasing effective cutting power. "
        "Best for thick carbon steel. Leaves an oxide layer on edges."
    ),
    "nitrogen": (
        "Inert gas — prevents oxidation and delivers clean, bright edges. "
        "Required for stainless steel, aluminum, and parts that will be welded or painted."
    ),
    "compressed_air": (
        "Economical blend (≈ 78 % N₂ + 21 % O₂). Intermediate quality at significantly "
        "lower cost than pure gases. Suitable for thin sheets and non-critical edges."
    ),
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
        title = SubtitleLabel("Laser Cutting Gas")
        title.setObjectName("mainTitle")
        subtitle = BodyLabel(
            "Select material and cutting parameters to get the recommended assist gas."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        root.addWidget(title)
        root.addSpacing(2)
        root.addWidget(subtitle)
        root.addSpacing(22)

        # ── Input card ───────────────────────────────────────────────────────
        input_card = QFrame()
        input_card.setObjectName("printCard")
        input_inner = QVBoxLayout(input_card)
        input_inner.setContentsMargins(20, 16, 20, 18)
        input_inner.setSpacing(12)

        input_section = QLabel("Parameters")
        input_section.setObjectName("printSectionLabel")
        input_inner.addWidget(input_section)

        # Row 1: material + thickness
        row1 = _row_widget()
        row1_layout = QHBoxLayout(row1)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(16)

        mat_col = _col()
        _field_label("Material", mat_col)
        self.material_combo = QComboBox()
        self.material_combo.setObjectName("gasCombo")
        self.material_combo.setMinimumHeight(36)
        self.material_combo.addItems([
            "Carbon Steel",
            "Stainless Steel",
            "Galvanized Steel",
            "Aluminum",
        ])
        mat_col.addWidget(self.material_combo)

        thick_col = _col()
        _field_label("Thickness (mm)", thick_col)
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
        _field_label("Edge Quality", eq_col)
        self.edge_combo = QComboBox()
        self.edge_combo.setObjectName("gasCombo")
        self.edge_combo.setMinimumHeight(36)
        self.edge_combo.addItems(["High", "Medium", "Low"])
        eq_col.addWidget(self.edge_combo)

        pp_col = _col()
        _field_label("Post-Process", pp_col)
        self.post_combo = QComboBox()
        self.post_combo.setObjectName("gasCombo")
        self.post_combo.setMinimumHeight(36)
        self.post_combo.addItems(["None", "Welding", "Painting"])
        pp_col.addWidget(self.post_combo)

        row2_layout.addLayout(eq_col, 1)
        row2_layout.addLayout(pp_col, 1)
        input_inner.addWidget(row2)

        # Row 3: cost priority checkbox + calculate button
        row3 = _row_widget()
        row3_layout = QHBoxLayout(row3)
        row3_layout.setContentsMargins(0, 0, 0, 0)
        row3_layout.setSpacing(16)

        self.cost_check = QCheckBox("Prioritize cost reduction")
        self.cost_check.setObjectName("gasCheck")
        row3_layout.addWidget(self.cost_check)
        row3_layout.addStretch(1)

        self.calc_btn = QPushButton("Calculate")
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

        result_header = QLabel("Recommended Gas")
        result_header.setObjectName("printSectionLabel")
        result_inner.addWidget(result_header)

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

        reason_header = QLabel("Reasoning")
        reason_header.setObjectName("gasReasonHeader")
        result_inner.addWidget(reason_header)

        self.reason_label = QLabel("")
        self.reason_label.setObjectName("gasReason")
        self.reason_label.setWordWrap(True)
        result_inner.addWidget(self.reason_label)

        root.addWidget(self.result_card)
        root.addStretch(1)

        # Trigger once so result shows immediately on first view if desired
        self._calculate()

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _calculate(self) -> None:
        material_map = {
            "Carbon Steel": "carbon_steel",
            "Stainless Steel": "stainless_steel",
            "Galvanized Steel": "galvanized_steel",
            "Aluminum": "aluminum",
        }
        edge_map = {"High": "high", "Medium": "medium", "Low": "low"}
        post_map = {"None": "none", "Welding": "welding", "Painting": "painting"}

        material = material_map[self.material_combo.currentText()]
        thickness = self.thickness_spin.value()
        edge_quality = edge_map[self.edge_combo.currentText()]
        post_process = post_map[self.post_combo.currentText()]
        cost_priority = self.cost_check.isChecked()

        gas_key, reason = select_assist_gas(
            material, thickness, edge_quality, post_process, cost_priority
        )

        gas_display, gas_color = _GAS_DISPLAY[gas_key]
        gas_desc = _GAS_DETAIL[gas_key]

        self.gas_name_label.setText(gas_display)
        self.gas_name_label.setStyleSheet(
            f"color: {gas_color}; font-size: 22px; font-weight: 700; letter-spacing: 0.3px;"
        )
        self.gas_desc_label.setText(gas_desc)
        self.reason_label.setText(reason)
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


def _field_label(text: str, layout: QVBoxLayout) -> None:
    lbl = QLabel(text)
    lbl.setObjectName("printFieldLabel")
    layout.addWidget(lbl)
