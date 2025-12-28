#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           KOF ULTIMATE ONLINE - SERVEUR COMPLET                              ║
║           Comptes + Matchmaking ELO + Classement                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import http.server
import socketserver
import json
import hashlib
import secrets
import time
import threading
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# ============================================================================
# CONFIGURATION
# ============================================================================
PORT = 7700
DATA_DIR = Path(__file__).parent / "server_data"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"

class C:
    G = '\033[92m'; R = '\033[91m'; Y = '\033[93m'
    C = '\033[96m'; M = '\033[95m'; W = '\033[97m'
    B = '\033[1m'; X = '\033[0m'

# ============================================================================
# DATABASE
# ============================================================================
class Database:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.accounts = self._load()
        self.sessions = {}        # token -> {username, expires}
        self.online = {}          # username -> {status, last_seen, elo}
        self.matchmaking = {}     # username -> {elo, since}
        self.lock = threading.Lock()

        # Ajouter les bots
        self._init_bots()

    def _load(self):
        if ACCOUNTS_FILE.exists():
            try:
                return json.load(open(ACCOUNTS_FILE, 'r', encoding='utf-8'))
            except:
                return {}
        return {}

    def _save(self):
        json.dump(self.accounts, open(ACCOUNTS_FILE, 'w', encoding='utf-8'), indent=2)

    def _init_bots(self):
        bots = [
            ('CPU-Legende', 2400, 'legendary'),
            ('CPU-Master', 2000, 'master'),
            ('CPU-Expert', 1700, 'expert'),
            ('CPU-Normal', 1400, 'normal'),
            ('CPU-Easy', 1100, 'easy'),
            ('CPU-Debutant', 800, 'beginner')
        ]
        for name, elo, diff in bots:
            key = f"bot_{name.lower()}"
            if key not in self.accounts:
                self.accounts[key] = {
                    'username': f"🤖 {name}",
                    'password_hash': '',
                    'elo': elo,
                    'wins': 100, 'losses': 20,
                    'is_bot': True,
                    'difficulty': diff
                }
            # Bots toujours online
            self.online[f"🤖 {name}"] = {'status': 'online', 'last_seen': time.time(), 'is_bot': True}
        self._save()

    def hash_pw(self, pw):
        return hashlib.sha256(pw.encode()).hexdigest()

    # ---------- COMPTES ----------
    def register(self, username, password):
        with self.lock:
            if len(username) < 3:
                return {'success': False, 'error': 'Pseudo trop court (min 3)'}
            if len(username) > 20:
                return {'success': False, 'error': 'Pseudo trop long (max 20)'}
            if not username.replace('_', '').replace('-', '').isalnum():
                return {'success': False, 'error': 'Caractères invalides'}
            if len(password) < 4:
                return {'success': False, 'error': 'Mot de passe trop court (min 4)'}

            key = username.lower()
            if key in self.accounts:
                return {'success': False, 'error': 'Pseudo déjà pris'}

            self.accounts[key] = {
                'username': username,
                'password_hash': self.hash_pw(password),
                'elo': 1000,
                'wins': 0, 'losses': 0, 'matches': 0,
                'streak': 0, 'best_streak': 0,
                'created': datetime.now().isoformat(),
                'is_bot': False
            }
            self._save()
            print(f"{C.G}[+] Nouveau compte: {username}{C.X}")
            return {'success': True}

    def login(self, username, password):
        with self.lock:
            key = username.lower()
            acc = self.accounts.get(key)

            if not acc:
                return {'success': False, 'error': 'Compte introuvable'}
            if acc.get('is_bot'):
                return {'success': False, 'error': 'Compte bot'}
            if acc['password_hash'] != self.hash_pw(password):
                return {'success': False, 'error': 'Mot de passe incorrect'}

            token = secrets.token_hex(32)
            self.sessions[token] = {
                'username': acc['username'],
                'expires': time.time() + 86400
            }
            self.online[acc['username']] = {
                'status': 'online',
                'last_seen': time.time(),
                'is_bot': False
            }

            print(f"{C.C}[>] Login: {acc['username']} (ELO: {acc['elo']}){C.X}")
            return {
                'success': True,
                'token': token,
                'account': self._public_account(acc)
            }

    def validate(self, token):
        session = self.sessions.get(token)
        if not session or time.time() > session['expires']:
            return None
        acc = self.accounts.get(session['username'].lower())
        if acc:
            self.online[acc['username']] = {
                'status': self.online.get(acc['username'], {}).get('status', 'online'),
                'last_seen': time.time(),
                'is_bot': False
            }
        return acc

    def logout(self, token):
        session = self.sessions.pop(token, None)
        if session:
            self.online.pop(session['username'], None)
            self.matchmaking.pop(session['username'], None)
        return {'success': True}

    def _public_account(self, acc):
        return {
            'username': acc['username'],
            'elo': acc['elo'],
            'wins': acc['wins'],
            'losses': acc['losses'],
            'streak': acc.get('streak', 0),
            'is_bot': acc.get('is_bot', False)
        }

    # ---------- MATCHMAKING ----------
    def start_search(self, username):
        with self.lock:
            acc = self.accounts.get(username.lower())
            if not acc:
                return {'success': False}

            self.matchmaking[username] = {
                'elo': acc['elo'],
                'since': time.time()
            }
            if username in self.online:
                self.online[username]['status'] = 'searching'

            print(f"{C.Y}[?] Recherche: {username} (ELO: {acc['elo']}){C.X}")
            return {'success': True}

    def cancel_search(self, username):
        with self.lock:
            self.matchmaking.pop(username, None)
            if username in self.online:
                self.online[username]['status'] = 'online'
            return {'success': True}

    def find_match(self, username):
        with self.lock:
            if username not in self.matchmaking:
                return {'success': False, 'found': False}

            my_data = self.matchmaking[username]
            my_elo = my_data['elo']
            wait_time = time.time() - my_data['since']

            # Range augmente avec le temps
            elo_range = min(150 + int(wait_time * 5), 500)

            # Chercher un adversaire
            for opp_name, opp_data in self.matchmaking.items():
                if opp_name == username:
                    continue
                if abs(my_elo - opp_data['elo']) <= elo_range:
                    # Match trouvé!
                    self.matchmaking.pop(username, None)
                    self.matchmaking.pop(opp_name, None)

                    if username in self.online:
                        self.online[username]['status'] = 'ingame'
                    if opp_name in self.online:
                        self.online[opp_name]['status'] = 'ingame'

                    opp_acc = self.accounts.get(opp_name.lower().replace('🤖 ', 'bot_'))
                    if not opp_acc:
                        for k, v in self.accounts.items():
                            if v['username'] == opp_name:
                                opp_acc = v
                                break

                    print(f"{C.M}[!] MATCH: {username} vs {opp_name}{C.X}")

                    return {
                        'success': True,
                        'found': True,
                        'opponent': self._public_account(opp_acc) if opp_acc else {'username': opp_name, 'elo': opp_data['elo']}
                    }

            # Chercher aussi les bots si pas de joueur
            if wait_time > 3:
                for name, data in self.online.items():
                    if data.get('is_bot') and name not in self.matchmaking:
                        # Trouver le bot le plus proche en ELO
                        for k, acc in self.accounts.items():
                            if acc['username'] == name:
                                if abs(my_elo - acc['elo']) <= elo_range + 200:
                                    self.matchmaking.pop(username, None)
                                    print(f"{C.M}[!] MATCH vs BOT: {username} vs {name}{C.X}")
                                    return {
                                        'success': True,
                                        'found': True,
                                        'opponent': self._public_account(acc)
                                    }

            return {'success': True, 'found': False, 'searching': True, 'range': elo_range}

    def challenge_bot(self, username, bot_name):
        with self.lock:
            # Trouver le bot
            bot_acc = None
            for k, acc in self.accounts.items():
                if acc['username'] == bot_name and acc.get('is_bot'):
                    bot_acc = acc
                    break

            if not bot_acc:
                return {'success': False, 'error': 'Bot introuvable'}

            if username in self.online:
                self.online[username]['status'] = 'ingame'

            print(f"{C.M}[!] DÉFI BOT: {username} vs {bot_name}{C.X}")
            return {
                'success': True,
                'opponent': self._public_account(bot_acc)
            }

    # ---------- MATCH RESULT ----------
    def record_match(self, winner, loser):
        with self.lock:
            # Trouver les comptes
            w_key = winner.lower().replace('🤖 ', 'bot_')
            l_key = loser.lower().replace('🤖 ', 'bot_')

            w_acc = self.accounts.get(w_key)
            l_acc = self.accounts.get(l_key)

            if not w_acc or not l_acc:
                return {'success': False}

            # Calcul ELO
            K = 32
            w_elo, l_elo = w_acc['elo'], l_acc['elo']
            expected = 1 / (1 + 10 ** ((l_elo - w_elo) / 400))
            w_new = round(w_elo + K * (1 - expected))
            l_new = round(l_elo + K * (-expected))

            # Update
            w_acc['elo'] = w_new
            w_acc['wins'] = w_acc.get('wins', 0) + 1
            w_acc['matches'] = w_acc.get('matches', 0) + 1
            w_acc['streak'] = w_acc.get('streak', 0) + 1
            w_acc['best_streak'] = max(w_acc.get('best_streak', 0), w_acc['streak'])

            l_acc['elo'] = l_new
            l_acc['losses'] = l_acc.get('losses', 0) + 1
            l_acc['matches'] = l_acc.get('matches', 0) + 1
            l_acc['streak'] = 0

            self._save()

            # Reset status
            if winner in self.online:
                self.online[winner]['status'] = 'online'
            if loser in self.online:
                self.online[loser]['status'] = 'online'

            print(f"{C.G}[✓] {winner} +{w_new-w_elo} | {loser} {l_new-l_elo}{C.X}")

            return {
                'success': True,
                'winner': {'username': winner, 'old': w_elo, 'new': w_new, 'delta': w_new - w_elo},
                'loser': {'username': loser, 'old': l_elo, 'new': l_new, 'delta': l_new - l_elo}
            }

    # ---------- LEADERBOARD ----------
    def get_leaderboard(self, limit=50):
        with self.lock:
            all_accounts = [a for a in self.accounts.values() if not a.get('is_bot')]
            sorted_accs = sorted(all_accounts, key=lambda x: x['elo'], reverse=True)[:limit]

            result = []
            for i, acc in enumerate(sorted_accs, 1):
                total = acc['wins'] + acc['losses']
                wr = (acc['wins'] / total * 100) if total > 0 else 0
                result.append({
                    'rank': i,
                    'username': acc['username'],
                    'elo': acc['elo'],
                    'wins': acc['wins'],
                    'losses': acc['losses'],
                    'winrate': round(wr, 1),
                    'online': acc['username'] in self.online
                })
            return result

    def get_online(self):
        with self.lock:
            now = time.time()
            # Nettoyer inactifs
            inactive = [u for u, d in self.online.items() if not d.get('is_bot') and now - d['last_seen'] > 300]
            for u in inactive:
                del self.online[u]

            players = []
            for username, data in self.online.items():
                # Trouver le compte
                key = username.lower().replace('🤖 ', 'bot_')
                acc = self.accounts.get(key)
                if acc:
                    players.append({
                        'username': acc['username'],
                        'elo': acc['elo'],
                        'status': data['status'],
                        'is_bot': acc.get('is_bot', False)
                    })

            return sorted(players, key=lambda x: (-1 if x['is_bot'] else 0, -x['elo']))


