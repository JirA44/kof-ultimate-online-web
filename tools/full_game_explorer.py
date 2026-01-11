#!/usr/bin/env python3
"""
KOF Ultimate Online - Full Game Explorer
Automatically explores ALL menus and options to find bugs
"""

import subprocess
import time
import os
import json
from datetime import datetime

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except ImportError:
    subprocess.run(["pip", "install", "pyautogui"], capture_output=True)
    import pyautogui
    pyautogui.FAILSAFE = False

GAME_PATH = r"D:\KOF Ultimate Online"
LOG_FILE = os.path.join(GAME_PATH, "Ikemen.log")
RESULTS_FILE = os.path.join(GAME_PATH, "save", "full_exploration_results.json")

class GameExplorer:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "crashes": [],
            "warnings": [],
            "passed": 0,
            "failed": 0
        }
        self.delay = 0.25

    def clear_log(self):
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)

    def check_crash(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                return True, f.read()
        return False, None

    def key(self, k, times=1):
        for _ in range(times):
            pyautogui.press(k)
            time.sleep(self.delay)

    def down(self, n=1): self.key('down', n)
    def up(self, n=1): self.key('up', n)
    def left(self, n=1): self.key('left', n)
    def right(self, n=1): self.key('right', n)
    def confirm(self): self.key('a')
    def back(self): self.key('s')
    def wait(self, s=1): time.sleep(s)

    def test(self, name, actions):
        """Execute a test sequence"""
        print(f"  [{len(self.results['tests'])+1:02d}] {name}...", end=" ", flush=True)
        self.clear_log()

        try:
            for action in actions:
                # Parse action
                if callable(action):
                    action()
                elif action.startswith("d"):
                    self.down(int(action[1:] or 1))
                elif action.startswith("u"):
                    self.up(int(action[1:] or 1))
                elif action.startswith("l"):
                    self.left(int(action[1:] or 1))
                elif action.startswith("r"):
                    self.right(int(action[1:] or 1))
                elif action == "a":
                    self.confirm()
                elif action == "b":
                    self.back()
                elif action.startswith("w"):
                    self.wait(float(action[1:] or 1))

                # Check crash
                crashed, log = self.check_crash()
                if crashed:
                    print(f"CRASH!")
                    self.results["crashes"].append({"test": name, "error": log[:500]})
                    self.results["failed"] += 1
                    self.results["tests"].append({"name": name, "status": "CRASH", "error": log[:200]})
                    # Try to recover
                    for _ in range(5):
                        self.back()
                        self.wait(0.3)
                    return False

            print("OK")
            self.results["passed"] += 1
            self.results["tests"].append({"name": name, "status": "OK"})
            return True

        except Exception as e:
            print(f"ERROR: {e}")
            self.results["failed"] += 1
            self.results["tests"].append({"name": name, "status": "ERROR", "error": str(e)})
            return False

    def explore_all(self):
        """Explore all game menus"""
        print("\n" + "="*60)
        print("  KOF ULTIMATE ONLINE - FULL GAME EXPLORER")
        print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("="*60)
        print("\n  Starting in 3 seconds... (game should be on main menu)")
        self.wait(3)

        # ============================================================
        # MAIN MENU EXPLORATION
        # ============================================================
        print("\n" + "-"*40)
        print("  MAIN MENU TESTS")
        print("-"*40)

        # Test 1: Arcade Mode Entry/Exit
        self.test("Arcade Mode > Enter > Exit", [
            "a", "w2", "b", "w1", "b", "w1"
        ])

        # Test 2: Versus Mode Entry/Exit
        self.test("Versus Mode > Enter > Exit", [
            "d1", "a", "w2", "b", "w1", "b", "w1"
        ])

        # Test 3: Team Arcade
        self.test("Team Arcade > Enter > Exit", [
            "d2", "a", "w2", "b", "w1", "b", "w1"
        ])

        # Test 4: Team Versus
        self.test("Team Versus > Enter > Exit", [
            "d3", "a", "w2", "b", "w1", "b", "w1"
        ])

        # ============================================================
        # ONLINE MENU EXPLORATION
        # ============================================================
        print("\n" + "-"*40)
        print("  ONLINE MENU TESTS")
        print("-"*40)

        # Test: Online Menu
        self.test("Online Menu > Open", [
            "d4", "a", "w1"
        ])

        # Test: Rankings - scroll through all
        self.test("Rankings > View All > Scroll", [
            "a", "w1",  # Enter rankings
            "d10", "w0.5", "u10", "w0.5",  # Scroll
            "b", "w1"  # Back
        ])

        # Test: Profile
        self.test("My Profile > View", [
            "d1", "a", "w2",
            "b", "w1"
        ])

        # Test: Live Lobby - all options
        self.test("Live Lobby > All Options", [
            "d2", "a", "w1",  # Enter lobby
            "a", "w1.5", "b", "w0.5",  # Find Ranked
            "d1", "a", "w1.5", "b", "w0.5",  # Find Casual
            "d2", "a", "w1.5", "b", "w0.5",  # Train AI
            "d3", "a", "w1.5", "b", "w0.5",  # Create Lobby
            "d4", "a", "w1",  # View Leaderboard
            "b", "w1",  # Back from leaderboard
            "b", "w1"  # Back from lobby
        ])

        # Back to main menu
        self.test("Return to Main Menu", [
            "b", "w1"
        ])

        # ============================================================
        # OPTIONS MENU EXPLORATION
        # ============================================================
        print("\n" + "-"*40)
        print("  OPTIONS MENU TESTS")
        print("-"*40)

        # Find Options (usually near bottom)
        self.test("Options > Enter > Navigate", [
            "d7", "a", "w1",  # Enter options (adjust if needed)
            "d1", "w0.3", "d1", "w0.3", "d1", "w0.3",
            "u3", "w0.3",
            "b", "w1"
        ])

        # ============================================================
        # CHARACTER SELECT EXPLORATION
        # ============================================================
        print("\n" + "-"*40)
        print("  CHARACTER SELECT TESTS")
        print("-"*40)

        # Versus mode character select
        self.test("Versus > Character Grid Navigation", [
            "d1", "a", "w2",  # Enter versus
            # Navigate character grid
            "r5", "w0.3", "d3", "w0.3", "l5", "w0.3", "u3", "w0.3",
            "b", "w1", "b", "w1"
        ])

        # Quick character selection test
        self.test("Versus > Select Random Chars", [
            "d1", "a", "w2",
            "a", "w0.5",  # Select P1 char
            "a", "w0.5",  # Select P2 char
            "w1",
            "b", "w0.5", "b", "w0.5", "b", "w1"  # Back out
        ])

        # ============================================================
        # TRAINING MODE
        # ============================================================
        print("\n" + "-"*40)
        print("  TRAINING MODE TESTS")
        print("-"*40)

        self.test("Training Mode > Enter > Exit", [
            "d5", "a", "w2",  # Enter training (adjust position)
            "b", "w1", "b", "w1"
        ])

        # ============================================================
        # SURVIVAL MODE
        # ============================================================
        print("\n" + "-"*40)
        print("  OTHER MODES TESTS")
        print("-"*40)

        self.test("Survival > Enter > Exit", [
            "d6", "a", "w2",
            "b", "w1", "b", "w1"
        ])

        # ============================================================
        # WATCH MODE
        # ============================================================
        self.test("Watch Mode > Enter > Exit", [
            "d8", "a", "w2",
            "b", "w1"
        ])

        # ============================================================
        # RAPID MENU SWITCHING (stress test)
        # ============================================================
        print("\n" + "-"*40)
        print("  STRESS TESTS")
        print("-"*40)

        self.test("Rapid Menu Navigation", [
            "d1", "a", "w0.3", "b", "w0.3",
            "d2", "a", "w0.3", "b", "w0.3",
            "d3", "a", "w0.3", "b", "w0.3",
            "d4", "a", "w0.3", "b", "w0.3",
            "u4", "w0.3"
        ])

        self.test("Online Rapid Access", [
            "d4", "a", "w0.5",  # Online
            "a", "w0.3", "b", "w0.3",  # Rankings
            "d1", "a", "w0.3", "b", "w0.3",  # Profile
            "d2", "a", "w0.3", "b", "w0.3",  # Lobby
            "b", "w0.5"  # Back
        ])

        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate exploration report"""
        print("\n" + "="*60)
        print("  EXPLORATION RESULTS")
        print("="*60)

        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0

        print(f"\n  Tests Passed: {self.results['passed']}/{total} ({pass_rate:.1f}%)")
        print(f"  Tests Failed: {self.results['failed']}/{total}")

        if self.results["crashes"]:
            print(f"\n  CRASHES FOUND: {len(self.results['crashes'])}")
            for crash in self.results["crashes"]:
                print(f"    - {crash['test']}")
                print(f"      {crash['error'][:100]}...")

        # List all results
        print("\n  Detailed Results:")
        for t in self.results["tests"]:
            status = "✓" if t["status"] == "OK" else "✗"
            print(f"    {status} {t['name']}")

        # Save
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n  Full report: {RESULTS_FILE}")

        if self.results["failed"] == 0:
            print("\n  " + "="*40)
            print("  ALL EXPLORATIONS PASSED!")
            print("  " + "="*40)
        else:
            print("\n  " + "="*40)
            print(f"  {self.results['failed']} ISSUES FOUND")
            print("  " + "="*40)


if __name__ == "__main__":
    print("="*60)
    print("  KOF ULTIMATE ONLINE - FULL GAME EXPLORER")
    print("="*60)
    print("\n  This will automatically explore ALL game menus.")
    print("  Make sure:")
    print("    1. Game is running")
    print("    2. Game is on MAIN MENU")
    print("    3. Don't touch keyboard/mouse during test")

    explorer = GameExplorer()
    explorer.explore_all()
