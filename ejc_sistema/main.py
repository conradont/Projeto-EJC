"""Ponto de entrada do sistema EJC"""
import sys
from PyQt6.QtWidgets import QApplication, QStyleFactory
from ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

