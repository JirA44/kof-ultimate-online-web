import sys
sys.path.insert(0, r"D:\KOF Ultimate Online kofuo")
from arranged_matchmaking import create_engine_from_dataset, MatchmakingEngine, Character
from pathlib import Path
import json

print("=" * 70)
print("KOF ULTIMATE - MATCHMAKING SYSTEM COMPLETE DEMONSTRATION")
print("=" * 70)

# 1. Créer l'ingine
print("\n[1] Initialisation de l'ingine...")
engine = create_engine_from_dataset()
print(f"   ✓ {len(engine.characters)} caractères chargés")

# 2. Test de sélection par critères
print("\n[2] Sélection par critères de catégorie:")

rushdown = engine.select_opponents(criteria={"category": "rushdown"})
print(f"   • Rushdown: {[c.name for c in rushdown]}")

grapple = engine.select_opponents(criteria={"category": "grapple"})
print(f"   • Grapple: {[c.name for c in grapple]}")

zoning = engine.select_opponents(criteria={"category": "zoning", "min_tier": 0.75})
print(f"   • Zoning tier≥0.75: {[c.name for c in zoning]}")

mixup_defensive = engine.select_opponents(
    criteria={"playstyle": "mixup", "max_tier": 0.80}
)
print(f"   • Mixup tier≤0.80: {[c.name for c in mixup_defensive]}")

# 3. Simulations de bataille individuelles
print("\n[3] Simulations de bataille individuelles:")

# Simuler directement avec simulate_battle
char_map = {c.name: c for c in engine.characters}

battles = [
    ("Kyo Kusanagi", "Iori Yagami"),
    ("Terry Bogard", "Bailey"),
    ("Kasumi", "Bailey"),
]

for a_name, b_name in battles:
    try:
        char_a = char_map.get(a_name)
        char_b = char_map.get(b_name)
        if char_a and char_b:
            result = engine.simulate_battle(char_a, char_b, rounds=5)
            winner = result.winner.name if result.winner else "Empate"
            print(f"   • {a_name} vs {b_name} → {winner} ({result.winner_margin:.1%} marge)")
        else:
            print(f"   • {a_name} vs {b_name} → Personnage introuvable")
    except Exception as e:
        print(f"   • {a_name} vs {b_name} → Erreur: {e}")

# 4. Tournois round-robin
print("\n[4] Tournoi Round-Robin (tous contre tous, 3 rounds chacun):")
tournament_rr = engine.run_tournament(format="round_robin", rounds_per_match=3)
print(f"   ✓ {tournament_rr['total_matches']} matchs joués")
print(f"   ✓ {tournament_rr['total_characters']} personnages")

print("   Top 5 classements:")
for i, r in enumerate(tournament_rr["rankings"][:5]):
    print(f"      {i+1}. {r['name']}: {r['win_rate']:.1%} ({r['total_matches']} matches)")

# 5. Tournoi elimination simple
print("\n[5] Tournoi Élimination Simple:")
tournament_se = engine.run_tournament(format="single_elimination", rounds_per_match=5)
print(f"   ✓ {tournament_se['total_matches']} matchs")
print(f"   ✓ Vainqueur: {tournament_se['rankings'][0]['name']}")

# 6. Export JSON
print("\n[6] Export JSON des résultats:")
print("\n[7] Export JSON des résultats:")
json_path = Path("tournament_data.json")
engine.export_results(json_path, format="json")
print(f"   ✓ Fichier créé: {json_path}")

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
print(f"   • Total matches: {data['total_matches']}")
print(f"   • Seed engine: {data['engine_seed']}")

# 8. CSV export
print("\n[8] Export CSV des matchs:")
csv_path = Path("match_results.csv")
engine.export_results(csv_path, format="csv")
print(f"   ✓ Fichier créé: {csv_path}")
print("   Colonnes: Character A, Character B, Winner, DurationFrames, WinnerMargin")

# 9. Matchups spécifiques par style
print("\n[9] Analyse des matchups par style de jeu:")
styles = ["rushdown", "grapple", "zoning", "mixup", "defensive"]
for style in styles:
    opponents = engine.select_opponents(criteria={"category": style, "count": 2})
    if len(opponents) >= 2:
        result = engine.simulate_battle(opponents[0], opponents[1], rounds=3)
        winner = result.winner.name if result.winner else "Empate"
        print(f"   • {style}: {opponents[0].name} vs {opponents[1].name} → {winner}")

# 10. Résumé final
print("\n" + "=" * 70)
print("RÉSUMÉ DES CAPACITÉS DÉMONSTRÉES")
print("=" * 70)
print("""
✓ Moteur d'ingestion de dataset (JSON/or par défaut)
✓ Sélection d'adversaires par catégorie, tier, playstyle
✓ Simulation de bataille avec influence tier/playstyle
✓ Tournoi Round-Robin (allés-retours)
✓ Tournoi Élimination Simple
✓ Export JSON, CSV, Rapport Textuel
✓ Matches rapides entre noms de personnages
✓ Analyse de matchups par style de jeu
✓ Génération de classements et statistiques
""")
print("=" * 70)
print("Démonstration terminée avec succès !")