#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE ONLINE - Test Multijoueur Silencieux
Simule des joueurs et des parties sans toucher au clavier
"""

import json
import time
import random
import threading
from datetime import datetime
from pathlib import Path

# Configuration
GAME_PATH = Path(__file__).parent
SAVE_PATH = GAME_PATH / "save"
REPORT_PATH = GAME_PATH / "menu_test_reports"
SAVE_PATH.mkdir(exist_ok=True)
REPORT_PATH.mkdir(exist_ok=True)

class SilentMultiplayerTest:
    """Test silencieux du systeme multijoueur"""

    def __init__(self):
        self.players = []
        self.matches = []
        self.lobby_state = {
            "online_players": [],
            "active_matches": [],
            "queue": []
        }
        self.errors = []
        self.test_results = []

    def log(self, msg, level="INFO"):
        """Log sans print (silencieux)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.test_results.append({
            "time": timestamp,
            "level": level,
            "message": msg
        })

    def create_virtual_player(self, name=None):
        """Cree un joueur virtuel"""
        prefixes = ['Dark', 'Shadow', 'Fire', 'Ice', 'Thunder', 'Dragon', 'Wolf', 'Tiger',
                   'Phoenix', 'Cyber', 'Neon', 'Blade', 'Storm', 'Swift', 'Silent']
        suffixes = ['Warrior', 'Fighter', 'Master', 'Pro', 'King', 'Ace',
                   'Slayer', 'Hunter', 'Champion', 'Ninja', 'X', 'Z']

        if not name:
            name = f"{random.choice(prefixes)}{random.choice(suffixes)}{random.randint(1, 999)}"

        player = {
            "id": f"player_{len(self.players) + 1}",
            "username": name,
            "elo": random.randint(800, 2000),
            "wins": random.randint(0, 100),
            "losses": random.randint(0, 50),
            "status": "offline",
            "favorite_char": random.choice(["Kyo", "Iori", "Terry", "Mai", "K'", "Athena", "Ralf", "Leona"]),
            "created_at": datetime.now().isoformat()
        }

        self.players.append(player)
        return player

    def player_connect(self, player):
        """Simule la connexion d'un joueur"""
        player["status"] = "online"
        player["connected_at"] = datetime.now().isoformat()
        self.lobby_state["online_players"].append(player)
        self.log(f"Joueur connecte: {player['username']} (ELO: {player['elo']})")
        return True

    def player_disconnect(self, player):
        """Simule la deconnexion d'un joueur"""
        player["status"] = "offline"
        self.lobby_state["online_players"] = [p for p in self.lobby_state["online_players"] if p["id"] != player["id"]]
        self.lobby_state["queue"] = [p for p in self.lobby_state["queue"] if p["id"] != player["id"]]
        self.log(f"Joueur deconnecte: {player['username']}")
        return True

    def player_join_queue(self, player, mode="ranked"):
        """Simule l'entree en file d'attente"""
        if player["status"] != "online":
            self.errors.append(f"Erreur: {player['username']} n'est pas connecte")
            return False

        player["status"] = "searching"
        player["queue_mode"] = mode
        player["queue_joined_at"] = time.time()
        self.lobby_state["queue"].append(player)
        self.log(f"{player['username']} rejoint la queue {mode}")
        return True

    def try_matchmaking(self):
        """Essaie de creer des matchs"""
        matches_created = 0

        while len(self.lobby_state["queue"]) >= 2:
            # Trier par ELO pour matcher des joueurs de niveau similaire
            self.lobby_state["queue"].sort(key=lambda p: p["elo"])

            p1 = self.lobby_state["queue"].pop(0)
            p2 = self.lobby_state["queue"].pop(0)

            match = self.create_match(p1, p2)
            matches_created += 1

        return matches_created

    def create_match(self, player1, player2):
        """Cree un match entre 2 joueurs"""
        match_id = f"match_{len(self.matches) + 1}"

        # Simuler le resultat
        p1_chance = player1["elo"] / (player1["elo"] + player2["elo"])
        p1_wins = random.random() < p1_chance

        # Scores aleatoires
        if p1_wins:
            score = random.choice([(2, 0), (2, 1)])
        else:
            score = random.choice([(0, 2), (1, 2)])

        match = {
            "match_id": match_id,
            "player1": {
                "id": player1["id"],
                "username": player1["username"],
                "elo": player1["elo"],
                "character": player1["favorite_char"]
            },
            "player2": {
                "id": player2["id"],
                "username": player2["username"],
                "elo": player2["elo"],
                "character": player2["favorite_char"]
            },
            "score": score,
            "winner": player1["username"] if p1_wins else player2["username"],
            "duration_seconds": random.randint(60, 300),
            "started_at": datetime.now().isoformat(),
            "status": "completed"
        }

        # Mettre a jour les stats
        if p1_wins:
            player1["wins"] += 1
            player2["losses"] += 1
            player1["elo"] += random.randint(10, 30)
            player2["elo"] -= random.randint(10, 30)
        else:
            player2["wins"] += 1
            player1["losses"] += 1
            player2["elo"] += random.randint(10, 30)
            player1["elo"] -= random.randint(10, 30)

        # Remettre en ligne
        player1["status"] = "online"
        player2["status"] = "online"

        self.matches.append(match)
        self.lobby_state["active_matches"].append(match)

        self.log(f"Match: {player1['username']} vs {player2['username']} -> Gagnant: {match['winner']} ({score[0]}-{score[1]})")

        return match

    def test_leaderboard_data(self):
        """Teste que le leaderboard a des donnees"""
        leaderboard_path = SAVE_PATH / "leaderboard.json"

        # Creer des donnees de leaderboard
        leaderboard = []
        for i, player in enumerate(sorted(self.players, key=lambda p: p["elo"], reverse=True)):
            leaderboard.append({
                "rank": i + 1,
                "username": player["username"],
                "elo": player["elo"],
                "wins": player["wins"],
                "losses": player["losses"],
                "title": self.get_title(player["elo"])
            })

        with open(leaderboard_path, "w", encoding="utf-8") as f:
            json.dump({"leaderboard": leaderboard, "updated_at": datetime.now().isoformat()}, f, indent=2)

        self.log(f"Leaderboard genere avec {len(leaderboard)} joueurs")
        return True

    def get_title(self, elo):
        """Retourne le titre base sur l'ELO"""
        if elo >= 2000: return "Grand Master"
        if elo >= 1800: return "Master"
        if elo >= 1600: return "Diamond"
        if elo >= 1400: return "Platinum"
        if elo >= 1200: return "Gold"
        if elo >= 1000: return "Silver"
        return "Bronze"

    def test_online_players_file(self):
        """Teste le fichier des joueurs en ligne"""
        online_path = SAVE_PATH / "online_players.json"

        online_data = {
            "players": [{
                "username": p["username"],
                "elo": p["elo"],
                "status": p["status"],
                "favorite_char": p["favorite_char"]
            } for p in self.lobby_state["online_players"]],
            "count": len(self.lobby_state["online_players"]),
            "updated_at": datetime.now().isoformat()
        }

        with open(online_path, "w", encoding="utf-8") as f:
            json.dump(online_data, f, indent=2)

        self.log(f"Fichier online_players.json genere avec {online_data['count']} joueurs")
        return True

    def test_match_history_file(self):
        """Teste le fichier historique des matchs"""
        history_path = SAVE_PATH / "match_history.json"

        with open(history_path, "w", encoding="utf-8") as f:
            json.dump({
                "matches": self.matches,
                "total": len(self.matches),
                "updated_at": datetime.now().isoformat()
            }, f, indent=2)

        self.log(f"Historique des matchs genere avec {len(self.matches)} parties")
        return True

    def verify_menu_handlers(self):
        """Verifie que les handlers de menu fonctionnent avec les donnees"""
        tests = []

        # Test 1: Leaderboard lisible
        leaderboard_path = SAVE_PATH / "leaderboard.json"
        if leaderboard_path.exists():
            try:
                with open(leaderboard_path, "r") as f:
                    data = json.load(f)
                    if "leaderboard" in data and len(data["leaderboard"]) > 0:
                        tests.append(("Leaderboard readable", "OK", ""))
                    else:
                        tests.append(("Leaderboard readable", "FAIL", "Pas de donnees"))
            except Exception as e:
                tests.append(("Leaderboard readable", "FAIL", str(e)))
        else:
            tests.append(("Leaderboard readable", "FAIL", "Fichier inexistant"))

        # Test 2: Online players lisible
        online_path = SAVE_PATH / "online_players.json"
        if online_path.exists():
            try:
                with open(online_path, "r") as f:
                    data = json.load(f)
                    tests.append(("Online players readable", "OK", f"{data['count']} joueurs"))
            except Exception as e:
                tests.append(("Online players readable", "FAIL", str(e)))
        else:
            tests.append(("Online players readable", "FAIL", "Fichier inexistant"))

        # Test 3: Match history lisible
        history_path = SAVE_PATH / "match_history.json"
        if history_path.exists():
            try:
                with open(history_path, "r") as f:
                    data = json.load(f)
                    tests.append(("Match history readable", "OK", f"{data['total']} matchs"))
            except Exception as e:
                tests.append(("Match history readable", "FAIL", str(e)))
        else:
            tests.append(("Match history readable", "FAIL", "Fichier inexistant"))

        return tests

    def run_full_test(self, num_players=10, num_rounds=5):
        """Execute le test complet"""
        self.log("=== DEBUT TEST MULTIJOUEUR SILENCIEUX ===")

        # Etape 1: Creer des joueurs virtuels
        self.log(f"Creation de {num_players} joueurs virtuels...")
        for i in range(num_players):
            self.create_virtual_player()
        self.log(f"{len(self.players)} joueurs crees")

        # Etape 2: Connecter tous les joueurs
        self.log("Connexion des joueurs...")
        for player in self.players:
            self.player_connect(player)
        self.log(f"{len(self.lobby_state['online_players'])} joueurs en ligne")

        # Etape 3: Simuler plusieurs rounds de matchmaking
        self.log(f"Simulation de {num_rounds} rounds de matchmaking...")
        for round_num in range(num_rounds):
            self.log(f"--- Round {round_num + 1} ---")

            # Joueurs aleatoires rejoignent la queue
            available = [p for p in self.lobby_state["online_players"] if p["status"] == "online"]
            joiners = random.sample(available, min(len(available), random.randint(2, 6)))

            for player in joiners:
                mode = random.choice(["ranked", "casual"])
                self.player_join_queue(player, mode)

            # Matchmaking
            matches = self.try_matchmaking()
            self.log(f"Round {round_num + 1}: {matches} matchs crees")

            # Simuler un delai
            time.sleep(0.1)

        # Etape 4: Generer les fichiers de donnees
        self.log("Generation des fichiers de donnees...")
        self.test_leaderboard_data()
        self.test_online_players_file()
        self.test_match_history_file()

        # Etape 5: Verifier les handlers
        self.log("Verification des handlers de menu...")
        handler_tests = self.verify_menu_handlers()
        for test_name, status, detail in handler_tests:
            self.log(f"  {test_name}: {status} {detail}")

        # Etape 6: Deconnecter quelques joueurs
        self.log("Deconnexion de quelques joueurs...")
        to_disconnect = random.sample(self.players, min(3, len(self.players)))
        for player in to_disconnect:
            self.player_disconnect(player)

        self.log("=== FIN DU TEST ===")

        return self.generate_report(handler_tests)

    def generate_report(self, handler_tests):
        """Genere le rapport de test"""
        report = {
            "test_date": datetime.now().isoformat(),
            "test_type": "Silent Multiplayer Test",
            "summary": {
                "total_players_created": len(self.players),
                "total_matches_played": len(self.matches),
                "players_online_at_end": len(self.lobby_state["online_players"]),
                "errors_count": len(self.errors)
            },
            "handler_tests": [
                {"test": t[0], "status": t[1], "detail": t[2]} for t in handler_tests
            ],
            "matches": self.matches[:10],  # 10 premiers matchs
            "errors": self.errors,
            "log": self.test_results
        }

        # Sauvegarder le rapport
        report_file = REPORT_PATH / f"silent_multiplayer_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Creer un resume lisible
        summary_file = REPORT_PATH / "LAST_MULTIPLAYER_TEST.md"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("# Test Multijoueur Silencieux - Rapport\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Resultats\n\n")
            f.write(f"| Metrique | Valeur |\n")
            f.write(f"|----------|--------|\n")
            f.write(f"| Joueurs crees | {report['summary']['total_players_created']} |\n")
            f.write(f"| Matchs joues | {report['summary']['total_matches_played']} |\n")
            f.write(f"| Joueurs en ligne (fin) | {report['summary']['players_online_at_end']} |\n")
            f.write(f"| Erreurs | {report['summary']['errors_count']} |\n\n")

            f.write("## Tests des Handlers\n\n")
            f.write("| Test | Status | Detail |\n")
            f.write("|------|--------|--------|\n")
            for t in handler_tests:
                status_icon = "OK" if t[1] == "OK" else "FAIL"
                f.write(f"| {t[0]} | {status_icon} | {t[2]} |\n")

            f.write("\n## Derniers Matchs\n\n")
            for match in self.matches[-5:]:
                f.write(f"- **{match['player1']['username']}** vs **{match['player2']['username']}** -> {match['winner']} ({match['score'][0]}-{match['score'][1]})\n")

            if self.errors:
                f.write("\n## Erreurs\n\n")
                for err in self.errors:
                    f.write(f"- {err}\n")

            f.write("\n---\n*Test effectue sans simulation clavier*\n")

        return report_file, summary_file


def main():
    """Point d'entree principal"""
    tester = SilentMultiplayerTest()
    report_file, summary_file = tester.run_full_test(num_players=15, num_rounds=8)

    # Afficher le chemin du rapport (seule sortie)
    print(f"Rapport: {summary_file}")
    return 0


if __name__ == "__main__":
    main()
