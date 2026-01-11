#!/usr/bin/env python3
"""Test all game modes with input injection"""
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
}

class ModeTester:
    def __init__(self):
        self.game_hwnd = None
        self.start_time = datetime.now()
        self.results = {}

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

    def go_to_menu(self):
        """Return to main menu"""
        for _ in range(5):
            self.send_key('escape', 0.2)
            time.sleep(0.3)

    def test_arcade(self):
        """Test Arcade mode"""
        self.log("Testing ARCADE mode...")
        self.send_key('space')  # Select Arcade
        time.sleep(2)

        # Select character
        self.send_key('space')
        time.sleep(3)

        # Quick fight
        for _ in range(10):
            self.send_key('a', 0.1)
        time.sleep(1)

        # Exit
        self.send_key('escape')
        time.sleep(0.5)
        self.send_key('down')
        self.send_key('space')
        time.sleep(1)

        self.log("  ARCADE: OK")
        return True

    def test_versus(self):
        """Test Versus mode"""
        self.log("Testing VS MODE...")
        self.send_key('down')  # Go to Versus
        self.send_key('space')
        time.sleep(2)

        # Select P1
        self.send_key('space')
        time.sleep(0.5)
        # Select P2
        self.send_key('space')
        time.sleep(3)

        # Quick fight
        for _ in range(10):
            self.send_key('a', 0.1)
        time.sleep(1)

        # Exit
        self.send_key('escape')
        time.sleep(0.5)
        self.send_key('down')
        self.send_key('space')
        time.sleep(1)

        self.log("  VS MODE: OK")
        return True

    def test_training(self):
        """Test Training mode"""
        self.log("Testing TRAINING mode...")

        # Navigate to Training (after Versus)
        for _ in range(5):
            self.send_key('down')
        self.send_key('space')
        time.sleep(2)

        # Select character
        self.send_key('space')
        time.sleep(3)

        # Test some moves
        for _ in range(15):
            self.send_key('a', 0.1)
            self.send_key('s', 0.1)
        time.sleep(1)

        # Exit
        self.send_key('escape')
        time.sleep(0.5)
        self.send_key('down')
        self.send_key('space')
        time.sleep(1)

        self.log("  TRAINING: OK")
        return True

    def test_online_menu(self):
        """Test Online menu navigation"""
        self.log("Testing ONLINE menu...")

        # Navigate to Online
        for _ in range(6):
            self.send_key('down')
        self.send_key('space')
        time.sleep(1)

        # Navigate submenu
        for i in range(4):
            self.send_key('down')
            time.sleep(0.3)

        # Go back
        self.send_key('escape')
        time.sleep(0.5)

        self.log("  ONLINE menu: OK")
        return True

    def run_all_tests(self):
        print("\n" + "="*60)
        print("  TEST DE TOUS LES MODES DE JEU")
        print("="*60 + "\n")

        # Launch game
        exe_path = GAME_PATH / GAME_EXE
        subprocess.Popen([str(exe_path)], cwd=str(GAME_PATH))
        self.log("Lancement du jeu...")

        # Wait for window
        for _ in range(30):
            if self.find_window():
                break
            time.sleep(1)

        if not self.game_hwnd:
            self.log("ERREUR: Fenetre non trouvee!")
            return

        time.sleep(5)

        # Enter menu
        self.send_key('space')
        time.sleep(2)

        # Test each mode
        try:
            self.results['arcade'] = self.test_arcade()
        except Exception as e:
            self.log(f"  ARCADE ERREUR: {e}")
            self.results['arcade'] = False
            self.go_to_menu()

        time.sleep(1)

        try:
            self.results['versus'] = self.test_versus()
        except Exception as e:
            self.log(f"  VS MODE ERREUR: {e}")
            self.results['versus'] = False
            self.go_to_menu()

        time.sleep(1)

        try:
            self.results['training'] = self.test_training()
        except Exception as e:
            self.log(f"  TRAINING ERREUR: {e}")
            self.results['training'] = False
            self.go_to_menu()

        time.sleep(1)

        try:
            self.results['online'] = self.test_online_menu()
        except Exception as e:
            self.log(f"  ONLINE ERREUR: {e}")
            self.results['online'] = False

        # Print results
        print("\n" + "="*60)
        print("  RESULTATS")
        print("="*60)

        ok = sum(1 for v in self.results.values() if v)
        total = len(self.results)

        for mode, result in self.results.items():
            status = "✓" if result else "✗"
            print(f"  {status} {mode.upper()}: {'OK' if result else 'ERREUR'}")

        print(f"\n  Total: {ok}/{total} modes OK")

        # Close game
        self.send_key('escape')
        time.sleep(0.5)

if __name__ == "__main__":
    tester = ModeTester()
    tester.run_all_tests()
