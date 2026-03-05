"""Left-side navigation panel for the Calculators section."""

from typing import Type

from PyQt5.QtCore import QEvent, QSize, pyqtSignal
from PyQt5.QtWidgets import QButtonGroup, QFrame, QPushButton, QVBoxLayout


class CalculatorsNavPanel(QFrame):
    """Navbar panel with calculator tool buttons."""

    # Emits the index of the selected calculator (0 = Laser Gas, 1 = Sheet Metal Weight)
    calculator_changed = pyqtSignal(int)

    def __init__(self, SubtitleLabel: Type, BodyLabel: Type, PushButton: Type, parent=None):
        super().__init__(parent)
        self.setObjectName("navPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        self._nav_title = SubtitleLabel()
        self._nav_title.setObjectName("navTitle")

        self._nav_subtitle = BodyLabel()
        self._nav_subtitle.setObjectName("navSubtitle")
        self._nav_subtitle.setWordWrap(True)

        try:
            from qfluentwidgets import FluentIcon
            self.laser_gas_btn = QPushButton()
            self.laser_gas_btn.setIcon(FluentIcon.CALORIES.icon())
            self.laser_gas_btn.setIconSize(QSize(16, 16))
        except (ImportError, AttributeError):
            self.laser_gas_btn = QPushButton()

        self.laser_gas_btn.setObjectName("utilNavButton")
        self.laser_gas_btn.setCheckable(True)
        self.laser_gas_btn.setChecked(True)
        self.laser_gas_btn.setMinimumHeight(42)

        try:
            from qfluentwidgets import FluentIcon
            self.sheet_metal_btn = QPushButton()
            self.sheet_metal_btn.setIcon(FluentIcon.WEIGHT.icon())
            self.sheet_metal_btn.setIconSize(QSize(16, 16))
        except (ImportError, AttributeError):
            self.sheet_metal_btn = QPushButton()

        self.sheet_metal_btn.setObjectName("utilNavButton")
        self.sheet_metal_btn.setCheckable(True)
        self.sheet_metal_btn.setChecked(False)
        self.sheet_metal_btn.setMinimumHeight(42)

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)
        self._btn_group.addButton(self.laser_gas_btn, 0)
        self._btn_group.addButton(self.sheet_metal_btn, 1)

        layout.addWidget(self._nav_title)
        layout.addWidget(self._nav_subtitle)
        layout.addSpacing(12)
        layout.addWidget(self.laser_gas_btn)
        layout.addWidget(self.sheet_metal_btn)
        layout.addStretch(1)

        self._btn_group.buttonClicked.connect(
            lambda btn: self.calculator_changed.emit(self._btn_group.id(btn))
        )

        self.retranslateUi()

    # ── i18n ─────────────────────────────────────────────────────────────────

    def retranslateUi(self) -> None:
        self._nav_title.setText(self.tr("Calculators"))
        self._nav_subtitle.setText(self.tr("Select a calculator."))
        self.laser_gas_btn.setText("  " + self.tr("Laser Cutting Gas"))
        self.sheet_metal_btn.setText("  " + self.tr("Sheet Metal Weight"))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
