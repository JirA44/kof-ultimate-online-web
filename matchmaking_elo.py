#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE ONLINE - MATCHMAKING + ELO + CLASSEMENT COMPLET
"""

import socket
import threading
import json
import time
import random
from datetime import datetime
from pathlib import Path

PORT = 7600
DATA = Path(__file__).parent / "matchmaking_data"
PLAYERS = DATA / "players.json"
DEFAULT_ELO = 1000
K = 32
RANGE = 150

class C:
    G='\033[92m';R='\033[91m';Y='\033[93m';C='\033[96m';M='\033[95m';W='\033[97m';B='\033[1m';X='\033[0m'

class Elo:
    @staticmethod
    def calc(w,l,k=K):
        e=1/(1+10**((l-w)/400))
        return round(w+k*(1-e)),round(l+k*(-e))

    @staticmethod
    def rank(elo):
        for t,n,e in [(2400,"Legende","👑"),(2200,"GrandMaster","🏆"),(2000,"Master","💎"),
                      (1800,"Diamond","💠"),(1600,"Platinum","🥇"),(1400,"Gold","🥈"),
                      (1200,"Silver","🥉"),(1000,"Bronze","🔸"),(0,"Debutant","🔹")]:
            if elo>=t: return n,e
        return "Debutant","🔹"

class DB:
    def __init__(self):
        DATA.mkdir(parents=True,exist_ok=True)
        self.d = json.load(open(PLAYERS,'r')) if PLAYERS.exists() else {}

    def save(self): json.dump(self.d,open(PLAYERS,'w'),indent=2)

    def get(self,name,ip=""):
        if name not in self.d:
            self.d[name]={'name':name,'elo':DEFAULT_ELO,'wins':0,'losses':0,'matches':0,'streak':0,'best':0}
        self.d[name]['ip']=ip; self.d[name]['seen']=datetime.now().isoformat()
        self.save(); return self.d[name]

    def match(self,w,l):
        if w not in self.d or l not in self.d: return None
        ow,ol = self.d[w]['elo'],self.d[l]['elo']
        self.d[w]['elo'],self.d[l]['elo'] = Elo.calc(ow,ol)
        self.d[w]['wins']+=1; self.d[w]['matches']+=1; self.d[w]['streak']+=1
        self.d[w]['best']=max(self.d[w]['best'],self.d[w]['streak'])
        self.d[l]['losses']+=1; self.d[l]['matches']+=1; self.d[l]['streak']=0
        self.save()
        return {'w':{'name':w,'old':ow,'new':self.d[w]['elo'],'d':self.d[w]['elo']-ow},
                'l':{'name':l,'old':ol,'new':self.d[l]['elo'],'d':self.d[l]['elo']-ol}}

    def top(self,n=50):
        res=[]
        for i,p in enumerate(sorted(self.d.values(),key=lambda x:x['elo'],reverse=True)[:n],1):
            r,e=Elo.rank(p['elo'])
            wr=(p['wins']/(p['wins']+p['losses'])*100) if p['wins']+p['losses']>0 else 0
            res.append({'#':i,'e':e,'name':p['name'],'elo':p['elo'],'rank':r,
                       'w':p['wins'],'l':p['losses'],'wr':round(wr,1),'m':p['matches'],'s':p['streak'],'bs':p['best']})
        return res

class Lobby:
    def __init__(self,db):
        self.db=db; self.q={}; self.lock=threading.Lock()

    def join(self,name,ip,conn):
        with self.lock:
            p=self.db.get(name,ip)
            self.q[name]={'p':p,'c':conn,'ip':ip,'t':time.time(),'s':False}
            r,e=Elo.rank(p['elo'])
            print(f"{C.G}[+] {e} {name} ({p['elo']} - {r}){C.X}")
            return p

    def leave(self,name):
        with self.lock:
            if name in self.q: del self.q[name]; print(f"{C.Y}[-] {name}{C.X}")

    def search(self,name):
        with self.lock:
            if name in self.q: self.q[name]['s']=True; self.q[name]['t']=time.time()

    def find(self,name):
        with self.lock:
            if name not in self.q: return None
            me=self.q[name]; elo=me['p']['elo']; wait=time.time()-me['t']
            rng=min(RANGE+wait*3,500); best=None; bd=99999
            for n,d in self.q.items():
                if n==name or not d['s']: continue
                diff=abs(elo-d['p']['elo'])
                if diff<=rng and diff<bd: best,bd=n,diff
            return best

    def match(self,p1,p2):
        with self.lock:
            if p1 not in self.q or p2 not in self.q: return None
            d1,d2=self.q.pop(p1),self.q.pop(p2)
            print(f"\n{C.M}{C.B}[MATCH] {p1}({d1['p']['elo']}) VS {p2}({d2['p']['elo']}){C.X}")
            return {'p1':{'n':p1,'elo':d1['p']['elo'],'ip':d1['ip']},
                    'p2':{'n':p2,'elo':d2['p']['elo'],'ip':d2['ip']},'host':d1['ip']}

    def status(self):
        with self.lock:
            ps=[]
            for n,d in self.q.items():
                r,e=Elo.rank(d['p']['elo'])
                ps.append({'n':n,'elo':d['p']['elo'],'r':r,'e':e,'s':d['s']})
            return {'online':len(self.q),'search':sum(1 for d in self.q.values() if d['s']),
                    'players':sorted(ps,key=lambda x:x['elo'],reverse=True)}

class Server:
    def __init__(self):
        self.db=DB(); self.lobby=Lobby(self.db); self.run=True

    def start(self):
        s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.bind(('0.0.0.0',PORT)); s.listen(50)
        print(f"\n{C.C}{C.B}{'='*60}\n{'KOF ULTIMATE ONLINE - MATCHMAKING ELO':^60}\n{'='*60}{C.X}\n")
        print(f"{C.G}[OK] Port {PORT}{C.X}\n")
        threading.Thread(target=self._auto,daemon=True).start()
        while self.run:
            try: c,a=s.accept(); threading.Thread(target=self._h,args=(c,a),daemon=True).start()
            except: pass

    def _h(self,c,a):
        ip,name=a[0],None
        try:
            c.settimeout(300)
            while True:
                data=c.recv(4096)
                if not data: break
                m=json.loads(data.decode()); act=m.get('a'); r={'s':'err'}
                if act=='join': name=m.get('n',f'P{random.randint(1000,9999)}'); p=self.lobby.join(name,ip,c); rk,em=Elo.rank(p['elo']); r={'s':'ok','p':p,'r':rk,'e':em}
                elif act=='search': self.lobby.search(name) if name else None; r={'s':'ok'}
                elif act=='cancel': self.lobby.q[name]['s']=False if name and name in self.lobby.q else None; r={'s':'ok'}
                elif act=='result': res=self.db.match(m.get('w'),m.get('l')); r={'s':'ok','res':res} if res else r; print(f"{C.G}[WIN] {m.get('w')} +{res['w']['d']}{C.X}") if res else None
                elif act=='lobby': r={'s':'ok','lobby':self.lobby.status()}
                elif act=='top': r={'s':'ok','top':self.db.top()}
                elif act=='leave': break
                c.send(json.dumps(r).encode())
        except: pass
        finally: self.lobby.leave(name) if name else None; c.close()

    def _auto(self):
        while self.run:
            time.sleep(2)
            with self.lobby.lock: searching=[n for n,d in self.lobby.q.items() if d['s']]
            for name in searching:
                opp=self.lobby.find(name)
                if opp:
                    match=self.lobby.match(name,opp)
                    if match:
                        for pn in [name,opp]:
                            try: self.lobby.q[pn]['c'].send(json.dumps({'a':'match','m':match}).encode()) if pn in self.lobby.q else None
                            except: pass

def client():
    print(f"\n{C.C}=== KOF ULTIMATE ONLINE ==={C.X}\n")
    srv=input("Serveur (localhost): ").strip() or 'localhost'
    name=input("Pseudo: ").strip() or f"P{random.randint(100,999)}"
    try:
        s=socket.socket(); s.connect((srv,PORT)); s.settimeout(300)
        s.send(json.dumps({'a':'join','n':name}).encode())
        r=json.loads(s.recv(4096).decode())
        if r['s']=='ok':
            p=r['p']; print(f"\n{C.G}{r['e']} {name} - {p['elo']} ELO ({r['r']}) | {p['wins']}W/{p['losses']}L{C.X}\n")
            while True:
                print(f"{C.W}1.Match 2.Lobby 3.Classement 4.Quit{C.X}")
                ch=input("> ").strip()
                if ch=='1':
                    s.send(json.dumps({'a':'search'}).encode()); print(f"{C.Y}Recherche...{C.X}")
                    while True:
                        data=s.recv(4096)
                        if data:
                            msg=json.loads(data.decode())
                            if msg.get('a')=='match':
                                m=msg['m']; print(f"\n{C.G}{C.B}MATCH!{C.X}\n  {m['p1']['n']}({m['p1']['elo']}) VS {m['p2']['n']}({m['p2']['elo']})\n  {C.C}Host: {m['host']}:7500{C.X}"); break
                            break
                elif ch=='2': s.send(json.dumps({'a':'lobby'}).encode()); r=json.loads(s.recv(4096).decode()); lb=r.get('lobby',{}); print(f"\n{C.C}Online:{lb.get('online',0)} Searching:{lb.get('search',0)}{C.X}"); [print(f"  {p['e']} {p['n']}: {p['elo']} {'(search)' if p['s'] else ''}") for p in lb.get('players',[])[:10]]
                elif ch=='3': s.send(json.dumps({'a':'top'}).encode()); r=json.loads(s.recv(4096).decode()); print(f"\n{C.M}{C.B}=== CLASSEMENT ==={C.X}"); [print(f"  {p['#']:2}. {p['e']} {p['name']}: {p['elo']} ({p['w']}W/{p['l']}L) {p['wr']}%") for p in r.get('top',[])[:20]]; print()
                elif ch=='4': s.send(json.dumps({'a':'leave'}).encode()); break
        s.close()
    except Exception as e: print(f"{C.R}Erreur: {e}{C.X}")

if __name__=="__main__":
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='client': client()
    else: print("\nUsage:\n  python matchmaking_elo.py         <- Serveur\n  python matchmaking_elo.py client  <- Client\n"); Server().start()
