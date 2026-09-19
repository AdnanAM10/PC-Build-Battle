import json
import sqlite3
import os
from pathlib import Path
from dataclasses import asdict
from datetime import datetime
from .models import Component, Build, Challenge
from .seed_data import catalog
from .services import earned


class Database:
    def __init__(self,path=None):
        if path is None:
            folder=Path(os.environ.get('LOCALAPPDATA',Path.home()))/'PCBuildBattle'
            folder.mkdir(parents=True,exist_ok=True)
            path=folder/'progress.sqlite3'
        self.path=str(path)
        self.conn=sqlite3.connect(path)
        self.conn.row_factory=sqlite3.Row
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS parts(id TEXT PRIMARY KEY, data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS builds(id INTEGER PRIMARY KEY, player TEXT, challenge TEXT, mode TEXT, price INTEGER, budget INTEGER, score INTEGER, created TEXT, data TEXT);
            CREATE TABLE IF NOT EXISTS achievements(name TEXT PRIMARY KEY, created TEXT);
            CREATE TABLE IF NOT EXISTS rivals(player TEXT, challenge TEXT, price INTEGER, score INTEGER, created TEXT);
        ''')
        with self.conn:
            self.conn.executemany('INSERT OR IGNORE INTO parts VALUES(?,?)',[(p.id,json.dumps(asdict(p))) for p in catalog()])
            if not self.conn.execute('SELECT 1 FROM rivals').fetchone():
                self.conn.executemany('INSERT INTO rivals VALUES(?,?,?,?,?)',[(n,'Exhibition build',p,s,'2026-01-01') for n,p,s in [('NeonBuilder',1480,97),('ThermalKing',1200,94),('SocketMaster',980,92),('PixelPilot',1400,85),('CableGoblin',780,72)]])

    def get(self,key,default=None):
        row=self.conn.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set(self,key,value):
        with self.conn: self.conn.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',(key,json.dumps(value)))

    def parts(self):
        return [Component(**json.loads(r[0])) for r in self.conn.execute('SELECT data FROM parts')]

    def history(self):
        return [dict(r) for r in self.conn.execute('SELECT * FROM builds ORDER BY id DESC')]

    def unlocked(self):
        return {r[0] for r in self.conn.execute('SELECT name FROM achievements')}

    def save_draft(self,build):
        self.set('draft',dict(challenge=build.challenge.to_dict(),parts={k:p.id for k,p in build.parts.items()},discounts=build.discounts,event_used=build.event_used))

    def draft(self):
        d=self.get('draft')
        if not d: return None
        lookup={p.id:p for p in self.parts()}
        return Build(Challenge(**d['challenge']),{k:lookup[v] for k,v in d['parts'].items() if v in lookup},d.get('discounts',{}),d.get('event_used',False))

    def submit(self,build,result):
        now=datetime.now().isoformat(timespec='seconds')
        unlocked=self.unlocked()
        new=[a for a in earned(build,result,len(self.history())+1) if a not in unlocked]
        result['unlocked']=new
        data=dict(result=result,parts={k:asdict(v) for k,v in build.parts.items()},challenge=build.challenge.to_dict(),discounts=build.discounts)
        with self.conn:
            self.conn.execute('INSERT INTO builds(player,challenge,mode,price,budget,score,created,data) VALUES(?,?,?,?,?,?,?,?)',
                (self.get('username','Builder01'),build.challenge.name,build.challenge.mode,build.cost,build.challenge.budget,result['total'],now,json.dumps(data)))
            self.conn.executemany('INSERT OR IGNORE INTO achievements VALUES(?,?)',[(a,now) for a in new])
            self.conn.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',('xp',json.dumps(self.get('xp',0)+result['xp'])))
            self.conn.execute('DELETE FROM settings WHERE key=?',('draft',))
        return result

    def leaderboard(self):
        return [dict(r) for r in self.conn.execute('SELECT player,challenge,price,score,created FROM builds UNION ALL SELECT player,challenge,price,score,created FROM rivals ORDER BY score DESC, created DESC LIMIT 100')]

    def close(self): self.conn.close()
