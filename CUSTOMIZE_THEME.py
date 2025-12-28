#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE ONLINE - THEME CUSTOMIZER
Allows changing game backgrounds and visual themes
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

GAME_DIR = Path(__file__).parent
DATA_DIR = GAME_DIR / "data"
THEMES_DIR = GAME_DIR / "themes"
SAVE_DIR = GAME_DIR / "save"

# Available color themes for the menu
COLOR_THEMES = {
    "dark": {
        "name": "Dark Mode (Default)",
        "bgclearcolor": "0,0,0",
        "description": "Classic dark KOF theme"
    },
    "blue": {
        "name": "Ocean Blue",
        "bgclearcolor": "10,20,60",
        "description": "Deep blue oceanic theme"
    },
    "red": {
        "name": "Crimson Fire",
        "bgclearcolor": "40,5,5",
        "description": "Intense red fire theme"
    },
    "green": {
        "name": "Toxic Green",
        "bgclearcolor": "5,30,10",
        "description": "Mysterious green theme"
    },
    "purple": {
        "name": "Royal Purple",
        "bgclearcolor": "25,10,40",
        "description": "Elegant purple theme"
    },
    "gold": {
        "name": "Golden Glory",
        "bgclearcolor": "45,35,10",
        "description": "Champion's gold theme"
    }
}

class ThemeCustomizer:
    def __init__(self):
        self.current_theme = self.load_current_theme()

    def load_current_theme(self):
        """Load current theme from config"""
        config_path = SAVE_DIR / "theme_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"color": "dark"}

    def save_theme_config(self, theme_id):
        """Save theme configuration"""
        SAVE_DIR.mkdir(exist_ok=True)
        config = {"color": theme_id, "timestamp": datetime.now().isoformat()}
        config_path = SAVE_DIR / "theme_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def apply_color_theme(self, theme_id):
        """Apply color theme to system.def"""
        if theme_id not in COLOR_THEMES:
            print(f"  Unknown theme: {theme_id}")
            return False

        theme = COLOR_THEMES[theme_id]
        system_def = DATA_DIR / "system.def"

        if not system_def.exists():
            print("  Error: system.def not found!")
            return False

        # Backup
        backup_path = DATA_DIR / "system.def.theme_backup"
        if not backup_path.exists():
            shutil.copy(system_def, backup_path)

        # Read and modify
        try:
            content = system_def.read_text(encoding='utf-8', errors='ignore')

            # Update background color for TitleBGdef
            import re
            content = re.sub(
                r'(\[TitleBGdef\]\s*\n)bgclearcolor\s*=\s*[\d,\s]+\n',
                f'\\1bgclearcolor = {theme["bgclearcolor"]}\n',
                content
            )

            # Update SelectBGdef too
            content = re.sub(
                r'(\[SelectBGdef\]\s*\n)bgclearcolor\s*=\s*[\d,\s]+\n',
                f'\\1bgclearcolor = {theme["bgclearcolor"]}\n',
                content
            )

            # Update VictoryBGdef
            content = re.sub(
                r'(\[VictoryBGdef\]\s*\n)bgclearcolor\s*=\s*[\d,\s]+\n',
                f'\\1bgclearcolor = {theme["bgclearcolor"]}\n',
                content
            )

            system_def.write_text(content, encoding='utf-8')
            self.save_theme_config(theme_id)

            print(f"  Applied theme: {theme['name']}")
            return True

        except Exception as e:
            print(f"  Error applying theme: {e}")
            return False

    def show_menu(self):
        """Show theme selection menu"""
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    KOF ULTIMATE ONLINE - THEME CUSTOMIZER                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                         Select Your Theme                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)

        current = self.current_theme.get("color", "dark")

        print("  Available Themes:\n")
        themes_list = list(COLOR_THEMES.keys())

        for i, theme_id in enumerate(themes_list, 1):
            theme = COLOR_THEMES[theme_id]
            marker = " [CURRENT]" if theme_id == current else ""
            print(f"  [{i}] {theme['name']}{marker}")
            print(f"      {theme['description']}\n")

        print(f"  [R] Restore default theme")
        print(f"  [Q] Quit\n")

        return themes_list

    def run(self):
        """Run the theme customizer"""
        while True:
            themes_list = self.show_menu()

            choice = input("  Your choice: ").strip().lower()

            if choice == 'q':
                print("\n  Goodbye!")
                break
            elif choice == 'r':
                self.apply_color_theme("dark")
                print("\n  Default theme restored!")
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(themes_list):
                        theme_id = themes_list[idx]
                        self.apply_color_theme(theme_id)
                        print(f"\n  Theme applied! Restart the game to see changes.")
                    else:
                        print("\n  Invalid choice!")
                except ValueError:
                    print("\n  Invalid input!")

            input("\n  Press Enter to continue...")


def main():
    customizer = ThemeCustomizer()
    customizer.run()


if __name__ == "__main__":
    main()
