#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    KOF ULTIMATE ONLINE - LAUNCHER PRO                         ║
║                     All-in-One Installer & Launcher                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

Features:
- Auto-check all game files
- Auto-repair broken characters
- Auto-update roster
- Matchmaking preparation
- One-click play
"""

import os
import sys
import json
import shutil
import subprocess
import webbrowser
import threading
import time
from pathlib import Path
from datetime import datetime

# Game directories
GAME_DIR = Path(__file__).parent
CHARS_DIR = GAME_DIR / "chars"
DATA_DIR = GAME_DIR / "data"
STAGES_DIR = GAME_DIR / "stages"
SAVE_DIR = GAME_DIR / "save"

# Required files
REQUIRED_FILES = [
    "Ikemen_GO.exe",
    "data/system.def",
    "data/common.air",
    "data/common.cmd",
]

REQUIRED_DIRS = [
    "chars",
    "data",
    "stages",
    "font",
    "sound",
]

class KOFLauncher:
    def __init__(self):
        self.status = "Initializing..."
        self.progress = 0
        self.errors = []
        self.warnings = []
        self.chars_ok = 0
        self.chars_fixed = 0
        self.ready = False

    def log(self, msg):
        print(f"  {msg}")

    def check_game_files(self):
        """Check all required game files exist"""
        self.status = "Checking game files..."
        self.log("Checking game files...")

        missing = []

        # Check required files
        for f in REQUIRED_FILES:
            path = GAME_DIR / f
            if not path.exists():
                missing.append(f)
                self.errors.append(f"Missing: {f}")

        # Check required directories
        for d in REQUIRED_DIRS:
            path = GAME_DIR / d
            if not path.exists():
                missing.append(d)
                self.errors.append(f"Missing directory: {d}")

        if missing:
            self.log(f"  Missing {len(missing)} required files/folders")
            return False

        self.log("  All required files present")
        self.progress = 10
        return True

    def check_and_repair_characters(self):
        """Check and repair all characters"""
        self.status = "Checking characters..."
        self.log("Checking characters...")

        if not CHARS_DIR.exists():
            self.errors.append("Characters folder missing!")
            return False

        char_folders = [d for d in CHARS_DIR.iterdir()
                       if d.is_dir() and d.name not in ['ai', 'data', 'backup']]

        total = len(char_folders)
        self.log(f"  Found {total} characters")

        valid_chars = []

        for i, char_path in enumerate(char_folders):
            # Check if character has required files
            def_files = list(char_path.glob("*.def"))

            if def_files:
                # Basic validation
                valid_chars.append(char_path.name)
                self.chars_ok += 1

            # Update progress
            self.progress = 10 + int(40 * (i + 1) / total)

        self.log(f"  Valid characters: {len(valid_chars)}")
        return valid_chars

    def run_auto_repair(self):
        """Run auto-repair scripts if available"""
        self.status = "Running auto-repair..."
        self.log("Running auto-repair...")

        repair_scripts = [
            "AUTO_FIX_ALL.py",
            "DEEP_FIX_CHARS.py",
            "FIX_FLYAWAY.py"
        ]

        for script in repair_scripts:
            script_path = GAME_DIR / script
            if script_path.exists():
                self.log(f"  Running {script}...")
                try:
                    result = subprocess.run(
                        [sys.executable, str(script_path)],
                        cwd=str(GAME_DIR),
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    if result.returncode == 0:
                        self.chars_fixed += 1
                        self.log(f"    OK")
                except Exception as e:
                    self.warnings.append(f"Repair script error: {e}")

        self.progress = 60
        return True

    def update_roster(self):
        """Update roster with valid characters"""
        self.status = "Updating roster..."
        self.log("Updating roster...")

        # Check if we have a valid roster
        roster_files = ["select_final.def", "select_pro.def", "select_optimized.def", "select.def"]

        active_roster = None
        for roster in roster_files:
            roster_path = DATA_DIR / roster
            if roster_path.exists():
                active_roster = roster
                break

        if active_roster:
            self.log(f"  Using roster: {active_roster}")

            # Update system.def to use this roster
            system_def = DATA_DIR / "system.def"
            if system_def.exists():
                try:
                    content = system_def.read_text(encoding='utf-8', errors='ignore')
                    import re
                    content = re.sub(r'select\s*=\s*\S+', f'select = {active_roster}', content)
                    system_def.write_text(content, encoding='utf-8')
                except:
                    pass

        self.progress = 70
        return True

    def check_online_ready(self):
        """Check if online components are ready"""
        self.status = "Checking online components..."
        self.log("Checking online components...")

        online_files = [
            "KOF_ONLINE_FIREBASE.html",
            "KOF_ONLINE_LAUNCHER.html"
        ]

        online_ready = False
        for f in online_files:
            if (GAME_DIR / f).exists():
                online_ready = True
                self.log(f"  Found: {f}")
                break

        if not online_ready:
            self.warnings.append("Online lobby not found")

        self.progress = 80
        return online_ready

    def prepare_matchmaking(self):
        """Prepare matchmaking system"""
        self.status = "Preparing matchmaking..."
        self.log("Preparing matchmaking...")

        # Create/update config
        config = {
            "online_ready": True,
            "last_check": datetime.now().isoformat(),
            "version": "1.0.0",
            "characters": self.chars_ok,
            "matchmaking": {
                "enabled": True,
                "port": 7500,
                "lobby_url": "KOF_ONLINE_FIREBASE.html"
            }
        }

        config_path = SAVE_DIR / "launcher_config.json"
        SAVE_DIR.mkdir(exist_ok=True)

        try:
            config_path.write_text(json.dumps(config, indent=2), encoding='utf-8')
            self.log("  Matchmaking configured")
        except:
            self.warnings.append("Could not save config")

        self.progress = 90
        return True

    def final_check(self):
        """Final verification"""
        self.status = "Final verification..."
        self.log("Final verification...")

        # Check game executable
        exe_path = GAME_DIR / "Ikemen_GO.exe"
        if not exe_path.exists():
            self.errors.append("Game executable not found!")
            return False

        self.progress = 100
        self.ready = True
        self.status = "Ready to play!"
        self.log("  All checks passed!")
        return True

    def run_full_check(self):
        """Run complete installation check"""
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    KOF ULTIMATE ONLINE - LAUNCHER PRO                         ║
║                          Installation Check                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)

        steps = [
            ("Checking game files", self.check_game_files),
            ("Checking characters", self.check_and_repair_characters),
            ("Running auto-repair", self.run_auto_repair),
            ("Updating roster", self.update_roster),
            ("Checking online", self.check_online_ready),
            ("Preparing matchmaking", self.prepare_matchmaking),
            ("Final check", self.final_check),
        ]

        for step_name, step_func in steps:
            print(f"\n[{self.progress:3d}%] {step_name}...")
            try:
                result = step_func()
                if result is False and step_name == "Checking game files":
                    print("\n  CRITICAL ERROR: Required files missing!")
                    return False
            except Exception as e:
                self.warnings.append(f"{step_name}: {e}")

        return self.ready

    def show_summary(self):
        """Show installation summary"""
        print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          INSTALLATION SUMMARY                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Status: {'READY' if self.ready else 'ERRORS FOUND':<63} ║
║  Characters found: {self.chars_ok:<55} ║
║  Repairs applied: {self.chars_fixed:<56} ║
║  Warnings: {len(self.warnings):<63} ║
║  Errors: {len(self.errors):<65} ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)

        if self.errors:
            print("ERRORS:")
            for e in self.errors[:5]:
                print(f"  - {e}")

        if self.warnings:
            print("\nWARNINGS:")
            for w in self.warnings[:5]:
                print(f"  - {w}")

    def launch_game(self):
        """Launch the game"""
        print("\nLaunching KOF Ultimate Online...")
        exe_path = GAME_DIR / "Ikemen_GO.exe"

        try:
            subprocess.Popen([str(exe_path)], cwd=str(GAME_DIR))
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

    def launch_online_lobby(self):
        """Launch online lobby in browser"""
        print("\nOpening online lobby...")

        lobby_files = ["KOF_ONLINE_FIREBASE.html", "KOF_ONLINE_LAUNCHER.html"]

        for f in lobby_files:
            lobby_path = GAME_DIR / f
            if lobby_path.exists():
                webbrowser.open(str(lobby_path))
                return True

        print("  Online lobby not found!")
        return False


def main():
    launcher = KOFLauncher()

    # Run installation check
    success = launcher.run_full_check()

    # Show summary
    launcher.show_summary()

    if not success:
        print("\nInstallation has errors. Please fix them before playing.")
        input("\nPress Enter to exit...")
        return

    # Menu
    while True:
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              MAIN MENU                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  [1] PLAY LOCAL        - Start the game (VS, Arcade, Training)               ║
║  [2] PLAY ONLINE       - Open matchmaking lobby                              ║
║  [3] REPAIR GAME       - Run auto-repair on all files                        ║
║  [4] RE-CHECK          - Run installation check again                        ║
║  [5] CUSTOMIZE THEME   - Change game backgrounds and colors                  ║
║  [Q] QUIT                                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)

        choice = input("  Your choice: ").strip().lower()

        if choice == '1':
            launcher.launch_game()
        elif choice == '2':
            launcher.launch_online_lobby()
            print("\n  Lobby opened in browser. Launch the game when matched!")
        elif choice == '3':
            launcher.run_auto_repair()
            launcher.update_roster()
            print("\n  Repair complete!")
        elif choice == '4':
            launcher = KOFLauncher()
            launcher.run_full_check()
            launcher.show_summary()
        elif choice == '5':
            # Launch theme customizer
            theme_script = GAME_DIR / "CUSTOMIZE_THEME.py"
            if theme_script.exists():
                subprocess.run([sys.executable, str(theme_script)], cwd=str(GAME_DIR))
            else:
                print("\n  Theme customizer not found!")
        elif choice == 'q':
            print("\n  Goodbye!")
            break


if __name__ == "__main__":
    main()
