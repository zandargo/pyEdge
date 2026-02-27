"""Left-side document navigation panel."""

from typing import Type

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

        nav_title = SubtitleLabel("Open Documents")
        nav_title.setObjectName("navTitle")

        nav_subtitle = BodyLabel("Select the current document from Solid Edge.")
        nav_subtitle.setObjectName("navSubtitle")
        nav_subtitle.setWordWrap(True)

        self.doc_count_label = BodyLabel("Documents: 0")
        self.doc_count_label.setObjectName("docCount")

        self.doc_list = QListWidget(self)
        self.doc_list.setObjectName("docList")
        self.doc_list.setMinimumHeight(260)
        self.doc_list.setEnabled(False)

        self.refresh_btn = PushButton("Refresh List")
        self.refresh_btn.setObjectName("secondaryButton")
        self.refresh_btn.setMinimumHeight(38)
        self.refresh_btn.setEnabled(False)

        self.connect_btn = PrimaryPushButton("Connect")
        self.connect_btn.setObjectName("primaryButton")
        self.connect_btn.setMinimumHeight(40)

        self.disconnect_btn = PushButton("Disconnect")
        self.disconnect_btn.setObjectName("secondaryButton")
        self.disconnect_btn.setMinimumHeight(40)
        self.disconnect_btn.setEnabled(False)

        layout.addWidget(nav_title)
        layout.addWidget(nav_subtitle)
        layout.addWidget(self.doc_count_label)
        layout.addSpacing(8)
        layout.addWidget(self.doc_list, 1)
        layout.addWidget(self.refresh_btn)
        layout.addSpacing(8)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.disconnect_btn)
