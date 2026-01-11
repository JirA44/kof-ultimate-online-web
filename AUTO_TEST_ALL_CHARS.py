#!/usr/bin/env python3
"""
KOF Ultimate Online - Testeur Automatique Complet
Teste TOUS les personnages automatiquement sans intervention
"""

import subprocess
import time
import os
import json
import psutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"D:\KOF Ultimate Online")
GAME_EXE = BASE_DIR / "Ikemen_GO.exe"
DATA_DIR = BASE_DIR / "data"
CHARS_DIR = BASE_DIR / "chars"
RESULTS_FILE = "auto_test_results.json"

# Temps d'attente
GAME_STARTUP_TIME = 5      # Secondes pour demarrer
CHAR_LOAD_TIME = 3         # Secondes pour charger un perso
FIGHT_TIME = 8             # Secondes de combat
TOTAL_TIMEOUT = 20         # Timeout total par test

class AutoTester:
    def __init__(self):
        self.results = {
            'date': datetime.now().isoformat(),
            'passed': [],
            'crashed': [],
            'errors': []
        }
        self.log_lines = []

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {msg}"
        print(line)
        self.log_lines.append(line)

    def get_all_char_folders(self):
        """Liste tous les dossiers de personnages"""
        if not CHARS_DIR.exists():
            return []
        return sorted([d.name for d in CHARS_DIR.iterdir() if d.is_dir()])

    def create_test_select(self, char_name, opponent="kfm"):
        """Cree un select.def avec 1 perso a tester vs opponent"""
        content = f"""; AUTO TEST - {char_name}
[Characters]
{char_name}, stages/Abyss-Rugal-Palace.def
{opponent}, stages/Abyss-Rugal-Palace.def

[ExtraStages]
stages/Abyss-Rugal-Palace.def

[Options]
arcade.maxmatches = 1,0,0,0,0,0,0,0,0,0
"""
        select_file = DATA_DIR / "select.def"
        with open(select_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def is_game_running(self):
        """Verifie si Ikemen tourne"""
        for proc in psutil.process_iter(['name']):
            try:
                if 'ikemen' in proc.info['name'].lower():
                    return True
            except:
                pass
        return False

    def kill_game(self):
        """Force la fermeture du jeu"""
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if 'ikemen' in proc.info['name'].lower():
                    proc.kill()
                    time.sleep(1)
            except:
                pass

    def test_character(self, char_name):
        """Teste un personnage - retourne True si OK, False si crash"""
        self.log(f"  Testing: {char_name}")

        # Creer le select.def de test
        self.create_test_select(char_name)

        # S'assurer que le jeu n'est pas deja lance
        self.kill_game()
        time.sleep(1)

        try:
            # Lancer le jeu
            process = subprocess.Popen(
                [str(GAME_EXE)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(BASE_DIR)
            )

            start_time = time.time()

            # Attendre et surveiller
            while time.time() - start_time < TOTAL_TIMEOUT:
                # Verifier si le process est mort (crash)
                poll = process.poll()
                if poll is not None:
                    elapsed = time.time() - start_time
                    if elapsed < GAME_STARTUP_TIME + 2:
                        # Crash au demarrage
                        self.log(f"    CRASH au demarrage ({elapsed:.1f}s)")
                        return False
                    else:
                        # Crash pendant le jeu
                        self.log(f"    CRASH en jeu ({elapsed:.1f}s)")
                        return False

                time.sleep(0.5)

            # Timeout atteint = le jeu tourne encore = OK
            self.log(f"    OK (stable {TOTAL_TIMEOUT}s)")
            self.kill_game()
            return True

        except Exception as e:
            self.log(f"    ERREUR: {e}")
            self.kill_game()
            return False

    def run_full_test(self):
        """Lance le test complet de tous les personnages"""
        self.log("=" * 60)
        self.log("   AUTO TEST COMPLET - TOUS LES PERSONNAGES")
        self.log("=" * 60)
        self.log("")

        chars = self.get_all_char_folders()
        total = len(chars)

        self.log(f"Personnages a tester: {total}")
        self.log(f"Temps estime: ~{total * (TOTAL_TIMEOUT + 3) // 60} minutes")
        self.log("")

        for i, char in enumerate(chars, 1):
            self.log(f"[{i:3}/{total}] {char}")

            passed = self.test_character(char)

            if passed:
                self.results['passed'].append(char)
            else:
                self.results['crashed'].append(char)

            # Petite pause entre les tests
            time.sleep(2)

        self.save_results()
        self.generate_stable_select()
        self.print_summary()

    def save_results(self):
        """Sauvegarde les resultats"""
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # Sauvegarder aussi le log
        with open("auto_test.log", 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.log_lines))

    def generate_stable_select(self):
        """Genere un select.def avec seulement les persos stables"""
        output = f"""; IKEMEN GO - ROSTER AUTO-TESTE
; Genere le {datetime.now().strftime("%Y-%m-%d %H:%M")}
; {len(self.results['passed'])} personnages stables
; {len(self.results['crashed'])} crashes exclus

[Characters]
"""
        for char in sorted(self.results['passed']):
            output += f"{char}, stages/Abyss-Rugal-Palace.def\n"

        output += "\n; === CRASHES ===\n"
        for char in sorted(self.results['crashed']):
            output += f"; {char} - CRASH\n"

        output += """
[ExtraStages]
stages/Abyss-Rugal-Palace.def

[Options]
arcade.maxmatches = 10,0,0,0,0,0,0,0,0,0
"""

        # Sauvegarder
        stable_file = DATA_DIR / "select_auto_tested.def"
        with open(stable_file, 'w', encoding='utf-8') as f:
            f.write(output)

        # Appliquer comme select.def principal
        select_file = DATA_DIR / "select.def"
        with open(select_file, 'w', encoding='utf-8') as f:
            f.write(output)

        self.log(f"\nselect.def genere avec {len(self.results['passed'])} persos stables")

    def print_summary(self):
        """Affiche le resume"""
        self.log("")
        self.log("=" * 60)
        self.log("   RESULTATS FINAUX")
        self.log("=" * 60)
        self.log(f"   STABLES:  {len(self.results['passed']):3}")
        self.log(f"   CRASHES:  {len(self.results['crashed']):3}")
        self.log("")

        if self.results['crashed']:
            self.log("Personnages qui crashent:")
            for char in self.results['crashed'][:30]:
                self.log(f"   - {char}")
            if len(self.results['crashed']) > 30:
                self.log(f"   ... et {len(self.results['crashed'])-30} autres")


def quick_test(chars_to_test):
    """Test rapide d'une liste specifique"""
    tester = AutoTester()

    for char in chars_to_test:
        tester.log(f"Testing: {char}")
        passed = tester.test_character(char)
        if passed:
            tester.results['passed'].append(char)
        else:
            tester.results['crashed'].append(char)
        time.sleep(2)

    tester.save_results()
    tester.generate_stable_select()
    tester.print_summary()


if __name__ == "__main__":
    print("KOF Ultimate Online - Auto Tester")
    print("=" * 40)
    print()
    print("1. Test COMPLET (tous les persos)")
    print("2. Test RAPIDE (10 persos)")
    print("3. Quitter")
    print()

    choice = input("Choix: ").strip()

    if choice == "1":
        tester = AutoTester()
        tester.run_full_test()
    elif choice == "2":
        # Test rapide avec 10 persos de base
        quick_chars = [
            "kfm", "billy", "Nero", "Cronus", "Clone Zero",
            "Ash", "Athena_XI", "Geese-KOFM", "Magnus", "Eve"
        ]
        quick_test(quick_chars)
    else:
        print("Abandon.")
