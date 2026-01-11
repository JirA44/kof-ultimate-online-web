#!/usr/bin/env python3
"""Test de combats aléatoires pour vérifier la stabilité"""
import subprocess
import time
import os
import random
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

GAME_PATH = Path(r"D:\KOF Ultimate Online kofuo")
GAME_EXE = "Ikemen_GO.exe"

VK_CODES = {
    'space': win32con.VK_SPACE,
    'escape': win32con.VK_ESCAPE,
    'up': win32con.VK_UP,
    'down': win32con.VK_DOWN,
    'left': win32con.VK_LEFT,
    'right': win32con.VK_RIGHT,
    'a': ord('A'),
    's': ord('S'),
    'b': ord('B'),
    'c': ord('C'),
    'x': ord('X'),
    'y': ord('Y'),
    'z': ord('Z'),
}

class RandomFightTester:
    def __init__(self):
        self.game_hwnd = None
        self.start_time = datetime.now()
        self.fights_completed = 0
        self.fights_crashed = 0

    def log(self, msg):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"[{elapsed:>6.1f}s] {msg}")

    def find_window(self):
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                # Elargir les mots-clés de détection
                if any(k.lower() in title.lower() for k in ["KOF", "Ikemen", "MUGEN", "King of Fighters", "Ultimate"]):
                    windows.append(hwnd)
            return True
        windows = []
        win32gui.EnumWindows(callback, windows)
        if windows:
            self.game_hwnd = windows[0]
            return True
        return False

    def is_game_running(self):
        """Vérifie si le processus du jeu est toujours actif"""
        import subprocess
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Ikemen_GO.exe'],
                                    capture_output=True, encoding='cp437', errors='ignore')
            running = result.stdout and 'Ikemen_GO.exe' in result.stdout
            if not running:
                self.log(f"  [DEBUG] Process check failed: {result.stdout[:100] if result.stdout else 'None'}")
            return running
        except Exception as e:
            self.log(f"  [DEBUG] Tasklist exception: {e}")
            # Si tasklist échoue, vérifier via la fenêtre
            return self.find_window()

    def send_key(self, key, hold=0.1):
        if not self.game_hwnd or key not in VK_CODES:
            return
        vk = VK_CODES[key]
        lparam = win32api.MapVirtualKey(vk, 0) << 16 | 1
        win32api.SendMessage(self.game_hwnd, win32con.WM_KEYDOWN, vk, lparam)
        time.sleep(hold)
        lparam_up = lparam | (0x3 << 30)
        win32api.SendMessage(self.game_hwnd, win32con.WM_KEYUP, vk, lparam_up)
        time.sleep(0.05)

    def random_char_select(self):
        """Sélection aléatoire d'un personnage"""
        self.find_window()  # Rafraichir le handle

        # Mouvements aléatoires dans la grille (moins nombreux)
        moves = random.randint(1, 5)
        for _ in range(moves):
            direction = random.choice(['up', 'down', 'left', 'right'])
            self.send_key(direction, 0.1)
            time.sleep(0.1)

        # Sélectionner
        self.send_key('space')
        time.sleep(0.5)

    def do_random_fight(self, duration=10):
        """Combat aléatoire pendant X secondes"""
        attack_keys = ['a', 'b', 'c', 'x', 'y', 'z']
        move_keys = ['up', 'down', 'left', 'right']

        end_time = time.time() + duration
        while time.time() < end_time:
            try:
                # Rafraîchir le handle de fenêtre (peut changer en combat)
                self.find_window()

                # Action aléatoire
                action = random.choice(['attack', 'move', 'combo'])
                if action == 'attack':
                    key = random.choice(attack_keys)
                    self.send_key(key, 0.08)
                elif action == 'move':
                    key = random.choice(move_keys)
                    self.send_key(key, 0.1)
                else:
                    # Combo
                    for _ in range(3):
                        self.send_key(random.choice(move_keys), 0.05)
                        self.send_key(random.choice(attack_keys), 0.05)
                time.sleep(0.05)
            except:
                pass

        # Vérifier que le PROCESSUS est toujours actif (plus fiable que la fenêtre)
        return self.is_game_running()

    def kill_game(self):
        """Force la fermeture du jeu"""
        subprocess.run(['taskkill', '/IM', 'Ikemen_GO.exe', '/F'],
                      capture_output=True, encoding='cp437', errors='ignore')
        time.sleep(1)

    def run_fight_test(self, num_fights=5):
        print("\n" + "=" * 60)
        print(f"  TEST DE {num_fights} COMBATS ALEATOIRES")
        print("=" * 60 + "\n")

        # S'assurer qu'aucune instance n'est en cours
        self.kill_game()

        # Lancer le jeu
        exe_path = GAME_PATH / GAME_EXE
        process = subprocess.Popen([str(exe_path)], cwd=str(GAME_PATH))
        self.log("Lancement du jeu...")

        for _ in range(30):
            if self.find_window():
                break
            time.sleep(1)

        if not self.game_hwnd:
            self.log("ERREUR: Fenetre non trouvee!")
            return

        time.sleep(5)

        for fight_num in range(1, num_fights + 1):
            self.log(f"--- COMBAT {fight_num}/{num_fights} ---")

            try:
                # Retour menu (lentement pour éviter les bugs)
                for _ in range(3):
                    self.find_window()  # Rafraichir handle
                    self.send_key('escape', 0.2)
                    time.sleep(0.5)
                time.sleep(1)

                # Aller dans VS Mode
                self.find_window()
                self.send_key('space')
                time.sleep(1.5)
                self.send_key('down')  # VS Mode
                time.sleep(0.2)
                self.send_key('space')
                time.sleep(1.5)

                # Sélection P1
                self.log("  Selection P1...")
                self.random_char_select()
                time.sleep(0.5)

                # Sélection P2
                self.log("  Selection P2...")
                self.random_char_select()
                time.sleep(1)

                # Sélection stage (random)
                self.send_key('space')
                time.sleep(2)

                # Combat!
                self.log("  Combat en cours...")
                # Debug: montrer le titre de la fenêtre avant le combat
                if self.game_hwnd:
                    try:
                        title = win32gui.GetWindowText(self.game_hwnd)
                        self.log(f"  [DEBUG] Window title: {title}")
                    except:
                        pass
                fight_ok = self.do_random_fight(duration=8)

                if fight_ok:
                    self.fights_completed += 1
                    self.log(f"  Combat {fight_num} OK!")
                else:
                    self.fights_crashed += 1
                    self.log(f"  Combat {fight_num} CRASH!")

                # Quitter le combat (lentement)
                self.find_window()
                self.send_key('escape')
                time.sleep(0.5)
                self.find_window()
                self.send_key('down')  # Yes
                time.sleep(0.2)
                self.send_key('space')
                time.sleep(1.5)

            except Exception as e:
                self.log(f"  ERREUR: {e}")
                self.fights_crashed += 1

        # Résultats
        print("\n" + "=" * 60)
        print("  RESULTATS DES COMBATS")
        print("=" * 60)
        print(f"  Combats réussis: {self.fights_completed}/{num_fights}")
        print(f"  Crashes: {self.fights_crashed}")

        if self.fights_crashed == 0:
            print("\n  ✓ TOUS LES COMBATS SE SONT BIEN DEROULES!")
        else:
            print(f"\n  ⚠ {self.fights_crashed} crash(es) detecte(s)")

        print("=" * 60 + "\n")

        # Fermer
        self.send_key('escape')

if __name__ == "__main__":
    tester = RandomFightTester()
    tester.run_fight_test(num_fights=5)
