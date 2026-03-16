#!/usr/bin/env python3
"""
KOF ULTIMATE ONLINE - BATTLENET VS TEST SYSTEM
===============================================
Lance le serveur matchmaking + 2 instances du jeu qui se connectent
et jouent ensemble via le systeme Battle.net.

Usage:
    python BATTLENET_VS_TEST.py              # Test complet
    python BATTLENET_VS_TEST.py --server     # Serveur seul
    python BATTLENET_VS_TEST.py --clients    # Clients seuls (serveur deja lance)
    python BATTLENET_VS_TEST.py --infinite   # Matchs infinis
"""

import subprocess
import threading
import socket
import json
import time
import random
import os
import sys
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_PATH = Path(r"D:\KOF Ultimate Online kofuo")
IKEMEN_EXE = BASE_PATH / "Ikemen_GO.exe"
SAVE_PATH = BASE_PATH / "save"
PROFILES_PATH = SAVE_PATH / "profiles"

# Serveur matchmaking
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999

# Personnages pour les matchs
CHARACTERS = [
    "kyo", "iori", "terry", "mai", "athena", "kula", "k", "ryo",
    "robert", "andy", "joe", "king", "leona", "clark", "ralf",
    "chizuru", "goenitz", "rugal", "orochi", "geese", "krauser",
    "benimaru", "shingo", "yuri", "takuma", "sie", "chin", "choi"
]

# Noms pour les joueurs IA
AI_NAMES = [
    "Dragon_Master", "Shadow_King", "FireFist_99", "Thunder_God",
    "Ice_Queen", "Night_Wolf", "Steel_Samurai", "Phoenix_Lord",
    "Storm_Rider", "Dark_Knight", "Flame_Emperor", "Wind_Dancer"
]


# ============================================================================
# MATCHMAKING SERVER
# ============================================================================

