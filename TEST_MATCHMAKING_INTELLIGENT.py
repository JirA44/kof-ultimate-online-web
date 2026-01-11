#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST MATCHMAKING INTELLIGENT
Simule plusieurs joueurs avec différents MMR qui testent le système de matchmaking
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class VirtualPlayer:
    """Un joueur virtuel avec son propre MMR et historique"""

    def __init__(self, name, skill_level):
        self.name = name
        self.skill_level = skill_level  # 1-10
        self.mmr = 1000 + (skill_level * 100)  # 1100 à 2000 MMR
        self.matches_played = 0
        self.wins = 0
        self.losses = 0
        self.match_history = []
        self.opponents_faced = []

    def get_win_probability(self, opponent):
        """Calcule la probabilité de victoire contre un adversaire"""
        mmr_diff = self.mmr - opponent.mmr
        # Formule Elo-like
        expected = 1 / (1 + 10 ** (-mmr_diff / 400))
        return expected

    def play_match(self, opponent):
        """Joue un match contre un adversaire"""
        win_prob = self.get_win_probability(opponent)

        # Simuler le résultat
        did_win = random.random() < win_prob

        # Mettre à jour les stats
        self.matches_played += 1
        opponent.matches_played += 1

        if did_win:
            self.wins += 1
            opponent.losses += 1
            result = "WIN"
        else:
            self.losses += 1
            opponent.wins += 1
            result = "LOSS"

        # Calculer le changement de MMR
        k_factor = 32
        expected_score = win_prob
        actual_score = 1 if did_win else 0
        mmr_change = int(k_factor * (actual_score - expected_score))

        self.mmr += mmr_change
        opponent.mmr -= mmr_change

        # Enregistrer dans l'historique
        match_data = {
            'opponent': opponent.name,
            'opponent_mmr': opponent.mmr + mmr_change,  # MMR avant le match
            'result': result,
            'mmr_before': self.mmr - mmr_change,
            'mmr_after': self.mmr,
            'mmr_change': mmr_change,
            'mmr_difference': abs(self.mmr - opponent.mmr),
            'timestamp': datetime.now().isoformat()
        }

        self.match_history.append(match_data)
        self.opponents_faced.append(opponent.name)

        return did_win, mmr_change

    def get_stats(self):
        """Retourne les statistiques du joueur"""
        winrate = (self.wins / self.matches_played * 100) if self.matches_played > 0 else 0
        avg_mmr_diff = sum(m['mmr_difference'] for m in self.match_history) / len(self.match_history) if self.match_history else 0

        return {
            'name': self.name,
            'skill_level': self.skill_level,
            'mmr': self.mmr,
            'matches': self.matches_played,
            'wins': self.wins,
            'losses': self.losses,
            'winrate': winrate,
            'avg_mmr_diff': avg_mmr_diff
        }

