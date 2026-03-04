"""Left-side navigation panel for the Calculators section."""

from typing import Type

from PyQt5.QtCore import QEvent, QSize
from PyQt5.QtWidgets import QButtonGroup, QFrame, QPushButton, QVBoxLayout


class CalculatorsNavPanel(QFrame):
    """Navbar panel with calculator tool buttons."""

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

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)
        self._btn_group.addButton(self.laser_gas_btn)

        layout.addWidget(self._nav_title)
        layout.addWidget(self._nav_subtitle)
        layout.addSpacing(12)
        layout.addWidget(self.laser_gas_btn)
        layout.addStretch(1)

        self.retranslateUi()

    # ── i18n ─────────────────────────────────────────────────────────────────

    def retranslateUi(self) -> None:
        self._nav_title.setText(self.tr("Calculators"))
        self._nav_subtitle.setText(self.tr("Select a calculator."))
        self.laser_gas_btn.setText("  " + self.tr("Laser Cutting Gas"))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