class MatchmakingServer:
    """Serveur de matchmaking simplifie pour les tests"""

    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.players = {}
        self.queue = []
        self.matches = []
        self.lock = threading.Lock()

    def start(self):
        """Demarre le serveur"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(10)
            self.running = True

            print(f"[SERVER] Demarre sur {self.host}:{self.port}")

            # Thread matchmaking
            threading.Thread(target=self._matchmaking_loop, daemon=True).start()

            # Accepter les connexions
            while self.running:
                try:
                    self.socket.settimeout(1.0)
                    client, addr = self.socket.accept()
                    threading.Thread(
                        target=self._handle_client,
                        args=(client, addr),
                        daemon=True
                    ).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[SERVER] Erreur: {e}")

        except Exception as e:
            print(f"[SERVER] Erreur demarrage: {e}")

    def stop(self):
        """Arrete le serveur"""
        self.running = False
        if self.socket:
            self.socket.close()
        print("[SERVER] Arrete")

    def _handle_client(self, client, addr):
        """Gere un client"""
        username = None

        try:
            data = client.recv(4096).decode('utf-8')
            if not data:
                return

            request = json.loads(data)
            action = request.get("action")

            if action == "connect":
                username = request.get("username")
                player_data = request.get("player_data", {})

                with self.lock:
                    self.players[username] = {
                        "username": username,
                        "socket": client,
                        "stats": player_data.get("stats", {}),
                        "status": "online"
                    }

                print(f"[SERVER] {username} connecte (MMR: {player_data.get('stats', {}).get('ranking_points', 1200)})")

                response = {"status": "success", "message": "Connecte"}
                client.send(json.dumps(response).encode('utf-8'))

                # Boucle de commandes
                self._command_loop(client, username)

        except Exception as e:
            print(f"[SERVER] Erreur client: {e}")
        finally:
            if username:
                self._disconnect(username)
            try:
                client.close()
            except:
                pass

    def _command_loop(self, client, username):
        """Boucle de commandes pour un joueur"""
        while self.running:
            try:
                client.settimeout(1.0)
                data = client.recv(4096).decode('utf-8')
                if not data:
                    break

                request = json.loads(data)
                action = request.get("action")

                if action == "search_match":
                    self._add_to_queue(username)
                    response = {"status": "success", "message": "Recherche lancee"}
                    client.send(json.dumps(response).encode('utf-8'))

                elif action == "cancel_search":
                    self._remove_from_queue(username)
                    response = {"status": "success", "message": "Recherche annulee"}
                    client.send(json.dumps(response).encode('utf-8'))

                elif action == "disconnect":
                    break

            except socket.timeout:
                continue
            except Exception as e:
                break

    def _add_to_queue(self, username):
        """Ajoute un joueur a la queue"""
        with self.lock:
            if username in self.players:
                self.players[username]["status"] = "searching"

                entry = {
                    "username": username,
                    "mmr": self.players[username]["stats"].get("ranking_points", 1200),
                    "joined_at": time.time()
                }
                self.queue.append(entry)
                print(f"[QUEUE] {username} en recherche (MMR: {entry['mmr']})")

    def _remove_from_queue(self, username):
        """Retire un joueur de la queue"""
        with self.lock:
            self.queue = [p for p in self.queue if p["username"] != username]
            if username in self.players:
                self.players[username]["status"] = "online"

    def _matchmaking_loop(self):
        """Boucle de matchmaking"""
        while self.running:
            with self.lock:
                if len(self.queue) >= 2:
                    # Trier par MMR
                    self.queue.sort(key=lambda x: x["mmr"])

                    # Matcher les 2 plus proches
                    p1 = self.queue.pop(0)
                    p2 = self.queue.pop(0)

                    self._create_match(p1["username"], p2["username"])

            time.sleep(0.5)

    def _create_match(self, user1, user2):
        """Cree un match entre 2 joueurs"""
        match_id = f"match_{len(self.matches)+1}_{int(time.time())}"

        match = {
            "match_id": match_id,
            "player1": user1,
            "player2": user2,
            "created_at": datetime.now().isoformat()
        }
        self.matches.append(match)

        print(f"\n{'='*50}")
        print(f"[MATCH FOUND] {user1} VS {user2}")
        print(f"{'='*50}\n")

        # Notifier les joueurs
        for username in [user1, user2]:
            if username in self.players:
                opponent = user2 if username == user1 else user1
                opp_data = self.players.get(opponent, {})

                notification = {
                    "event": "match_found",
                    "match_id": match_id,
                    "opponent": {
                        "username": opponent,
                        "mmr": opp_data.get("stats", {}).get("ranking_points", 1200)
                    }
                }

                try:
                    self.players[username]["socket"].send(
                        json.dumps(notification).encode('utf-8')
                    )
                    self.players[username]["status"] = "in_match"
                except:
                    pass

    def _disconnect(self, username):
        """Deconnecte un joueur"""
        self._remove_from_queue(username)
        with self.lock:
            if username in self.players:
                del self.players[username]
        print(f"[SERVER] {username} deconnecte")


# ============================================================================
# VIRTUAL PLAYER (CLIENT IA)
# ============================================================================

class VirtualPlayer:
    """Joueur virtuel qui se connecte au serveur"""

    def __init__(self, player_id, name=None):
        self.player_id = player_id
        self.name = name or random.choice(AI_NAMES) + f"_{random.randint(100, 999)}"
        self.socket = None
        self.connected = False
        self.in_match = False
        self.opponent = None
        self.mmr = random.randint(1000, 2000)
        self.process = None  # Processus du jeu

        # Stats du joueur
        self.stats = {
            "ranking_points": self.mmr,
            "level": random.randint(1, 50),
            "wins": random.randint(10, 200),
            "losses": random.randint(5, 100),
            "main_character": random.choice(CHARACTERS)
        }

    def connect(self, host=SERVER_HOST, port=SERVER_PORT):
        """Se connecte au serveur"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))

            # Envoyer la connexion
            request = {
                "action": "connect",
                "username": self.name,
                "player_data": {
                    "stats": self.stats
                }
            }
            self.socket.send(json.dumps(request).encode('utf-8'))

            # Recevoir la reponse
            response = json.loads(self.socket.recv(4096).decode('utf-8'))

            if response.get("status") == "success":
                self.connected = True
                print(f"[P{self.player_id}] {self.name} connecte (MMR: {self.mmr})")
                return True

        except Exception as e:
            print(f"[P{self.player_id}] Erreur connexion: {e}")

        return False

    def search_match(self):
        """Lance la recherche de match"""
        if not self.connected:
            return False

        try:
            request = {"action": "search_match", "mode": "ranked"}
            self.socket.send(json.dumps(request).encode('utf-8'))

            # Recevoir confirmation
            response = json.loads(self.socket.recv(4096).decode('utf-8'))

            if response.get("status") == "success":
                print(f"[P{self.player_id}] {self.name} en recherche...")
                return True

        except Exception as e:
            print(f"[P{self.player_id}] Erreur recherche: {e}")

        return False

    def wait_for_match(self, timeout=60):
        """Attend qu'un match soit trouve"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                self.socket.settimeout(1.0)
                data = self.socket.recv(4096).decode('utf-8')

                if data:
                    event = json.loads(data)

                    if event.get("event") == "match_found":
                        self.in_match = True
                        self.opponent = event.get("opponent", {})
                        print(f"[P{self.player_id}] Match trouve! VS {self.opponent.get('username')}")
                        return True

            except socket.timeout:
                continue
            except Exception as e:
                print(f"[P{self.player_id}] Erreur attente: {e}")
                break

        return False

    def launch_game(self, as_host=False, opponent_ip="127.0.0.1"):
        """Lance le jeu pour jouer le match"""
        if not IKEMEN_EXE.exists():
            print(f"[P{self.player_id}] Jeu non trouve: {IKEMEN_EXE}")
            return False

        # Creer une config personnalisee
        config = self._create_config(as_host, opponent_ip)

        # Arguments de lancement
        args = [str(IKEMEN_EXE)]
        args.extend(["-config", str(config)])

        try:
            self.process = subprocess.Popen(
                args,
                cwd=str(BASE_PATH),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"[P{self.player_id}] Jeu lance (PID: {self.process.pid})")
            return True

        except Exception as e:
            print(f"[P{self.player_id}] Erreur lancement: {e}")
            return False

    def _create_config(self, as_host, opponent_ip):
        """Cree une config pour cette instance"""
        config_path = SAVE_PATH / f"config_p{self.player_id}.json"

        # Charger config de base
        base_config = SAVE_PATH / "config.json"
        if base_config.exists():
            with open(base_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}

        # Modifier pour netplay
        config["Fullscreen"] = False
        config["GameWidth"] = 640
        config["GameHeight"] = 480
        config["Difficulty"] = 8

        # Position fenetre
        if self.player_id == 1:
            config["WindowX"] = 50
            config["WindowY"] = 50
        else:
            config["WindowX"] = 700
            config["WindowY"] = 50

        # Config reseau
        if as_host:
            config["ListenPort"] = "7500"
        else:
            if "IP" not in config:
                config["IP"] = {}
            config["IP"]["default"] = f"{opponent_ip}:7500"

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        return config_path

    def disconnect(self):
        """Se deconnecte"""
        try:
            if self.socket:
                request = {"action": "disconnect"}
                self.socket.send(json.dumps(request).encode('utf-8'))
                self.socket.close()
        except:
            pass

        if self.process:
            self.process.terminate()

        self.connected = False
        print(f"[P{self.player_id}] {self.name} deconnecte")


# ============================================================================
# BATTLENET TEST SYSTEM
# ============================================================================

class BattleNetTest:
    """Systeme de test Battle.net complet"""

    def __init__(self):
        self.server = None
        self.server_thread = None
        self.players = []
        self.match_count = 0

    def start_server(self):
        """Demarre le serveur matchmaking"""
        print("\n[SYSTEM] Demarrage du serveur matchmaking...")

        self.server = MatchmakingServer()
        self.server_thread = threading.Thread(target=self.server.start, daemon=True)
        self.server_thread.start()

        time.sleep(1)  # Attendre que le serveur soit pret
        return True

    def create_players(self, count=2):
        """Cree les joueurs virtuels"""
        print(f"\n[SYSTEM] Creation de {count} joueurs virtuels...")

        self.players = []
        for i in range(count):
            player = VirtualPlayer(i + 1)
            self.players.append(player)

        return True

    def connect_players(self):
        """Connecte tous les joueurs au serveur"""
        print("\n[SYSTEM] Connexion des joueurs...")

        for player in self.players:
            if not player.connect():
                return False
            time.sleep(0.5)

        return True

    def run_match(self):
        """Execute un match complet"""
        self.match_count += 1

        print(f"\n{'='*60}")
        print(f"  MATCH #{self.match_count}")
        print(f"{'='*60}")

        # Les joueurs lancent la recherche
        for player in self.players:
            player.search_match()
            time.sleep(0.3)

        # Attendre le match
        threads = []
        for player in self.players:
            t = threading.Thread(target=player.wait_for_match)
            t.start()
            threads.append(t)

        for t in threads:
            t.join(timeout=30)

        # Verifier si le match est trouve
        if all(p.in_match for p in self.players):
            print("\n[SYSTEM] Match confirme! Lancement des jeux...")

            # Lancer le jeu pour chaque joueur
            # P1 = host, P2 = client
            self.players[0].launch_game(as_host=True)
            time.sleep(2)
            self.players[1].launch_game(as_host=False, opponent_ip="127.0.0.1")

            print("\n[SYSTEM] Jeux lances! Les IA vont jouer...")

            # Attendre la fin du match (surveiller les processus)
            while any(p.process and p.process.poll() is None for p in self.players):
                time.sleep(1)

            print(f"\n[SYSTEM] Match #{self.match_count} termine!")

            # Reset pour le prochain match
            for player in self.players:
                player.in_match = False
                player.opponent = None

            return True
        else:
            print("\n[SYSTEM] Echec du matchmaking")
            return False

    def run_infinite(self):
        """Mode matchs infinis"""
        print("\n[SYSTEM] Mode infini - Ctrl+C pour arreter")

        try:
            while True:
                if not self.run_match():
                    time.sleep(5)  # Pause en cas d'echec
                time.sleep(3)  # Pause entre les matchs

        except KeyboardInterrupt:
            print("\n\n[SYSTEM] Arret demande")

    def cleanup(self):
        """Nettoie tout"""
        print("\n[SYSTEM] Nettoyage...")

        for player in self.players:
            player.disconnect()

        if self.server:
            self.server.stop()

        print("[SYSTEM] Termine")

    def show_stats(self):
        """Affiche les stats de la session"""
        print(f"\n{'='*40}")
        print(f"  STATISTIQUES DE SESSION")
        print(f"{'='*40}")
        print(f"  Matchs joues: {self.match_count}")
        if self.server:
            print(f"  Matchs totaux serveur: {len(self.server.matches)}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="KOF Ultimate Online - Battle.net VS Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python BATTLENET_VS_TEST.py              # Test complet (1 match)
  python BATTLENET_VS_TEST.py --matches 5  # 5 matchs
  python BATTLENET_VS_TEST.py --infinite   # Matchs infinis
  python BATTLENET_VS_TEST.py --server     # Serveur seul
        """
    )

    parser.add_argument('--server', '-s', action='store_true',
                        help='Lancer le serveur seul')
    parser.add_argument('--clients', '-c', action='store_true',
                        help='Lancer les clients seuls (serveur deja actif)')
    parser.add_argument('--matches', '-m', type=int, default=1,
                        help='Nombre de matchs (defaut: 1)')
    parser.add_argument('--infinite', '-i', action='store_true',
                        help='Mode matchs infinis')
    parser.add_argument('--players', '-p', type=int, default=2,
                        help='Nombre de joueurs (defaut: 2)')

    args = parser.parse_args()

    print("\n" + "="*60)
    print("  KOF ULTIMATE ONLINE - BATTLENET VS TEST")
    print("="*60)

    test = BattleNetTest()

    try:
        if args.server:
            # Mode serveur seul
            test.start_server()
            print("\n[SYSTEM] Serveur actif. Ctrl+C pour arreter.")
            while True:
                time.sleep(1)

        else:
            # Mode complet
            if not args.clients:
                test.start_server()

            test.create_players(args.players)
            test.connect_players()

            if args.infinite:
                test.run_infinite()
            else:
                for i in range(args.matches):
                    if i > 0:
                        print(f"\n[PAUSE] Prochain match dans 3 secondes...")
                        time.sleep(3)
                    test.run_match()

            test.show_stats()

    except KeyboardInterrupt:
        print("\n\n[SYSTEM] Interruption utilisateur")

    finally:
        test.cleanup()


if __name__ == "__main__":
    main()
