"""Custom frameless title bar component."""

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton


class TitleBar(QFrame):
    """Reusable title bar with window control buttons."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(6)

        self.window_title_label = QLabel("pyEdge", self)
        self.window_title_label.setObjectName("windowTitle")

        self.min_btn = QToolButton(self)
        self.min_btn.setObjectName("minBtn")
        self.min_btn.setFixedSize(42, 30)
        self.min_btn.setToolTip("Minimize")

        self.max_btn = QToolButton(self)
        self.max_btn.setObjectName("maxBtn")
        self.max_btn.setFixedSize(42, 30)

        self.close_btn = QToolButton(self)
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(42, 30)
        self.close_btn.setIconSize(QSize(12, 12))
        self.close_btn.setToolTip("Close")

        layout.addWidget(self.window_title_label)
        layout.addStretch(1)
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)
