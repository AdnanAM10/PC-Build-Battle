THEME = '''
* { font-family: "Segoe UI"; font-size: 13px; color: #e9eef8; }
QMainWindow, QWidget#root { background: #0c1019; }
QWidget { background: transparent; }
QFrame#sidebar { background: #10151f; border-right: 1px solid #252c3b; }
QFrame#card { background: #151d2b; border: 1px solid #293348; border-radius: 14px; }
QFrame#hero { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #202d48,stop:.6 #152c35,stop:1 #153a36); border: 1px solid #3c5c66; border-radius: 18px; }
QLabel { background: transparent; border: none; }
QLabel#muted { color: #96a4ba; }
QLabel#eyebrow { color: #65e8bf; font-size: 11px; font-weight: 700; letter-spacing: 2px; }
QLabel#title { font-size: 30px; font-weight: 750; }
QLabel#heading { font-size: 18px; font-weight: 700; }
QLabel#number { font-size: 30px; font-weight: 750; }
QLabel#score { font-size: 76px; font-weight: 800; color: #68ecc4; }
QPushButton { background: #222e42; border: 1px solid #34445d; border-radius: 8px; padding: 10px 15px; font-weight: 600; }
QPushButton:hover { background: #30435d; border-color: #6f95bd; }
QPushButton:pressed { background: #172133; }
QPushButton:disabled { color: #6a778c; background: #1a2332; border-color: #283246; }
QPushButton#primary { background: #68ecc4; color: #09271f; border: none; }
QPushButton#primary:hover { background: #9ff8da; }
QPushButton#nav { text-align: left; background: transparent; border: none; padding: 12px 18px; color: #9eacc0; }
QPushButton#nav:hover { background: #1b283a; color: #fff; }
QPushButton#nav:checked { background: #203d39; color: #7df1cd; border-left: 3px solid #68ecc4; }
QPushButton#category { text-align: left; padding: 13px 10px; }
QPushButton#category:checked { background: #28473f; border-color: #68ecc4; color: #8af3d4; }
QLineEdit, QComboBox { background: #101724; border: 1px solid #344158; border-radius: 7px; padding: 9px; selection-background-color: #326858; }
QLineEdit:focus, QComboBox:focus { border-color: #68ecc4; }
QComboBox QAbstractItemView { background: #192436; selection-background-color: #305647; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: #101724; width: 7px; margin: 0; }
QScrollBar::handle:vertical { background: #36465e; border-radius: 3px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QProgressBar { background: #263044; border: none; border-radius: 4px; height: 7px; text-align: center; }
QProgressBar::chunk { background: #68ecc4; border-radius: 4px; }
QCheckBox { spacing: 10px; padding: 8px 0; }
QCheckBox::indicator { width: 18px; height: 18px; }
QTableWidget { background: #151d2b; alternate-background-color: #192233; gridline-color: #2b3548; border: 1px solid #2b3548; border-radius: 8px; selection-background-color: #28473f; }
QHeaderView::section { background: #1c2739; color: #9dacbf; border: none; padding: 12px; font-weight: 600; }
QTableWidget::item { padding: 9px; }
QToolTip { background: #26354a; color: #fff; border: 1px solid #4b6280; padding: 8px; }
QMessageBox { background: #151d2b; }
'''
