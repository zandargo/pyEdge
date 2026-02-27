"""Main document workspace panel with dynamic pages by document type."""

from typing import Any, Dict, List, Tuple, Type

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QFrame, QHBoxLayout, QLabel, QScrollArea, QStackedWidget, QVBoxLayout, QWidget


class DocumentPanel(QFrame):
    """Right-side panel that hosts status and document-type pages."""

    def __init__(self, SubtitleLabel: Type, BodyLabel: Type, PushButton: Type, parent=None):
        super().__init__(parent)
        self.setObjectName("mainPanel")

        self._PushButtonClass = PushButton
        self.page_widgets: Dict[str, Dict[str, Any]] = {}
        self.doc_pages: Dict[str, QFrame] = {}
        self.action_buttons: Dict[str, List] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        self.main_title = SubtitleLabel("Document Workspace")
        self.main_title.setObjectName("mainTitle")

        self.connection_label = BodyLabel("")
        self.connection_label.setObjectName("connection")

        self.doc_stack = QStackedWidget(self)
        self.doc_stack.setObjectName("docStack")

        for doc_type in ("Part", "Assembly", "Draft", "Unknown"):
            page = self._build_document_page(doc_type, BodyLabel)
            self.doc_pages[doc_type] = page
            self.doc_stack.addWidget(page)

        self.empty_page = self._build_empty_page(BodyLabel)
        self.doc_stack.addWidget(self.empty_page)

        layout.addWidget(self.main_title)
        layout.addWidget(self.connection_label)
        layout.addSpacing(4)
        layout.addWidget(self.doc_stack, 1)

    def _build_document_page(self, doc_type: str, BodyLabel: Type) -> QFrame:
        page = QFrame(self.doc_stack)
        page.setObjectName("docPage")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)

        title = QLabel(f"{doc_type} Document")
        title.setObjectName("pageTitle")

        subtitles = {
            "Part": "Tools and metadata for standalone model files.",
            "Assembly": "Context for component structures and top-level design files.",
            "Draft": "Drawing view workspace for detailing and annotation files.",
            "Unknown": "Metadata view for documents with an unrecognized type.",
        }
        subtitle = BodyLabel(subtitles.get(doc_type, "Document details."))
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        name_key = QLabel("Name")
        name_key.setObjectName("metaKey")
        name_value = QLabel("-")
        name_value.setObjectName("metaValue")
        name_value.setWordWrap(True)

        path_key = QLabel("Path")
        path_key.setObjectName("metaKey")
        path_value = QLabel("-")
        path_value.setObjectName("metaValue")
        path_value.setWordWrap(True)

        active_key = QLabel("Active in Solid Edge")
        active_key.setObjectName("metaKey")
        active_value = QLabel("-")
        active_value.setObjectName("metaValue")

        custom_props_key = None
        custom_props_scroll = None
        custom_props_panel = None
        custom_props_form = None
        custom_props_hint = None
        if doc_type == "Draft":
            custom_props_key = QLabel("Custom Properties")
            custom_props_key.setObjectName("customPropsTitle")

            custom_props_panel = QFrame(page)
            custom_props_panel.setObjectName("metaValue")

            panel_layout = QVBoxLayout(custom_props_panel)
            panel_layout.setContentsMargins(8, 8, 8, 8)
            panel_layout.setSpacing(6)

            custom_props_hint = QLabel("Loading custom properties...")
            custom_props_hint.setObjectName("pageSubtitle")
            custom_props_hint.setWordWrap(True)

            custom_props_form_host = QWidget(custom_props_panel)
            custom_props_form = QFormLayout(custom_props_form_host)
            custom_props_form.setContentsMargins(0, 0, 0, 0)
            custom_props_form.setSpacing(8)
            custom_props_form.setLabelAlignment(Qt.AlignLeft)
            custom_props_form.setFormAlignment(Qt.AlignTop)

            panel_layout.addWidget(custom_props_hint)
            panel_layout.addWidget(custom_props_form_host)

            custom_props_scroll = QScrollArea(page)
            custom_props_scroll.setObjectName("customPropsScroll")
            custom_props_scroll.setWidgetResizable(True)
            custom_props_scroll.setFrameShape(QFrame.NoFrame)
            custom_props_scroll.setMinimumHeight(200)
            custom_props_scroll.setWidget(custom_props_panel)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        action_buttons = []
        for label, action_key in self.type_action_specs(doc_type):
            action_btn = self._PushButtonClass(label)
            action_btn.setObjectName("secondaryButton")
            action_btn.setProperty("docType", doc_type)
            action_btn.setProperty("actionKey", action_key)
            action_row.addWidget(action_btn)
            action_buttons.append(action_btn)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(6)
        layout.addWidget(name_key)
        layout.addWidget(name_value)
        layout.addWidget(path_key)
        layout.addWidget(path_value)
        layout.addWidget(active_key)
        layout.addWidget(active_value)
        if custom_props_key and custom_props_scroll:
            layout.addWidget(custom_props_key)
            layout.addWidget(custom_props_scroll)
        layout.addSpacing(10)
        layout.addLayout(action_row)
        layout.addStretch(1)

        self.page_widgets[doc_type] = {
            "name": name_value,
            "path": path_value,
            "active": active_value,
        }
        if custom_props_form is not None and custom_props_hint is not None:
            self.page_widgets[doc_type]["custom_props_form"] = custom_props_form
            self.page_widgets[doc_type]["custom_props_hint"] = custom_props_hint
        self.action_buttons[doc_type] = action_buttons
        return page

    def _build_empty_page(self, BodyLabel: Type) -> QFrame:
        page = QFrame(self.doc_stack)
        page.setObjectName("emptyPage")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 18, 18, 18)

        title = QLabel("No Document Selected")
        title.setObjectName("pageTitle")

        self.empty_message = BodyLabel("")
        self.empty_message.setObjectName("pageSubtitle")
        self.empty_message.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(self.empty_message)
        layout.addStretch(1)
        return page

    @staticmethod
    def type_action_specs(doc_type: str) -> List[Tuple[str, str]]:
        by_type = {
            "Part": [
                ("Activate Part", "activate"),
                ("Copy Part Name", "copy_name"),
                ("Open Part Folder", "open_folder"),
            ],
            "Assembly": [
                ("Activate Assembly", "activate"),
                ("Copy Assembly Path", "copy_path"),
                ("Open Assembly Folder", "open_folder"),
            ],
            "Draft": [
                ("Activate Draft", "activate"),
                ("Save Custom Properties", "save_custom_props"),
                ("Copy Draft Path", "copy_path"),
                ("Open Draft Folder", "open_folder"),
            ],
            "Unknown": [
                ("Activate Document", "activate"),
                ("Copy Name", "copy_name"),
                ("Open Folder", "open_folder"),
            ],
        }
        return by_type.get(doc_type, by_type["Unknown"])
