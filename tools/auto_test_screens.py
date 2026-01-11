#!/usr/bin/env python3
"""
KOF Ultimate Online - Automated Screen Testing System
Tests all menu screens automatically and reports issues
"""

import subprocess
import time
import os
import json
from datetime import datetime

GAME_PATH = r"D:\KOF Ultimate Online"
IKEMEN_EXE = os.path.join(GAME_PATH, "Ikemen_GO.exe")
LOG_FILE = os.path.join(GAME_PATH, "Ikemen.log")
RESULTS_FILE = os.path.join(GAME_PATH, "save", "test_results.json")

class GameTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "passed": 0,
            "failed": 0,
            "warnings": []
        }

    def clear_log(self):
        """Clear the crash log"""
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)

    def check_crash(self):
        """Check if game crashed"""
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return True, content
        return False, None

    def test_lua_syntax(self):
        """Test Lua files for syntax errors"""
        print("\n" + "="*60)
        print("  TEST 1: LUA SYNTAX CHECK")
        print("="*60)

        lua_files = [
            "external/script/main.lua",
            "external/script/leaderboard_screen.lua",
            "external/script/profile_screen.lua",
            "external/script/live_lobby_screen.lua",
            "external/script/ai_training.lua"
        ]

        errors = []
        for lua_file in lua_files:
            filepath = os.path.join(GAME_PATH, lua_file)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Check for common issues
                issues = []

                # Check for unterminated strings (literal newlines in patterns)
                if 'gmatch("[^' in content and ']+")' not in content:
                    # More detailed check
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'gmatch("[^' in line and ']+")' not in line:
                            issues.append(f"Line {i+1}: Possible unterminated string in gmatch")

                # Check for unbalanced brackets
                if content.count('{') != content.count('}'):
                    issues.append("Unbalanced curly braces")
                if content.count('(') != content.count(')'):
                    issues.append("Unbalanced parentheses")

                if issues:
                    errors.append({"file": lua_file, "issues": issues})
                    print(f"  [FAIL] {lua_file}")
                    for issue in issues:
                        print(f"         - {issue}")
                else:
                    print(f"  [OK] {lua_file}")
            else:
                print(f"  [SKIP] {lua_file} (not found)")

        test_result = {
            "name": "Lua Syntax Check",
            "passed": len(errors) == 0,
            "errors": errors
        }
        self.results["tests"].append(test_result)

        if len(errors) == 0:
            self.results["passed"] += 1
            print("\n  Result: PASSED")
        else:
            self.results["failed"] += 1
            print(f"\n  Result: FAILED ({len(errors)} files with issues)")

        return len(errors) == 0

    def test_json_files(self):
        """Test JSON data files"""
        print("\n" + "="*60)
        print("  TEST 2: JSON DATA FILES")
        print("="*60)

        json_files = [
            "save/leaderboard.json",
            "save/player_profile.json",
            "save/online_config.json"
        ]

        errors = []
        for json_file in json_files:
            filepath = os.path.join(GAME_PATH, json_file)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"  [OK] {json_file}")

                    # Validate leaderboard structure
                    if "leaderboard" in json_file and "rankings" in data:
                        print(f"       - {len(data['rankings'])} players loaded")
                except json.JSONDecodeError as e:
                    errors.append({"file": json_file, "error": str(e)})
                    print(f"  [FAIL] {json_file}: {e}")
            else:
                print(f"  [WARN] {json_file} (not found)")
                self.results["warnings"].append(f"Missing file: {json_file}")

        test_result = {
            "name": "JSON Data Files",
            "passed": len(errors) == 0,
            "errors": errors
        }
        self.results["tests"].append(test_result)

        if len(errors) == 0:
            self.results["passed"] += 1
            print("\n  Result: PASSED")
        else:
            self.results["failed"] += 1
            print(f"\n  Result: FAILED ({len(errors)} files with errors)")

        return len(errors) == 0

    def test_screen_modules(self):
        """Test that screen modules are properly structured"""
        print("\n" + "="*60)
        print("  TEST 3: SCREEN MODULE STRUCTURE")
        print("="*60)

        modules = {
            "leaderboard_screen.lua": ("leaderboard_screen", ["open", "close", "isActive", "handleInput", "getDisplayText"]),
            "profile_screen.lua": ("profile_screen", ["open", "close", "isActive", "handleInput", "getDisplayText"]),
            "live_lobby_screen.lua": ("live_lobby", ["open", "close", "isActive", "handleInput", "getDisplayText", "update"])
        }

        errors = []
        for module_file, (module_name, required_funcs) in modules.items():
            filepath = os.path.join(GAME_PATH, "external", "script", module_file)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                missing = []
                for func in required_funcs:
                    if f"function {module_name}.{func}" not in content and \
                       f"{module_name}.{func} = function" not in content:
                        missing.append(func)

                if missing:
                    errors.append({"file": module_file, "missing": missing})
                    print(f"  [FAIL] {module_file}")
                    print(f"         Missing: {', '.join(missing)}")
                else:
                    print(f"  [OK] {module_file}")
            else:
                errors.append({"file": module_file, "error": "File not found"})
                print(f"  [FAIL] {module_file} (not found)")

        test_result = {
            "name": "Screen Module Structure",
            "passed": len(errors) == 0,
            "errors": errors
        }
        self.results["tests"].append(test_result)

        if len(errors) == 0:
            self.results["passed"] += 1
            print("\n  Result: PASSED")
        else:
            self.results["failed"] += 1
            print(f"\n  Result: FAILED")

        return len(errors) == 0

    def test_main_handlers(self):
        """Test that main.lua has proper handlers for online screens"""
        print("\n" + "="*60)
        print("  TEST 4: MAIN.LUA HANDLERS")
        print("="*60)

        main_lua = os.path.join(GAME_PATH, "external", "script", "main.lua")

        if not os.path.exists(main_lua):
            print("  [FAIL] main.lua not found!")
            self.results["failed"] += 1
            return False

        with open(main_lua, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        handlers = ["rankings", "profile", "lobby"]
        errors = []

        for handler in handlers:
            pattern = f"main.t_itemname['{handler}']"
            if pattern in content:
                # Check for proper structure
                start = content.find(pattern)
                end = content.find("return nil\nend", start)
                if end == -1:
                    end = content.find("return nil\r\nend", start)

                if end > start:
                    handler_code = content[start:end+15]

                    checks = {
                        "main.f_bgReset": "Background reset",
                        "main.f_refresh": "Proper refresh",
                        "clearColor": "Clear color",
                        "bgDraw": "Background draw",
                        'font = "font/': "Valid font path"
                    }

                    issues = []
                    for check, desc in checks.items():
                        if check not in handler_code:
                            issues.append(f"Missing: {desc}")

                    if issues:
                        errors.append({"handler": handler, "issues": issues})
                        print(f"  [WARN] {handler}: {', '.join(issues)}")
                    else:
                        print(f"  [OK] {handler}")
                else:
                    errors.append({"handler": handler, "error": "Malformed handler"})
                    print(f"  [FAIL] {handler}: Malformed handler")
            else:
                errors.append({"handler": handler, "error": "Handler not found"})
                print(f"  [FAIL] {handler}: Handler not found")

        test_result = {
            "name": "Main.lua Handlers",
            "passed": len(errors) == 0,
            "errors": errors
        }
        self.results["tests"].append(test_result)

        if len(errors) == 0:
            self.results["passed"] += 1
            print("\n  Result: PASSED")
        else:
            self.results["failed"] += 1
            print(f"\n  Result: FAILED")

        return len(errors) == 0

    def test_font_files(self):
        """Test that required font files exist"""
        print("\n" + "="*60)
        print("  TEST 5: FONT FILES")
        print("="*60)

        fonts = [
            "font/f-6x9.fnt",
            "font/FONT MENU.fnt"
        ]

        errors = []
        for font in fonts:
            filepath = os.path.join(GAME_PATH, font)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"  [OK] {font} ({size} bytes)")
            else:
                errors.append(font)
                print(f"  [FAIL] {font} (not found)")

        test_result = {
            "name": "Font Files",
            "passed": len(errors) == 0,
            "missing": errors
        }
        self.results["tests"].append(test_result)

        if len(errors) == 0:
            self.results["passed"] += 1
            print("\n  Result: PASSED")
        else:
            self.results["failed"] += 1
            print(f"\n  Result: FAILED ({len(errors)} fonts missing)")

        return len(errors) == 0

    def test_game_launch(self):
        """Test that game launches without immediate crash"""
        print("\n" + "="*60)
        print("  TEST 6: GAME LAUNCH TEST")
        print("="*60)

        self.clear_log()

        print("  Starting game...")
        try:
            # Launch game
            process = subprocess.Popen(
                [IKEMEN_EXE],
                cwd=GAME_PATH,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait for potential crash
            time.sleep(5)

            crashed, log = self.check_crash()

            if crashed:
                print(f"  [FAIL] Game crashed!")
                print(f"  Error: {log[:500] if log else 'Unknown'}")
                self.results["failed"] += 1
                self.results["tests"].append({
                    "name": "Game Launch",
                    "passed": False,
                    "error": log
                })
                return False
            else:
                print("  [OK] Game running without crash")
                self.results["passed"] += 1
                self.results["tests"].append({
                    "name": "Game Launch",
                    "passed": True
                })

                # Keep game running for more tests
                print("  Waiting 5 more seconds for stability check...")
                time.sleep(5)

                crashed, log = self.check_crash()
                if crashed:
                    print(f"  [WARN] Late crash detected: {log[:200] if log else 'Unknown'}")
                    self.results["warnings"].append("Late crash after 5 seconds")
                else:
                    print("  [OK] Game still stable after 10 seconds")

                return True

        except Exception as e:
            print(f"  [FAIL] Could not launch game: {e}")
            self.results["failed"] += 1
            return False

    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*60)
        print("  FINAL REPORT")
        print("="*60)

        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0

        print(f"\n  Tests Passed: {self.results['passed']}/{total} ({pass_rate:.1f}%)")
        print(f"  Tests Failed: {self.results['failed']}/{total}")

        if self.results["warnings"]:
            print(f"\n  Warnings: {len(self.results['warnings'])}")
            for warn in self.results["warnings"]:
                print(f"    - {warn}")

        # Save results
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n  Results saved to: {RESULTS_FILE}")

        # Overall status
        if self.results["failed"] == 0:
            print("\n  " + "="*40)
            print("  STATUS: ALL TESTS PASSED!")
            print("  " + "="*40)
            return True
        else:
            print("\n  " + "="*40)
            print("  STATUS: SOME TESTS FAILED")
            print("  " + "="*40)
            return False

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("  KOF ULTIMATE ONLINE - AUTOMATED TEST SYSTEM")
        print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("="*60)

        # Run tests
        self.test_lua_syntax()
        self.test_json_files()
        self.test_screen_modules()
        self.test_main_handlers()
        self.test_font_files()
        self.test_game_launch()

        # Generate report
        return self.generate_report()


if __name__ == "__main__":
    tester = GameTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
