import random
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QMessageBox, QSplitter, QLayout
from .widgets import label, button, card, scroll, clear, StatMeter
from ..models import CATEGORIES
from ..services import metrics, compatibility, objectives, score
from ..challenges import requirement_text


class PartsBrowser(QWidget):
    def __init__(self,window,editable=False):
        super().__init__(); self.window=window; self.editable=editable; self.category='CPU'
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        filters=QHBoxLayout(); self.search=QLineEdit(); self.search.setPlaceholderText('Search hardware…'); self.search.setClearButtonEnabled(True)
        self.sort=QComboBox(); self.sort.addItems(['Price: low to high','Price: high to low','Performance'])
        filters.addWidget(self.search,1); filters.addWidget(self.sort); outer.addLayout(filters)
        filters2=QHBoxLayout()
        self.brand=QComboBox(); self.socket=QComboBox(); self.form=QComboBox()
        for combo in [self.brand,self.socket,self.form]: filters2.addWidget(combo); combo.currentTextChanged.connect(self.refresh)
        outer.addLayout(filters2)
        self.count=label('','muted'); outer.addWidget(self.count)
        self.items=QWidget(); self.list=QVBoxLayout(self.items); self.list.setContentsMargins(0,0,6,0); self.list.setSpacing(10)
        self.list.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.scroller=scroll(self.items)
        outer.addWidget(self.scroller,1)
        self.search.textChanged.connect(self.refresh); self.sort.currentTextChanged.connect(self.refresh)
        self.set_category('CPU')

    def set_category(self,category):
        self.category=category
        parts=[p for p in self.window.parts if p.category==category]
        for combo,key,title in [(self.brand,'brand','All brands'),(self.socket,'socket','All sockets'),(self.form,'form_factor','All sizes')]:
            combo.blockSignals(True); combo.clear(); combo.addItem(title)
            values={p.brand if key=='brand' else p.specs.get(key) for p in parts}
            if key=='form_factor' and category=='Case': values={s for p in parts for s in p.specs['supports']}
            combo.addItems(sorted(v for v in values if v)); combo.setEnabled(combo.count()>1); combo.blockSignals(False)
        self.refresh()
        self.scroller.verticalScrollBar().setValue(0)

    def refresh(self,*args):
        clear(self.list)
        parts=[p for p in self.window.parts if p.category==self.category and self.search.text().lower() in (p.name+' '+p.brand).lower()]
        if self.brand.currentIndex()>0: parts=[p for p in parts if p.brand==self.brand.currentText()]
        if self.socket.currentIndex()>0: parts=[p for p in parts if p.specs.get('socket')==self.socket.currentText()]
        if self.form.currentIndex()>0: parts=[p for p in parts if p.specs.get('form_factor')==self.form.currentText() or self.form.currentText() in p.specs.get('supports',[])]
        parts.sort(key=lambda p:p.performance if self.sort.currentIndex()==2 else p.price,reverse=self.sort.currentIndex()!=0)
        self.count.setText(f'{len(parts)} COMPONENTS  /  {self.category.upper()}')
        for part in parts:
            frame,layout=card(self.list)
            row=QHBoxLayout(); row.addWidget(label(part.brand.upper(),'eyebrow')); row.addStretch()
            price=part.price-self.window.build.discounts.get(part.id,0) if self.window.build else part.price
            row.addWidget(label(f'${price:,}','heading')); layout.addLayout(row)
            layout.addWidget(label(part.name,'heading'))
            specs='  ·  '.join(f'{k.replace("_"," ").title()}: {", ".join(map(str,v)) if isinstance(v,list) else "Yes" if v is True else "No" if v is False else v}' for k,v in part.specs.items())
            layout.addWidget(label(specs,'muted'))
            row=QHBoxLayout(); row.addWidget(label(f'PERF  {part.performance}    /    {part.watts}W draw','muted')); row.addStretch()
            if self.editable:
                selected=self.window.build and self.window.build.parts.get(self.category)==part
                add=button('✓ EQUIPPED' if selected else '+ ADD TO BUILD',lambda checked=False,p=part:self.add(p),not selected)
                add.setEnabled(not selected); row.addWidget(add)
            layout.addLayout(row)
        if not parts: self.list.addWidget(label('No hardware matches these filters. Try another brand or clear your search.','muted'))
        self.list.addStretch()

    def add(self,part):
        self.window.build.parts[part.category]=part
        self.window.db.save_draft(self.window.build)
        self.window.builder.update_build(); self.refresh()


