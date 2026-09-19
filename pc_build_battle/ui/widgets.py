from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient, QPainterPath
from PySide6.QtWidgets import QWidget, QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QProgressBar, QScrollArea, QSizePolicy, QLayout


def label(text,kind=None):
    w=QLabel(str(text))
    w.setWordWrap(True)
    w.setTextFormat(Qt.TextFormat.PlainText)
    if kind: w.setObjectName(kind)
    return w


def button(text,callback,primary=False):
    w=QPushButton(text)
    if primary: w.setObjectName('primary')
    w.clicked.connect(callback)
    w.setCursor(Qt.CursorShape.PointingHandCursor)
    return w


def card(parent_layout=None,hero=False):
    w=QFrame(); w.setObjectName('hero' if hero else 'card')
    layout=QVBoxLayout(w); layout.setContentsMargins(20,18,20,18); layout.setSpacing(12)
    layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
    w.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)
    if parent_layout is not None: parent_layout.addWidget(w)
    return w,layout


def clear(layout):
    while layout.count():
        item=layout.takeAt(0)
        if item.widget():
            widget=item.widget()
            widget.hide()
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout(): clear(item.layout())


def scroll(content):
    area=QScrollArea(); area.setWidgetResizable(True); area.setWidget(content)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    return area


class StatMeter(QWidget):
    def __init__(self,title,value=0,color='#68ecc4'):
        super().__init__()
        layout=QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(6)
        row=QHBoxLayout(); row.addWidget(label(title,'muted')); self.value=label(value); row.addWidget(self.value,0,Qt.AlignmentFlag.AlignRight)
        layout.addLayout(row)
        self.bar=QProgressBar(); self.bar.setRange(0,100); self.bar.setTextVisible(False); self.bar.setFixedHeight(7)
        self.bar.setStyleSheet(f'QProgressBar::chunk {{background:{color};border-radius:3px;}}')
        layout.addWidget(self.bar); self.set_value(value)

    def set_value(self,value,animated=False):
        self.value.setText(str(value))
        if animated:
            self.anim=QPropertyAnimation(self.bar,b'value'); self.anim.setDuration(500); self.anim.setStartValue(self.bar.value()); self.anim.setEndValue(value); self.anim.setEasingCurve(QEasingCurve.Type.OutCubic); self.anim.start()
        else: self.bar.setValue(value)


class TowerArt(QWidget):
    """Resolution-independent desktop PC illustration, painted locally."""
    def __init__(self):
        super().__init__(); self.setMinimumSize(200,230); self.setMaximumWidth(300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.scale(self.width()/260,self.height()/260)
        p.setPen(QPen(QColor('#355b63'),1))
        for i in range(7): p.drawLine(0,200+i*10,260,130+i*10)
        grad=QLinearGradient(45,20,220,230); grad.setColorAt(0,QColor('#283c50')); grad.setColorAt(1,QColor('#0b121f'))
        p.setBrush(grad); p.setPen(QPen(QColor('#7897a8'),2)); p.drawRoundedRect(58,20,145,207,13,13)
        p.setBrush(QColor('#0e1928')); p.setPen(QPen(QColor('#3b6571'),1)); p.drawRoundedRect(72,37,83,167,6,6)
        p.setPen(QPen(QColor('#6eebc6'),3))
        for y in [67,121,175]:
            p.setBrush(QColor('#122e33')); p.drawEllipse(QPointF(178,y),17,17)
            p.setPen(QPen(QColor('#73a6ff'),2)); p.drawEllipse(QPointF(178,y),11,11); p.setPen(QPen(QColor('#6eebc6'),3))
        p.setBrush(QColor('#263d53')); p.setPen(QPen(QColor('#83a9cf'),1)); p.drawRoundedRect(84,60,54,53,5,5)
        p.setPen(QPen(QColor('#a797f4'),3)); p.drawEllipse(QPointF(111,86),18,18)
        p.setBrush(QColor('#334655')); p.setPen(QPen(QColor('#6eebc6'),2)); p.drawRoundedRect(80,137,67,21,3,3)
        p.setPen(QPen(QColor('#8c9da9'),3)); p.drawLine(78,229,78,238); p.drawLine(183,229,183,238)
        p.end()


class ScoreChart(QWidget):
    def __init__(self,scores):
        super().__init__(); self.scores=scores; self.setMinimumHeight(170)

    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h=self.width(),self.height()
        p.setPen(QPen(QColor('#2b374b'),1))
        for y in [20,h//2,h-25]: p.drawLine(25,y,w-15,y)
        if not self.scores:
            p.setPen(QColor('#97a8bf')); p.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter,'Your first build starts the story.'); return
        points=[QPointF(28+i*max(1,w-50)/max(1,len(self.scores)-1),h-25-s*(h-50)/100) for i,s in enumerate(self.scores)]
        path=QPainterPath(points[0])
        for pt in points[1:]: path.lineTo(pt)
        p.setPen(QPen(QColor('#68ecc4'),3)); p.drawPath(path); p.setBrush(QColor('#68ecc4'))
        for pt in points: p.drawEllipse(pt,4,4)
        p.end()
