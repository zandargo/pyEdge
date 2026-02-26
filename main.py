import sys
from PyQt5.QtWidgets import QApplication

from app_ui import ModernCADApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Using a standard window to house our modern widget
    w = ModernCADApp()
    w.resize(400, 300)
    w.show()
    app.exec()