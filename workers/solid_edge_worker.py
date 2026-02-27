"""Worker thread for Solid Edge COM operations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

from PyQt5.QtCore import QThread, pyqtSignal

from models import DocumentInfo
from services.solid_edge import (
    activate_document_by_full_name,
    diagnose_solid_edge_connection,
    disconnect_from_solid_edge,
    get_open_documents,
)


class WorkerPayload(TypedDict):
    ok: bool
    message: str
    documents: List[DocumentInfo]
    active_name: Optional[str]


class SolidEdgeWorker(QThread):
    """Background worker for connect/refresh/disconnect/activate actions."""

    finished = pyqtSignal(str, dict)

    def __init__(self, action: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.action = action
        self.payload = payload or {}

    def run(self) -> None:
        """Execute COM action off the UI thread and emit a structured payload."""
        if self.action in {"connect", "refresh"}:
            self._handle_connect_or_refresh()
            return

        if self.action == "disconnect":
            self._handle_disconnect()
            return

        if self.action == "activate":
            self._handle_activate()
            return

    def _handle_connect_or_refresh(self) -> None:
        try:
            documents, active_name = get_open_documents()
            message = f"Loaded {len(documents)} open document(s)." if documents else "Connected, but no open documents were found."
            payload: WorkerPayload = {
                "ok": True,
                "message": message,
                "documents": documents,
                "active_name": active_name,
            }
            self.finished.emit(
                self.action,
                payload,
            )
        except Exception:
            diagnostics = {}
            try:
                diagnostics = diagnose_solid_edge_connection()
            except Exception:
                diagnostics = {}

            diagnostic_message = ""
            if diagnostics:
                diagnostic_message = (
                    f" | active={diagnostics.get('active_document') or 'None'}"
                    f", count={diagnostics.get('documents_count')}"
                    f", visible={diagnostics.get('visible')}"
                )

            payload: WorkerPayload = {
                "ok": False,
                "message": f"Error: Solid Edge must be open with at least one active document.{diagnostic_message}",
                "documents": [],
                "active_name": None,
            }
            self.finished.emit(
                self.action,
                payload,
            )

    def _handle_disconnect(self) -> None:
        try:
            disconnect_from_solid_edge()
            payload: WorkerPayload = {
                "ok": True,
                "message": "Disconnected.",
                "documents": [],
                "active_name": None,
            }
            self.finished.emit(
                "disconnect",
                payload,
            )
        except Exception:
            payload: WorkerPayload = {
                "ok": False,
                "message": "Error: Failed to disconnect from Solid Edge.",
                "documents": [],
                "active_name": None,
            }
            self.finished.emit(
                "disconnect",
                payload,
            )

    def _handle_activate(self) -> None:
        try:
            full_name = self.payload.get("full_name")
            name = self.payload.get("name")
            activated = activate_document_by_full_name(full_name, name)
            if not activated:
                payload: WorkerPayload = {
                    "ok": False,
                    "message": "Error: Could not activate the selected document.",
                    "documents": [],
                    "active_name": None,
                }
                self.finished.emit(
                    "activate",
                    payload,
                )
                return

            documents, active_name = get_open_documents()
            payload: WorkerPayload = {
                "ok": True,
                "message": "Selected document activated in Solid Edge.",
                "documents": documents,
                "active_name": active_name,
            }
            self.finished.emit(
                "activate",
                payload,
            )
        except Exception:
            payload: WorkerPayload = {
                "ok": False,
                "message": "Error: Failed to activate document.",
                "documents": [],
                "active_name": None,
            }
            self.finished.emit(
                "activate",
                payload,
            )
