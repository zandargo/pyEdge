"""Worker thread for Solid Edge COM operations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

from PyQt5.QtCore import QThread, pyqtSignal

from models import DocumentInfo
from services.solid_edge import (
    activate_document_by_full_name,
    diagnose_solid_edge_connection,
    disconnect_from_solid_edge,
    get_draft_custom_properties,
    get_open_documents,
    set_active_draft_custom_properties,
)


class WorkerPayload(TypedDict, total=False):
    ok: bool
    message: str
    documents: List[DocumentInfo]
    active_name: Optional[str]
    custom_properties: List[Dict[str, Any]]
    selection_key: Optional[str]


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

        if self.action == "draft_custom_properties":
            self._handle_draft_custom_properties()
            return

        if self.action == "save_draft_custom_properties":
            self._handle_save_draft_custom_properties()
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

    def _handle_draft_custom_properties(self) -> None:
        try:
            full_name = self.payload.get("full_name")
            name = self.payload.get("name")
            selection_key = self.payload.get("selection_key")

            custom_properties = get_draft_custom_properties(full_name, name)
            payload: WorkerPayload = {
                "ok": True,
                "message": "Loaded draft custom properties.",
                "documents": [],
                "active_name": None,
                "custom_properties": custom_properties,
                "selection_key": selection_key,
            }
            self.finished.emit("draft_custom_properties", payload)
        except Exception:
            payload: WorkerPayload = {
                "ok": False,
                "message": "Failed to load draft custom properties.",
                "documents": [],
                "active_name": None,
                "custom_properties": {},
                "selection_key": self.payload.get("selection_key"),
            }
            self.finished.emit("draft_custom_properties", payload)

    def _handle_save_draft_custom_properties(self) -> None:
        try:
            full_name = self.payload.get("full_name")
            name = self.payload.get("name")
            properties = self.payload.get("custom_properties") or []

            saved = set_active_draft_custom_properties(full_name, name, properties)
            payload: WorkerPayload = {
                "ok": bool(saved),
                "message": "Draft custom properties saved." if saved else "Draft must be active to save custom properties.",
                "documents": [],
                "active_name": None,
            }
            self.finished.emit("save_draft_custom_properties", payload)
        except Exception:
            payload: WorkerPayload = {
                "ok": False,
                "message": "Failed to save draft custom properties.",
                "documents": [],
                "active_name": None,
            }
            self.finished.emit("save_draft_custom_properties", payload)
