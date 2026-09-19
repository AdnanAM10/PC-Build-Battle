from PySide6.QtWidgets import QHBoxLayout, QGridLayout
from .dashboard_pages import Page, table
from .widgets import label, button, card, StatMeter
from ..models import Challenge


class ResultsPage(Page):
    def __init__(self,window):
        super().__init__(window,'Build complete.','The parts are in. The judges have spoken.'); self.data=None

    def refresh(self):
        self.reset()
        if not self.data:
            self.layout.addWidget(label('Finish your first build to see a result.','muted')); return
        result=self.data['result']; challenge=self.data['challenge']
        frame,layout=card(self.layout,True); layout.addWidget(label(challenge['name'].upper(),'eyebrow'))
        row=QHBoxLayout(); row.addWidget(label(str(result['total']),'score')); row.addWidget(label('/ 100','heading')); row.addStretch(); row.addWidget(label(result['rank'].upper(),'title')); layout.addLayout(row)
        layout.addWidget(label(f'+{result["xp"]} XP EARNED   /   Saved to your local build history','eyebrow'))
        if result.get('unlocked'): layout.addWidget(label('◆ ACHIEVEMENTS  /  '+' · '.join(result['unlocked']),'heading'))
        grid=QGridLayout()
        for i,(name,value) in enumerate(result['categories'].items()):
            frame,layout=card(); meter=StatMeter(name,0,['#78aaff','#eabd76','#68ecc4','#b9a1fb','#80c8f1','#ed8bc9'][i]); layout.addWidget(meter); meter.set_value(value,self.window.db.get('animations',True)); grid.addWidget(frame,i//3,i%3)
        self.layout.addLayout(grid)
        if result['bonuses']: self.layout.addWidget(label('BONUSES  /  '+'  ·  '.join(f'{name} +{points}' for name,points in result['bonuses']),'eyebrow'))
        self.layout.addWidget(label('Meet your judges','heading')); row=QHBoxLayout()
        for name,comment in result['judges']:
            frame,layout=card(); layout.addWidget(label(name,'eyebrow')); layout.addWidget(label('“'+comment+'”','heading')); row.addWidget(frame)
        self.layout.addLayout(row)
        if result['issues']:
            frame,layout=card(self.layout); layout.addWidget(label('Engineering notes','heading'))
            for issue in result['issues']: layout.addWidget(label('⚠ '+issue,'muted'))
        failed=[k for k,v in result['objectives'].items() if not v]
        if failed: self.layout.addWidget(label('Missed objectives: '+', '.join(failed),'muted'))
        parts=self.data['parts']; discounts=self.data.get('discounts',{})
        cost=sum(p['price']-discounts.get(p['id'],0) for p in parts.values())
        self.layout.addWidget(label(f'Build manifest  /  ${cost:,} of ${challenge["budget"]:,}','heading'))
        self.layout.addWidget(table(['SLOT','COMPONENT','PRICE'],[(cat,p['name'],f'${p["price"]-discounts.get(p["id"],0):,}') for cat,p in parts.items()]))
        row=QHBoxLayout(); row.addWidget(button('REMATCH  →',lambda:self.window.start_challenge(Challenge(**challenge)),True)); row.addWidget(button('FIND ANOTHER CHALLENGE',lambda:self.window.navigate('Challenges'))); row.addStretch(); self.layout.addLayout(row); self.layout.addStretch()
