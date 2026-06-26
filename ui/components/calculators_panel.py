"""Laser Cutting Gas calculator panel."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Type

from translations import get_saved_locale
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QColor, QDoubleValidator
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
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
    rules = _SCORING_RULES
    gases = _GAS_ORDER
    max_score = 0.0

    for gas in gases:
        max_edge = max(opt[gas] for opt in rules["edge_quality"].values())
        max_post = max(opt[gas] for opt in rules["post_processing"].values())
        max_cost = max(opt[gas] for opt in rules["low_cost_priority"].values())
        max_score = max(max_score, max_edge * max_post * max_cost)

    return 0.0, max_score


_SCORE_MIN, _SCORE_MAX = _compute_score_range()


# ── Scoring algorithm ─────────────────────────────────────────────────────────

def _thickness_range(t: float) -> str:
    """Format thickness for display."""
    return f"{t:.2f} mm"


def _material_gas_allowed(material: str, gas: str, thickness_mm: float) -> bool:
    gas_rule = _SCORING_RULES["materials"].get(material, {}).get(gas)
    if gas_rule is None:
        return False

    allowed_thickness = gas_rule.get("allowed_thickness")
    if not allowed_thickness:
        return False

    min_thickness = float(allowed_thickness[0])
    max_thickness = float(allowed_thickness[-1])
    return min_thickness <= thickness_mm <= max_thickness


def score_assist_gas(
    material: str,
    thickness_mm: float,
    edge_quality: str,
    post_process: str,
    cost_priority: bool,
) -> tuple[dict[str, float], dict[str, dict[str, float]], list[str]]:
    """Return (total_scores_per_gas, per-category breakdown, disallowed_gases)."""
    rules = _SCORING_RULES
    gases = _GAS_ORDER

    material_scores: dict[str, float] = {}
    disallowed: list[str] = []
    for gas in gases:
        allowed = _material_gas_allowed(material, gas, thickness_mm)
        material_scores[gas] = 1.0 if allowed else 0.0
        if not allowed:
            disallowed.append(gas)

    scores = material_scores.copy()
    breakdown: dict[str, dict[str, float]] = {
        "material": material_scores,
        "thickness": {g: 1.0 for g in gases},
    }

    eq_s = rules["edge_quality"][edge_quality]
    breakdown["edge_quality"] = eq_s
    for g in gases:
        scores[g] *= eq_s[g]

    pp_s = rules["post_processing"][post_process]
    breakdown["post_processing"] = pp_s
    for g in gases:
        scores[g] *= pp_s[g]

    cost_s = rules["low_cost_priority"]["high" if cost_priority else "low"]
    breakdown["cost_priority"] = cost_s
    for g in gases:
        scores[g] *= cost_s[g]

    return scores, breakdown, disallowed


# ── Asset paths ─────────────────────────────────────────────────────────────

_CHECK_ICON = Path(__file__).parent.parent.parent / "assets" / "icons" / "check_white.svg"

# ── Color helpers ─────────────────────────────────────────────────────────────

_GAS_COLORS = {
    "oxygen": "#ff6b6b",
    "nitrogen": "#4fc3f7",
    "compressed_air": "#81c784",
}


def _score_bar_color(score: float, lowest: float, highest: float) -> str:
    """Return a hex color interpolated from red (lowest) to green (highest)."""
    if highest <= lowest:
        pct = 1.0
    else:
        pct = max(0.0, min(1.0, (score - lowest) / (highest - lowest)))
    red = int(200 * (1.0 - pct))
    green = int(140 * pct)
    return f"#{red:02x}{green:02x}00"


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
        self.thickness_combo = QComboBox()
        self.thickness_combo.setObjectName("gasCombo")
        self.thickness_combo.setMinimumHeight(36)
        self.thickness_combo.setEditable(True)
        self.thickness_combo.setInsertPolicy(QComboBox.NoInsert)
        self.thickness_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.thickness_combo.lineEdit().setValidator(QDoubleValidator(0.01, 200.0, 2, self.thickness_combo.lineEdit()))
        self.thickness_combo.lineEdit().installEventFilter(self)
        thick_col.addWidget(self.thickness_combo)

        row1_layout.addLayout(mat_col, 2)
        row1_layout.addLayout(thick_col, 1)
        input_inner.addWidget(row1)

# Row 2: post process + cost priority checkbox
        row2 = _row_widget()
        row2_layout = QHBoxLayout(row2)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(16)

        pp_col = _col()
        self._pp_lbl = _field_label_widget("")
        pp_col.addWidget(self._pp_lbl)
        self.post_combo = QComboBox()
        self.post_combo.setObjectName("gasCombo")
        self.post_combo.setMinimumHeight(36)
        for internal_key in ("none", "welding", "painting"):
            self.post_combo.addItem("", internal_key)
        pp_col.addWidget(self.post_combo)

        row2_layout.addLayout(pp_col, 2)

        cost_col = QHBoxLayout()
        cost_col.setContentsMargins(0, 0, 0, 0)
        cost_col.setSpacing(0)
        cost_col.addStretch(1)

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
        self.cost_check.setChecked(True)
        cost_col.addWidget(self.cost_check)
        row2_layout.addLayout(cost_col, 1)

        input_inner.addWidget(row2)

        self._error_lbl = QLabel()
        self._error_lbl.setObjectName("gasErrorLabel")
        self._error_lbl.setWordWrap(True)
        self._error_lbl.setVisible(False)
        self._error_lbl.setStyleSheet("color: #f87171; font-size: 12px;")
        input_inner.addWidget(self._error_lbl)

        # ── Real-time recalculation ───────────────────────────────────────────
        self.material_combo.currentIndexChanged.connect(self._on_material_changed)
        self.material_combo.currentIndexChanged.connect(self._calculate)
        self.thickness_combo.currentTextChanged.connect(self._calculate)
        self.post_combo.currentIndexChanged.connect(self._calculate)
        self.cost_check.stateChanged.connect(self._calculate)
        root.addWidget(input_card)
        root.addSpacing(14)

        # ── Recommended gas card ─────────────────────────────────────────────
        self.recommended_card = QFrame()
        self.recommended_card.setObjectName("gasResultCard")
        recommended_inner = QVBoxLayout(self.recommended_card)
        recommended_inner.setContentsMargins(20, 18, 20, 18)
        recommended_inner.setSpacing(12)

        recommended_row = QWidget()
        recommended_row.setStyleSheet("background: transparent;")
        recommended_layout = QHBoxLayout(recommended_row)
        recommended_layout.setContentsMargins(0, 0, 0, 0)
        recommended_layout.setSpacing(8)

        self._recommended_label = QLabel()
        self._recommended_label.setObjectName("gasRecommendedLabelPrefix")
        self._recommended_label.setStyleSheet(
            "color: #aadddd; font-size: 16px; font-weight: 600;"
        )
        recommended_layout.addWidget(self._recommended_label)

        self._recommended_gas_lbl = QLabel()
        self._recommended_gas_lbl.setObjectName("gasRecommendedLabel")
        self._recommended_gas_lbl.setStyleSheet(
            "color: #dddddd; font-size: 24px; font-weight: 700;"
        )
        recommended_layout.addWidget(self._recommended_gas_lbl)
        recommended_layout.addStretch(1)

        recommended_inner.addWidget(recommended_row)

        self.recommended_card.setVisible(False)
        root.addWidget(self.recommended_card)
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

        # Factor table: 4 parameter rows × 3 gas columns
        self.factor_table = QTableWidget(4, 3)
        self.factor_table.setObjectName("gasFactorTable")
        self.factor_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.factor_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.factor_table.verticalHeader().setDefaultSectionSize(34)
        self.factor_table.verticalHeader().setMinimumWidth(170)
        self.factor_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.factor_table.setSelectionMode(QTableWidget.NoSelection)
        self.factor_table.setFocusPolicy(Qt.NoFocus)
        self.factor_table.setFixedHeight(34 * 4 + 36)
        result_inner.addWidget(self.factor_table)

        root.addWidget(self.result_card)
        root.addStretch(1)

        self.retranslateUi()
        self._populate_thickness_options(self.material_combo.currentData())
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
        self._pp_lbl.setText(self.tr("Post-Process"))
        self.cost_check.setText(self.tr("Prioritize cost reduction"))
        self._recommended_label.setText(self._localized_recommended_gas_prefix())
        self._recommended_gas_lbl.setText("")
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
        for i, text in enumerate([self.tr("None"), self.tr("Welding"), self.tr("Painting")]):
            self.post_combo.setItemText(i, text)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def _localized_recommended_gas_prefix(self) -> str:
        prefix = self.tr("Recommended gas:")
        if not prefix or prefix == "Recommended gas":
            prefix = self.tr("Recommended gas:")
        if not prefix or prefix == "Recommended gas:":
            current_locale = get_saved_locale()
            if current_locale == "pt_BR":
                return "Gás recomendado:"
        return prefix

    def eventFilter(self, watched, event):
        if watched is self.thickness_combo.lineEdit():
            if event.type() in (QEvent.MouseButtonRelease, QEvent.FocusIn):
                self.thickness_combo.showPopup()
        return super().eventFilter(watched, event)

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

    def _populate_thickness_options(self, material: str | None) -> None:
        if not material:
            self.thickness_combo.clear()
            return

        material_rules = _SCORING_RULES["materials"].get(material, {})
        values: set[float] = set()
        for gas_rule in material_rules.values():
            allowed = gas_rule.get("allowed_thickness") or []
            for t in allowed:
                values.add(float(t))

        sorted_values = sorted(values)
        self.thickness_combo.blockSignals(True)
        self.thickness_combo.clear()
        for thickness in sorted_values:
            self.thickness_combo.addItem(f"{thickness:g}", thickness)
        if sorted_values:
            self.thickness_combo.setCurrentIndex(0)
            self.thickness_combo.lineEdit().setText(f"{sorted_values[0]:g}")
        else:
            self.thickness_combo.lineEdit().clear()
        self.thickness_combo.blockSignals(False)

    def _on_material_changed(self, _index: int) -> None:
        self._populate_thickness_options(self.material_combo.currentData())

    def _parse_thickness(self) -> float | None:
        text = self.thickness_combo.currentText().strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    # ── Calculation ───────────────────────────────────────────────────────────

    def _calculate(self) -> None:
        material = self.material_combo.currentData()
        thickness = self._parse_thickness()
        edge_quality = "medium"
        post_process = self.post_combo.currentData()
        cost_priority = self.cost_check.isChecked()

        if thickness is None:
            self.result_card.setVisible(False)
            return

        if not material or not post_process:
            return

        scores, breakdown, disallowed = score_assist_gas(
            material, thickness, edge_quality, post_process, cost_priority
        )

        # if disallowed:
        #     disallowed_labels = [self._gas_display_name(g) for g in disallowed]
        #     self._error_lbl.setText(
        #         self.tr(
        #             "The following gases are not allowed for this material/thickness: {0}"
        #         ).format(", ".join(disallowed_labels))
        #     )
        #     self._error_lbl.setVisible(True)
        # else:
        #     self._error_lbl.setVisible(False)

        # ── Ranking rows (fixed order: Compressed Air, Oxygen, Nitrogen) ────────
        score_values = [scores[g] for g in _GAS_DISPLAY_ORDER]
        lowest_score = min(score_values)
        highest_score = max(score_values)

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
                f"QProgressBar::chunk {{ background-color: {_score_bar_color(gas_score, lowest_score, highest_score)};"
                f" border-radius: 3px; }}"
            )

        # ── Factor table ──────────────────────────────────────────────────────
        # Row vertical-header labels (include the selected value for context)
        cost_text = self.tr("High") if cost_priority else self.tr("Low")
        self.factor_table.setVerticalHeaderLabels([
            self.tr("Material: ") + self.material_combo.currentText(),
            self.tr("Thickness: ") + _thickness_range(thickness),
            self.tr("Post-Process: ") + self.post_combo.currentText(),
            self.tr("Cost Priority: ") + cost_text,
        ])

        best_gas = max(_GAS_DISPLAY_ORDER, key=lambda g: scores[g])
        best_name = self._gas_display_name(best_gas) if scores[best_gas] > 0 else self.tr("None")
        self._recommended_label.setText(self._localized_recommended_gas_prefix())
        self._recommended_gas_lbl.setText(best_name)
        self.recommended_card.setVisible(True)

        # Cells: ✓ green if score > 0, ✗ red if score < 0, — neutral if zero
        cat_keys = ["material", "thickness", "post_processing", "cost_priority"]
        for row_idx, cat in enumerate(cat_keys):
            for col_idx, gas in enumerate(_GAS_DISPLAY_ORDER):
                s = breakdown[cat][gas]
                if cat == "material" and s == 0:
                    text, bg, fg = "✗", "#5d1a1a", "#ef9a9a"
                elif s > 0:
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
