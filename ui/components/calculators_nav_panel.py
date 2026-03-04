"""Left-side navigation panel for the Calculators section."""

from typing import Type

from PyQt5.QtCore import QSize
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

        nav_title = SubtitleLabel("Calculators")
        nav_title.setObjectName("navTitle")

        nav_subtitle = BodyLabel("Select a calculator.")
        nav_subtitle.setObjectName("navSubtitle")
        nav_subtitle.setWordWrap(True)

        try:
            from qfluentwidgets import FluentIcon
            self.laser_gas_btn = QPushButton("  Laser Cutting Gas")
            self.laser_gas_btn.setIcon(FluentIcon.CALORIES.icon())
            self.laser_gas_btn.setIconSize(QSize(16, 16))
        except (ImportError, AttributeError):
            self.laser_gas_btn = QPushButton("  Laser Cutting Gas")

        self.laser_gas_btn.setObjectName("utilNavButton")
        self.laser_gas_btn.setCheckable(True)
        self.laser_gas_btn.setChecked(True)
        self.laser_gas_btn.setMinimumHeight(42)

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)
        self._btn_group.addButton(self.laser_gas_btn)

        layout.addWidget(nav_title)
        layout.addWidget(nav_subtitle)
        layout.addSpacing(12)
        layout.addWidget(self.laser_gas_btn)
        layout.addStretch(1)
