"""Qt i18n translation management for pyEdge."""

from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import QCoreApplication, QSettings, QTranslator

_TRANSLATIONS_DIR = Path(__file__).parent

# Locales listed in display order for the Settings UI.
SUPPORTED_LOCALES: list[tuple[str, str]] = [
    ("en_US", "English (United States)"),
    ("pt_BR", "Português (Brasil)"),
]

_current_translator: QTranslator | None = None


def get_saved_locale() -> str:
    """Return the last saved locale code (defaults to 'en_US')."""
    settings = QSettings("pyEdge", "pyEdge")
    return str(settings.value("language/locale", "en_US"))


def save_locale(locale: str) -> None:
    """Persist the chosen locale code to QSettings."""
    settings = QSettings("pyEdge", "pyEdge")
    settings.setValue("language/locale", locale)


def install_translator(locale: str) -> bool:
    """Load and install the translator for *locale*.

    English (en_US) is the source language – removing any active translator
    reverts to the default strings.  Returns True on success.
    """
    global _current_translator

    app = QCoreApplication.instance()
    if app is None:
        return False

    # Remove the previous translator first.
    if _current_translator is not None:
        app.removeTranslator(_current_translator)
        _current_translator = None

    # English is the base language; no .qm file needed.
    if locale == "en_US":
        return True

    translator = QTranslator(app)
    qm_path = str(_TRANSLATIONS_DIR / f"pyedge_{locale}.qm")
    if translator.load(qm_path):
        app.installTranslator(translator)
        _current_translator = translator
        return True

    return False
