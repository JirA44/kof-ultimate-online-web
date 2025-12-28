#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST AUTOMATIQUE DES PERSONNAGES - KOF Ultimate Online
Lance des combats AI vs AI et détecte les crashs/freezes
"""

import os
import sys
import time
import subprocess
import psutil
from pathlib import Path
from datetime import datetime

GAME_DIR = Path(__file__).parent
CHARS_DIR = GAME_DIR / "chars"
DATA_DIR = GAME_DIR / "data"
IKEMEN_EXE = GAME_DIR / "Ikemen_GO.exe"

# Durée max d'un test (secondes) - si dépasse = freeze
MAX_TEST_TIME = 30

def get_all_chars():
    """Liste tous les personnages"""
    chars = []
    for d in CHARS_DIR.iterdir():
        if d.is_dir() and d.name not in ['ai', 'data', 'backup']:
            # Vérifier qu'il y a un .def
            if list(d.glob("*.def")):
                chars.append(d.name)
    return sorted(chars)

def create_test_roster(char1, char2="kfm"):
    """Crée un roster de test avec 2 personnages"""
    content = f"""; TEST ROSTER
[Characters]
{char1}, stages/Abyss-Rugal-Palace.def
{char2}, stages/Abyss-Rugal-Palace.def

[ExtraStages]
stages/Abyss-Rugal-Palace.def

[Options]
arcade.maxmatches = 1,0,0,0,0,0,0,0,0,0
"""
    roster_path = DATA_DIR / "select_autotest.def"
    roster_path.write_text(content, encoding='utf-8')
    return roster_path

def update_system_def(roster_name):
    """Met à jour system.def pour utiliser le roster de test"""
    system_def = DATA_DIR / "system.def"
    content = system_def.read_text(encoding='utf-8', errors='ignore')

    # Remplacer la ligne select
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if line.strip().startswith('select') and '=' in line:
            new_lines.append(f'select = {roster_name}')
        else:
            new_lines.append(line)

    system_def.write_text('\n'.join(new_lines), encoding='utf-8')

def is_game_running():
    """Vérifie si le jeu tourne"""
    for proc in psutil.process_iter(['name']):
        if 'ikemen' in proc.info['name'].lower():
            return True
    return False

def kill_game():
    """Tue le processus du jeu"""
    for proc in psutil.process_iter(['name', 'pid']):
        if 'ikemen' in proc.info['name'].lower():
            try:
                proc.kill()
            except:
                pass

def test_character(char_name, reference_char="kfm"):
    """
    Teste un personnage en lançant le jeu
    Retourne: (success, message)
    """
    print(f"  Testing {char_name}...", end=" ", flush=True)

    # Créer le roster de test
    create_test_roster(char_name, reference_char)
    update_system_def("select_autotest.def")

    # Tuer le jeu s'il tourne
    kill_game()
    time.sleep(1)

    # Lancer le jeu
    try:
        proc = subprocess.Popen(
            [str(IKEMEN_EXE)],
            cwd=str(GAME_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"❌ Erreur lancement: {e}")
        return False, f"Erreur lancement: {e}"

    # Attendre que le jeu démarre
    time.sleep(3)

    # Vérifier s'il tourne toujours
    start_time = time.time()
    crashed = False

    while time.time() - start_time < MAX_TEST_TIME:
        if proc.poll() is not None:
            # Le processus s'est terminé (crash probable)
            crashed = True
            break
        time.sleep(1)

    # Tuer le jeu
    kill_game()
    time.sleep(1)

    if crashed:
        print("❌ CRASH")
        return False, "Crash détecté"
    else:
        print("✅ OK (pas de crash en 30s)")
        return True, "Stable"

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║           TEST AUTOMATIQUE DES PERSONNAGES - KOF ULTIMATE ONLINE             ║
║                    Détection des crashs par AI vs AI                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Vérifier que kfm existe (personnage de référence)
    kfm_path = CHARS_DIR / "kfm"
    if not kfm_path.exists():
        print("❌ Personnage 'kfm' requis comme référence!")
        print("   Le test utilise kfm comme adversaire stable.")
        return

    chars = get_all_chars()
    print(f"📋 {len(chars)} personnages à tester\n")

    stable_chars = []
    crashed_chars = []

    # Tester chaque personnage
    for i, char in enumerate(chars, 1):
        print(f"[{i}/{len(chars)}]", end=" ")

        success, msg = test_character(char)

        if success:
            stable_chars.append(char)
        else:
            crashed_chars.append((char, msg))

        # Pause entre les tests
        time.sleep(2)

    # Résultats
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              RÉSULTATS                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ✅ Stables: {len(stable_chars):<60}║
║  ❌ Crashs: {len(crashed_chars):<61}║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Sauvegarder le roster stable
    if stable_chars:
        roster_content = "; ROSTER AUTO-TESTÉ - Personnages stables uniquement\n\n[Characters]\n"
        for char in stable_chars:
            roster_content += f"{char}, stages/Abyss-Rugal-Palace.def\n"
        roster_content += "\n[ExtraStages]\nstages/Abyss-Rugal-Palace.def\n"

        output_path = DATA_DIR / "select_auto_tested.def"
        output_path.write_text(roster_content, encoding='utf-8')
        print(f"✅ Roster sauvegardé: {output_path}")

    # Afficher les personnages qui ont crashé
    if crashed_chars:
        print("\n❌ Personnages instables:")
        for char, msg in crashed_chars[:20]:
            print(f"   - {char}: {msg}")

if __name__ == "__main__":
    main()