class MatchmakingTester:
    """Testeur de matchmaking avec joueurs virtuels"""

    def __init__(self):
        self.base_path = Path(r"D:\KOF Ultimate Online kofuo")
        self.players = []
        self.matchmaking_queue = []
        self.matches_completed = 0
        self.results_file = self.base_path / "matchmaking_test_results.json"

    def log(self, message, level="INFO"):
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✓",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "MATCH": "⚔️",
            "PLAYER": "👤"
        }
        print(f"{icons.get(level, '')} {message}")

    def create_players(self):
        """Crée une variété de joueurs virtuels"""
        self.log("Création des joueurs virtuels...", "INFO")

        # Débutants (MMR ~1100-1300)
        self.players.append(VirtualPlayer("Noob_Alex", 1))
        self.players.append(VirtualPlayer("Beginner_Bob", 2))
        self.players.append(VirtualPlayer("Newbie_Charlie", 3))

        # Intermédiaires (MMR ~1400-1600)
        self.players.append(VirtualPlayer("Average_Dave", 4))
        self.players.append(VirtualPlayer("Mid_Emma", 5))
        self.players.append(VirtualPlayer("Regular_Frank", 6))

        # Avancés (MMR ~1700-1900)
        self.players.append(VirtualPlayer("Pro_Grace", 7))
        self.players.append(VirtualPlayer("Expert_Henry", 8))
        self.players.append(VirtualPlayer("Master_Ivy", 9))

        # Elite (MMR ~2000+)
        self.players.append(VirtualPlayer("Legend_Jack", 10))

        for player in self.players:
            self.log(f"  Créé: {player.name} (Niveau {player.skill_level}, MMR {player.mmr})", "PLAYER")

        self.log(f"\n{len(self.players)} joueurs virtuels créés!", "SUCCESS")

    def find_match(self, player):
        """Trouve un adversaire approprié pour un joueur"""
        # Critères de matchmaking : MMR similaire (±200 MMR)
        mmr_range = 200

        # Trouver tous les adversaires potentiels
        potential_opponents = [
            p for p in self.players
            if p != player and abs(p.mmr - player.mmr) <= mmr_range
        ]

        if not potential_opponents:
            # Élargir la recherche si pas d'adversaire trouvé
            mmr_range = 400
            potential_opponents = [
                p for p in self.players
                if p != player and abs(p.mmr - player.mmr) <= mmr_range
            ]

        if potential_opponents:
            # Choisir l'adversaire le plus proche en MMR
            opponent = min(potential_opponents, key=lambda p: abs(p.mmr - player.mmr))
            return opponent

        return None

    def simulate_match(self, player1, player2):
        """Simule un match entre deux joueurs"""
        mmr_diff = abs(player1.mmr - player2.mmr)

        self.log(f"\n{'='*70}", "MATCH")
        self.log(f"MATCH #{self.matches_completed + 1}", "MATCH")
        self.log(f"  {player1.name} (MMR {player1.mmr}) VS {player2.name} (MMR {player2.mmr})", "MATCH")
        self.log(f"  Différence MMR: {mmr_diff}", "INFO")

        # Jouer le match
        p1_won, mmr_change = player1.play_match(player2)

        winner = player1.name if p1_won else player2.name
        self.log(f"  Résultat: {winner} gagne! (MMR change: ±{abs(mmr_change)})", "SUCCESS")
        self.log(f"  Nouveau MMR: {player1.name}={player1.mmr}, {player2.name}={player2.mmr}", "INFO")

        self.matches_completed += 1

        # Vérifier la qualité du matchmaking
        if mmr_diff <= 100:
            quality = "EXCELLENT"
        elif mmr_diff <= 200:
            quality = "GOOD"
        elif mmr_diff <= 300:
            quality = "ACCEPTABLE"
        else:
            quality = "POOR"

        self.log(f"  Qualité du match: {quality}", "INFO")

        return {
            'match_id': self.matches_completed,
            'player1': player1.name,
            'player2': player2.name,
            'player1_mmr': player1.mmr - mmr_change if p1_won else player1.mmr + abs(mmr_change),
            'player2_mmr': player2.mmr + mmr_change if p1_won else player2.mmr - abs(mmr_change),
            'mmr_difference': mmr_diff,
            'winner': winner,
            'quality': quality
        }

    def run_matchmaking_cycle(self, rounds=10):
        """Exécute plusieurs cycles de matchmaking"""
        self.log(f"\n{'='*70}", "INFO")
        self.log(f"DÉBUT DES TESTS DE MATCHMAKING", "INFO")
        self.log(f"{'='*70}\n", "INFO")

        match_records = []

        for round_num in range(1, rounds + 1):
            self.log(f"\n{'─'*70}", "INFO")
            self.log(f"ROUND {round_num}/{rounds}", "INFO")
            self.log(f"{'─'*70}", "INFO")

            # Mélanger les joueurs pour simuler l'ordre de queue
            available_players = self.players.copy()
            random.shuffle(available_players)

            matched_this_round = set()

            # Tenter de faire des matchs pour chaque joueur
            for player in available_players:
                if player in matched_this_round:
                    continue

                opponent = self.find_match(player)

                if opponent and opponent not in matched_this_round:
                    match_record = self.simulate_match(player, opponent)
                    match_records.append(match_record)
                    matched_this_round.add(player)
                    matched_this_round.add(opponent)

                    # Petit délai pour la lisibilité
                    time.sleep(0.5)

            self.log(f"\nRound {round_num} terminé: {len(matched_this_round)//2} matchs joués", "SUCCESS")

        return match_records

    def analyze_results(self, match_records):
        """Analyse les résultats du matchmaking"""
        self.log(f"\n{'='*70}", "INFO")
        self.log("ANALYSE DES RÉSULTATS", "INFO")
        self.log(f"{'='*70}\n", "INFO")

        # Statistiques globales
        total_matches = len(match_records)
        avg_mmr_diff = sum(m['mmr_difference'] for m in match_records) / total_matches if total_matches > 0 else 0

        quality_counts = defaultdict(int)
        for match in match_records:
            quality_counts[match['quality']] += 1

        self.log(f"Total de matchs: {total_matches}", "INFO")
        self.log(f"Différence MMR moyenne: {avg_mmr_diff:.1f}", "INFO")
        self.log(f"\nQualité des matchs:", "INFO")
        for quality in ['EXCELLENT', 'GOOD', 'ACCEPTABLE', 'POOR']:
            count = quality_counts[quality]
            percentage = (count / total_matches * 100) if total_matches > 0 else 0
            self.log(f"  {quality}: {count} ({percentage:.1f}%)", "SUCCESS" if quality in ['EXCELLENT', 'GOOD'] else "WARNING")

        # Statistiques par joueur
        self.log(f"\n{'─'*70}", "INFO")
        self.log("STATISTIQUES DES JOUEURS", "INFO")
        self.log(f"{'─'*70}\n", "INFO")

        players_sorted = sorted(self.players, key=lambda p: p.mmr, reverse=True)

        for player in players_sorted:
            stats = player.get_stats()
            self.log(
                f"{stats['name']:20} | "
                f"MMR: {stats['mmr']:4} | "
                f"W/L: {stats['wins']:2}/{stats['losses']:2} | "
                f"Winrate: {stats['winrate']:5.1f}% | "
                f"Avg MMR diff: {stats['avg_mmr_diff']:5.1f}",
                "PLAYER"
            )

        # Évaluation du système de matchmaking
        self.log(f"\n{'='*70}", "INFO")
        self.log("ÉVALUATION DU MATCHMAKING", "INFO")
        self.log(f"{'='*70}\n", "INFO")

        excellent_good_percentage = (quality_counts['EXCELLENT'] + quality_counts['GOOD']) / total_matches * 100 if total_matches > 0 else 0

        if excellent_good_percentage >= 80:
            rating = "EXCELLENT ⭐⭐⭐⭐⭐"
            self.log(f"Le système de matchmaking est {rating}", "SUCCESS")
        elif excellent_good_percentage >= 60:
            rating = "BON ⭐⭐⭐⭐"
            self.log(f"Le système de matchmaking est {rating}", "SUCCESS")
        elif excellent_good_percentage >= 40:
            rating = "MOYEN ⭐⭐⭐"
            self.log(f"Le système de matchmaking est {rating}", "WARNING")
        else:
            rating = "PAUVRE ⭐⭐"
            self.log(f"Le système de matchmaking est {rating}", "ERROR")

        self.log(f"\n{excellent_good_percentage:.1f}% des matchs sont de bonne qualité ou excellente", "INFO")

        if avg_mmr_diff <= 150:
            self.log("✓ La différence MMR moyenne est excellente (<150)", "SUCCESS")
        elif avg_mmr_diff <= 250:
            self.log("✓ La différence MMR moyenne est acceptable (<250)", "SUCCESS")
        else:
            self.log("⚠ La différence MMR moyenne est élevée (>250)", "WARNING")

        return {
            'total_matches': total_matches,
            'avg_mmr_diff': avg_mmr_diff,
            'quality_distribution': dict(quality_counts),
            'rating': rating,
            'player_stats': [p.get_stats() for p in players_sorted],
            'match_records': match_records
        }

    def save_results(self, results):
        """Sauvegarde les résultats dans un fichier JSON"""
        results['timestamp'] = datetime.now().isoformat()

        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        self.log(f"\nRésultats sauvegardés: {self.results_file.name}", "SUCCESS")

    def generate_report(self, results):
        """Génère un rapport HTML"""
        report_file = self.base_path / "MATCHMAKING_TEST_REPORT.html"

        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport Test Matchmaking - KOF Ultimate</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-card h3 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .stat-card p {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .quality-bar {{
            background: #f0f0f0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .quality-item {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}
        .quality-label {{
            width: 120px;
            font-weight: bold;
        }}
        .quality-progress {{
            flex: 1;
            height: 25px;
            background: #e0e0e0;
            border-radius: 5px;
            overflow: hidden;
            margin: 0 10px;
        }}
        .quality-fill {{
            height: 100%;
            transition: width 0.3s;
        }}
        .excellent {{ background: #4caf50; }}
        .good {{ background: #8bc34a; }}
        .acceptable {{ background: #ffc107; }}
        .poor {{ background: #f44336; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .rating {{
            text-align: center;
            font-size: 2em;
            color: #667eea;
            margin: 30px 0;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Rapport Test Matchmaking</h1>
        <p style="text-align: center; color: #666; margin-bottom: 30px;">
            KOF Ultimate Online - {datetime.now().strftime("%d/%m/%Y %H:%M")}
        </p>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>{results['total_matches']}</h3>
                <p>Matchs Joués</p>
            </div>
            <div class="stat-card">
                <h3>{results['avg_mmr_diff']:.0f}</h3>
                <p>Diff. MMR Moyenne</p>
            </div>
            <div class="stat-card">
                <h3>{len(results['player_stats'])}</h3>
                <p>Joueurs Testés</p>
            </div>
        </div>

        <div class="rating">
            {results['rating']}
        </div>

        <h2>Qualité des Matchs</h2>
        <div class="quality-bar">
"""

        for quality, color in [('EXCELLENT', 'excellent'), ('GOOD', 'good'),
                               ('ACCEPTABLE', 'acceptable'), ('POOR', 'poor')]:
            count = results['quality_distribution'].get(quality, 0)
            percentage = (count / results['total_matches'] * 100) if results['total_matches'] > 0 else 0

            html += f"""
            <div class="quality-item">
                <div class="quality-label">{quality}</div>
                <div class="quality-progress">
                    <div class="quality-fill {color}" style="width: {percentage}%"></div>
                </div>
                <div>{count} ({percentage:.1f}%)</div>
            </div>
"""

        html += """
        </div>

        <h2>Statistiques des Joueurs</h2>
        <table>
            <thead>
                <tr>
                    <th>Joueur</th>
                    <th>MMR</th>
                    <th>Matchs</th>
                    <th>Victoires</th>
                    <th>Défaites</th>
                    <th>Winrate</th>
                    <th>Avg MMR Diff</th>
                </tr>
            </thead>
            <tbody>
"""

        for player in results['player_stats']:
            html += f"""
                <tr>
                    <td>{player['name']}</td>
                    <td>{player['mmr']}</td>
                    <td>{player['matches']}</td>
                    <td>{player['wins']}</td>
                    <td>{player['losses']}</td>
                    <td>{player['winrate']:.1f}%</td>
                    <td>{player['avg_mmr_diff']:.0f}</td>
                </tr>
"""

        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)

        self.log(f"Rapport HTML généré: {report_file.name}", "SUCCESS")
        return report_file

    def run(self, rounds=10):
        """Lance le test complet du matchmaking"""
        self.create_players()

        print("\n")
        time.sleep(1)

        match_records = self.run_matchmaking_cycle(rounds)
        results = self.analyze_results(match_records)

        self.save_results(results)
        report_file = self.generate_report(results)

        # Ouvrir le rapport
        os.startfile(str(report_file))

        return results

if __name__ == "__main__":
    tester = MatchmakingTester()

    # Nombre de rounds à tester (10 = ~50 matchs)
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    print("\n" + "="*70)
    print("  🎮 TEST INTELLIGENT DU MATCHMAKING")
    print("="*70 + "\n")

    results = tester.run(rounds)

    print("\n" + "="*70)
    print("  ✓ TEST TERMINÉ!")
    print("="*70)
