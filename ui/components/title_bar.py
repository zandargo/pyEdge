"""Custom frameless title bar component."""

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
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

        self.window_icon_label = QLabel(self)
        self.window_icon_label.setObjectName("windowIcon")
        self.window_icon_label.setFixedSize(18, 18)

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

        layout.addWidget(self.window_icon_label)
        layout.addWidget(self.window_title_label)
        layout.addStretch(1)
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

    def set_app_icon(self, icon: QIcon) -> None:
        """Render the provided window icon in the custom title bar."""
        if icon.isNull():
            self.window_icon_label.clear()
            return
        pixmap = icon.pixmap(18, 18)
        self.window_icon_label.setPixmap(pixmap)
