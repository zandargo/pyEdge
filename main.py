import sys
from pathlib import Path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from ui import ModernCADApp

if __name__ == "__main__":
    app = QApplication(sys.argv)

    icon_path = Path(__file__).resolve().parent / "assets" / "icons" / "pyEdge001.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    w = ModernCADApp()
    if icon_path.exists():
        w.setWindowIcon(QIcon(str(icon_path)))
    w.resize(1180, 760)
    w.show()
    app.exec()