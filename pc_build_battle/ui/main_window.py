from copy import deepcopy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QStackedWidget, QProgressBar, QMessageBox
from .widgets import label, button
from .build_page import BuildPage
from .dashboard_pages import HomePage, ChallengesPage, PartsPage, LeaderboardPage, AchievementsPage, StatsPage, SettingsPage
from .results_page import ResultsPage
from ..models import Build


class MainWindow(QMainWindow):
    def __init__(self,db):
        super().__init__(); self.db=db; self.parts=db.parts(); self.build=db.draft(); self.last_result=None
        self.setWindowTitle('PC BUILD BATTLE'); self.resize(1440,940); self.setMinimumSize(1050,720)
        root=QWidget(); root.setObjectName('root'); self.setCentralWidget(root); layout=QHBoxLayout(root); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        sidebar=QFrame(); sidebar.setObjectName('sidebar'); sidebar.setFixedWidth(216); side=QVBoxLayout(sidebar); side.setContentsMargins(16,28,16,22); side.setSpacing(8)
        side.addWidget(label('▣  PC BUILD','heading')); side.addWidget(label('     B A T T L E','eyebrow')); side.addSpacing(25); side.addWidget(label('   PLAY & EXPLORE','muted'))
        self.nav={}
        for icon,name in [('⌂','Home'),('⚑','Challenges'),('▣','Build'),('▤','Parts Library'),('≡','Leaderboard'),('◇','Achievements'),('↗','Player Stats'),('⚙','Settings')]:
            b=button(f'{icon}    {name}',lambda checked=False,n=name:self.navigate(n)); b.setObjectName('nav'); b.setCheckable(True); self.nav[name]=b; side.addWidget(b)
        side.addStretch(); side.addWidget(label('●  LOCAL / OFFLINE','eyebrow')); side.addSpacing(15)
        self.profile=label('','heading'); self.level=label('','muted'); self.xp=QProgressBar(); self.xp.setTextVisible(False); self.xp.setRange(0,500); self.xp.setFixedHeight(6)
        side.addWidget(self.profile); side.addWidget(self.level); side.addWidget(self.xp); self.total=label('','muted'); side.addWidget(self.total); layout.addWidget(sidebar)
        main=QWidget(); body=QVBoxLayout(main); body.setContentsMargins(28,23,25,20); body.setSpacing(17)
        top=QHBoxLayout(); top.addWidget(label('THE ULTIMATE PC BUILDING PLAYGROUND','eyebrow')); top.addStretch(); top.addWidget(label('SEASON 01   /   BUILD DIFFERENT','muted')); body.addLayout(top)
        self.stack=QStackedWidget(); body.addWidget(self.stack,1); layout.addWidget(main,1)
        self.builder=BuildPage(self)
        self.pages={'Home':HomePage(self),'Challenges':ChallengesPage(self),'Build':self.builder,'Parts Library':PartsPage(self),'Leaderboard':LeaderboardPage(self),'Achievements':AchievementsPage(self),'Player Stats':StatsPage(self),'Settings':SettingsPage(self),'Results':ResultsPage(self)}
        for page in self.pages.values(): self.stack.addWidget(page)
        self.update_profile(); self.navigate('Home')

    def update_profile(self):
        xp=self.db.get('xp',0); self.profile.setText(self.db.get('username','Builder01')); self.level.setText(f'Level {xp//500+1}  ·  {xp%500} / 500 XP'); self.xp.setValue(xp%500); self.total.setText(f'{len(self.db.history())} builds completed')

    def navigate(self,name):
        self.pages[name].refresh(); self.stack.setCurrentWidget(self.pages[name])
        for n,b in self.nav.items(): b.setChecked(n==name)
        self.update_profile()

    def start_challenge(self,challenge):
        if self.build and self.build.parts:
            answer=QMessageBox.question(self,'Replace current draft?','Starting a new challenge replaces your saved in-progress build. Continue?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
            if answer!=QMessageBox.StandardButton.Yes: return
        self.build=Build(deepcopy(challenge)); self.db.save_draft(self.build); self.navigate('Build')

    def show_results(self,data):
        self.pages['Results'].data=data; self.navigate('Results')

    def closeEvent(self,event):
        if self.build: self.db.save_draft(self.build)
        event.accept()
