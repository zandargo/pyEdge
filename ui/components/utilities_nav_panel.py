"""Left-side navigation panel for the Utilities section."""

from typing import Type

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QButtonGroup, QFrame, QPushButton, QVBoxLayout


class UtilitiesNavPanel(QFrame):
    """Navbar panel with utility tool buttons."""

    def __init__(self, SubtitleLabel: Type, BodyLabel: Type, PushButton: Type, parent=None):
        super().__init__(parent)
        self.setObjectName("navPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        nav_title = SubtitleLabel("Utilities")
        nav_title.setObjectName("navTitle")

        nav_subtitle = BodyLabel("Select a utility tool.")
        nav_subtitle.setObjectName("navSubtitle")
        nav_subtitle.setWordWrap(True)

        try:
            from qfluentwidgets import FluentIcon
            self.printing_btn = QPushButton("  Printing")
            self.printing_btn.setIcon(FluentIcon.PRINT.icon())
            self.printing_btn.setIconSize(QSize(16, 16))
        except (ImportError, AttributeError):
            self.printing_btn = QPushButton("  Printing")

        self.printing_btn.setObjectName("utilNavButton")
        self.printing_btn.setCheckable(True)
        self.printing_btn.setChecked(True)
        self.printing_btn.setMinimumHeight(42)

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)
        self._btn_group.addButton(self.printing_btn)

        layout.addWidget(nav_title)
        layout.addWidget(nav_subtitle)
        layout.addSpacing(12)
        layout.addWidget(self.printing_btn)
        layout.addStretch(1)