class BuildPage(QWidget):
    def __init__(self,window):
        super().__init__(); self.window=window
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        header=QHBoxLayout(); self.title=label('The workbench','title'); header.addWidget(self.title); header.addStretch()
        self.event=button('⚡ RANDOM EVENT',self.random_event); header.addWidget(self.event); outer.addLayout(header)
        self.subtitle=label('Choose a challenge to start building.','muted'); outer.addWidget(self.subtitle)
        self.splitter=QSplitter(Qt.Orientation.Horizontal); outer.addWidget(self.splitter,1)
        categories=QWidget(); cats=QVBoxLayout(categories); cats.setContentsMargins(0,10,8,0)
        cats.addWidget(label('COMPONENTS','eyebrow')); self.cat_buttons={}
        for category in CATEGORIES:
            b=button(category,lambda checked=False,c=category:self.select_category(c)); b.setObjectName('category'); b.setCheckable(True); cats.addWidget(b); self.cat_buttons[category]=b
        cats.addStretch(); categories.setMinimumWidth(140); self.splitter.addWidget(categories)
        self.browser=PartsBrowser(window,True); self.browser.setMinimumWidth(300); self.splitter.addWidget(self.browser)
        self.panel=QWidget(); self.panel_layout=QVBoxLayout(self.panel); self.panel_layout.setContentsMargins(10,0,0,0)
        self.panel_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        right=scroll(self.panel); right.setMinimumWidth(265); self.splitter.addWidget(right); self.splitter.setSizes([155,490,315])
        self.select_category('CPU')

    def select_category(self,category):
        for c,b in self.cat_buttons.items(): b.setChecked(c==category)
        self.browser.set_category(category)

    def refresh(self):
        self.update_build(); self.browser.refresh()

    def update_build(self):
        clear(self.panel_layout)
        build=self.window.build
        self.splitter.setVisible(build is not None); self.event.setVisible(build is not None and self.window.db.get('events',False))
        if not build:
            self.title.setText('Your next great build starts here')
            self.subtitle.setText('Open Challenges to choose a mission, or start the featured challenge from Home.'); return
        self.title.setText(build.challenge.name)
        self.subtitle.setText(f'{build.challenge.mode}  /  ${build.challenge.budget:,} budget  /  Draft saved automatically')
        self.event.setEnabled(not build.event_used)
        frame,layout=card(self.panel_layout)
        row=QHBoxLayout(); row.addWidget(label('YOUR BUILD','eyebrow')); row.addStretch(); row.addWidget(label(f'{len(build.parts)} / 8','muted')); layout.addLayout(row)
        for cat in CATEGORIES:
            part=build.parts.get(cat)
            row=QHBoxLayout(); text=QVBoxLayout(); text.setSpacing(2)
            text.addWidget(label(cat.upper(),'muted')); text.addWidget(label(part.name if part else 'Empty slot'))
            row.addLayout(text,1)
            if part:
                row.addWidget(label(f'${part.price-build.discounts.get(part.id,0):,}'))
                remove=button('×',lambda checked=False,c=cat:self.remove(c)); remove.setFixedWidth(30); remove.setStyleSheet('padding:4px;'); remove.setToolTip(f'Remove {cat}'); row.addWidget(remove)
            layout.addLayout(row)
        row=QHBoxLayout(); row.addWidget(label('TOTAL','muted')); row.addStretch(); row.addWidget(label(f'${build.cost:,}','number')); layout.addLayout(row)
        remain=build.challenge.budget-build.cost
        status=label(f'${abs(remain):,} {"remaining" if remain>=0 else "OVER BUDGET"}'); status.setStyleSheet(f'color:{"#68ecc4" if remain>=0 else "#ff8395"};font-weight:bold;'); layout.addWidget(status)
        layout.addWidget(label(f'{build.watts}W estimated  ·  {round(build.watts*1.2/50+.499)*50}W+ recommended PSU','muted'))
        submit=button('SUBMIT BUILD  →',self.submit,True); submit.setEnabled(len(build.parts)==len(CATEGORIES)); layout.addWidget(submit)
        if len(build.parts)<8: layout.addWidget(label('Fill all eight slots to submit. Incompatible builds can still be judged.','muted'))
        frame,layout=card(self.panel_layout); layout.addWidget(label('LIVE TELEMETRY','eyebrow'))
        colors=['#78aaff','#b9a1fb','#f4b772','#68ecc4','#8bc8f6','#ed8bc9']
        for (key,value),color in zip(metrics(build).items(),colors): layout.addWidget(StatMeter(key.title(),value,color))
        frame,layout=card(self.panel_layout); layout.addWidget(label('MISSION CHECKLIST','eyebrow'))
        for key,passed in objectives(build).items():
            text=f'Under ${build.challenge.budget:,}' if key=='budget' else requirement_text(key,build.challenge.requirements[key])
            l=label(('✓  ' if passed else '○  ')+text); l.setStyleSheet(f'color:{"#68ecc4" if passed else "#a0adc0"}'); layout.addWidget(l)
        issues=compatibility(build)
        if issues:
            frame,layout=card(self.panel_layout); layout.addWidget(label('⚠ COMPATIBILITY','heading'))
            for issue in issues:
                l=label(issue); l.setStyleSheet('color:#ff9aa9;'); layout.addWidget(l)
        self.panel_layout.addStretch()

    def remove(self,category):
        self.window.build.parts.pop(category,None); self.window.db.save_draft(self.window.build); self.refresh()

    def submit(self):
        build=self.window.build
        if not build or len(build.parts)!=8: return
        result=self.window.db.submit(build,score(build)); self.window.build=None
        self.window.last_result=dict(result=result,parts={k:vars(v) for k,v in build.parts.items()},challenge=build.challenge.to_dict(),discounts=build.discounts)
        self.window.show_results(self.window.last_result)

    def random_event(self):
        build=self.window.build
        if not build or build.event_used: return
        options=['customer','power','sale']
        if 'GPU' in build.parts: options.append('drop')
        if 'Motherboard' in build.parts: options.append('stock')
        event=random.choice(options)
        if event=='drop': build.discounts[build.parts['GPU'].id]=40; text='PRICE DROP: your selected GPU is $40 cheaper for this build.'
        elif event=='stock': build.parts.pop('Motherboard'); text='STOCK SHORTAGE: your motherboard order was cancelled. Select a replacement.'
        elif event=='customer': build.challenge.requirements['storage']=2000; text='CUSTOMER CHANGE: at least 2 TB of storage is now required.'
        elif event=='power': build.challenge.requirements['power']=450; text='POWER LIMIT: the customer now needs the system to stay at or below 450W.'
        else:
            for part in self.window.parts:
                if part.category=='CPU' and part.brand=='AMD': build.discounts[part.id]=round(part.price*.1)
            text='FLASH SALE: all AMD CPUs are 10% off for this build.'
        build.event_used=True; self.window.db.save_draft(build); self.refresh(); QMessageBox.information(self,'Market event',text)
