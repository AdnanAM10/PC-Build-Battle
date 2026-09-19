import json
from collections import Counter
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QLineEdit, QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QLayout
from .widgets import label, button, card, scroll, clear, StatMeter, TowerArt, ScoreChart
from .build_page import PartsBrowser
from ..challenges import featured, daily, generate, MODES, requirement_text
from ..models import CATEGORIES
from ..services import ACHIEVEMENTS


class Page(QWidget):
    def __init__(self,window,title,subtitle):
        super().__init__(); self.window=window
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        content=QWidget(); self.layout=QVBoxLayout(content); self.layout.setContentsMargins(0,0,8,15); self.layout.setSpacing(18)
        self.layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        outer.addWidget(scroll(content)); self.title=title; self.subtitle=subtitle

    def reset(self):
        clear(self.layout); self.layout.addWidget(label(self.title,'title')); self.layout.addWidget(label(self.subtitle,'muted'))


def challenge_card(challenge,callback,hero=False):
    frame,layout=card(hero=hero)
    layout.addWidget(label(challenge.mode.upper(),'eyebrow'))
    layout.addWidget(label(challenge.name,'title' if hero else 'heading'))
    layout.addWidget(label(challenge.description,'muted'))
    layout.addWidget(label(f'${challenge.budget:,}  BUDGET','heading'))
    for k,v in challenge.requirements.items(): layout.addWidget(label('○  '+requirement_text(k,v),'muted'))
    bonus=[]
    for k,v in challenge.bonuses.items():
        bonus.append({'saving':f'+5 below ${challenge.budget-v:,}' if isinstance(v,int) else '', 'power':f'+3 below {v}W','rgb':f'+3 for {v} RGB parts','white':'+3 for a white case','quiet':f'+3 cooler noise ≤ {v}'}.get(k,k))
    if bonus: layout.addWidget(label('BONUS  /  '+' · '.join(bonus),'eyebrow'))
    layout.addStretch(); layout.addWidget(button('START CHALLENGE  →',lambda:callback(challenge),True))
    return frame


class HomePage(Page):
    def __init__(self,window): super().__init__(window,'Welcome to the battlestation.','Pick your parts. Prove your instincts. Build something legendary.')

    def refresh(self):
        self.reset(); db=self.window.db; history=db.history(); xp=db.get('xp',0)
        row=QHBoxLayout()
        values=[('BUILDER LEVEL',f'{xp//500+1:02}',f'{xp%500} / 500 XP to next level'),('BUILDS COMPLETED',str(len(history)),'Every build tells a story'),('AVERAGE SCORE',f'{sum(h["score"] for h in history)/len(history):.0f}' if history else '—','Aim for the top 1%'),('PERSONAL BEST',str(max((h['score'] for h in history),default=0)),f'{len(db.unlocked())} / 10 achievements')]
        for name,value,note in values:
            frame,layout=card(); layout.addWidget(label(name,'eyebrow')); layout.addWidget(label(value,'number')); layout.addWidget(label(note,'muted')); row.addWidget(frame)
        self.layout.addLayout(row)
        frame,layout=card(hero=True); self.layout.addWidget(frame)
        hero=QHBoxLayout(); details=QVBoxLayout(); details.setSpacing(13)
        details.addWidget(label('FEATURED CHALLENGE   /   01','eyebrow')); details.addWidget(label('1440p Gaming Beast','title'))
        details.addWidget(label('Your budget is limited. Your ambition isn’t.\nCraft a high-frame-rate machine for your next gaming obsession.','muted'))
        details.addWidget(label('$1,500 BUDGET     •     FPS KING','heading'))
        details.addWidget(label('32 GB RAM   /   2 TB SSD   /   Dedicated GPU   /   Wi-Fi','muted'))
        details.addWidget(label('+5 below $1,400   ·   +3 below 500W','eyebrow'))
        actions=QHBoxLayout(); actions.addWidget(button('START CHALLENGE  →',lambda:self.window.start_challenge(featured()),True))
        if self.window.build: actions.addWidget(button('RESUME BUILD',lambda:self.window.navigate('Build')))
        actions.addStretch(); details.addLayout(actions); hero.addLayout(details,3); hero.addWidget(TowerArt(),1); layout.addLayout(hero)
        row=QHBoxLayout(); row.addWidget(label('Find your next battle','heading')); row.addStretch(); row.addWidget(button('ALL CHALLENGES  ↗',lambda:self.window.navigate('Challenges'))); self.layout.addLayout(row)
        row=QHBoxLayout()
        for ch in [daily(),generate('Tiny Titan'),generate('AI Rig')]: row.addWidget(challenge_card(ch,self.window.start_challenge))
        self.layout.addLayout(row)
        self.layout.addWidget(label('Recent builds','heading'))
        if not history:
            frame,layout=card(self.layout); layout.addWidget(label('An empty workbench. Endless possibilities.','heading')); layout.addWidget(label('Start the featured challenge, fill all eight component slots, and submit your build to meet the judges.','muted'))
        for h in history[:5]:
            frame,layout=card(self.layout); row=QHBoxLayout(); row.addWidget(label(f'{h["challenge"]}  ·  ${h["price"]:,}','heading')); row.addStretch(); row.addWidget(label(f'{h["score"]}/100','heading')); row.addWidget(button('VIEW RESULT',lambda checked=False,d=h['data']:self.window.show_results(json.loads(d)))); layout.addLayout(row)
        self.layout.addStretch()