# ============================================================================
# API HANDLER
# ============================================================================
db = Database()

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _respond(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self._respond({})

    def do_GET(self):
        path = urlparse(self.path).path

        if path == '/api/leaderboard':
            self._respond({'success': True, 'leaderboard': db.get_leaderboard()})
        elif path == '/api/online':
            self._respond({'success': True, 'players': db.get_online()})
        elif path == '/api/status':
            self._respond({
                'success': True,
                'server': 'KOF Ultimate Online',
                'accounts': len([a for a in db.accounts.values() if not a.get('is_bot')]),
                'online': len([o for o in db.online.values() if not o.get('is_bot')]),
                'searching': len(db.matchmaking)
            })
        else:
            self._respond({'error': 'Not found'}, 404)

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}

        path = urlparse(self.path).path

        if path == '/api/register':
            self._respond(db.register(data.get('username', ''), data.get('password', '')))

        elif path == '/api/login':
            self._respond(db.login(data.get('username', ''), data.get('password', '')))

        elif path == '/api/logout':
            self._respond(db.logout(data.get('token', '')))

        elif path == '/api/session':
            acc = db.validate(data.get('token', ''))
            if acc:
                self._respond({'success': True, 'account': db._public_account(acc)})
            else:
                self._respond({'success': False})

        elif path == '/api/search':
            acc = db.validate(data.get('token', ''))
            if acc:
                self._respond(db.start_search(acc['username']))
            else:
                self._respond({'success': False})

        elif path == '/api/cancel':
            acc = db.validate(data.get('token', ''))
            if acc:
                self._respond(db.cancel_search(acc['username']))
            else:
                self._respond({'success': False})

        elif path == '/api/find':
            acc = db.validate(data.get('token', ''))
            if acc:
                self._respond(db.find_match(acc['username']))
            else:
                self._respond({'success': False})

        elif path == '/api/challenge':
            acc = db.validate(data.get('token', ''))
            if acc:
                self._respond(db.challenge_bot(acc['username'], data.get('bot', '')))
            else:
                self._respond({'success': False})

        elif path == '/api/match':
            self._respond(db.record_match(data.get('winner', ''), data.get('loser', '')))

        else:
            self._respond({'error': 'Not found'}, 404)


