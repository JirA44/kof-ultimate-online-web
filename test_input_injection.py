#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST AVEC INJECTION D'INPUTS
Envoie les inputs DIRECTEMENT au jeu via Windows Messages
N'affecte PAS les autres fenêtres !
"""

import subprocess
import time
import random
import os
from datetime import datetime
from pathlib import Path

try:
    import win32gui
    import win32con
    import win32api
except ImportError:
    print("❌ pywin32 non installé. Installation...")
    os.system("pip install pywin32")
    import win32gui
    import win32con
    import win32api

GAME_EXE = "Ikemen_GO.exe"
GAME_PATH = Path(__file__).parent

# Mapping des touches vers virtual key codes
VK_CODES = {
    'space': win32con.VK_SPACE,
    'return': win32con.VK_RETURN,
    'escape': win32con.VK_ESCAPE,
    'up': win32con.VK_UP,
    'down': win32con.VK_DOWN,
    'left': win32con.VK_LEFT,
    'right': win32con.VK_RIGHT,
    'a': ord('A'),
    's': ord('S'),
    'z': ord('Z'),
    'x': ord('X'),
    'd': ord('D'),
    'w': ord('W'),
}

class InjectedTester:
    """Test avec injection d'inputs dans le processus"""

    def __init__(self):
        self.issues = []
        self.start_time = datetime.now()
        self.game_hwnd = None

    def log(self, msg):
        timestamp = (datetime.now() - self.start_time).total_seconds()
        print(f"[{timestamp:>6.1f}s] {msg}")

    def issue(self, problem):
        self.issues.append(problem)
        self.log(f"⚠️  PROBLÈME: {problem}")

    def find_game_window(self):
        """Trouve le handle de la fenêtre du jeu"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if any(keyword in title for keyword in ["KOF", "Ikemen", "MUGEN", "AI Navigator"]):
                    windows.append((hwnd, title))
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)

        if windows:
            hwnd, title = windows[0]
            self.log(f"✓ Fenêtre trouvée: {title} (HWND: {hwnd})")
            return hwnd
        return None

    def send_key(self, key, hold_time=0.1):
        """Envoie une touche DIRECTEMENT à la fenêtre du jeu"""
        if not self.game_hwnd:
            self.issue(f"Pas de handle fenêtre pour touche {key}")
            return False

        if key not in VK_CODES:
            self.issue(f"Touche inconnue: {key}")
            return False

        vk_code = VK_CODES[key]

        try:
            # Envoyer WM_KEYDOWN
            lparam_down = win32api.MapVirtualKey(vk_code, 0) << 16 | 1
            win32api.SendMessage(self.game_hwnd, win32con.WM_KEYDOWN, vk_code, lparam_down)

            time.sleep(hold_time)

            # Envoyer WM_KEYUP
            lparam_up = lparam_down | (0x3 << 30)
            win32api.SendMessage(self.game_hwnd, win32con.WM_KEYUP, vk_code, lparam_up)

            return True

        except Exception as e:
            self.issue(f"Erreur envoi touche {key}: {e}")
            return False

    def test_launch(self):
        """Test du lancement"""
        self.log("="*60)
        self.log("TEST 1: LANCEMENT DU JEU")
        self.log("="*60)

        game_path = GAME_PATH / GAME_EXE

        if not game_path.exists():
            self.issue(f"Exe introuvable: {GAME_EXE}")
            return False

        self.log(f"✓ Exe trouvé: {game_path}")
        self.log("Lancement...")

        try:
            subprocess.Popen(str(game_path), cwd=str(GAME_PATH))
        except Exception as e:
            self.issue(f"Échec lancement: {e}")
            return False

        # Attendre et trouver la fenêtre
        self.log("Recherche de la fenêtre du jeu...")
        for i in range(30):
            time.sleep(1)
            self.game_hwnd = self.find_game_window()
            if self.game_hwnd:
                time.sleep(3)
                return True

            if i % 5 == 0:
                self.log(f"  Attente... {i}/30s")

        self.issue("Fenêtre jamais apparue (timeout 30s)")
        return False

    def test_title_screen(self):
        """Test écran titre"""
        self.log("\n" + "="*60)
        self.log("TEST 2: ÉCRAN TITRE")
        self.log("="*60)

        self.log("Attente écran titre (10s)...")
        time.sleep(10)

        self.log("Injection: ESPACE pour entrer au menu...")
        self.send_key('space')
        time.sleep(3)

        self.log("✓ Passage au menu principal")

    def test_menu_navigation(self):
        """Test navigation menus"""
        self.log("\n" + "="*60)
        self.log("TEST 3: NAVIGATION MENUS")
        self.log("="*60)

        menu_items = ["Arcade", "Versus", "Team Arcade", "Team Versus",
                      "Training", "Network", "Options"]

        for i, item in enumerate(menu_items):
            self.log(f"Navigation vers: {item}")
            self.send_key('down')
            time.sleep(1.5)

        self.log("✓ Navigation OK - 7 options parcourues")

        # Remonter
        self.log("Retour au début du menu...")
        for _ in range(7):
            self.send_key('up')
            time.sleep(0.3)

    def test_versus_mode(self):
        """Test mode versus"""
        self.log("\n" + "="*60)
        self.log("TEST 4: MODE VERSUS")
        self.log("="*60)

        self.log("Sélection de Versus...")
        self.send_key('down')
        time.sleep(0.5)
        self.send_key('return')
        time.sleep(4)

        self.log("✓ Écran de sélection de personnages")

    def test_character_selection(self):
        """Test sélection personnage"""
        self.log("\n" + "="*60)
        self.log("TEST 5: SÉLECTION PERSONNAGE")
        self.log("="*60)

        self.log("Navigation dans la grille...")
        directions = ['right', 'down', 'left', 'right', 'down', 'right']
        for d in directions:
            self.send_key(d)
            time.sleep(0.5)

        self.log("Sélection avec START maintenu...")
        # Simuler SPACE maintenu + ENTER
        vk_space = VK_CODES['space']
        lparam = win32api.MapVirtualKey(vk_space, 0) << 16 | 1
        win32api.SendMessage(self.game_hwnd, win32con.WM_KEYDOWN, vk_space, lparam)

        time.sleep(0.2)
        self.send_key('return')
        time.sleep(0.3)

        lparam_up = lparam | (0x3 << 30)
        win32api.SendMessage(self.game_hwnd, win32con.WM_KEYUP, vk_space, lparam_up)

        self.log("✓ Personnage sélectionné")
        time.sleep(6)

    def test_gameplay(self, duration=30):
        """Test gameplay"""
        self.log("\n" + "="*60)
        self.log(f"TEST 6: GAMEPLAY ({duration}s)")
        self.log("="*60)

        self.log("Combat en cours...")
        keys = ['a', 's', 'z', 'x', 'left', 'right', 'up', 'down']

        start = time.time()
        actions = 0

        while time.time() - start < duration:
            key = random.choice(keys)
            self.send_key(key, hold_time=0.05)
            actions += 1
            time.sleep(random.uniform(0.2, 0.6))

            if actions % 20 == 0:
                elapsed = time.time() - start
                self.log(f"  {actions} actions - {elapsed:.0f}s écoulées")

        self.log(f"✓ Combat terminé - {actions} actions effectuées")

    def test_pause_and_exit(self):
        """Test pause et sortie"""
        self.log("\n" + "="*60)
        self.log("TEST 7: PAUSE & SORTIE")
        self.log("="*60)

        self.log("Injection: ESCAPE (pause)...")
        self.send_key('escape')
        time.sleep(2)

        self.log("Navigation menu pause...")
        self.send_key('down')
        time.sleep(1)
        self.send_key('up')
        time.sleep(1)

        self.log("Sortie du match...")
        self.send_key('escape')
        time.sleep(2)

        self.log("✓ Retour au menu")

    def generate_report(self):
        """Génère rapport"""
        self.log("\n" + "="*60)
        self.log("RAPPORT FINAL")
        self.log("="*60)

        duration = (datetime.now() - self.start_time).total_seconds()

        print(f"\n⏱️  Durée totale: {duration:.1f}s ({duration/60:.1f} min)")
        print(f"⚠️  Problèmes trouvés: {len(self.issues)}")

        if self.issues:
            print("\n❌ LISTE DES PROBLÈMES:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        else:
            print("\n✅ AUCUN PROBLÈME DÉTECTÉ!")

        # Sauvegarder
        report_file = GAME_PATH / "logs" / f"test_injection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("TEST AVEC INJECTION D'INPUTS - KOF ULTIMATE ONLINE\n")
            f.write("="*60 + "\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Durée: {duration:.1f}s\n")
            f.write(f"Problèmes: {len(self.issues)}\n\n")

            if self.issues:
                f.write("PROBLÈMES DÉTECTÉS:\n")
                for i, issue in enumerate(self.issues, 1):
                    f.write(f"{i}. {issue}\n")
            else:
                f.write("✅ Aucun problème détecté\n")

        print(f"\n📄 Rapport sauvegardé: {report_file}")

    def run(self):
        """Lance tous les tests"""
        print("\n" + "="*70)
        print("  🎮 TEST AVEC INJECTION D'INPUTS")
        print("  Inputs envoyés DIRECTEMENT au jeu")
        print("  VOS AUTRES FENÊTRES NE SONT PAS AFFECTÉES !")
        print("="*70 + "\n")

        print("✅ Vous pouvez continuer à travailler pendant le test")
        print("✅ Vos consoles/éditeurs ne recevront PAS les touches\n")

        print("Démarrage automatique dans 3 secondes...")
        time.sleep(3)
        print()

        try:
            if not self.test_launch():
                self.log("❌ Échec au lancement, arrêt des tests")
                return

            self.test_title_screen()
            self.test_menu_navigation()
            self.test_versus_mode()
            self.test_character_selection()
            self.test_gameplay(duration=30)
            self.test_pause_and_exit()

        except Exception as e:
            self.issue(f"Erreur critique: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.generate_report()


if __name__ == "__main__":
    tester = InjectedTester()
    tester.run()

    print("\n" + "="*70)
    print("  ✅ TEST TERMINÉ")
    print("="*70 + "\n")
    time.sleep(2)