class ChallengesPage(Page):
    def __init__(self,window): super().__init__(window,'Choose your battle','Nine ways to build. One chance to impress the judges.'); self.generated=None

    def refresh(self):
        self.reset()
        row=QHBoxLayout(); self.mode=QComboBox(); self.mode.addItems(['Surprise me']+MODES); row.addWidget(self.mode)
        row.addWidget(button('GENERATE REQUEST  ↻',self.random,True)); row.addStretch(); self.layout.addLayout(row)
        if self.generated: self.layout.addWidget(challenge_card(self.generated,self.window.start_challenge,True))
        self.layout.addWidget(label('DAILY ROTATION  /  '+daily().name,'eyebrow'))
        self.layout.addWidget(challenge_card(daily(),self.window.start_challenge))
        grid=QGridLayout()
        for i,mode in enumerate(MODES): grid.addWidget(challenge_card(generate(mode),self.window.start_challenge),i//3,i%3)
        self.layout.addLayout(grid); self.layout.addStretch()

    def random(self):
        self.generated=generate(None if self.mode.currentIndex()==0 else self.mode.currentText()); self.refresh()


class PartsPage(QWidget):
    def __init__(self,window):
        super().__init__(); layout=QVBoxLayout(self); layout.setContentsMargins(0,0,0,0)
        layout.addWidget(label('The hardware vault','title')); layout.addWidget(label('120 components. Infinite combinations. Prices and benchmarks are approximate game values.','muted'))
        self.category=QComboBox(); self.category.addItems(CATEGORIES); layout.addWidget(self.category)
        self.browser=PartsBrowser(window); layout.addWidget(self.browser,1); self.category.currentTextChanged.connect(self.browser.set_category)

    def refresh(self): self.browser.refresh()


def table(headers,rows):
    w=QTableWidget(len(rows),len(headers)); w.setHorizontalHeaderLabels(headers); w.verticalHeader().hide()
    w.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); w.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); w.setAlternatingRowColors(True)
    w.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    w.setMinimumHeight(min(600,max(180,len(rows)*44+45)))
    for i,row in enumerate(rows):
        w.setRowHeight(i,44)
        for j,value in enumerate(row): w.setItem(i,j,QTableWidgetItem(str(value)))
    return w


class LeaderboardPage(Page):
    def __init__(self,window): super().__init__(window,'The local legends','Your builds compete with fictional exhibition scores. Everything stays on this PC.')

    def refresh(self):
        self.reset(); self.layout.addWidget(table(['RANK','BUILDER','CHALLENGE','PRICE','SCORE','DATE'],
            [(f'#{i+1}',r['player'],r['challenge'],f'${r["price"]:,}',r['score'],r['created'][:10]) for i,r in enumerate(self.window.db.leaderboard())])); self.layout.addStretch()


