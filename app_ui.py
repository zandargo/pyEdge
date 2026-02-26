from PyQt5.QtCore import QEvent, QEasingCurve, QParallelAnimationGroup, QPoint, QPropertyAnimation, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QGraphicsOpacityEffect, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from services.solid_edge import get_active_document_name


class SolidEdgeWorker(QThread):
    finished = pyqtSignal(str)

    def run(self):
        try:
            doc_name = get_active_document_name()
            self.finished.emit(f"Successfully linked to: {doc_name}")
        except Exception:
            self.finished.emit("Error: Solid Edge must be open with an active document.")


class ModernCADApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint, True)

        self._entry_animated = False
        self._entry_animation = None
        self._drag_pos = None

        # Import after QApplication exists to avoid premature QWidget creation.
        from qfluentwidgets import PrimaryPushButton, BodyLabel, SubtitleLabel, setTheme, Theme

        setTheme(Theme.DARK)

        self._build_ui(PrimaryPushButton, BodyLabel, SubtitleLabel)
        self._set_status("ready", "Status: Ready")

        self.action_btn.clicked.connect(self.run_task)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._entry_animated:
            self._start_entry_animation()
            self._entry_animated = True

    def eventFilter(self, obj, event):
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
        self.setObjectName("root")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.title_bar = QFrame(self)
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(42)

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(12, 0, 8, 0)
        title_layout.setSpacing(6)

        self.window_title_label = QLabel("pyEdge", self.title_bar)
        self.window_title_label.setObjectName("windowTitle")

        self.min_btn = QPushButton("_", self.title_bar)
        self.min_btn.setObjectName("winBtn")
        self.min_btn.setFixedSize(34, 26)
        self.min_btn.clicked.connect(self.showMinimized)

        self.max_btn = QPushButton("[]", self.title_bar)
        self.max_btn.setObjectName("winBtn")
        self.max_btn.setFixedSize(34, 26)
        self.max_btn.clicked.connect(self._toggle_maximize)

        self.close_btn = QPushButton("X", self.title_bar)
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(34, 26)
        self.close_btn.clicked.connect(self.close)

        title_layout.addWidget(self.window_title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(self.min_btn)
        title_layout.addWidget(self.max_btn)
        title_layout.addWidget(self.close_btn)

        self.title_bar.installEventFilter(self)
        self.window_title_label.installEventFilter(self)

        outer.addWidget(self.title_bar)

        content = QWidget(self)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 28, 28, 28)

        center = QHBoxLayout()
        center.addStretch(1)

        self.card = QFrame(self)
        self.card.setObjectName("card")
        self.card.setMinimumWidth(520)
        self.card.setMaximumWidth(640)

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

        outer.addWidget(content, 1)

        self.setStyleSheet(
            """
            QWidget#root {
                background-color: qlineargradient(
                    x1: 0,
                    y1: 0,
                    x2: 1,
                    y2: 1,
                    stop: 0 #0a111a,
                    stop: 0.55 #111827,
                    stop: 1 #091019
                );
            }
            QFrame#titleBar {
                background-color: rgba(7, 11, 18, 220);
                border-bottom: 1px solid rgba(255, 255, 255, 18);
            }
            QLabel#windowTitle {
                color: #cfd7e6;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.4px;
            }
            QPushButton#winBtn {
                color: #d4deef;
                background-color: transparent;
                border: 1px solid rgba(255, 255, 255, 28);
                border-radius: 8px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton#winBtn:hover {
                background-color: rgba(255, 255, 255, 16);
            }
            QPushButton#closeBtn {
                color: #ffe4e4;
                background-color: rgba(220, 60, 60, 55);
                border: 1px solid rgba(255, 255, 255, 25);
                border-radius: 8px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton#closeBtn:hover {
                background-color: rgba(230, 75, 75, 95);
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

    def _start_entry_animation(self):
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
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _set_status(self, state, message):
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
        self._set_status("processing", "Status: Processing...")
        self.action_btn.setEnabled(False)
        self.worker = SolidEdgeWorker()
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def _on_worker_finished(self, msg):
        status_state = "success" if msg.startswith("Successfully") else "error"
        self._set_status(status_state, msg)
        self.action_btn.setEnabled(True)
