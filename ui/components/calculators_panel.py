"""Laser Cutting Gas calculator panel."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Type

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# ── Load scoring rules ────────────────────────────────────────────────────────

_RULES_PATH = Path(__file__).parent.parent.parent / "ref" / "gasScoring.json"
_SCORING_RULES: dict = json.loads(_RULES_PATH.read_text(encoding="utf-8"))

# Scoring computation order (matches JSON).
_GAS_ORDER: list[str] = list(_SCORING_RULES["gases"])

# Fixed display order: Compressed Air → Oxygen → Nitrogen.
_GAS_DISPLAY_ORDER: list[str] = ["compressed_air", "oxygen", "nitrogen"]


def _compute_score_range() -> tuple[float, float]:
    """Pre-compute the theoretical min/max total score any gas can receive."""
    weights = _SCORING_RULES["weights"]
    cat_weight = {
        "material": "material",
        "thickness": "thickness",
        "edge_quality": "edge_quality",
        "post_processing": "post_processing",
        "cost_priority": "cost_priority",
    }
    total_max = total_min = 0.0
    for cat, wkey in cat_weight.items():
        all_vals = [s for opt in _SCORING_RULES["rules"][cat].values() for s in opt.values()]
        total_max += max(all_vals) * weights[wkey]
        total_min += min(all_vals) * weights[wkey]
    return total_min, total_max


_SCORE_MIN, _SCORE_MAX = _compute_score_range()


# ── Scoring algorithm ─────────────────────────────────────────────────────────

def _thickness_range(t: float) -> str:
    if t <= 3:
        return "<=3"
    elif t <= 6:
        return "3-6"
    elif t <= 12:
        return "6-12"
    return ">12"


def score_assist_gas(
    material: str,
    thickness_mm: float,
    edge_quality: str,
    post_process: str,
    cost_priority: bool,
) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    """Return (total_scores_per_gas, per-category breakdown) via weighted scoring."""
    weights = _SCORING_RULES["weights"]
    rules = _SCORING_RULES["rules"]
    gases = _GAS_ORDER

    scores: dict[str, float] = {g: 0.0 for g in gases}
    breakdown: dict[str, dict[str, float]] = {}

    # Material
    mat_key = material if material in rules["material"] else "other"
    mat_s = rules["material"][mat_key]
    breakdown["material"] = mat_s
    for g in gases:
        scores[g] += mat_s[g] * weights["material"]

    # Thickness
    thick_s = rules["thickness"][_thickness_range(thickness_mm)]
    breakdown["thickness"] = thick_s
    for g in gases:
        scores[g] += thick_s[g] * weights["thickness"]

    # Edge quality
    eq_s = rules["edge_quality"][edge_quality]
    breakdown["edge_quality"] = eq_s
    for g in gases:
        scores[g] += eq_s[g] * weights["edge_quality"]

    # Post processing
    pp_s = rules["post_processing"][post_process]
    breakdown["post_processing"] = pp_s
    for g in gases:
        scores[g] += pp_s[g] * weights["post_processing"]

    # Cost priority: bool → "high" / "low"
    cost_s = rules["cost_priority"]["high" if cost_priority else "low"]
    breakdown["cost_priority"] = cost_s
    for g in gases:
        scores[g] += cost_s[g] * weights["cost_priority"]

    return scores, breakdown


# ── Asset paths ─────────────────────────────────────────────────────────────

_CHECK_ICON = Path(__file__).parent.parent.parent / "assets" / "icons" / "check_white.svg"

# ── Color helpers ─────────────────────────────────────────────────────────────

_GAS_COLORS = {
    "oxygen": "#ff6b6b",
    "nitrogen": "#4fc3f7",
    "compressed_air": "#81c784",
}


def _score_bar_color(score: float) -> str:
    """Return a hex color interpolated from red (low) to green (high)."""
    pct = max(0.0, min(1.0, (score - _SCORE_MIN) / (_SCORE_MAX - _SCORE_MIN)))
    r = int(220 * (1.0 - pct))
    g = int(200 * pct)
    return f"#{r:02x}{g:02x}14"


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

        # Row 3: cost priority checkbox
        row3 = _row_widget()
        row3_layout = QHBoxLayout(row3)
        row3_layout.setContentsMargins(0, 0, 0, 0)
        row3_layout.setSpacing(16)

        self.cost_check = QCheckBox()
        self.cost_check.setObjectName("gasCheck")
        _p = _CHECK_ICON.as_posix()
        self.cost_check.setStyleSheet(
            "QCheckBox::indicator {"
            " width:16px; height:16px; border-radius:4px;"
            " border:1px solid rgba(183,213,255,80);"
            " background-color:rgba(255,255,255,8);}"
            "QCheckBox::indicator:checked {"
            f" background-color:rgba(45,140,255,200);"
            f" border-color:rgba(45,140,255,220);"
            f" image:url({_p});}}"
        )
        row3_layout.addWidget(self.cost_check)
        row3_layout.addStretch(1)

        input_inner.addWidget(row3)

        # ── Real-time recalculation ───────────────────────────────────────────
        self.material_combo.currentIndexChanged.connect(self._calculate)
        self.thickness_spin.valueChanged.connect(self._calculate)
        self.edge_combo.currentIndexChanged.connect(self._calculate)
        self.post_combo.currentIndexChanged.connect(self._calculate)
        self.cost_check.stateChanged.connect(self._calculate)
        root.addWidget(input_card)
        root.addSpacing(14)

        # ── Result card ──────────────────────────────────────────────────────
        self.result_card = QFrame()
        self.result_card.setObjectName("gasResultCard")
        self.result_card.setVisible(False)
        result_inner = QVBoxLayout(self.result_card)
        result_inner.setContentsMargins(20, 18, 20, 18)
        result_inner.setSpacing(12)

        # Score ranking header
        self._result_header = QLabel()
        self._result_header.setObjectName("printSectionLabel")
        result_inner.addWidget(self._result_header)

        # Three gas ranking rows — filled dynamically by _calculate, sorted descending.
        # Each row: (name QLabel, QProgressBar)
        self._rank_rows: list[tuple[QLabel, QProgressBar]] = []
        for _ in range(3):
            row_frame = QFrame()
            row_frame.setObjectName("gasRankRow")
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(10, 7, 10, 7)
            row_layout.setSpacing(10)

            name_lbl = QLabel()
            name_lbl.setObjectName("gasRankName")
            name_lbl.setFixedWidth(148)
            row_layout.addWidget(name_lbl)

            bar = QProgressBar()
            bar.setObjectName("gasScoreBar")
            bar.setRange(0, 100)
            bar.setTextVisible(False)
            bar.setFixedHeight(16)
            bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            row_layout.addWidget(bar, 1)

            self._rank_rows.append((name_lbl, bar))
            result_inner.addWidget(row_frame)

        # Separator
        sep = QFrame()
        sep.setObjectName("gasSeparator")
        sep.setFrameShape(QFrame.HLine)
        result_inner.addWidget(sep)

        # Factor analysis header
        self._factor_header = QLabel()
        self._factor_header.setObjectName("gasReasonHeader")
        result_inner.addWidget(self._factor_header)

        # Factor table: 5 parameter rows × 3 gas columns
        self.factor_table = QTableWidget(5, 3)
        self.factor_table.setObjectName("gasFactorTable")
        self.factor_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.factor_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.factor_table.verticalHeader().setDefaultSectionSize(34)
        self.factor_table.verticalHeader().setMinimumWidth(170)
        self.factor_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.factor_table.setSelectionMode(QTableWidget.NoSelection)
        self.factor_table.setFocusPolicy(Qt.NoFocus)
        self.factor_table.setFixedHeight(34 * 5 + 36)
        result_inner.addWidget(self.factor_table)

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
        self._result_header.setText(self.tr("Score Ranking"))
        self._factor_header.setText(self.tr("Factor Analysis"))

        # Table column headers — fixed order: Compressed Air, Oxygen, Nitrogen
        self.factor_table.setHorizontalHeaderLabels([
            self.tr("Compressed Air"),
            self.tr("O₂  Oxygen"),
            self.tr("N₂  Nitrogen"),
        ])

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
            return self.tr("O₂  Oxygen")
        elif gas_key == "nitrogen":
            return self.tr("N₂  Nitrogen")
        elif gas_key == "compressed_air":
            return self.tr("Compressed Air")
        return gas_key

    # ── Calculation ───────────────────────────────────────────────────────────

    def _calculate(self) -> None:
        material = self.material_combo.currentData()
        thickness = self.thickness_spin.value()
        edge_quality = self.edge_combo.currentData()
        post_process = self.post_combo.currentData()
        cost_priority = self.cost_check.isChecked()

        if not material or not edge_quality or not post_process:
            return

        scores, breakdown = score_assist_gas(
            material, thickness, edge_quality, post_process, cost_priority
        )

        # ── Ranking rows (fixed order: Compressed Air, Oxygen, Nitrogen) ────────
        for (gas_key, gas_score), (name_lbl, bar) in zip(
            [(g, scores[g]) for g in _GAS_DISPLAY_ORDER], self._rank_rows
        ):
            name_lbl.setText(self._gas_display_name(gas_key))
            name_lbl.setStyleSheet(
                f"color: {_GAS_COLORS[gas_key]}; font-size: 13px; font-weight: 700;"
            )
            pct = max(0.0, min(1.0, (gas_score - _SCORE_MIN) / (_SCORE_MAX - _SCORE_MIN)))
            bar.setValue(int(pct * 100))
            bar.setStyleSheet(
                f"QProgressBar::chunk {{ background-color: {_score_bar_color(gas_score)};"
                f" border-radius: 3px; }}"
            )

        # ── Factor table ──────────────────────────────────────────────────────
        # Row vertical-header labels (include the selected value for context)
        cost_text = self.tr("High") if cost_priority else self.tr("Low")
        self.factor_table.setVerticalHeaderLabels([
            self.tr("Material: ") + self.material_combo.currentText(),
            self.tr("Thickness: ") + _thickness_range(thickness),
            self.tr("Edge Quality: ") + self.edge_combo.currentText(),
            self.tr("Post-Process: ") + self.post_combo.currentText(),
            self.tr("Cost Priority: ") + cost_text,
        ])

        # Cells: ✓ green if score > 0, ✗ red if score < 0, — neutral if zero
        cat_keys = ["material", "thickness", "edge_quality", "post_processing", "cost_priority"]
        for row_idx, cat in enumerate(cat_keys):
            for col_idx, gas in enumerate(_GAS_DISPLAY_ORDER):
                s = breakdown[cat][gas]
                if s > 0:
                    text, bg, fg = "✓", "#1b5e20", "#a5d6a7"
                elif s < 0:
                    text, bg, fg = "✗", "#5d1a1a", "#ef9a9a"
                else:
                    text, bg, fg = "—", "#1e2a3a", "#7a91b8"
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(QColor(bg))
                item.setForeground(QColor(fg))
                self.factor_table.setItem(row_idx, col_idx, item)

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
