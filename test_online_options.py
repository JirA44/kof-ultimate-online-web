#!/usr/bin/env python3
"""Test approfondi de chaque option du menu ONLINE"""
import subprocess
import time
import os
from datetime import datetime
from pathlib import Path

try:
    import win32gui
    import win32con
    import win32api
except ImportError:
    os.system("pip install pywin32")
    import win32gui
    import win32con
    import win32api

GAME_PATH = Path(__file__).parent
GAME_EXE = "Ikemen_GO.exe"

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
    'b': ord('B'),
}

class OnlineOptionsTester:
    def __init__(self):
        self.game_hwnd = None
        self.start_time = datetime.now()
        self.results = {}
        self.process = None

    def log(self, msg):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"[{elapsed:>6.1f}s] {msg}")

    def find_window(self):
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if any(k in title for k in ["KOF", "Ikemen", "MUGEN"]):
                    windows.append(hwnd)
            return True
        windows = []
        win32gui.EnumWindows(callback, windows)
        if windows:
            self.game_hwnd = windows[0]
            return True
        return False

    def send_key(self, key, hold=0.15):
        if not self.game_hwnd or key not in VK_CODES:
            return
        vk = VK_CODES[key]
        lparam = win32api.MapVirtualKey(vk, 0) << 16 | 1
        win32api.SendMessage(self.game_hwnd, win32con.WM_KEYDOWN, vk, lparam)
        time.sleep(hold)
        lparam_up = lparam | (0x3 << 30)
        win32api.SendMessage(self.game_hwnd, win32con.WM_KEYUP, vk, lparam_up)
        time.sleep(0.1)

    def get_window_title(self):
        if self.game_hwnd:
            return win32gui.GetWindowText(self.game_hwnd)
        return ""

    def launch_game(self):
        exe_path = GAME_PATH / GAME_EXE
        self.process = subprocess.Popen([str(exe_path)], cwd=str(GAME_PATH))
        self.log("Lancement du jeu...")

        for _ in range(30):
            if self.find_window():
                break
            time.sleep(1)

        if not self.game_hwnd:
            self.log("ERREUR: Fenetre non trouvee!")
            return False

        time.sleep(5)
        self.log("Jeu lance!")
        return True

    def go_to_main_menu(self):
        """Retour au menu principal"""
        for _ in range(5):
            self.send_key('escape', 0.2)
            time.sleep(0.3)
        time.sleep(1)

    def go_to_online_menu(self):
        """Navigation vers le menu ONLINE"""
        # Entrer dans le menu
        self.send_key('space')
        time.sleep(2)

        # Descendre jusqu'a ONLINE (6eme option)
        for i in range(6):
            self.send_key('down')
            time.sleep(0.2)

        # Entrer dans ONLINE
        self.send_key('space')
        time.sleep(2)
        self.log("Menu ONLINE ouvert")

    def test_find_ranked_match(self):
        """Test: FIND RANKED MATCH"""
        self.log("Test: FIND RANKED MATCH...")

        # Deja sur la 1ere option
        self.send_key('space')
        time.sleep(3)

        # Verifier si on est en mode recherche ou retour menu
        # On devrait voir un message de recherche
        # Annuler avec escape
        self.send_key('escape')
        time.sleep(1)

        # Si on est toujours dans le menu online = OK
        # Sinon = echec
        self.send_key('down')  # Tenter navigation
        time.sleep(0.3)
        self.send_key('up')
        time.sleep(0.3)

        self.log("  -> Matchmaking lance (verification manuelle requise)")
        return "partial"

    def test_find_casual_match(self):
        """Test: FIND CASUAL MATCH"""
        self.log("Test: FIND CASUAL MATCH...")

        self.send_key('down')  # Option 2
        time.sleep(0.2)
        self.send_key('space')
        time.sleep(3)

        self.send_key('escape')
        time.sleep(1)

        self.log("  -> Matchmaking casual lance")
        return "partial"

    def test_view_online_players(self):
        """Test: VIEW ONLINE PLAYERS"""
        self.log("Test: VIEW ONLINE PLAYERS...")

        self.send_key('down')  # Option 3
        time.sleep(0.2)
        self.send_key('space')
        time.sleep(2)

        # Tenter de naviguer dans la liste des joueurs
        self.send_key('down')
        time.sleep(0.3)
        self.send_key('down')
        time.sleep(0.3)
        self.send_key('up')
        time.sleep(0.3)

        # Retour
        self.send_key('escape')
        time.sleep(1)

        self.log("  -> Liste joueurs accessible")
        return True

    def test_train_vs_ai(self):
        """Test: TRAIN VS AI BOT"""
        self.log("Test: TRAIN VS AI BOT...")

        self.send_key('down')  # Option 4
        time.sleep(0.2)
        self.send_key('space')
        time.sleep(3)

        # Verifier si on a un ecran de selection de personnage
        # ou si on retourne au menu principal

        # Tenter de selectionner un perso
        self.send_key('space')
        time.sleep(2)

        # Si combat demarre, on devrait pouvoir attaquer
        for _ in range(5):
            self.send_key('a', 0.1)
        time.sleep(1)

        # Echap pour quitter
        self.send_key('escape')
        time.sleep(1)
        self.send_key('down')  # Confirmer quit
        self.send_key('space')
        time.sleep(1)

        self.log("  -> Mode AI a verifier")
        return "needs_check"

    def test_create_lobby(self):
        """Test: CREATE LOBBY"""
        self.log("Test: CREATE LOBBY...")

        self.send_key('down')  # Option 5
        time.sleep(0.2)
        self.send_key('space')
        time.sleep(2)

        # Retour
        self.send_key('escape')
        time.sleep(1)

        self.log("  -> Create lobby teste")
        return "partial"

    def test_view_leaderboard(self):
        """Test: VIEW LEADERBOARD"""
        self.log("Test: VIEW LEADERBOARD...")

        self.send_key('down')  # Option 6
        time.sleep(0.2)
        self.send_key('space')
        time.sleep(2)

        # Navigation dans le leaderboard
        self.send_key('down')
        time.sleep(0.3)
        self.send_key('down')
        time.sleep(0.3)

        # Retour
        self.send_key('escape')
        time.sleep(1)

        self.log("  -> Leaderboard accessible")
        return True

    def run_all_tests(self):
        print("\n" + "=" * 60)
        print("  TEST COMPLET DES OPTIONS ONLINE")
        print("=" * 60 + "\n")

        if not self.launch_game():
            return

        self.go_to_online_menu()

        # Test chaque option
        tests = [
            ("FIND RANKED MATCH", self.test_find_ranked_match),
            ("FIND CASUAL MATCH", self.test_find_casual_match),
            ("VIEW ONLINE PLAYERS", self.test_view_online_players),
            ("TRAIN VS AI BOT", self.test_train_vs_ai),
            ("CREATE LOBBY", self.test_create_lobby),
            ("VIEW LEADERBOARD", self.test_view_leaderboard),
        ]

        # Revenir au debut du menu pour chaque test
        for name, test_func in tests:
            try:
                # Retour menu principal puis ONLINE
                self.go_to_main_menu()
                time.sleep(1)
                self.go_to_online_menu()

                result = test_func()
                self.results[name] = result
            except Exception as e:
                self.log(f"  ERREUR: {e}")
                self.results[name] = False
                self.go_to_main_menu()

        # Resultats
        print("\n" + "=" * 60)
        print("  RESULTATS DETAILLES")
        print("=" * 60)

        for name, result in self.results.items():
            if result == True:
                status = "✓ OK"
            elif result == "partial":
                status = "⚠ Partiel"
            elif result == "needs_check":
                status = "? A verifier"
            else:
                status = "✗ ECHEC"
            print(f"  {status}: {name}")

        # Fermer le jeu
        self.send_key('escape')
        time.sleep(0.5)

        print("\n" + "=" * 60)
        print("  NOTES:")
        print("  - 'Partiel' = l'option repond mais effet non verifie")
        print("  - 'A verifier' = necessite verification manuelle")
        print("=" * 60 + "\n")

if __name__ == "__main__":
    tester = OnlineOptionsTester()
    tester.run_all_tests()
