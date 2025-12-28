#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE ONLINE - FULL SYSTEM TEST
Tests all components of the game installation
"""

import os
import sys
import json
import time
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime

GAME_DIR = Path(__file__).parent

class FullTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def test(self, name, condition, details=""):
        """Run a test and record result"""
        if condition:
            self.results.append(("PASS", name, details))
            self.passed += 1
            print(f"  [PASS] {name}")
        else:
            self.results.append(("FAIL", name, details))
            self.failed += 1
            print(f"  [FAIL] {name} - {details}")
        return condition

    def test_game_files(self):
        """Test 1: Game files exist"""
        print("\n[TEST 1] Game Files")
        print("-" * 50)

        self.test("Ikemen_GO.exe exists",
                  (GAME_DIR / "Ikemen_GO.exe").exists())

        self.test("data folder exists",
                  (GAME_DIR / "data").exists())

        self.test("chars folder exists",
                  (GAME_DIR / "chars").exists())

        self.test("stages folder exists",
                  (GAME_DIR / "stages").exists())

        self.test("system.def exists",
                  (GAME_DIR / "data" / "system.def").exists())

    def test_roster(self):
        """Test 2: Roster configuration"""
        print("\n[TEST 2] Roster Configuration")
        print("-" * 50)

        # Check roster files
        roster_files = ["select_final.def", "select_pro.def", "select_optimized.def"]
        found_roster = None
        for r in roster_files:
            if (GAME_DIR / "data" / r).exists():
                found_roster = r
                break

        self.test("Roster file exists", found_roster is not None, found_roster or "No roster found")

        if found_roster:
            roster_path = GAME_DIR / "data" / found_roster
            content = roster_path.read_text(encoding='utf-8', errors='ignore')
            lines = [l for l in content.split('\n') if l.strip() and not l.startswith(';') and ',' in l]
            char_count = len(lines)
            self.test(f"Roster has characters", char_count > 0, f"{char_count} characters")

        # Check system.def points to valid roster
        system_def = GAME_DIR / "data" / "system.def"
        if system_def.exists():
            content = system_def.read_text(encoding='utf-8', errors='ignore')
            import re
            match = re.search(r'select\s*=\s*(\S+)', content)
            if match:
                active_roster = match.group(1)
                roster_exists = (GAME_DIR / "data" / active_roster).exists()
                self.test("system.def points to valid roster", roster_exists, active_roster)

    def test_characters(self):
        """Test 3: Character files"""
        print("\n[TEST 3] Characters")
        print("-" * 50)

        chars_dir = GAME_DIR / "chars"
        if not chars_dir.exists():
            self.test("Characters folder", False, "Missing")
            return

        char_folders = [d for d in chars_dir.iterdir() if d.is_dir()]
        self.test("Character folders exist", len(char_folders) > 0, f"{len(char_folders)} folders")

        # Check random sample of characters
        valid_chars = 0
        for char in char_folders[:20]:  # Check first 20
            def_files = list(char.glob("*.def"))
            if def_files:
                valid_chars += 1

        self.test("Characters have DEF files", valid_chars > 0, f"{valid_chars}/20 checked")

    def test_stages(self):
        """Test 4: Stages"""
        print("\n[TEST 4] Stages")
        print("-" * 50)

        stages_dir = GAME_DIR / "stages"
        if not stages_dir.exists():
            self.test("Stages folder", False, "Missing")
            return

        stage_files = list(stages_dir.glob("*.def"))
        self.test("Stage DEF files exist", len(stage_files) > 0, f"{len(stage_files)} stages")

        # Check main stage
        main_stage = stages_dir / "Abyss-Rugal-Palace.def"
        self.test("Main stage exists", main_stage.exists())

    def test_config(self):
        """Test 5: Game configuration"""
        print("\n[TEST 5] Configuration")
        print("-" * 50)

        config_path = GAME_DIR / "save" / "config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.test("config.json is valid JSON", True)
                self.test("Debug mode off", config.get("DebugMode") == False)
            except:
                self.test("config.json is valid JSON", False, "Parse error")
        else:
            self.test("config.json exists", False, "Not found")

    def test_online_components(self):
        """Test 6: Online components"""
        print("\n[TEST 6] Online Components")
        print("-" * 50)

        # Check lobby HTML
        lobby_files = ["KOF_ONLINE_FIREBASE.html", "KOF_ONLINE_LAUNCHER.html"]
        found_lobby = False
        for f in lobby_files:
            if (GAME_DIR / f).exists():
                found_lobby = True
                self.test(f"Lobby file: {f}", True)

                # Check if Firebase config exists in file
                content = (GAME_DIR / f).read_text(encoding='utf-8', errors='ignore')
                has_firebase = "firebase" in content.lower()
                self.test("Firebase integration", has_firebase)
                break

        if not found_lobby:
            self.test("Online lobby exists", False, "No lobby file found")

    def test_launcher(self):
        """Test 7: Launcher"""
        print("\n[TEST 7] Launcher")
        print("-" * 50)

        launcher = GAME_DIR / "KOF_LAUNCHER.py"
        self.test("KOF_LAUNCHER.py exists", launcher.exists())

        bat_launcher = GAME_DIR / "INSTALL_AND_PLAY.bat"
        self.test("INSTALL_AND_PLAY.bat exists", bat_launcher.exists())

        play_bat = GAME_DIR / "PLAY_KOF.bat"
        self.test("PLAY_KOF.bat exists", play_bat.exists())

    def test_repair_scripts(self):
        """Test 8: Repair scripts"""
        print("\n[TEST 8] Repair Scripts")
        print("-" * 50)

        scripts = ["AUTO_FIX_ALL.py", "DEEP_FIX_CHARS.py", "FIX_FLYAWAY.py"]
        for s in scripts:
            self.test(f"{s} exists", (GAME_DIR / s).exists())

    def test_game_launch(self):
        """Test 9: Game launch"""
        print("\n[TEST 9] Game Launch")
        print("-" * 50)

        exe_path = GAME_DIR / "Ikemen_GO.exe"
        if not exe_path.exists():
            self.test("Game executable", False, "Not found")
            return

        try:
            # Launch game
            proc = subprocess.Popen(
                [str(exe_path)],
                cwd=str(GAME_DIR),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait a bit
            time.sleep(3)

            # Check if still running
            if proc.poll() is None:
                self.test("Game launches without crash", True)
                # Kill it for now
                proc.terminate()
            else:
                self.test("Game launches without crash", False, "Crashed immediately")

        except Exception as e:
            self.test("Game launches", False, str(e))

    def test_matchmaking_config(self):
        """Test 10: Matchmaking configuration"""
        print("\n[TEST 10] Matchmaking")
        print("-" * 50)

        config_path = GAME_DIR / "save" / "launcher_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.test("Launcher config exists", True)
                self.test("Matchmaking enabled", config.get("matchmaking", {}).get("enabled", False))
            except:
                self.test("Launcher config valid", False, "Parse error")
        else:
            self.test("Launcher config exists", False, "Run launcher first")

    def run_all_tests(self):
        """Run all tests"""
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    KOF ULTIMATE ONLINE - FULL SYSTEM TEST                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)

        self.test_game_files()
        self.test_roster()
        self.test_characters()
        self.test_stages()
        self.test_config()
        self.test_online_components()
        self.test_launcher()
        self.test_repair_scripts()
        self.test_game_launch()
        self.test_matchmaking_config()

        # Summary
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            TEST RESULTS                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Total Tests: {total:<60}║
║  Passed: {self.passed:<65}║
║  Failed: {self.failed:<65}║
║  Success Rate: {success_rate:.1f}%{' '*56}║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Status: {'ALL TESTS PASSED!' if self.failed == 0 else 'SOME TESTS FAILED':<63}║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)

        # Show failures
        if self.failed > 0:
            print("\nFailed tests:")
            for status, name, details in self.results:
                if status == "FAIL":
                    print(f"  - {name}: {details}")

        # Save results
        report = {
            "timestamp": datetime.now().isoformat(),
            "passed": self.passed,
            "failed": self.failed,
            "success_rate": success_rate,
            "results": [{"status": s, "name": n, "details": d} for s, n, d in self.results]
        }

        with open(GAME_DIR / "test_report.json", 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: test_report.json")

        return self.failed == 0


if __name__ == "__main__":
    tester = FullTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
