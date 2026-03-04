"""Settings panel – language selector and app preferences."""

from __future__ import annotations

from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QComboBox, QFrame, QLabel, QVBoxLayout

from translations import SUPPORTED_LOCALES, get_saved_locale, install_translator, save_locale


class SettingsPanel(QFrame):
    """Panel that exposes application-level settings (language, etc.)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("mainPanel")

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────────
        self._title_lbl = QLabel()
        self._title_lbl.setObjectName("mainTitle")
        root.addWidget(self._title_lbl)
        root.addSpacing(22)

        # ── Language card ────────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("printCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 18)
        card_layout.setSpacing(10)

        self._lang_section = QLabel()
        self._lang_section.setObjectName("printSectionLabel")
        card_layout.addWidget(self._lang_section)

        self._lang_desc = QLabel()
        self._lang_desc.setObjectName("pageSubtitle")
        self._lang_desc.setWordWrap(True)
        card_layout.addWidget(self._lang_desc)

        self.lang_combo = QComboBox()
        self.lang_combo.setObjectName("gasCombo")
        self.lang_combo.setMinimumHeight(36)
        for locale, display in SUPPORTED_LOCALES:
            self.lang_combo.addItem(display, locale)

        # Pre-select the currently saved locale.
        saved = get_saved_locale()
        for i in range(self.lang_combo.count()):
            if self.lang_combo.itemData(i) == saved:
                self.lang_combo.setCurrentIndex(i)
                break

        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        card_layout.addWidget(self.lang_combo)

        root.addWidget(card)
        root.addStretch(1)

        self.retranslateUi()

    # ── i18n ─────────────────────────────────────────────────────────────────

    def retranslateUi(self) -> None:
        self._title_lbl.setText(self.tr("Settings"))
        self._lang_section.setText(self.tr("Interface Language"))
        self._lang_desc.setText(self.tr("Changes take effect immediately."))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_language_changed(self, index: int) -> None:
        locale = self.lang_combo.itemData(index)
        if locale:
            save_locale(locale)
            install_translator(locale)
