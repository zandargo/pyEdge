"""Worker thread for file-search and print operations."""

from __future__ import annotations

import glob
import os
import re
import string
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import QThread, pyqtSignal

PATTERN_FULL = re.compile(r"^(\d{3})-(\d{4})-(\w{2})$", re.IGNORECASE)
PATTERN_PARTIAL = re.compile(r"^(\d{3})-(\d{4})$")


def _list_printers() -> List[str]:
    try:
        import win32print  # type: ignore
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        printers = win32print.EnumPrinters(flags, None, 2)
        return [p["pPrinterName"] for p in printers]
    except (ImportError, OSError, Exception):
        return []


def _list_drives() -> List[str]:
    try:
        import win32api  # type: ignore
        raw = win32api.GetLogicalDriveStrings()
        return [d.rstrip("\\") for d in raw.split("\x00") if d]
    except (ImportError, OSError, Exception):
        return [f"{c}:" for c in string.ascii_uppercase if os.path.exists(f"{c}:\\")]


def _search_preferred(code: str, drive: str) -> List[str]:
    """Search the structured Desenhos folder tree for .dft files matching code."""
    base = os.path.join(drive + "\\", "Desenhos")
    m_full = PATTERN_FULL.match(code)
    m_partial = PATTERN_PARTIAL.match(code)

    if m_full:
        client, part, rev = m_full.group(1), m_full.group(2), m_full.group(3).upper()
        pattern = os.path.join(
            base, f"{client}-*", f"{client}-{part}", f"Rev-{rev}", f"{client}-{part}-{rev}*.dft"
        )
    elif m_partial:
        client, part = m_partial.group(1), m_partial.group(2)
        pattern = os.path.join(
            base, f"{client}-*", f"{client}-{part}", "Rev-*", f"{client}-{part}-*.dft"
        )
    else:
        pattern = os.path.join(base, "**", f"*{code}*.dft")

    return sorted(glob.glob(pattern, recursive=False))


def _search_deep(code: str, drive: str) -> List[str]:
    """Recursive search across the entire drive for .dft files matching code."""
    m_full = PATTERN_FULL.match(code)
    m_partial = PATTERN_PARTIAL.match(code)

    if m_full:
        client, part, rev = m_full.group(1), m_full.group(2), m_full.group(3).upper()
        pattern = os.path.join(drive + "\\", "**", f"{client}-{part}-{rev}*.dft")
    elif m_partial:
        client, part = m_partial.group(1), m_partial.group(2)
        pattern = os.path.join(drive + "\\", "**", f"{client}-{part}-*.dft")
    else:
        pattern = os.path.join(drive + "\\", "**", f"*{code}*.dft")

    return sorted(glob.glob(pattern, recursive=True))


def _print_files(files: List[str], printer: str, copies: int, prop_name: str = "", prop_value: str = "") -> Dict[str, Any]:
    if not files:
        return {"ok": False, "message": "No files selected."}

    from services.solid_edge import print_draft_file  # local import avoids circular risk

    errors: List[str] = []
    for path in files:
        try:
            print_draft_file(path, printer=printer, copies=copies, prop_name=prop_name, prop_value=prop_value)
        except Exception as exc:
            errors.append(f"{os.path.basename(path)}: {exc}")

    if errors:
        return {"ok": False, "message": "Some files failed: " + "; ".join(errors)}
    return {"ok": True, "message": f"Sent {len(files)} file(s) to '{printer or 'default printer'}'."}


class PrintingWorker(QThread):
    """Background worker for printer enumeration, file search, and printing."""

    finished = pyqtSignal(str, dict)

    def __init__(self, action: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.action = action
        self.payload = payload or {}

    def run(self) -> None:
        if self.action == "list_setup":
            self.finished.emit("list_setup", {
                "printers": _list_printers(),
                "drives": _list_drives(),
            })

        elif self.action == "search_files":
            code = self.payload.get("code", "").strip().upper()
            drive = self.payload.get("drive", "P:")
            files = _search_preferred(code, drive)
            self.finished.emit("search_files", {
                "ok": True,
                "files": files,
                "deep_available": len(files) == 0,
            })

        elif self.action == "deep_search":
            code = self.payload.get("code", "").strip().upper()
            drive = self.payload.get("drive", "P:")
            files = _search_deep(code, drive)
            self.finished.emit("deep_search", {
                "ok": True,
                "files": files,
            })

        elif self.action == "print_files":
            result = _print_files(
                self.payload.get("files", []),
                self.payload.get("printer", ""),
                int(self.payload.get("copies", 1)),
                self.payload.get("property", ""),
                self.payload.get("property_value", ""),
            )
            self.finished.emit("print_files", result)
