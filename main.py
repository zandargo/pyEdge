import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication

from translations import get_saved_locale, install_translator
from ui import ModernCADApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configure application-level font anti-aliasing
    default_font = app.font()
    default_font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(default_font)
    
    # Set high DPI awareness for better rendering
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # Install the saved locale translator before any UI is created.
    install_translator(get_saved_locale())

    icon_path = Path(__file__).resolve().parent / "assets" / "icons" / "pyEdge001.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    w = ModernCADApp()
    if icon_path.exists():
        w.setWindowIcon(QIcon(str(icon_path)))
    w.resize(1180, 760)
    w.show()
    app.exec()