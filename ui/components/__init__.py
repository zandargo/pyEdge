"""Composable UI building blocks for the main pyEdge window."""

from .document_panel import DocumentPanel
from .navigation_panel import NavigationPanel
from .title_bar import TitleBar
from .utilities_nav_panel import UtilitiesNavPanel
from .printing_panel import PrintingPanel

__all__ = ["TitleBar", "NavigationPanel", "DocumentPanel", "UtilitiesNavPanel", "PrintingPanel"]
