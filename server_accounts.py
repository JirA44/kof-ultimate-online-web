#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE ONLINE - SERVEUR CENTRAL
Comptes persistants + Matchmaking + ELO
"""

import http.server
import socketserver
import json
import hashlib
import os
import time
import threading
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Configuration
PORT = 7700
DATA_DIR = Path(__file__).parent / "server_data"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"

# Couleurs console
class C:
    G = '\033[92m'
    R = '\033[91m'
    Y = '\033[93m'
    C = '\033[96m'
    M = '\033[95m'
    W = '\033[97m'
    B = '\033[1m'
    X = '\033[0m'

class Database:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.accounts = self._load(ACCOUNTS_FILE, {})
        self.sessions = self._load(SESSIONS_FILE, {})
        self.online = {}  # {username: {last_seen, status}}
        self.lock = threading.Lock()

    def _load(self, path, default):
        if path.exists():
            try:
                return json.load(open(path, 'r', encoding='utf-8'))
            except:
                return default
        return default

    def _save_accounts(self):
        json.dump(self.accounts, open(ACCOUNTS_FILE, 'w', encoding='utf-8'), indent=2)

    def _save_sessions(self):
        json.dump(self.sessions, open(SESSIONS_FILE, 'w', encoding='utf-8'), indent=2)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        with self.lock:
            username_lower = username.lower()

            # Validations
            if len(username) < 3:
                return {'success': False, 'error': 'Pseudo trop court (min 3)'}
            if len(username) > 20:
                return {'success': False, 'error': 'Pseudo trop long (max 20)'}
            if not username.replace('_', '').replace('-', '').isalnum():
                return {'success': False, 'error': 'Pseudo invalide (lettres, chiffres, _ -)'}
            if len(password) < 4:
                return {'success': False, 'error': 'Mot de passe trop court (min 4)'}
            if username_lower in self.accounts:
                return {'success': False, 'error': 'Ce pseudo est déjà pris'}

            # Créer le compte
            self.accounts[username_lower] = {
                'username': username,
                'password_hash': self.hash_password(password),
                'elo': 1000,
                'wins': 0,
                'losses': 0,
                'matches': 0,
                'streak': 0,
                'best_streak': 0,
                'created_at': datetime.now().isoformat(),
                'last_login': None
            }
            self._save_accounts()
            print(f"{C.G}[+] Nouveau compte: {username}{C.X}")
            return {'success': True, 'message': 'Compte créé!'}

    def login(self, username, password):
        with self.lock:
            username_lower = username.lower()
            account = self.accounts.get(username_lower)

            if not account:
                return {'success': False, 'error': 'Compte introuvable'}

            if account['password_hash'] != self.hash_password(password):
                return {'success': False, 'error': 'Mot de passe incorrect'}

            # Créer session
            import secrets
            token = secrets.token_hex(32)
            self.sessions[token] = {
                'username': account['username'],
                'created_at': time.time(),
                'expires_at': time.time() + 86400  # 24h
            }
            self._save_sessions()

            # Update last login
            account['last_login'] = datetime.now().isoformat()
            self._save_accounts()

            # Mark online
            self.online[account['username']] = {
                'last_seen': time.time(),
                'status': 'online'
            }

            print(f"{C.C}[>] Login: {account['username']} (ELO: {account['elo']}){C.X}")
            return {
                'success': True,
                'token': token,
                'account': {
                    'username': account['username'],
                    'elo': account['elo'],
                    'wins': account['wins'],
                    'losses': account['losses'],
                    'matches': account['matches'],
                    'streak': account['streak'],
                    'best_streak': account['best_streak']
                }
            }

    def validate_session(self, token):
        with self.lock:
            session = self.sessions.get(token)
            if not session:
                return None
            if time.time() > session['expires_at']:
                del self.sessions[token]
                self._save_sessions()
                return None

            username_lower = session['username'].lower()
            account = self.accounts.get(username_lower)
            if account:
                self.online[account['username']] = {
                    'last_seen': time.time(),
                    'status': 'online'
                }
            return account

    def logout(self, token):
        with self.lock:
            session = self.sessions.pop(token, None)
            if session:
                self.online.pop(session['username'], None)
                self._save_sessions()
            return {'success': True}

    def get_leaderboard(self, limit=50):
        with self.lock:
            sorted_accounts = sorted(
                self.accounts.values(),
                key=lambda x: x['elo'],
                reverse=True
            )[:limit]

            result = []
            for i, acc in enumerate(sorted_accounts, 1):
                wr = (acc['wins'] / (acc['wins'] + acc['losses']) * 100) if acc['wins'] + acc['losses'] > 0 else 0
                result.append({
                    'rank': i,
                    'username': acc['username'],
                    'elo': acc['elo'],
                    'wins': acc['wins'],
                    'losses': acc['losses'],
                    'winrate': round(wr, 1),
                    'streak': acc['streak'],
                    'online': acc['username'] in self.online
                })
            return result

    def get_online_players(self):
        with self.lock:
            # Nettoyer les joueurs inactifs (>5min)
            now = time.time()
            inactive = [u for u, d in self.online.items() if now - d['last_seen'] > 300]
            for u in inactive:
                del self.online[u]

            players = []
            for username, data in self.online.items():
                acc = self.accounts.get(username.lower())
                if acc:
                    players.append({
                        'username': acc['username'],
                        'elo': acc['elo'],
                        'wins': acc['wins'],
                        'losses': acc['losses'],
                        'status': data['status']
                    })
            return sorted(players, key=lambda x: x['elo'], reverse=True)

    def update_status(self, username, status):
        with self.lock:
            if username in self.online:
                self.online[username]['status'] = status
                self.online[username]['last_seen'] = time.time()

    def record_match(self, winner, loser):
        with self.lock:
            w_acc = self.accounts.get(winner.lower())
            l_acc = self.accounts.get(loser.lower())

            if not w_acc or not l_acc:
                return None

            # Calcul ELO
            K = 32
            w_elo, l_elo = w_acc['elo'], l_acc['elo']
            expected = 1 / (1 + 10 ** ((l_elo - w_elo) / 400))
            w_new = round(w_elo + K * (1 - expected))
            l_new = round(l_elo + K * (0 - (1 - expected)))

            # Update winner
            w_acc['elo'] = w_new
            w_acc['wins'] += 1
            w_acc['matches'] += 1
            w_acc['streak'] += 1
            w_acc['best_streak'] = max(w_acc['best_streak'], w_acc['streak'])

            # Update loser
            l_acc['elo'] = l_new
            l_acc['losses'] += 1
            l_acc['matches'] += 1
            l_acc['streak'] = 0

            self._save_accounts()

            print(f"{C.M}[MATCH] {winner} ({w_elo}→{w_new}) bat {loser} ({l_elo}→{l_new}){C.X}")

            return {
                'winner': {'username': winner, 'old_elo': w_elo, 'new_elo': w_new, 'delta': w_new - w_elo},
                'loser': {'username': loser, 'old_elo': l_elo, 'new_elo': l_new, 'delta': l_new - l_elo}
            }


# Singleton DB
db = Database()


class APIHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Disable default logging

    def _send_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self._send_response({})

    def do_GET(self):
        path = urlparse(self.path).path

        if path == '/api/leaderboard':
            self._send_response({'success': True, 'leaderboard': db.get_leaderboard()})

        elif path == '/api/online':
            self._send_response({'success': True, 'players': db.get_online_players()})

        elif path == '/api/status':
            self._send_response({
                'success': True,
                'server': 'KOF Ultimate Online',
                'accounts': len(db.accounts),
                'online': len(db.online)
            })

        else:
            self._send_response({'error': 'Not found'}, 404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(body) if body else {}
        except:
            data = {}

        path = urlparse(self.path).path

        if path == '/api/register':
            username = data.get('username', '')
            password = data.get('password', '')
            result = db.register(username, password)
            self._send_response(result)

        elif path == '/api/login':
            username = data.get('username', '')
            password = data.get('password', '')
            result = db.login(username, password)
            self._send_response(result)

        elif path == '/api/logout':
            token = data.get('token', '')
            result = db.logout(token)
            self._send_response(result)

        elif path == '/api/session':
            token = data.get('token', '')
            account = db.validate_session(token)
            if account:
                self._send_response({
                    'success': True,
                    'account': {
                        'username': account['username'],
                        'elo': account['elo'],
                        'wins': account['wins'],
                        'losses': account['losses'],
                        'matches': account['matches'],
                        'streak': account['streak']
                    }
                })
            else:
                self._send_response({'success': False, 'error': 'Session invalide'})

        elif path == '/api/status_update':
            token = data.get('token', '')
            status = data.get('status', 'online')
            account = db.validate_session(token)
            if account:
                db.update_status(account['username'], status)
                self._send_response({'success': True})
            else:
                self._send_response({'success': False})

        elif path == '/api/match':
            winner = data.get('winner', '')
            loser = data.get('loser', '')
            result = db.record_match(winner, loser)
            if result:
                self._send_response({'success': True, 'result': result})
            else:
                self._send_response({'success': False, 'error': 'Joueurs introuvables'})

        else:
            self._send_response({'error': 'Not found'}, 404)


def main():
    print(f"\n{C.C}{C.B}{'='*60}")
    print(f"{'KOF ULTIMATE ONLINE - SERVEUR CENTRAL':^60}")
    print(f"{'='*60}{C.X}\n")

    print(f"{C.W}Port:     {C.G}{PORT}{C.X}")
    print(f"{C.W}Data:     {C.G}{DATA_DIR}{C.X}")
    print(f"{C.W}Comptes:  {C.G}{len(db.accounts)}{C.X}")
    print()

    print(f"{C.Y}API Endpoints:{C.X}")
    print(f"  POST /api/register  - Créer un compte")
    print(f"  POST /api/login     - Se connecter")
    print(f"  POST /api/logout    - Se déconnecter")
    print(f"  POST /api/session   - Valider session")
    print(f"  POST /api/match     - Enregistrer match")
    print(f"  GET  /api/leaderboard - Classement")
    print(f"  GET  /api/online    - Joueurs en ligne")
    print(f"  GET  /api/status    - Status serveur")
    print()

    with socketserver.TCPServer(("", PORT), APIHandler) as httpd:
        print(f"{C.G}[OK] Serveur démarré sur http://localhost:{PORT}{C.X}")
        print(f"{C.Y}[!] Gardez cette fenêtre ouverte!{C.X}\n")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
