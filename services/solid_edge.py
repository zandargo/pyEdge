import gc

import pythoncom
import win32com.client


def get_active_document_name():
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


def disconnect_from_solid_edge():
    """Force COM cleanup for any lingering Solid Edge references."""
    pythoncom.CoInitialize()
    try:
        gc.collect()
        pythoncom.CoFreeUnusedLibraries()
    finally:
        pythoncom.CoUninitialize()
