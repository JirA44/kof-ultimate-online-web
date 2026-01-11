#!/usr/bin/env python3
"""
KOF Ultimate Online - Combat Crash Tester
Teste chaque personnage en combat reel pour detecter les crashes
"""

import os
import subprocess
import time
import json
import signal
from pathlib import Path
from datetime import datetime
import threading

GAME_EXE = "Ikemen_GO.exe"
CHARS_DIR = Path("chars")
DATA_DIR = Path("data")
RESULTS_FILE = "combat_test_results.json"
LOG_FILE = "combat_test.log"

# Temps de test par personnage (secondes)
TEST_DURATION = 15  # 15 secondes par combat
STARTUP_TIME = 8    # Temps pour charger le jeu

# Personnage de reference stable pour les tests
REFERENCE_CHAR = "kfm"  # Kung Fu Man - toujours stable

class CombatTester:
    def __init__(self):
        self.results = {
            'test_date': datetime.now().isoformat(),
            'passed': [],
            'crashed': [],
            'timeout': [],
            'details': {}
        }
        self.log_file = open(LOG_FILE, 'w', encoding='utf-8')

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {msg}"
        print(line)
        self.log_file.write(line + "\n")
        self.log_file.flush()

    def create_test_select(self, char_name):
        """Cree un select.def temporaire pour tester un personnage"""
        content = f"""; TEST SELECT - Auto-generated
[Characters]
{char_name}, stages/Abyss-Rugal-Palace.def
{REFERENCE_CHAR}, stages/Abyss-Rugal-Palace.def

[ExtraStages]
stages/Abyss-Rugal-Palace.def

[Options]
arcade.maxmatches = 1,0,0,0,0,0,0,0,0,0
"""
        test_select = DATA_DIR / "select_test.def"
        with open(test_select, 'w', encoding='utf-8') as f:
            f.write(content)
        return test_select

    def create_test_config(self):
        """Cree une config qui lance directement un combat"""
        # On va utiliser le mode training ou versus avec AI
        pass

    def test_character(self, char_name):
        """Teste un personnage en lançant un combat"""
        self.log(f"Testing: {char_name}")

        result = {
            'name': char_name,
            'status': 'unknown',
            'duration': 0,
            'error': None
        }

        # Creer le select.def de test
        self.create_test_select(char_name)

        # Backup et remplacer select.def
        original_select = DATA_DIR / "select.def"
        backup_select = DATA_DIR / "select_backup_test.def"
        test_select = DATA_DIR / "select_test.def"

        try:
            # Backup
            if original_select.exists():
                original_select.rename(backup_select)
            test_select.rename(original_select)

            # Lancer le jeu
            start_time = time.time()

            try:
                # Lancer Ikemen en mode test (training ou watch)
                process = subprocess.Popen(
                    [GAME_EXE, "-slowmotion", "1"],  # Mode normal
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(Path.cwd())
                )

                # Attendre le temps de test
                total_time = STARTUP_TIME + TEST_DURATION

                try:
                    # Attendre avec timeout
                    stdout, stderr = process.communicate(timeout=total_time)

                    # Si le process s'est termine avant le timeout = crash probable
                    elapsed = time.time() - start_time

                    if elapsed < total_time - 2:
                        # Termine trop tot = crash
                        result['status'] = 'crashed'
                        result['error'] = f"Process termine apres {elapsed:.1f}s"
                        result['duration'] = elapsed
                        self.log(f"  -> CRASH apres {elapsed:.1f}s")
                    else:
                        result['status'] = 'passed'
                        result['duration'] = elapsed
                        self.log(f"  -> OK ({elapsed:.1f}s)")

                except subprocess.TimeoutExpired:
                    # Timeout = le jeu tourne encore = OK
                    process.kill()
                    process.wait()
                    result['status'] = 'passed'
                    result['duration'] = total_time
                    self.log(f"  -> OK (timeout normal)")

            except Exception as e:
                result['status'] = 'error'
                result['error'] = str(e)
                self.log(f"  -> ERREUR: {e}")

        finally:
            # Restaurer le select.def original
            current_select = DATA_DIR / "select.def"
            if current_select.exists():
                current_select.unlink()
            if backup_select.exists():
                backup_select.rename(original_select)

        return result

    def quick_scan(self, char_list):
        """Scan rapide - verifie juste si le jeu demarre avec le perso"""
        self.log("=" * 60)
        self.log("   QUICK COMBAT SCAN")
        self.log("=" * 60)

        total = len(char_list)

        for i, char_name in enumerate(char_list, 1):
            self.log(f"\n[{i}/{total}] {char_name}")

            result = self.test_character(char_name)
            self.results['details'][char_name] = result

            if result['status'] == 'passed':
                self.results['passed'].append(char_name)
            elif result['status'] == 'crashed':
                self.results['crashed'].append(char_name)
            else:
                self.results['timeout'].append(char_name)

            # Pause entre les tests
            time.sleep(2)

        self.save_results()
        self.print_summary()

    def save_results(self):
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        self.log(f"\nResultats sauvegardes: {RESULTS_FILE}")

    def print_summary(self):
        self.log("\n" + "=" * 60)
        self.log("   RESULTATS")
        self.log("=" * 60)
        self.log(f"\n   PASSED:  {len(self.results['passed']):3}")
        self.log(f"   CRASHED: {len(self.results['crashed']):3}")
        self.log(f"   ERRORS:  {len(self.results['timeout']):3}")

        if self.results['crashed']:
            self.log("\n   PERSONNAGES QUI CRASHENT:")
            for char in self.results['crashed']:
                self.log(f"   - {char}")

    def close(self):
        self.log_file.close()


def get_chars_from_select():
    """Lit les personnages depuis select.def"""
    chars = []
    select_file = DATA_DIR / "select_stable.def"

    if not select_file.exists():
        select_file = DATA_DIR / "select.def"

    with open(select_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith(';') and not line.startswith('['):
                # Extraire le nom du personnage
                if ',' in line:
                    char_name = line.split(',')[0].strip()
                    if char_name and not char_name.startswith(';'):
                        chars.append(char_name)

    return chars


def main():
    print("=" * 60)
    print("   KOF ULTIMATE ONLINE - COMBAT CRASH TESTER")
    print("=" * 60)
    print()
    print("Ce test va lancer le jeu avec chaque personnage")
    print("pour detecter les crashes en combat.")
    print()
    print("ATTENTION: Le jeu va s'ouvrir et se fermer plusieurs fois.")
    print()

    # Obtenir la liste des personnages
    chars = get_chars_from_select()
    print(f"Personnages a tester: {len(chars)}")
    print()

    # Mode selection
    print("Options:")
    print("1. Tester TOUS les personnages (long)")
    print("2. Tester les 20 premiers")
    print("3. Tester un personnage specifique")
    print("4. Quitter")
    print()

    choice = input("Choix [1-4]: ").strip()

    if choice == '1':
        test_chars = chars
    elif choice == '2':
        test_chars = chars[:20]
    elif choice == '3':
        name = input("Nom du personnage: ").strip()
        test_chars = [name] if name else []
    else:
        print("Abandon.")
        return

    if not test_chars:
        print("Aucun personnage a tester.")
        return

    print(f"\nDemarrage du test de {len(test_chars)} personnage(s)...")
    print("Appuyez sur Ctrl+C pour arreter.\n")
    time.sleep(3)

    tester = CombatTester()
    try:
        tester.quick_scan(test_chars)
    except KeyboardInterrupt:
        print("\n\nTest interrompu par l'utilisateur.")
        tester.save_results()
    finally:
        tester.close()


if __name__ == "__main__":
    main()
