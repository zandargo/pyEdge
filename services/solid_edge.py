import win32com.client


def get_active_document_name():
    """Return the active Solid Edge document name."""
    application = win32com.client.GetActiveObject("SolidEdge.Application")
    document = application.ActiveDocument
    return document.Name
