import gc
import os
from typing import Optional, Tuple

import pythoncom
import win32com.client

from models import DocumentInfo


def _iter_documents(application):
    """Yield open document COM objects across different collection interfaces."""
    documents_collection = getattr(application, "Documents", None)
    if documents_collection is None:
        return

    # Preferred path when the COM collection supports Python iteration.
    try:
        for document in documents_collection:
            yield document
        return
    except Exception:
        pass

    # Fallback path for COM collections that only expose Count/Item(1-based).
    count = int(getattr(documents_collection, "Count", 0) or 0)
    for index in range(1, count + 1):
        try:
            yield documents_collection.Item(index)
        except Exception:
            continue


def _resolve_document_type(document, full_name: str, display_name: str) -> str:
    """Infer a stable document type label from COM fields and file extension."""
    extension = os.path.splitext(full_name or display_name)[1].lower()
    if extension in {".par", ".psm"}:
        return "Part"
    if extension == ".asm":
        return "Assembly"
    if extension == ".dft":
        return "Draft"

    raw_type = getattr(document, "Type", None)

    # Fallback only when extension is unavailable/unknown.
    type_map = {
        1: "Part",
        2: "Assembly",
        3: "Draft",
    }
    if raw_type in type_map:
        return type_map[raw_type]
    return "Unknown"


def get_open_documents() -> Tuple[list[DocumentInfo], Optional[str]]:
    """Return all open Solid Edge documents with active flag and normalized type."""
    pythoncom.CoInitialize()
    try:
        application = win32com.client.GetActiveObject("SolidEdge.Application")
        active_document = getattr(application, "ActiveDocument", None)

        active_name = getattr(active_document, "Name", None)
        active_full_name = getattr(active_document, "FullName", None)

        documents = []
        for document in _iter_documents(application):
            try:
                name = getattr(document, "Name", "Untitled")
                full_name = getattr(document, "FullName", name)
                doc_type = _resolve_document_type(document, full_name, name)
                is_active = (
                    (active_full_name and full_name == active_full_name)
                    or (active_name and name == active_name)
                )

                documents.append(
                    DocumentInfo(
                        name=name,
                        full_name=full_name,
                        document_type=doc_type,
                        is_active=bool(is_active),
                    )
                )
            finally:
                del document

        # Some Solid Edge sessions expose only ActiveDocument but a non-enumerable
        # Documents collection; keep UI usable by surfacing the active file.
        if not documents and active_document is not None:
            fallback_name = getattr(active_document, "Name", "Untitled")
            fallback_full_name = getattr(active_document, "FullName", fallback_name)
            documents.append(
                DocumentInfo(
                    name=fallback_name,
                    full_name=fallback_full_name,
                    document_type=_resolve_document_type(active_document, fallback_full_name, fallback_name),
                    is_active=True,
                )
            )

        documents.sort(key=lambda item: (not item.is_active, item.name.lower()))

        del active_document
        del application
        gc.collect()
        pythoncom.CoFreeUnusedLibraries()
        return documents, active_name
    finally:
        pythoncom.CoUninitialize()


def _path_key(value) -> str:
    """Normalize path-like values for robust COM document matching."""
    if not value:
        return ""
    return os.path.normcase(str(value)).strip()


def activate_document_by_full_name(target_full_name: Optional[str], target_name: Optional[str] = None) -> bool:
    """Activate one open Solid Edge document by full path, falling back to name."""
    pythoncom.CoInitialize()
    try:
        application = win32com.client.GetActiveObject("SolidEdge.Application")
        wanted_full = _path_key(target_full_name)
        wanted_name = str(target_name or "").strip().lower()

        for document in _iter_documents(application):
            try:
                full_name = _path_key(getattr(document, "FullName", ""))
                name = str(getattr(document, "Name", "")).strip().lower()

                matches_full = bool(wanted_full and full_name and full_name == wanted_full)
                matches_name = bool(not wanted_full and wanted_name and name == wanted_name)
                if matches_full or matches_name:
                    document.Activate()
                    del document
                    del application
                    gc.collect()
                    pythoncom.CoFreeUnusedLibraries()
                    return True
            finally:
                try:
                    del document
                except Exception:
                    pass

        del application
        gc.collect()
        pythoncom.CoFreeUnusedLibraries()
        return False
    finally:
        pythoncom.CoUninitialize()


def get_active_document_name() -> str:
    """Return the active Solid Edge document name and release COM references."""
    pythoncom.CoInitialize()
    try:
        application = win32com.client.GetActiveObject("SolidEdge.Application")
        document = application.ActiveDocument
        document_name = document.Name

        # Explicit release helps avoid keeping the document locked by COM proxies.
        del document
        del application
        gc.collect()
        pythoncom.CoFreeUnusedLibraries()
        return document_name
    finally:
        pythoncom.CoUninitialize()


def disconnect_from_solid_edge() -> None:
    """Force COM cleanup for any lingering Solid Edge references."""
    pythoncom.CoInitialize()
    try:
        gc.collect()
        pythoncom.CoFreeUnusedLibraries()
    finally:
        pythoncom.CoUninitialize()


def diagnose_solid_edge_connection() -> dict:
    """Return lightweight diagnostics for troubleshooting COM visibility issues."""
    pythoncom.CoInitialize()
    try:
        application = win32com.client.GetActiveObject("SolidEdge.Application")
        active_document = getattr(application, "ActiveDocument", None)

        count_value = None
        try:
            count_value = int(getattr(application.Documents, "Count", -1))
        except Exception:
            count_value = -1

        diagnostics = {
            "active_document": getattr(active_document, "Name", None),
            "documents_count": count_value,
            "visible": bool(getattr(application, "Visible", False)),
        }

        del active_document
        del application
        gc.collect()
        pythoncom.CoFreeUnusedLibraries()
        return diagnostics
    finally:
        pythoncom.CoUninitialize()
