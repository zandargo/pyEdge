"""Left-side document navigation panel."""

from typing import Type

from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QFrame, QListWidget, QVBoxLayout


class NavigationPanel(QFrame):
    """Navbar-like panel with document list and connection controls."""

    def __init__(self, SubtitleLabel: Type, BodyLabel: Type, PrimaryPushButton: Type, PushButton: Type, parent=None):
        super().__init__(parent)
        self.setObjectName("navPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self._nav_title = SubtitleLabel()
        self._nav_title.setObjectName("navTitle")

        self._nav_subtitle = BodyLabel()
        self._nav_subtitle.setObjectName("navSubtitle")
        self._nav_subtitle.setWordWrap(True)

        self.doc_count_label = BodyLabel()
        self.doc_count_label.setObjectName("docCount")
        self._doc_count: int = 0

        self.doc_list = QListWidget(self)
        self.doc_list.setObjectName("docList")
        self.doc_list.setMinimumHeight(260)
        self.doc_list.setEnabled(False)

        self.refresh_btn = PushButton()
        self.refresh_btn.setObjectName("secondaryButton")
        self.refresh_btn.setMinimumHeight(38)
        self.refresh_btn.setEnabled(False)

        self.connect_btn = PrimaryPushButton()
        self.connect_btn.setObjectName("primaryButton")
        self.connect_btn.setMinimumHeight(40)

        self.disconnect_btn = PushButton()
        self.disconnect_btn.setObjectName("secondaryButton")
        self.disconnect_btn.setMinimumHeight(40)
        self.disconnect_btn.setEnabled(False)

        layout.addWidget(self._nav_title)
        layout.addWidget(self._nav_subtitle)
        layout.addWidget(self.doc_count_label)
        layout.addSpacing(8)
        layout.addWidget(self.doc_list, 1)
        layout.addWidget(self.refresh_btn)
        layout.addSpacing(8)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.disconnect_btn)

        self.retranslateUi()

    # ── i18n ─────────────────────────────────────────────────────────────────

    def set_doc_count(self, count: int) -> None:
        """Update the document count label with the given count."""
        self._doc_count = count
        self.doc_count_label.setText(self.tr("Documents: {0}").format(count))

    def retranslateUi(self) -> None:
        self._nav_title.setText(self.tr("Open Documents"))
        self._nav_subtitle.setText(self.tr("Select the current document from Solid Edge."))
        self.doc_count_label.setText(self.tr("Documents: {0}").format(self._doc_count))
        self.refresh_btn.setText(self.tr("Refresh List"))
        self.connect_btn.setText(self.tr("Connect"))
        self.disconnect_btn.setText(self.tr("Disconnect"))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
