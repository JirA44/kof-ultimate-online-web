#!/usr/bin/env python3
"""
KOF Ultimate Online - Game Explorer with Window Focus
"""

import subprocess
import time
import os
import json
from datetime import datetime

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except:
    subprocess.run(["pip", "install", "pyautogui"], capture_output=True)
    import pyautogui
    pyautogui.FAILSAFE = False

try:
    import pygetwindow as gw
except:
    subprocess.run(["pip", "install", "pygetwindow"], capture_output=True)
    import pygetwindow as gw

GAME_PATH = r"D:\KOF Ultimate Online"
LOG_FILE = os.path.join(GAME_PATH, "Ikemen.log")

def focus_game():
    """Focus the IKEMEN-GO game window"""
    windows = gw.getWindowsWithTitle('I.K.E.M.E.N')
    if not windows:
        windows = gw.getWindowsWithTitle('Ikemen')
    if not windows:
        windows = gw.getWindowsWithTitle('KOF')
    if windows:
        win = windows[0]
        win.activate()
        time.sleep(0.5)
        return True
    print("  [!] Game window not found!")
    return False

def clear_log():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

def check_crash():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', errors='ignore') as f:
            return True, f.read()
    return False, None

def key(k, times=1, delay=0.2):
    for _ in range(times):
        pyautogui.press(k)
        time.sleep(delay)

def test(name, actions, delay=0.25):
    """Run a test with window focus"""
    print(f"  {name}...", end=" ", flush=True)

    if not focus_game():
        print("NO WINDOW")
        return False

    clear_log()

    for action in actions:
        if action.startswith("d"):
            key('down', int(action[1:] or 1), delay)
        elif action.startswith("u"):
            key('up', int(action[1:] or 1), delay)
        elif action.startswith("l"):
            key('left', int(action[1:] or 1), delay)
        elif action.startswith("r"):
            key('right', int(action[1:] or 1), delay)
        elif action == "a":
            key('a', 1, delay)
        elif action == "b":
            key('s', 1, delay)
        elif action.startswith("w"):
            time.sleep(float(action[1:] or 1))

        crashed, log = check_crash()
        if crashed:
            print(f"CRASH: {log[:80]}")
            for _ in range(5):
                key('s', 1, 0.3)
            return False

    print("OK")
    return True

def main():
    print("\n" + "="*50)
    print("  KOF ULTIMATE ONLINE - GAME EXPLORER")
    print("="*50)

    # Check game is running
    if not focus_game():
        print("\n  Game not running! Starting...")
        subprocess.Popen([os.path.join(GAME_PATH, "Ikemen_GO.exe")], cwd=GAME_PATH)
        time.sleep(8)
        if not focus_game():
            print("  Failed to start game!")
            return

    print("\n  Game found! Starting tests in 2 seconds...")
    time.sleep(2)

    results = {"passed": 0, "failed": 0, "tests": []}

    # ========== MAIN MENU ==========
    print("\n--- MAIN MENU ---")

    if test("Arcade > Enter > Back", ["a", "w1", "b", "b", "w0.5"]):
        results["passed"] += 1
    else:
        results["failed"] += 1

    if test("Versus > Enter > Back", ["d1", "a", "w1", "b", "b", "w0.5"]):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # ========== ONLINE ==========
    print("\n--- ONLINE MENU ---")

    if test("Online > Open", ["d4", "a", "w1"]):
        results["passed"] += 1
    else:
        results["failed"] += 1

    if test("Rankings > View > Back", ["a", "w1", "d5", "u5", "b", "w0.5"]):
        results["passed"] += 1
    else:
        results["failed"] += 1

    if test("Profile > View > Back", ["d1", "a", "w1", "b", "w0.5"]):
        results["passed"] += 1
    else:
        results["failed"] += 1

    if test("Lobby > Open", ["d2", "a", "w1"]):
        results["passed"] += 1
    else:
        results["failed"] += 1

    if test("Lobby > Ranked > Cancel", ["a", "w1", "b", "w0.5"]):
        results["passed"] += 1
    else:
        results["failed"] += 1

    if test("Lobby > Casual > Cancel", ["d1", "a", "w1", "b", "w0.5"]):
        results["passed"] += 1
    else:
        results["failed"] += 1

    if test("Lobby > AI Training", ["d2", "a", "w1"]):
        results["passed"] += 1
    else:
        results["failed"] += 1

    if test("Lobby > Back to Menu", ["b", "b", "w0.5"]):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # ========== CHARACTER SELECT ==========
    print("\n--- CHARACTER SELECT ---")

    if test("Versus > Char Select > Navigate", ["d1", "a", "w1", "r5", "d3", "l5", "u3", "b", "b", "w0.5"]):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # ========== RESULTS ==========
    print("\n" + "="*50)
    total = results["passed"] + results["failed"]
    print(f"  RESULTS: {results['passed']}/{total} passed")
    if results["failed"] > 0:
        print(f"  {results['failed']} TESTS FAILED!")
    else:
        print("  ALL TESTS PASSED!")
    print("="*50)

if __name__ == "__main__":
    main()
