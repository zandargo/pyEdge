"""Main desktop UI for the pyEdge Solid Edge connector.

This module defines a worker thread for COM calls and a frameless, custom-
drawn Qt window with a modern titlebar and animated content card.
"""

from PyQt5.QtCore import QEvent, QEasingCurve, QParallelAnimationGroup, QPoint, QPropertyAnimation, QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QFrame, QGraphicsOpacityEffect, QHBoxLayout, QLabel, QToolButton, QVBoxLayout, QWidget

from services.solid_edge import get_active_document_name


class SolidEdgeWorker(QThread):
    """Background worker that fetches the active Solid Edge document name."""

    finished = pyqtSignal(str)

    def run(self):
        """Execute COM lookup off the UI thread and emit a user-facing message."""
        try:
            doc_name = get_active_document_name()
            self.finished.emit(f"Successfully linked to: {doc_name}")
        except Exception:
            self.finished.emit("Error: Solid Edge must be open with an active document.")


class ModernCADApp(QWidget):
    """Frameless pyEdge window with custom titlebar, animations, and actions."""

    def __init__(self):
        super().__init__()

        # Window shell setup (frameless + transparent so rounded outer corners work).
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._entry_animated = False
        self._entry_animation = None
        self._drag_pos = None

        # Import after QApplication exists to avoid premature QWidget creation.
        from qfluentwidgets import PrimaryPushButton, BodyLabel, SubtitleLabel, setTheme, Theme

        setTheme(Theme.DARK)

        self._build_ui(PrimaryPushButton, BodyLabel, SubtitleLabel)
        self._set_status("ready", "Status: Ready")

        # Primary action wiring.
        self.action_btn.clicked.connect(self.run_task)

    def showEvent(self, event):
        """Play one-time entry animation when the window first appears."""
        super().showEvent(event)
        if not self._entry_animated:
            self._start_entry_animation()
            self._entry_animated = True

    def changeEvent(self, event):
        """Keep titlebar icons and window corner behavior in sync with state."""
        if event.type() == QEvent.WindowStateChange:
            self._update_window_chrome()
        super().changeEvent(event)

    def eventFilter(self, obj, event):
        """Handle titlebar drag and double-click maximize/restore behavior."""
        if obj in (self.title_bar, self.window_title_label):
            if event.type() == QEvent.MouseButtonDblClick and event.button() == Qt.LeftButton:
                self._toggle_maximize()
                return True

            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self._drag_pos = event.globalPos()
                return True

            if event.type() == QEvent.MouseMove and self._drag_pos and event.buttons() & Qt.LeftButton:
                if self.isMaximized():
                    return True
                delta = event.globalPos() - self._drag_pos
                self.move(self.pos() + delta)
                self._drag_pos = event.globalPos()
                return True

            if event.type() == QEvent.MouseButtonRelease:
                self._drag_pos = None
                return True

        return super().eventFilter(obj, event)

    def _build_ui(self, PrimaryPushButton, BodyLabel, SubtitleLabel):
        """Create the full widget tree and stylesheet for the main window."""
        self.setObjectName("root")

        # Root layout: provides outer margin when window is not maximized.
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

        # Rounded window container; toggled to square corners when maximized.
        self.window_frame = QFrame(self)
        self.window_frame.setObjectName("windowFrame")
        self.window_frame.setProperty("maximized", False)

        frame_layout = QVBoxLayout(self.window_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        outer.addWidget(self.window_frame)

        # --- Titlebar ---
        self.title_bar = QFrame(self.window_frame)
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(42)

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(12, 0, 8, 0)
        title_layout.setSpacing(6)

        self.window_title_label = QLabel("pyEdge", self.title_bar)
        self.window_title_label.setObjectName("windowTitle")

        self.min_btn = QToolButton(self.title_bar)
        self.min_btn.setObjectName("minBtn")
        self.min_btn.setFixedSize(42, 30)
        self.min_btn.setToolTip("Minimize")
        self.min_btn.clicked.connect(self.showMinimized)

        self.max_btn = QToolButton(self.title_bar)
        self.max_btn.setObjectName("maxBtn")
        self.max_btn.setFixedSize(42, 30)
        self.max_btn.clicked.connect(self._toggle_maximize)

        self.close_btn = QToolButton(self.title_bar)
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(42, 30)
        self.close_btn.setIconSize(QSize(12, 12))
        self.close_btn.setToolTip("Close")
        self.close_btn.clicked.connect(self.close)

        title_layout.addWidget(self.window_title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(self.min_btn)
        title_layout.addWidget(self.max_btn)
        title_layout.addWidget(self.close_btn)

        self.title_bar.installEventFilter(self)
        self.window_title_label.installEventFilter(self)

        frame_layout.addWidget(self.title_bar)

        # --- Main content area ---
        content = QWidget(self.window_frame)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 28, 28, 28)

        center = QHBoxLayout()
        center.addStretch(1)

        self.card = QFrame(content)
        self.card.setObjectName("card")
        self.card.setMinimumWidth(520)
        self.card.setMaximumWidth(640)

        # Card fades/slides in on first show.
        self._card_opacity = QGraphicsOpacityEffect(self.card)
        self._card_opacity.setOpacity(0.0)
        self.card.setGraphicsEffect(self._card_opacity)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(28, 26, 28, 26)
        card_layout.setSpacing(12)

        self.title = SubtitleLabel("Solid Edge Connector")
        self.title.setObjectName("title")

        self.subtitle = BodyLabel("Bridge your active Solid Edge document in one click.")
        self.subtitle.setObjectName("subtitle")
        self.subtitle.setWordWrap(True)

        self.status_label = BodyLabel("")
        self.status_label.setObjectName("status")

        self.action_btn = PrimaryPushButton("Scan Active Document")
        self.action_btn.setObjectName("scanButton")
        self.action_btn.setMinimumHeight(44)

        btn_font = QFont()
        btn_font.setPointSize(10)
        btn_font.setBold(True)
        self.action_btn.setFont(btn_font)

        card_layout.addWidget(self.title)
        card_layout.addWidget(self.subtitle)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.status_label)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.action_btn)

        center.addWidget(self.card)
        center.addStretch(1)

        content_layout.addStretch(1)
        content_layout.addLayout(center)
        content_layout.addStretch(1)

        frame_layout.addWidget(content, 1)

        # Centralized stylesheet for shell, titlebar, and content card.
        self.setStyleSheet(
            """
            QWidget#root {
                background: transparent;
            }
            QFrame#windowFrame {
                background-color: qlineargradient(
                    x1: 0,
                    y1: 0,
                    x2: 1,
                    y2: 1,
                    stop: 0 #0a111a,
                    stop: 0.55 #111827,
                    stop: 1 #091019
                );
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 16px;
            }
            QFrame#windowFrame[maximized="true"] {
                border-radius: 0px;
            }
            QFrame#titleBar {
                background-color: rgba(7, 11, 18, 220);
                border-bottom: 1px solid rgba(255, 255, 255, 18);
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }
            QFrame#windowFrame[maximized="true"] QFrame#titleBar {
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
            }
            QLabel#windowTitle {
                color: #cfd7e6;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.4px;
            }
            QToolButton#minBtn,
            QToolButton#maxBtn {
                color: #ffffff;
                background-color: transparent;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                font-family: "Segoe UI";
            }
            QToolButton#minBtn {
                font-size: 18px;
                padding-bottom: 3px;
            }
            QToolButton#maxBtn {
                font-size: 14px;
            }
            QToolButton#minBtn:hover,
            QToolButton#maxBtn:hover {
                background-color: rgba(255, 255, 255, 16);
            }
            QToolButton#minBtn:pressed,
            QToolButton#maxBtn:pressed {
                background-color: rgba(255, 255, 255, 26);
            }
            QToolButton#closeBtn {
                color: #ffffff;
                background-color: transparent;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
                font-family: "Segoe UI";
            }
            QToolButton#closeBtn:hover {
                background-color: rgba(235, 77, 75, 220);
            }
            QToolButton#closeBtn:pressed {
                background-color: rgba(201, 50, 47, 235);
            }
            QFrame#card {
                background-color: rgba(18, 24, 34, 220);
                border: 1px solid rgba(255, 255, 255, 24);
                border-radius: 18px;
            }
            QLabel#title {
                color: #eef4ff;
                font-size: 26px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QLabel#subtitle {
                color: #a3b3ca;
                font-size: 14px;
            }
            QLabel#status {
                font-size: 14px;
                font-weight: 600;
                padding: 8px 12px;
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 12);
            }
            QPushButton#scanButton {
                border-radius: 10px;
                background-color: #2d8cff;
            }
            QPushButton#scanButton:hover {
                background-color: #58a4ff;
            }
            QPushButton#scanButton:pressed {
                background-color: #1f78e0;
            }
            """
        )

        self._update_window_chrome()

    def _start_entry_animation(self):
        """Animate card opacity and vertical position during first paint."""
        start_pos = self.card.pos() + QPoint(0, 14)
        end_pos = self.card.pos()
        self.card.move(start_pos)

        fade = QPropertyAnimation(self._card_opacity, b"opacity", self)
        fade.setDuration(340)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.OutCubic)

        slide = QPropertyAnimation(self.card, b"pos", self)
        slide.setDuration(360)
        slide.setStartValue(start_pos)
        slide.setEndValue(end_pos)
        slide.setEasingCurve(QEasingCurve.OutCubic)

        self._entry_animation = QParallelAnimationGroup(self)
        self._entry_animation.addAnimation(fade)
        self._entry_animation.addAnimation(slide)
        self._entry_animation.start()

    def _toggle_maximize(self):
        """Toggle between maximized and normal states from titlebar controls."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _update_window_chrome(self):
        """Apply window-state-dependent chrome (margins, corners, icons)."""
        is_maximized = self.isMaximized()
        self.window_frame.setProperty("maximized", is_maximized)

        margin = 0 if is_maximized else 10
        self.layout().setContentsMargins(margin, margin, margin, margin)

        style = self.window_frame.style()
        style.unpolish(self.window_frame)
        style.polish(self.window_frame)
        self._update_titlebar_icons()
        self.window_frame.update()

    def _update_titlebar_icons(self):
        """Use text symbols for full control over color and size."""
        self.min_btn.setText("_")
        self.close_btn.setText("")
        self.close_btn.setIcon(self._build_close_icon())

        if self.isMaximized():
            self.max_btn.setText("❐")
            self.max_btn.setToolTip("Restore")
        else:
            self.max_btn.setText("□")
            self.max_btn.setToolTip("Maximize")

    def _build_close_icon(self):
        """Create a crisp, anti-aliased close icon independent of font rendering."""
        size = 12
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(Qt.white)
        pen.setWidthF(1.6)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        margin = 2.3
        painter.drawLine(QPoint(int(margin), int(margin)), QPoint(int(size - margin), int(size - margin)))
        painter.drawLine(QPoint(int(size - margin), int(margin)), QPoint(int(margin), int(size - margin)))
        painter.end()

        return QIcon(pixmap)

    def _set_status(self, state, message):
        """Render status text with state-specific accent colors."""
        colors = {
            "ready": "#8da0bf",
            "processing": "#fbbf24",
            "success": "#34d399",
            "error": "#f87171",
        }
        self.status_label.setText(message)
        self.status_label.setStyleSheet(
            f"color: {colors.get(state, '#8da0bf')};"
            "background-color: rgba(255, 255, 255, 10);"
            "border: 1px solid rgba(255, 255, 255, 18);"
        )

    def run_task(self):
        """Start document lookup in worker thread and lock UI action button."""
        self._set_status("processing", "Status: Processing...")
        self.action_btn.setEnabled(False)
        self.worker = SolidEdgeWorker()
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def _on_worker_finished(self, msg):
        """Update status from worker result and re-enable action button."""
        status_state = "success" if msg.startswith("Successfully") else "error"
        self._set_status(status_state, msg)
        self.action_btn.setEnabled(True)
