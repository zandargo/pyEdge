import sys
from PyQt5.QtWidgets import QApplication

from ui import ModernCADApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ModernCADApp()
    w.resize(1180, 760)
    w.show()
    app.exec()