import gc
import os
from datetime import date, datetime
from typing import Any, Optional, Tuple

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


def _iter_com_collection(collection):
    """Yield items from COM collections with iterator or Count/Item fallback."""
    if collection is None:
        return

    try:
        for item in collection:
            yield item
        return
    except Exception:
        pass

    count = int(getattr(collection, "Count", 0) or 0)
    for index in range(1, count + 1):
        try:
            yield collection.Item(index)
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


def _serialize_date_value(value: Any) -> str:
    """Serialize COM date-like values to a stable yyyy-MM-dd string."""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")

    text = str(value or "").strip()
    if not text:
        return ""
    return text.split(" ", 1)[0].split("T", 1)[0]


def _infer_custom_property_type(value: Any) -> str:
    """Infer UI editor type from COM property value."""
    if isinstance(value, bool):
        return "Boolean"
    if isinstance(value, (int, float)):
        return "Number"
    if isinstance(value, (datetime, date)):
        return "Date"

    text = str(value or "").strip()
    if text:
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                datetime.strptime(text.split("T", 1)[0], fmt)
                return "Date"
            except Exception:
                continue
    return "Text"


def _read_document_custom_properties(document) -> list[dict[str, Any]]:
    """Read user custom properties with inferred value types."""
    properties = getattr(document, "Properties", None)
    if properties is None:
        return []

    custom_set = None
    for prop_set in _iter_com_collection(properties):
        set_name = str(getattr(prop_set, "Name", "")).strip().lower()
        if "custom" in set_name:
            custom_set = prop_set
            break

    if custom_set is None:
        try:
            custom_set = properties.Item("Custom")
        except Exception:
            custom_set = None

    if custom_set is None:
        return []

    custom_props: list[dict[str, Any]] = []
    for prop in _iter_com_collection(custom_set):
        key = str(getattr(prop, "Name", "")).strip()
        if not key:
            continue
        value = getattr(prop, "Value", "")
        prop_type = _infer_custom_property_type(value)
        normalized_value: Any = "" if value is None else value
        if prop_type == "Date":
            normalized_value = _serialize_date_value(normalized_value)

        custom_props.append(
            {
                "name": key,
                "type": prop_type,
                "value": normalized_value,
            }
        )

    custom_props.sort(key=lambda item: str(item.get("name", "")).lower())
    return custom_props


def _get_custom_property_set(document):
    """Return the custom property set COM object for a document, if available."""
    properties = getattr(document, "Properties", None)
    if properties is None:
        return None

    for prop_set in _iter_com_collection(properties):
        set_name = str(getattr(prop_set, "Name", "")).strip().lower()
        if "custom" in set_name:
            return prop_set

    try:
        return properties.Item("Custom")
    except Exception:
        return None


def get_draft_custom_properties(target_full_name: Optional[str], target_name: Optional[str] = None) -> list[dict[str, Any]]:
    """Return custom properties for a selected Draft document by path/name."""
    pythoncom.CoInitialize()
    try:
        application = win32com.client.GetActiveObject("SolidEdge.Application")
        wanted_full = _path_key(target_full_name)
        wanted_name = str(target_name or "").strip().lower()

        for document in _iter_documents(application):
            try:
                full_name = _path_key(getattr(document, "FullName", ""))
                name = str(getattr(document, "Name", "")).strip().lower()
                doc_type = _resolve_document_type(document, full_name, name)

                if doc_type != "Draft":
                    continue

                matches_full = bool(wanted_full and full_name and full_name == wanted_full)
                matches_name = bool(not wanted_full and wanted_name and name == wanted_name)
                if not (matches_full or matches_name):
                    continue

                custom_props = _read_document_custom_properties(document)
                del document
                del application
                gc.collect()
                pythoncom.CoFreeUnusedLibraries()
                return custom_props
            finally:
                try:
                    del document
                except Exception:
                    pass

        del application
        gc.collect()
        pythoncom.CoFreeUnusedLibraries()
        return []
    finally:
        pythoncom.CoUninitialize()


def _coerce_custom_property_value(raw_value: Any, prop_type: str) -> Any:
    """Convert UI values back to COM-compatible primitive values."""
    if prop_type == "Boolean":
        if isinstance(raw_value, bool):
            return raw_value
        return str(raw_value or "").strip().lower() in {"1", "true", "yes", "y", "on"}

    if prop_type == "Number":
        try:
            return float(raw_value)
        except Exception:
            return 0.0

    if prop_type == "Date":
        if isinstance(raw_value, (datetime, date)):
            return raw_value
        text = str(raw_value or "").strip()
        if not text:
            return ""
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(text, fmt)
            except Exception:
                continue
        return text

    return "" if raw_value is None else str(raw_value)


def set_active_draft_custom_properties(
    target_full_name: Optional[str],
    target_name: Optional[str],
    custom_properties: list[dict[str, Any]],
) -> bool:
    """Update custom properties only when the selected Draft is currently active."""
    pythoncom.CoInitialize()
    try:
        application = win32com.client.GetActiveObject("SolidEdge.Application")
        active_document = getattr(application, "ActiveDocument", None)

        active_full_name = _path_key(getattr(active_document, "FullName", ""))
        active_name = str(getattr(active_document, "Name", "")).strip().lower()
        wanted_full = _path_key(target_full_name)
        wanted_name = str(target_name or "").strip().lower()

        for document in _iter_documents(application):
            try:
                full_name = _path_key(getattr(document, "FullName", ""))
                name = str(getattr(document, "Name", "")).strip().lower()
                doc_type = _resolve_document_type(document, full_name, name)

                matches_full = bool(wanted_full and full_name and full_name == wanted_full)
                matches_name = bool(not wanted_full and wanted_name and name == wanted_name)
                is_active = bool((active_full_name and full_name == active_full_name) or (active_name and name == active_name))

                if doc_type != "Draft" or not (matches_full or matches_name) or not is_active:
                    continue

                custom_set = _get_custom_property_set(document)
                if custom_set is None:
                    return False

                for entry in custom_properties:
                    clean_key = str(entry.get("name", "")).strip()
                    if not clean_key:
                        continue

                    prop_type = str(entry.get("type", "Text") or "Text")
                    raw_value = entry.get("value", "")
                    typed_value = _coerce_custom_property_value(raw_value, prop_type)
                    try:
                        prop = custom_set.Item(clean_key)
                        prop.Value = typed_value
                    except Exception:
                        custom_set.Add(clean_key, typed_value)

                del document
                del active_document
                del application
                gc.collect()
                pythoncom.CoFreeUnusedLibraries()
                return True
            finally:
                try:
                    del document
                except Exception:
                    pass

        del active_document
        del application
        gc.collect()
        pythoncom.CoFreeUnusedLibraries()
        return False
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
