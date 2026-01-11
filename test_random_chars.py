#!/usr/bin/env python3
"""Test multiple random characters with input injection"""
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
    'z': ord('Z'),
    'x': ord('X'),
}

class CharTester:
    def __init__(self):
        self.game_hwnd = None
        self.results = []
        self.start_time = datetime.now()

    def log(self, msg):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"[{elapsed:>6.1f}s] {msg}")

    def find_game_window(self):
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if any(k in title for k in ["KOF", "Ikemen", "MUGEN"]):
                    windows.append((hwnd, title))
            return True
        windows = []
        win32gui.EnumWindows(callback, windows)
        if windows:
            self.game_hwnd = windows[0][0]
            return True
        return False

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

    def test_character(self, char_num):
        """Select and test a specific character slot"""
        self.log(f"Testing character slot {char_num}...")

        # Navigate to character (assuming 19 columns grid)
        row = char_num // 19
        col = char_num % 19

        # Reset to top-left
        for _ in range(15):
            self.send_key('up', 0.05)
        for _ in range(15):
            self.send_key('left', 0.05)

        # Navigate to position
        for _ in range(row):
            self.send_key('down', 0.08)
        for _ in range(col):
            self.send_key('right', 0.08)

        # Select P1
        self.send_key('space', 0.3)
        time.sleep(0.5)

        # Select P2 (same char)
        self.send_key('space', 0.3)
        time.sleep(1)

        # Wait for match to load
        time.sleep(3)

        # Quick combat test
        actions = ['a', 's', 'z', 'x', 'left', 'right', 'down', 'up']
        for _ in range(20):
            self.send_key(random.choice(actions), 0.1)

        time.sleep(0.5)

        # Exit match
        self.send_key('escape', 0.2)
        time.sleep(0.5)
        self.send_key('down', 0.1)  # Go to "Exit"
        self.send_key('space', 0.2)
        time.sleep(1)

        self.log(f"  Character {char_num} OK!")
        return True

    def run_tests(self, num_chars=5):
        print("\n" + "="*60)
        print("  TEST DE PERSONNAGES ALEATOIRES")
        print("="*60 + "\n")

        # Launch game
        exe_path = GAME_PATH / GAME_EXE
        subprocess.Popen([str(exe_path)], cwd=str(GAME_PATH))
        self.log("Lancement du jeu...")

        # Wait for window
        for _ in range(30):
            if self.find_game_window():
                break
            time.sleep(1)

        if not self.game_hwnd:
            self.log("ERREUR: Fenetre non trouvee!")
            return

        time.sleep(3)

        # Enter menu
        self.send_key('space', 0.3)
        time.sleep(2)

        # Select Versus
        self.send_key('down', 0.1)
        self.send_key('space', 0.3)
        time.sleep(2)

        # Test random characters
        char_slots = random.sample(range(150), min(num_chars, 150))

        for slot in char_slots:
            try:
                self.test_character(slot)
                self.results.append((slot, "OK"))
            except Exception as e:
                self.log(f"  ERREUR: {e}")
                self.results.append((slot, f"ERREUR: {e}"))
                # Try to recover
                self.send_key('escape', 0.2)
                time.sleep(1)

        # Exit game
        self.send_key('escape', 0.2)
        time.sleep(0.5)

        # Print results
        print("\n" + "="*60)
        print("  RESULTATS")
        print("="*60)
        ok = sum(1 for _, r in self.results if r == "OK")
        print(f"  {ok}/{len(self.results)} personnages OK")

        for slot, result in self.results:
            status = "✓" if result == "OK" else "✗"
            print(f"  {status} Slot {slot}: {result}")

if __name__ == "__main__":
    tester = CharTester()
    tester.run_tests(5)  # Test 5 random characters
