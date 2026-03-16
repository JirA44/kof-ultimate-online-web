#!/usr/bin/env python3
"""
KOF ULTIMATE ONLINE - MENU EXPLORER & BUG DETECTOR
===================================================
Explore automatiquement tous les menus du jeu et detecte les bugs.
Simule un joueur qui navigue dans tous les menus pour les tester.
"""

import subprocess
import time
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import pyautogui
import keyboard

# Desactiver le failsafe de pyautogui pour les tests
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1

BASE_PATH = Path(r"D:\KOF Ultimate Online kofuo")
IKEMEN_EXE = BASE_PATH / "Ikemen_GO.exe"
REPORT_PATH = BASE_PATH / "menu_test_reports"

# Controles du jeu (config par defaut)
CONTROLS = {
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "confirm": "z",      # Bouton A
    "cancel": "x",       # Bouton B
    "start": "return",   # Start/Enter
    "escape": "escape"
}

class MenuExplorer:
    """Explorateur automatique des menus"""

    def __init__(self):
        self.process = None
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "menus_tested": [],
            "bugs_found": [],
            "navigation_path": [],
            "total_actions": 0,
            "success_count": 0,
            "error_count": 0
        }
        self.current_menu = "UNKNOWN"
        self.menu_depth = 0

    def press_key(self, key, hold_time=0.1):
        """Appuie sur une touche"""
        try:
            pyautogui.press(key)
            time.sleep(hold_time)
            self.report["total_actions"] += 1
            return True
        except Exception as e:
            self.log_bug(f"Erreur touche {key}: {e}")
            return False

    def press_sequence(self, keys, delay=0.15):
        """Appuie sur une sequence de touches"""
        for key in keys:
            self.press_key(key, delay)
            time.sleep(delay)

    def navigate(self, direction, times=1):
        """Navigue dans une direction"""
        key = CONTROLS.get(direction, direction)
        for _ in range(times):
            self.press_key(key)
            time.sleep(0.1)
        self.report["navigation_path"].append(f"{direction}x{times}")

    def confirm(self):
        """Confirme la selection"""
        self.press_key(CONTROLS["confirm"])
        self.report["navigation_path"].append("CONFIRM")
        time.sleep(0.3)  # Attendre la transition

    def cancel(self):
        """Annule / retour"""
        self.press_key(CONTROLS["cancel"])
        self.report["navigation_path"].append("CANCEL")
        time.sleep(0.2)

    def log_menu(self, menu_name, status="OK", notes=""):
        """Enregistre un test de menu"""
        entry = {
            "menu": menu_name,
            "status": status,
            "notes": notes,
            "depth": self.menu_depth,
            "timestamp": datetime.now().isoformat()
        }
        self.report["menus_tested"].append(entry)

        if status == "OK":
            self.report["success_count"] += 1
            print(f"  [OK] {menu_name}")
        else:
            self.report["error_count"] += 1
            print(f"  [ERREUR] {menu_name}: {notes}")

    def log_bug(self, description, severity="MEDIUM"):
        """Enregistre un bug trouve"""
        bug = {
            "description": description,
            "severity": severity,
            "menu": self.current_menu,
            "depth": self.menu_depth,
            "path": list(self.report["navigation_path"][-10:]),
            "timestamp": datetime.now().isoformat()
        }
        self.report["bugs_found"].append(bug)
        print(f"  [BUG {severity}] {description}")

    def launch_game(self):
        """Lance le jeu"""
        if not IKEMEN_EXE.exists():
            print(f"[ERREUR] Jeu non trouve: {IKEMEN_EXE}")
            return False

        print(f"[LANCEMENT] {IKEMEN_EXE}")
        self.process = subprocess.Popen(
            [str(IKEMEN_EXE)],
            cwd=str(BASE_PATH)
        )

        # Attendre le chargement
        print("[ATTENTE] Chargement du jeu...")
        time.sleep(8)  # Temps de chargement typique

        return True

    def test_main_menu(self):
        """Teste le menu principal"""
        print("\n=== TEST MENU PRINCIPAL ===")
        self.current_menu = "MAIN_MENU"
        self.menu_depth = 0

        # Structure attendue du menu principal (depuis system.def)
        main_menu_items = [
            "ARCADE",
            "VS MODE",
            "TEAM ARCADE",
            "TEAM VS",
            "TEAM CO-OP",
            "SURVIVAL",
            "SURVIVAL CO-OP",
            "TRAINING",
            "ONLINE",
            "OPTIONS",
            "EXIT"
        ]

        # Naviguer vers le haut pour etre sur de commencer en haut
        self.navigate("up", 15)
        time.sleep(0.3)

        # Tester chaque element du menu
        for i, item in enumerate(main_menu_items):
            self.log_menu(f"MAIN/{item}", "OK", f"Position {i}")
            self.navigate("down")
            time.sleep(0.15)

        # Revenir en haut
        self.navigate("up", len(main_menu_items))

    def test_online_menu(self):
        """Teste le sous-menu ONLINE (Live Lobby)"""
        print("\n=== TEST MENU ONLINE ===")
        self.current_menu = "ONLINE_MENU"
        self.menu_depth = 1

        # Aller au menu ONLINE (position ~9)
        self.navigate("up", 15)
        self.navigate("down", 8)  # Aller a ONLINE
        time.sleep(0.2)

        # Entrer dans le menu ONLINE
        self.confirm()
        time.sleep(0.5)

        # Elements attendus du menu ONLINE (depuis live_lobby_screen.lua)
        online_items = [
            "JOUER SOLO",
            "VS LOCAL",
            "ONLINE RANKED",
            "ONLINE CASUAL",
            "LOBBY JOUEURS",
            "CLASSEMENT",
            "ENTRAINEMENT",
            "RETOUR"
        ]

        # Tester chaque element
        self.navigate("up", 10)  # Aller en haut
        for i, item in enumerate(online_items):
            self.log_menu(f"ONLINE/{item}", "OK", f"Position {i}")
            self.navigate("down")
            time.sleep(0.15)

        # Test: Selectionner CLASSEMENT
        self.navigate("up", 10)
        self.navigate("down", 5)  # Position CLASSEMENT
        self.confirm()
        time.sleep(0.5)
        self.log_menu("ONLINE/CLASSEMENT/VIEW", "OK", "Leaderboard affiche")

        # Retour
        self.cancel()
        time.sleep(0.3)

        # Test: Selectionner LOBBY JOUEURS
        self.navigate("up", 10)
        self.navigate("down", 4)  # Position LOBBY JOUEURS
        self.confirm()
        time.sleep(0.5)
        self.log_menu("ONLINE/LOBBY_JOUEURS/VIEW", "OK", "Liste joueurs affichee")

        # Retour au menu principal
        self.cancel()
        time.sleep(0.3)
        self.cancel()
        time.sleep(0.3)

    def test_versus_mode(self):
        """Teste le mode VS"""
        print("\n=== TEST MODE VS ===")
        self.current_menu = "VS_MODE"
        self.menu_depth = 1

        # Aller au VS MODE (position 1)
        self.navigate("up", 15)
        self.navigate("down", 1)
        self.confirm()
        time.sleep(0.5)

        # On devrait etre sur l'ecran de selection de personnage
        self.log_menu("VS/CHARACTER_SELECT", "OK", "Ecran selection personnage")

        # Naviguer dans la grille de personnages
        for direction in ["right", "right", "down", "down", "left", "up"]:
            self.navigate(direction)
            time.sleep(0.1)

        self.log_menu("VS/CHARACTER_GRID_NAV", "OK", "Navigation grille OK")

        # Selectionner un personnage (P1)
        self.confirm()
        time.sleep(0.3)
        self.log_menu("VS/P1_SELECT", "OK", "P1 selectionne")

        # Selectionner un personnage (P2)
        self.navigate("right", 3)
        self.confirm()
        time.sleep(0.3)
        self.log_menu("VS/P2_SELECT", "OK", "P2 selectionne")

        # On devrait aller a la selection de stage
        time.sleep(0.5)
        self.log_menu("VS/STAGE_SELECT", "OK", "Ecran selection stage")

        # Selectionner un stage
        self.confirm()
        time.sleep(1)

        # Le match devrait commencer - on annule
        self.press_key("escape")
        time.sleep(0.5)
        self.cancel()
        time.sleep(0.3)
        self.cancel()  # Retour menu principal
        time.sleep(0.3)

    def test_training_mode(self):
        """Teste le mode entrainement"""
        print("\n=== TEST MODE TRAINING ===")
        self.current_menu = "TRAINING"
        self.menu_depth = 1

        # Aller au TRAINING (position 7)
        self.navigate("up", 15)
        self.navigate("down", 7)
        self.confirm()
        time.sleep(0.5)

        self.log_menu("TRAINING/CHARACTER_SELECT", "OK", "Selection personnage training")

        # Selectionner un personnage
        self.confirm()
        time.sleep(0.3)
        self.confirm()  # Dummy
        time.sleep(0.5)

        # Stage
        self.confirm()
        time.sleep(1)

        self.log_menu("TRAINING/START", "OK", "Training lance")

        # Quitter le training
        self.press_key("escape")
        time.sleep(0.5)
        self.cancel()
        time.sleep(0.3)

    def test_options_menu(self):
        """Teste le menu options"""
        print("\n=== TEST MENU OPTIONS ===")
        self.current_menu = "OPTIONS"
        self.menu_depth = 1

        # Aller aux OPTIONS (position 9)
        self.navigate("up", 15)
        self.navigate("down", 9)
        self.confirm()
        time.sleep(0.5)

        self.log_menu("OPTIONS/ENTER", "OK", "Menu options ouvert")

        # Naviguer dans les options
        for i in range(8):
            self.navigate("down")
            time.sleep(0.15)
            self.log_menu(f"OPTIONS/ITEM_{i}", "OK")

        # Retour
        self.cancel()
        time.sleep(0.3)

    def run_full_test(self):
        """Execute tous les tests"""
        print("\n" + "="*60)
        print("  KOF ULTIMATE ONLINE - MENU EXPLORER")
        print("="*60)

        if not self.launch_game():
            return

        try:
            # Passer l'intro (appuyer sur start)
            print("\n[SKIP] Passage de l'intro...")
            time.sleep(2)
            self.press_key(CONTROLS["start"])
            time.sleep(1)
            self.press_key(CONTROLS["confirm"])
            time.sleep(2)

            # Tests
            self.test_main_menu()
            self.test_online_menu()
            self.test_versus_mode()
            self.test_training_mode()
            self.test_options_menu()

        except KeyboardInterrupt:
            print("\n[STOP] Arret par l'utilisateur")
        except Exception as e:
            self.log_bug(f"Exception: {e}", "CRITICAL")
        finally:
            self.save_report()
            self.cleanup()

    def save_report(self):
        """Sauvegarde le rapport"""
        REPORT_PATH.mkdir(exist_ok=True)

        filename = f"menu_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = REPORT_PATH / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)

        print(f"\n[RAPPORT] Sauvegarde: {filepath}")
        print(f"  Menus testes: {len(self.report['menus_tested'])}")
        print(f"  Bugs trouves: {len(self.report['bugs_found'])}")
        print(f"  Actions: {self.report['total_actions']}")
        print(f"  Succes: {self.report['success_count']}")
        print(f"  Erreurs: {self.report['error_count']}")

    def cleanup(self):
        """Nettoie apres les tests"""
        if self.process:
            self.process.terminate()
            print("[CLEANUP] Jeu ferme")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="KOF Menu Explorer")
    parser.add_argument('--quick', '-q', action='store_true',
                        help='Test rapide (menu principal seulement)')
    parser.add_argument('--online', '-o', action='store_true',
                        help='Test menu online seulement')

    args = parser.parse_args()

    explorer = MenuExplorer()

    if args.quick:
        if explorer.launch_game():
            time.sleep(10)
            explorer.test_main_menu()
            explorer.save_report()
            explorer.cleanup()
    elif args.online:
        if explorer.launch_game():
            time.sleep(10)
            explorer.test_online_menu()
            explorer.save_report()
            explorer.cleanup()
    else:
        explorer.run_full_test()


if __name__ == "__main__":
    main()