class AchievementsPage(Page):
    def __init__(self,window): super().__init__(window,'Proof of obsession','A little recognition for your very specific set of building skills.')

    def refresh(self):
        self.reset(); unlocked=self.window.db.unlocked(); self.layout.addWidget(StatMeter(f'{len(unlocked)} / 10 UNLOCKED',len(unlocked)*10,'#b9a1fb'))
        grid=QGridLayout()
        for i,(name,desc) in enumerate(ACHIEVEMENTS):
            frame,layout=card(); layout.addWidget(label('◆ UNLOCKED' if name in unlocked else '◇ LOCKED','eyebrow' if name in unlocked else 'muted')); layout.addWidget(label(name,'heading')); layout.addWidget(label(desc,'muted')); grid.addWidget(frame,i//2,i%2)
        self.layout.addLayout(grid); self.layout.addStretch()


class StatsPage(Page):
    def __init__(self,window): super().__init__(window,'Your builder DNA','Every decision leaves a signature. Here’s yours.')

    def refresh(self):
        self.reset(); hist=self.window.db.history(); n=len(hist); data=[json.loads(h['data']) for h in hist]
        def favorite(category,key):
            counts=Counter(d['parts'][category][key] for d in data)
            return counts.most_common(1)[0][0] if counts else '—'
        values=[('Completed builds',n),('Average score',f'{sum(h["score"] for h in hist)/n:.1f}' if n else '—'),('Highest score',max((h['score'] for h in hist),default=0)),
            ('Budget utilization',f'{sum(h["price"]/h["budget"] for h in hist)/n*100:.1f}%' if n else '—'),('Favorite CPU brand',favorite('CPU','brand')),('Favorite GPU brand',favorite('GPU','brand')),
            ('Most-used GPU',favorite('GPU','name')),('Virtual money spent',f'${sum(h["price"] for h in hist):,}'),('Perfect compatibility',sum(not d['result']['issues'] for d in data)),('Achievements unlocked',len(self.window.db.unlocked()))]
        grid=QGridLayout()
        for i,(name,value) in enumerate(values):
            frame,layout=card(); layout.addWidget(label(name.upper(),'eyebrow')); layout.addWidget(label(value,'heading')); grid.addWidget(frame,i//3,i%3)
        self.layout.addLayout(grid)
        frame,layout=card(self.layout); layout.addWidget(label('Build scores over time','heading')); layout.addWidget(ScoreChart([h['score'] for h in reversed(hist[:30])]))
        row=QHBoxLayout()
        for title,counts in [('GPU brand share',Counter(d['parts']['GPU']['brand'] for d in data)),('Challenge types completed',Counter(h['mode'] for h in hist))]:
            frame,layout=card(); layout.addWidget(label(title,'heading'))
            for name,count in counts.most_common(): layout.addWidget(StatMeter(f'{name}  ·  {count} builds',round(count/max(1,n)*100),'#78aaff'))
            if not counts: layout.addWidget(label('Complete a build to see your preferences.','muted'))
            row.addWidget(frame)
        self.layout.addLayout(row); self.layout.addStretch()


class SettingsPage(Page):
    def __init__(self,window): super().__init__(window,'Make it yours','A local game, on your terms.')

    def refresh(self):
        self.reset(); frame,layout=card(self.layout); layout.addWidget(label('PLAYER PROFILE','eyebrow'))
        self.name=QLineEdit(self.window.db.get('username','Builder01')); self.name.setMaxLength(24); self.name.setPlaceholderText('Builder name'); layout.addWidget(self.name)
        self.events=QCheckBox('Enable optional random events (one manually triggered event per build)'); self.events.setChecked(self.window.db.get('events',False)); layout.addWidget(self.events)
        self.animations=QCheckBox('Animate result meters'); self.animations.setChecked(self.window.db.get('animations',True)); layout.addWidget(self.animations)
        self.status=label('','eyebrow'); layout.addWidget(self.status); layout.addWidget(button('SAVE SETTINGS',self.save,True))
        frame,layout=card(self.layout); layout.addWidget(label('OFFLINE BY DESIGN','eyebrow')); layout.addWidget(label('All parts, challenges, and judges run locally. No accounts, telemetry, or internet connection required.','muted')); layout.addWidget(label('Progress database: '+self.window.db.path,'muted')); layout.addWidget(label('Hardware prices, wattages, and performance are simplified simulation values. Exhibition competitors are fictional.','muted')); self.layout.addStretch()

    def save(self):
        db=self.window.db; db.set('username',self.name.text().strip() or 'Builder01'); db.set('events',self.events.isChecked()); db.set('animations',self.animations.isChecked()); self.window.update_profile(); self.status.setText('✓ Settings saved')
