"""Run with python app.py. All gameplay is available offline."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / '.deps'))
from PySide6.QtWidgets import QApplication
from pc_build_battle.database import Database
from pc_build_battle.ui.main_window import MainWindow
from pc_build_battle.ui.theme import THEME


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('PC Build Battle')
    app.setOrganizationName('PCBuildBattle')
    app.setStyle('Fusion')
    app.setStyleSheet(THEME)
    db = Database()
    window = MainWindow(db)
    window.show()
    result = app.exec()
    db.close()
    return result


if __name__ == '__main__':
    sys.exit(main())
