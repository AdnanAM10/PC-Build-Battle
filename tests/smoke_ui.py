"""Run actual Qt navigation and gameplay offscreen with a disposable database."""
import os
import sys
import tempfile
import traceback
from unittest.mock import patch
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.deps')]
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from pc_build_battle.database import Database
from pc_build_battle.challenges import featured
from pc_build_battle.ui.main_window import MainWindow
from pc_build_battle.ui.theme import THEME

app=QApplication([]); app.setStyle('Fusion'); app.setStyleSheet(THEME)
if os.name=='nt' and os.environ.get('QT_QPA_PLATFORM')=='offscreen':
    for font in ['segoeui.ttf','segoeuib.ttf']:
        QFontDatabase.addApplicationFont(str(Path(os.environ['WINDIR'])/'Fonts'/font))
errors=[]
def report_error(*args):
    errors.append(args)
    traceback.print_exception(*args)
sys.excepthook=report_error
with tempfile.TemporaryDirectory() as tmp:
    db=Database(Path(tmp)/'smoke.sqlite3'); window=MainWindow(db); window.show(); app.processEvents()
    screenshots=ROOT/'screenshots'; screenshots.mkdir(exist_ok=True)
    window.grab().save(str(screenshots/'home.png'))
    for name,b in window.nav.items():
        QTest.mouseClick(b,Qt.MouseButton.LeftButton); app.processEvents()
        assert window.stack.currentWidget()==window.pages[name],name
    window.start_challenge(featured()); app.processEvents()
    lookup={p.id:p for p in window.parts}
    for id in ['cpu-6','cpu_cooler-3','motherboard-2','gpu-16','ram-5','storage-7','psu-8','case-3']:
        part=lookup[id]; window.builder.select_category(part.category); window.builder.browser.add(part); app.processEvents()
    window.builder.browser.search.setText('no such component'); app.processEvents()
    assert '0 COMPONENTS' in window.builder.browser.count.text()
    window.builder.browser.search.clear(); window.builder.select_category('GPU'); app.processEvents()
    window.builder.browser.brand.setCurrentText('NVIDIA'); app.processEvents()
    assert '7 COMPONENTS' in window.builder.browser.count.text()
    window.builder.browser.brand.setCurrentIndex(0)
    window.builder.browser.add(lookup['gpu-10']); app.processEvents()
    assert window.build.parts['GPU'].id=='gpu-10'
    window.builder.browser.add(lookup['gpu-16']); app.processEvents()
    window.grab().save(str(screenshots/'build.png'))
    assert db.draft().cost==window.build.cost
    window.builder.remove('GPU'); app.processEvents(); assert 'GPU' not in window.build.parts
    window.builder.browser.add(lookup['gpu-16']); app.processEvents()
    submit=next(b for b in window.builder.panel.findChildren(QPushButton) if b.text().startswith('SUBMIT'))
    assert submit.isEnabled(); QTest.mouseClick(submit,Qt.MouseButton.LeftButton); QTest.qWait(600)
    assert len(db.history())==1
    assert window.stack.currentWidget()==window.pages['Results']
    window.grab().save(str(screenshots/'results.png'))
    for name in window.nav: window.navigate(name); app.processEvents()
    window.navigate('Home'); app.processEvents()
    view=next(b for b in window.pages['Home'].findChildren(QPushButton) if b.text()=='VIEW RESULT')
    QTest.mouseClick(view,Qt.MouseButton.LeftButton); app.processEvents()
    assert window.pages['Results'].data['result']['total']==db.history()[0]['score']
    QTest.qWait(600)
    window.resize(1050,720); app.processEvents(); window.grab().save(str(screenshots/'compact.png'))
    window.navigate('Settings'); settings=window.pages['Settings']
    settings.name.setText('TestBuilder'); settings.events.setChecked(True); settings.save()
    assert db.get('username')=='TestBuilder' and db.get('events')
    for event in ['drop','stock','customer','power','sale']:
        window.build=None; window.start_challenge(featured())
        window.build.parts={lookup[id].category:lookup[id] for id in ['cpu-6','cpu_cooler-3','motherboard-2','gpu-16','ram-5','storage-7','psu-8','case-3']}
        with patch('pc_build_battle.ui.build_page.random.choice',return_value=event), patch('pc_build_battle.ui.build_page.QMessageBox.information'):
            window.builder.random_event()
        assert window.build.event_used and db.draft().event_used
        if event=='drop': assert window.build.discounts['gpu-16']==40
        if event=='stock': assert 'Motherboard' not in window.build.parts
        if event=='customer': assert window.build.challenge.requirements['storage']==2000
        if event=='power': assert window.build.challenge.requirements['power']==450
        if event=='sale': assert window.build.discounts['cpu-6']==19
    window.navigate('Build'); app.processEvents(); window.grab().save(str(screenshots/'compact-build.png'))
    window.close(); db.close()
    db=Database(Path(tmp)/'smoke.sqlite3'); assert len(db.history())==1 and db.get('xp')>0
    reopened=MainWindow(db); assert len(reopened.build.parts)==8 and reopened.build.event_used
    reopened.close(); db.close()
assert not errors,errors
print('PASS: 8 navigation pages, selection/replacement/removal, filters, draft recovery, submission, results, history, restart persistence, settings, all 5 events, compact layout.')
