#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE ONLINE - Lanceur de Test Silencieux
Lance le jeu, attend les resultats du test automatique, puis ferme le jeu
"""

import subprocess
import time
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Configuration
GAME_PATH = Path(__file__).parent
GAME_EXE = GAME_PATH / "Ikemen_GO.exe"
RESULTS_FILE = GAME_PATH / "save" / "auto_test_results.json"
LOG_FILE = GAME_PATH / "save" / "auto_test_log.txt"
REPORT_FILE = GAME_PATH / "menu_test_reports" / "AUTO_TEST_REPORT.md"

# Timeouts
MAX_WAIT_SECONDS = 60  # Max time to wait for results
CHECK_INTERVAL = 2     # Check every 2 seconds

def clear_old_results():
    """Supprime les anciens resultats"""
    for f in [RESULTS_FILE, LOG_FILE]:
        if f.exists():
            f.unlink()
    print("Anciens resultats supprimes")

def launch_game():
    """Lance le jeu en arriere-plan"""
    print(f"Lancement du jeu: {GAME_EXE}")

    if not GAME_EXE.exists():
        # Try alternative names
        alternatives = ["KOF_Ultimate_Online.exe", "Ikemen_GO_x64.exe", "Ikemen_GO.exe"]
        for alt in alternatives:
            alt_path = GAME_PATH / alt
            if alt_path.exists():
                global GAME_EXE
                GAME_EXE = alt_path
                break

    if not GAME_EXE.exists():
        print(f"ERREUR: Executable non trouve: {GAME_EXE}")
        return None

    try:
        # Lance le jeu sans bloquer
        process = subprocess.Popen(
            [str(GAME_EXE)],
            cwd=str(GAME_PATH),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"Jeu lance avec PID: {process.pid}")
        return process
    except Exception as e:
        print(f"ERREUR au lancement: {e}")
        return None

def wait_for_results(timeout=MAX_WAIT_SECONDS):
    """Attend que les resultats soient generes"""
    print(f"Attente des resultats (max {timeout}s)...")

    start_time = time.time()
    last_size = 0

    while time.time() - start_time < timeout:
        if RESULTS_FILE.exists():
            current_size = RESULTS_FILE.stat().st_size
            if current_size > 0 and current_size == last_size:
                # File size stable, results ready
                time.sleep(1)  # Wait a bit more to ensure write is complete
                return True
            last_size = current_size

        elapsed = int(time.time() - start_time)
        print(f"\r  Attente... {elapsed}s / {timeout}s", end="", flush=True)
        time.sleep(CHECK_INTERVAL)

    print()
    return False

def kill_game(process):
    """Ferme le jeu"""
    if process is None:
        return

    print("Fermeture du jeu...")
    try:
        process.terminate()
        process.wait(timeout=5)
        print("Jeu ferme proprement")
    except:
        try:
            process.kill()
            print("Jeu force a fermer")
        except:
            pass

def read_results():
    """Lit les resultats du test"""
    if not RESULTS_FILE.exists():
        return None

    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lecture resultats: {e}")
        return None

def display_summary(results):
    """Affiche un resume des resultats"""
    if not results:
        print("\nAucun resultat disponible")
        return

    print("\n" + "="*60)
    print("RESULTATS DU TEST AUTOMATIQUE")
    print("="*60)

    summary = results.get("summary", {})
    print(f"\nStatus: {summary.get('status', 'UNKNOWN')}")
    print(f"Erreurs: {summary.get('total_errors', 'N/A')}")
    print(f"Warnings: {summary.get('total_warnings', 'N/A')}")

    # Menu handlers
    menus = results.get("menus_tested", {})
    if menus:
        print(f"\nHandlers de menu: {len(menus)} testes")
        failed = [name for name, data in menus.items() if data.get("status") != "OK"]
        if failed:
            print(f"  ECHECS: {', '.join(failed)}")
        else:
            print("  Tous OK")

    # Modules
    modules = results.get("modules_tested", {})
    if modules:
        print(f"\nModules: {len(modules)} testes")
        failed = [name for name, data in modules.items() if data.get("status") != "OK"]
        if failed:
            print(f"  ECHECS: {', '.join(failed)}")
        else:
            print("  Tous OK")

    # Characters & Stages
    chars = results.get("characters", {})
    stages = results.get("stages", {})
    print(f"\nPersonnages: {chars.get('count', 'N/A')}")
    print(f"Stages: {stages.get('count', 'N/A')}")

    # Errors
    errors = results.get("errors", [])
    if errors:
        print(f"\nERREURS ({len(errors)}):")
        for err in errors[:5]:  # Show first 5
            print(f"  - [{err.get('type')}] {err.get('message')}")

    print("\n" + "="*60)
    print(f"Rapport complet: {REPORT_FILE}")
    print("="*60)

def main():
    print("="*60)
    print("KOF ULTIMATE ONLINE - TEST SILENCIEUX")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check if game is already running
    clear_old_results()

    # Launch game
    process = launch_game()
    if process is None:
        print("\nImpossible de lancer le jeu.")
        print("Le test sera execute au prochain demarrage manuel du jeu.")
        print(f"Les resultats seront dans: {REPORT_FILE}")
        return 1

    # Wait for results
    results_ready = wait_for_results()

    # Kill game
    kill_game(process)

    if not results_ready:
        print("\nTimeout: Les resultats n'ont pas ete generes a temps.")
        print("Verifiez que le mod silent_auto_test.lua est bien charge.")
        return 1

    # Read and display results
    results = read_results()
    display_summary(results)

    return 0 if results and results.get("summary", {}).get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
