"""Left-side navigation panel for the Utilities section."""

from typing import Type

from PyQt5.QtCore import QEvent, QSize
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

        self._nav_title = SubtitleLabel()
        self._nav_title.setObjectName("navTitle")

        self._nav_subtitle = BodyLabel()
        self._nav_subtitle.setObjectName("navSubtitle")
        self._nav_subtitle.setWordWrap(True)

        try:
            from qfluentwidgets import FluentIcon
            self.printing_btn = QPushButton()
            self.printing_btn.setIcon(FluentIcon.PRINT.icon())
            self.printing_btn.setIconSize(QSize(16, 16))
        except (ImportError, AttributeError):
            self.printing_btn = QPushButton()

        self.printing_btn.setObjectName("utilNavButton")
        self.printing_btn.setCheckable(True)
        self.printing_btn.setChecked(True)
        self.printing_btn.setMinimumHeight(42)

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)
        self._btn_group.addButton(self.printing_btn)

        layout.addWidget(self._nav_title)
        layout.addWidget(self._nav_subtitle)
        layout.addSpacing(12)
        layout.addWidget(self.printing_btn)
        layout.addStretch(1)

        self.retranslateUi()

    # ── i18n ─────────────────────────────────────────────────────────────────

    def retranslateUi(self) -> None:
        self._nav_title.setText(self.tr("Utilities"))
        self._nav_subtitle.setText(self.tr("Select a utility tool."))
        self.printing_btn.setText("  " + self.tr("Printing"))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
