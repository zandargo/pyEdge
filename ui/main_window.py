"""Main pyEdge window with document navigation and dynamic workspaces."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import (
    QEvent,
    QEasingCurve,
    QObject,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    Qt,
    QTimer,
)
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models import DocumentInfo
from services.solid_edge import disconnect_from_solid_edge
from ui.components import DocumentPanel, NavigationPanel, TitleBar
from ui.styles import APP_STYLESHEET
from workers import SolidEdgeWorker


class ModernCADApp(QWidget):
    """Frameless pyEdge window with a document navbar and dynamic workspace."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._entry_animated: bool = False
        self._entry_animation: Optional[QParallelAnimationGroup] = None
        self._drag_pos: Optional[QPoint] = None

        self._connected: bool = False
        self._documents: List[DocumentInfo] = []
        self._selected_document: Optional[DocumentInfo] = None
        self._selection_key: Optional[str] = None
        self._preferred_selection_key: Optional[str] = None
        self._status_message: str = ""
        self.worker: Optional[SolidEdgeWorker] = None

        from qfluentwidgets import BodyLabel, PrimaryPushButton, PushButton, SubtitleLabel, Theme, setTheme

        setTheme(Theme.DARK)

        self._build_ui(PrimaryPushButton, PushButton, BodyLabel, SubtitleLabel)
        self._set_status("ready", "Status: Ready")
        self._set_connection_indicator()
        self._show_empty_panel("Click Connect to load open Solid Edge documents.")

        self.nav_panel.connect_btn.clicked.connect(self.connect_task)
        self.nav_panel.refresh_btn.clicked.connect(self.refresh_task)
        self.nav_panel.disconnect_btn.clicked.connect(self.disconnect_task)
        self.nav_panel.doc_list.currentItemChanged.connect(self._on_document_changed)

        self._wire_document_actions()

        # Auto-load on startup so users immediately see currently open files.
        QTimer.singleShot(120, self.connect_task)

    def showEvent(self, event: QEvent) -> None:
        super().showEvent(event)
        if not self._entry_animated:
            self._start_entry_animation()
            self._entry_animated = True

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.WindowStateChange:
            self._update_window_chrome()
        super().changeEvent(event)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj in (self.title_bar, self.title_bar.window_title_label):
            if event.type() == QEvent.MouseButtonDblClick and hasattr(event, "button") and event.button() == Qt.LeftButton:
                self._toggle_maximize()
                return True

            if event.type() == QEvent.MouseButtonPress and hasattr(event, "button") and event.button() == Qt.LeftButton:
                self._drag_pos = event.globalPos() if hasattr(event, "globalPos") else None
                return True

            if event.type() == QEvent.MouseMove and self._drag_pos and hasattr(event, "buttons") and event.buttons() & Qt.LeftButton:
                if self.isMaximized():
                    return True
                if not hasattr(event, "globalPos"):
                    return True
                delta = event.globalPos() - self._drag_pos
                self.move(self.pos() + delta)
                self._drag_pos = event.globalPos()
                return True

            if event.type() == QEvent.MouseButtonRelease:
                self._drag_pos = None
                return True

        return super().eventFilter(obj, event)

    def _build_ui(self, PrimaryPushButton: Any, PushButton: Any, BodyLabel: Any, SubtitleLabel: Any) -> None:
        self.setObjectName("root")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

        from PyQt5.QtWidgets import QFrame, QGraphicsOpacityEffect, QHBoxLayout, QWidget as QtWidget

        self.window_frame = QFrame(self)
        self.window_frame.setObjectName("windowFrame")
        self.window_frame.setProperty("maximized", False)

        frame_layout = QVBoxLayout(self.window_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)
        outer.addWidget(self.window_frame)

        self.title_bar = TitleBar(self.window_frame)
        self.title_bar.min_btn.clicked.connect(self.showMinimized)
        self.title_bar.max_btn.clicked.connect(self._toggle_maximize)
        self.title_bar.close_btn.clicked.connect(self.close)
        self.title_bar.installEventFilter(self)
        self.title_bar.window_title_label.installEventFilter(self)
        frame_layout.addWidget(self.title_bar)

        self.workspace_container = QtWidget(self.window_frame)
        workspace_layout = QHBoxLayout(self.workspace_container)
        workspace_layout.setContentsMargins(20, 20, 20, 20)
        workspace_layout.setSpacing(18)

        self._workspace_opacity = QGraphicsOpacityEffect(self.workspace_container)
        self._workspace_opacity.setOpacity(0.0)
        self.workspace_container.setGraphicsEffect(self._workspace_opacity)

        self.nav_panel = NavigationPanel(SubtitleLabel, BodyLabel, PrimaryPushButton, PushButton, self.workspace_container)
        button_font = self.nav_panel.connect_btn.font()
        button_font.setPointSize(10)
        button_font.setBold(True)
        self.nav_panel.connect_btn.setFont(button_font)

        self.doc_panel = DocumentPanel(SubtitleLabel, BodyLabel, PushButton, self.workspace_container)

        workspace_layout.addWidget(self.nav_panel)
        workspace_layout.addWidget(self.doc_panel, 1)

        frame_layout.addWidget(self.workspace_container, 1)

        self.setStyleSheet(APP_STYLESHEET)
        self._update_window_chrome()

    def _wire_document_actions(self) -> None:
        for doc_type, buttons in self.doc_panel.action_buttons.items():
            for button in buttons:
                action_key = str(button.property("actionKey"))
                button.clicked.connect(
                    lambda _=False, t=doc_type, k=action_key: self._run_doc_action(t, k)
                )

    def _start_entry_animation(self) -> None:
        start_pos = self.workspace_container.pos() + QPoint(0, 14)
        end_pos = self.workspace_container.pos()
        self.workspace_container.move(start_pos)

        fade = QPropertyAnimation(self._workspace_opacity, b"opacity", self)
        fade.setDuration(340)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.OutCubic)

        slide = QPropertyAnimation(self.workspace_container, b"pos", self)
        slide.setDuration(360)
        slide.setStartValue(start_pos)
        slide.setEndValue(end_pos)
        slide.setEasingCurve(QEasingCurve.OutCubic)

        self._entry_animation = QParallelAnimationGroup(self)
        self._entry_animation.addAnimation(fade)
        self._entry_animation.addAnimation(slide)
        self._entry_animation.start()

    def _toggle_maximize(self) -> None:
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _update_window_chrome(self) -> None:
        is_maximized = self.isMaximized()
        self.window_frame.setProperty("maximized", is_maximized)

        margin = 0 if is_maximized else 10
        self.layout().setContentsMargins(margin, margin, margin, margin)

        style = self.window_frame.style()
        style.unpolish(self.window_frame)
        style.polish(self.window_frame)
        self._update_titlebar_icons()
        self.window_frame.update()

    def _update_titlebar_icons(self) -> None:
        self.title_bar.min_btn.setText("_")
        self.title_bar.close_btn.setText("")
        self.title_bar.close_btn.setIcon(self._build_close_icon())

        if self.isMaximized():
            self.title_bar.max_btn.setText("[]")
            self.title_bar.max_btn.setToolTip("Restore")
        else:
            self.title_bar.max_btn.setText("[ ]")
            self.title_bar.max_btn.setToolTip("Maximize")

    def _build_close_icon(self) -> QIcon:
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

    def _set_status(self, state: str, message: str) -> None:
        # Keep status text available for potential diagnostics without a visible status card.
        self._status_message = f"{state}: {message}"

    def _set_connection_indicator(self) -> None:
        if self._connected:
            self.doc_panel.connection_label.setText(
                f"Connection: Connected ({len(self._documents)} document(s))"
            )
            self.doc_panel.connection_label.setStyleSheet(
                "color: #34d399;"
                "background-color: rgba(52, 211, 153, 24);"
                "border: 1px solid rgba(52, 211, 153, 70);"
            )
            return

        self.doc_panel.connection_label.setText("Connection: Disconnected")
        self.doc_panel.connection_label.setStyleSheet(
            "color: #8da0bf;"
            "background-color: rgba(255, 255, 255, 8);"
            "border: 1px solid rgba(255, 255, 255, 14);"
        )

    def _show_empty_panel(self, message: str) -> None:
        self.doc_panel.empty_message.setText(message)
        self.doc_panel.doc_stack.setCurrentWidget(self.doc_panel.empty_page)

    def _start_worker(self, action: str, payload: Optional[Dict[str, str]] = None) -> None:
        self.nav_panel.connect_btn.setEnabled(False)
        self.nav_panel.refresh_btn.setEnabled(False)
        self.nav_panel.disconnect_btn.setEnabled(False)
        self.nav_panel.doc_list.setEnabled(False)

        self.worker = SolidEdgeWorker(action, payload)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def connect_task(self) -> None:
        self._set_status("processing", "Status: Connecting and loading documents...")
        self._start_worker("connect")

    def refresh_task(self) -> None:
        self._set_status("processing", "Status: Refreshing document list...")
        self._start_worker("refresh")

    def disconnect_task(self) -> None:
        self._set_status("processing", "Status: Disconnecting...")
        self._start_worker("disconnect")

    def _populate_document_list(self, documents: List[DocumentInfo]) -> None:
        previous_key = self._selection_key
        self.nav_panel.doc_list.clear()
        self.nav_panel.doc_count_label.setText(f"Documents: {len(documents)}")

        for document in documents:
            item = QListWidgetItem(document.list_label)
            item.setForeground(QColor("#d9e3f6"))
            item.setData(Qt.UserRole, document)
            self.nav_panel.doc_list.addItem(item)

        if not documents:
            self._selected_document = None
            self._selection_key = None
            self._preferred_selection_key = None
            self._show_empty_panel("Connected, but no open documents were found.")
            return

        selected_row = self._find_row_by_key(self._preferred_selection_key)
        if selected_row < 0:
            selected_row = self._find_row_by_key(previous_key)
        if selected_row < 0:
            selected_row = 0
            for index, document in enumerate(documents):
                if document.is_active:
                    selected_row = index
                    break

        self.nav_panel.doc_list.setCurrentRow(selected_row)
        self._preferred_selection_key = None

    def _on_document_changed(self, current: Optional[QListWidgetItem], _previous: Optional[QListWidgetItem]) -> None:
        if not current:
            return

        document = current.data(Qt.UserRole)
        self._selected_document = document
        self._selection_key = self._build_document_key(document)
        self._show_document_page(document)

    def _build_document_key(self, document: Optional[DocumentInfo]) -> Optional[str]:
        if not document:
            return None
        return document.selection_key

    def _find_row_by_key(self, key: Optional[str]) -> int:
        if not key:
            return -1

        for row in range(self.nav_panel.doc_list.count()):
            item = self.nav_panel.doc_list.item(row)
            document = item.data(Qt.UserRole) if item else None
            if self._build_document_key(document) == key:
                return row
        return -1

    def _show_document_page(self, document: DocumentInfo) -> None:
        doc_type = document.document_type
        if doc_type not in self.doc_panel.doc_pages:
            doc_type = "Unknown"

        self.doc_panel.main_title.setText(f"Document Workspace - {doc_type}")

        widgets = self.doc_panel.page_widgets[doc_type]
        widgets["name"].setText(document.name)
        widgets["path"].setText(document.full_name)
        widgets["active"].setText("Yes" if document.is_active else "No")

        self.doc_panel.doc_stack.setCurrentWidget(self.doc_panel.doc_pages[doc_type])

    def _copy_document_name(self, doc_type: str) -> None:
        widgets = self.doc_panel.page_widgets.get(doc_type, {})
        value = widgets.get("name")
        text = value.text() if value else ""
        if not text or text == "-":
            self._set_status("error", "Status: No document name to copy.")
            return

        QApplication.clipboard().setText(text)
        self._set_status("success", "Status: Document name copied.")

    def _copy_document_path(self, doc_type: str) -> None:
        widgets = self.doc_panel.page_widgets.get(doc_type, {})
        value = widgets.get("path")
        text = value.text() if value else ""
        if not text or text == "-":
            self._set_status("error", "Status: No document path to copy.")
            return

        QApplication.clipboard().setText(text)
        self._set_status("success", "Status: Document path copied.")

    def _open_document_folder(self, doc_type: str) -> None:
        widgets = self.doc_panel.page_widgets.get(doc_type, {})
        value = widgets.get("path")
        file_path = value.text() if value else ""

        if not file_path or file_path == "-":
            self._set_status("error", "Status: No document path available.")
            return

        folder_path = os.path.dirname(file_path)
        if not folder_path or not os.path.isdir(folder_path):
            self._set_status("error", "Status: Document folder not found.")
            return

        os.startfile(folder_path)
        self._set_status("success", "Status: Document folder opened.")

    def _run_doc_action(self, doc_type: str, action_key: str) -> None:
        if action_key == "copy_name":
            self._copy_document_name(doc_type)
            return

        if action_key == "copy_path":
            self._copy_document_path(doc_type)
            return

        if action_key == "open_folder":
            self._open_document_folder(doc_type)
            return

        if action_key == "activate":
            self._activate_selected_document()

    def _activate_selected_document(self) -> None:
        if not self._selected_document:
            self._set_status("error", "Status: No document selected for activation.")
            return

        self._set_status("processing", "Status: Activating document in Solid Edge...")
        self._preferred_selection_key = self._build_document_key(self._selected_document)
        self._start_worker(
            "activate",
            {
                "full_name": self._selected_document.full_name,
                "name": self._selected_document.name,
            },
        )

    def _on_worker_finished(self, action: str, payload: Dict[str, Any]) -> None:
        is_success = bool(payload.get("ok", False))
        message = str(payload.get("message", ""))

        if action in {"connect", "refresh", "activate"}:
            if is_success:
                self._connected = True
                self._documents = payload.get("documents", [])
                self._populate_document_list(self._documents)
            elif action == "connect":
                self._connected = False
                self._documents = []
                self.nav_panel.doc_list.clear()
                self._show_empty_panel("Could not connect to Solid Edge.")

        elif action == "disconnect" and is_success:
            self._connected = False
            self._documents = []
            self._selected_document = None
            self._selection_key = None
            self._preferred_selection_key = None
            self.nav_panel.doc_list.clear()
            self.nav_panel.doc_count_label.setText("Documents: 0")
            self.doc_panel.main_title.setText("Document Workspace")
            self._show_empty_panel("Click Connect to load open Solid Edge documents.")

        self._set_status("success" if is_success else "error", f"Status: {message}")
        self._set_connection_indicator()

        self.nav_panel.connect_btn.setEnabled(not self._connected)
        self.nav_panel.refresh_btn.setEnabled(self._connected)
        self.nav_panel.disconnect_btn.setEnabled(self._connected)
        self.nav_panel.doc_list.setEnabled(self._connected and bool(self._documents))

        has_selection = self._connected and self._selected_document is not None
        for buttons in self.doc_panel.action_buttons.values():
            for button in buttons:
                button.setEnabled(has_selection)

    def closeEvent(self, event: QEvent) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.wait(2000)

        try:
            disconnect_from_solid_edge()
        except Exception:
            pass

        super().closeEvent(event)
