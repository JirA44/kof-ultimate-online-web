#!/usr/bin/env python3
"""
KOF Ultimate Online - Menu Navigation Simulator
Simulates players navigating through all menus to find bugs
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
    print("Installing pyautogui...")
    subprocess.run(["pip", "install", "pyautogui"], capture_output=True)
    import pyautogui
    pyautogui.FAILSAFE = False

GAME_PATH = r"D:\KOF Ultimate Online"
LOG_FILE = os.path.join(GAME_PATH, "Ikemen.log")
RESULTS_FILE = os.path.join(GAME_PATH, "save", "menu_test_results.json")

class MenuSimulator:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "crashes": [],
            "passed": 0,
            "failed": 0
        }
        self.delay = 0.3  # Delay between inputs

    def clear_log(self):
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)

    def check_crash(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                return True, f.read()
        return False, None

    def press_key(self, key, times=1):
        """Press a key multiple times"""
        for _ in range(times):
            pyautogui.press(key)
            time.sleep(self.delay)

    def navigate_down(self, times=1):
        self.press_key('down', times)

    def navigate_up(self, times=1):
        self.press_key('up', times)

    def confirm(self):
        self.press_key('a')

    def back(self):
        self.press_key('s')

    def wait(self, seconds=1):
        time.sleep(seconds)

    def test_menu_path(self, path_name, actions):
        """Test a specific menu path"""
        print(f"\n  Testing: {path_name}")
        self.clear_log()

        try:
            for action in actions:
                if action.startswith("down"):
                    count = int(action.replace("down", "") or "1")
                    self.navigate_down(count)
                elif action.startswith("up"):
                    count = int(action.replace("up", "") or "1")
                    self.navigate_up(count)
                elif action == "confirm":
                    self.confirm()
                elif action == "back":
                    self.back()
                elif action.startswith("wait"):
                    seconds = float(action.replace("wait", "") or "1")
                    self.wait(seconds)

                # Check for crash after each action
                crashed, log = self.check_crash()
                if crashed:
                    print(f"    [CRASH] {path_name}")
                    print(f"    Error: {log[:200]}")
                    self.results["crashes"].append({
                        "path": path_name,
                        "error": log
                    })
                    self.results["failed"] += 1
                    return False

            print(f"    [OK] {path_name}")
            self.results["passed"] += 1
            self.results["tests"].append({
                "path": path_name,
                "status": "passed"
            })
            return True

        except Exception as e:
            print(f"    [ERROR] {path_name}: {e}")
            self.results["failed"] += 1
            return False

    def run_all_tests(self):
        """Run all menu navigation tests"""
        print("\n" + "="*60)
        print("  KOF ULTIMATE ONLINE - MENU NAVIGATION SIMULATOR")
        print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("="*60)

        # Wait for game to be ready
        print("\n  Waiting for game window...")
        self.wait(3)

        # Test paths - each path is a list of actions
        test_paths = [
            # Main Menu -> Online -> Rankings
            ("Online > Rankings", [
                "down4", "confirm",  # Go to Online
                "wait1",
                "confirm",  # Select Rankings (first option)
                "wait2",
                "back",  # Return
                "wait1",
                "back"  # Return to main
            ]),

            # Main Menu -> Online -> My Profile
            ("Online > My Profile", [
                "down4", "confirm",  # Go to Online
                "wait1",
                "down1", "confirm",  # Select My Profile
                "wait2",
                "back",
                "wait1",
                "back"
            ]),

            # Main Menu -> Online -> Live Lobby
            ("Online > Live Lobby", [
                "down4", "confirm",  # Go to Online
                "wait1",
                "down2", "confirm",  # Select Live Lobby
                "wait2",
                "back",
                "wait1",
                "back"
            ]),

            # Live Lobby -> Find Ranked Match
            ("Lobby > Find Ranked", [
                "down4", "confirm",  # Go to Online
                "wait1",
                "down2", "confirm",  # Select Live Lobby
                "wait1",
                "confirm",  # Find Ranked Match (first option)
                "wait2",
                "back",  # Cancel matchmaking
                "wait1",
                "back",  # Exit lobby
                "wait1",
                "back"
            ]),

            # Live Lobby -> Find Casual Match
            ("Lobby > Find Casual", [
                "down4", "confirm",
                "wait1",
                "down2", "confirm",
                "wait1",
                "down1", "confirm",  # Find Casual Match
                "wait2",
                "back",
                "wait1",
                "back",
                "wait1",
                "back"
            ]),

            # Live Lobby -> Train vs AI
            ("Lobby > Train AI", [
                "down4", "confirm",
                "wait1",
                "down2", "confirm",
                "wait1",
                "down2", "confirm",  # Train vs AI
                "wait2",
                "back",
                "wait1",
                "back"
            ]),

            # Rankings -> Scroll and view
            ("Rankings > Scroll", [
                "down4", "confirm",
                "wait1",
                "confirm",  # Rankings
                "wait1",
                "down5",  # Scroll down
                "wait1",
                "up5",  # Scroll up
                "wait1",
                "back",
                "wait1",
                "back"
            ]),
        ]

        print(f"\n  Running {len(test_paths)} menu navigation tests...")

        for path_name, actions in test_paths:
            self.test_menu_path(path_name, actions)
            self.wait(1)  # Pause between tests

        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate final report"""
        print("\n" + "="*60)
        print("  SIMULATION RESULTS")
        print("="*60)

        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0

        print(f"\n  Tests Passed: {self.results['passed']}/{total} ({pass_rate:.1f}%)")
        print(f"  Tests Failed: {self.results['failed']}/{total}")

        if self.results["crashes"]:
            print(f"\n  CRASHES DETECTED: {len(self.results['crashes'])}")
            for crash in self.results["crashes"]:
                print(f"    - {crash['path']}")

        # Save results
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n  Results saved to: {RESULTS_FILE}")

        if self.results["failed"] == 0:
            print("\n  " + "="*40)
            print("  ALL MENU TESTS PASSED!")
            print("  " + "="*40)
        else:
            print("\n  " + "="*40)
            print("  SOME TESTS FAILED - CHECK CRASHES")
            print("  " + "="*40)


if __name__ == "__main__":
    # First make sure game is running
    print("Starting menu navigation simulation...")
    print("Make sure the game is running and on the main menu!")

    simulator = MenuSimulator()
    simulator.run_all_tests()
