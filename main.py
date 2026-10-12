import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

try:
    from .database import DB
    from .main_window import MainWindow
except ImportError:
    from database import DB
    from main_window import MainWindow

if getattr(sys, "frozen", False):
    DB_PATH = Path(sys.executable).parent / "tutoring.db"
else:
    DB_PATH = Path(__file__).resolve().parent / "tutoring.db"


def main():
    app = QApplication(sys.argv)
    db = DB(DB_PATH)
    w = MainWindow(db)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