# ============================================================================
# MAIN
# ============================================================================
def main():
    print(f"\n{C.C}{C.B}{'═'*60}")
    print(f"{'KOF ULTIMATE ONLINE - SERVEUR':^60}")
    print(f"{'═'*60}{C.X}\n")

    print(f"  {C.W}Port:{C.X}      {C.G}{PORT}{C.X}")
    print(f"  {C.W}Comptes:{C.X}   {C.G}{len([a for a in db.accounts.values() if not a.get('is_bot')])}{C.X}")
    print(f"  {C.W}Bots:{C.X}      {C.G}6{C.X}")
    print()

    print(f"  {C.Y}Endpoints:{C.X}")
    print(f"    POST /api/register    - Créer compte")
    print(f"    POST /api/login       - Connexion")
    print(f"    POST /api/search      - Chercher match")
    print(f"    POST /api/find        - Trouver adversaire")
    print(f"    POST /api/challenge   - Défier bot")
    print(f"    POST /api/match       - Résultat match")
    print(f"    GET  /api/leaderboard - Classement")
    print(f"    GET  /api/online      - Joueurs en ligne")
    print()

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"  {C.G}[OK] http://localhost:{PORT}{C.X}")
        print(f"  {C.Y}[!] Gardez cette fenêtre ouverte!{C.X}\n")
        print(f"{'─'*60}\n")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
