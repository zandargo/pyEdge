"""Custom frameless title bar component with vector icons."""

from pathlib import Path
from PyQt5.QtCore import QEvent, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton


class TitleBar(QFrame):
    """Reusable title bar with window control buttons using vector icons."""

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

        # Load vector icons from SVG files
        icons_dir = Path(__file__).parent.parent.parent / "assets" / "icons"
        minimize_icon = QIcon(str(icons_dir / "minimize.svg"))
        maximize_icon = QIcon(str(icons_dir / "maximize.svg"))
        close_icon = QIcon(str(icons_dir / "close.svg"))

        # Create window control buttons with vector icons
        self.min_btn = QToolButton(self)
        self.min_btn.setObjectName("minBtn")
        self.min_btn.setIcon(minimize_icon)
        self.min_btn.setFixedSize(42, 30)
        self.min_btn.setIconSize(QSize(16, 16))

        self.max_btn = QToolButton(self)
        self.max_btn.setObjectName("maxBtn")
        self.max_btn.setIcon(maximize_icon)
        self._maximize_icon = maximize_icon
        self._restore_icon = QIcon(str(icons_dir / "restore.svg"))
        self.max_btn.setFixedSize(42, 30)
        self.max_btn.setIconSize(QSize(16, 16))

        self.close_btn = QToolButton(self)
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setIcon(close_icon)
        self.close_btn.setFixedSize(42, 30)
        self.close_btn.setIconSize(QSize(16, 16))

        layout.addWidget(self.window_icon_label)
        layout.addWidget(self.window_title_label)
        layout.addStretch(1)
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        self.retranslateUi()

    # ── i18n ───────────────────────────────────────────────────────────────

    def retranslateUi(self) -> None:
        self.min_btn.setToolTip(self.tr("Minimize"))
        self.max_btn.setToolTip(self.tr("Maximize"))
        self.close_btn.setToolTip(self.tr("Close"))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def set_maximize_state(self, is_maximized: bool) -> None:
        """Update the maximize button icon and tooltip based on window state."""
        if is_maximized:
            self.max_btn.setIcon(self._restore_icon)
            self.max_btn.setToolTip(self.tr("Restore"))
        else:
            self.max_btn.setIcon(self._maximize_icon)
            self.max_btn.setToolTip(self.tr("Maximize"))

    def set_app_icon(self, icon: QIcon) -> None:
        """Render the provided window icon in the custom title bar."""
        if icon.isNull():
            self.window_icon_label.clear()
            return
        pixmap = icon.pixmap(18, 18)
        self.window_icon_label.setPixmap(pixmap)
