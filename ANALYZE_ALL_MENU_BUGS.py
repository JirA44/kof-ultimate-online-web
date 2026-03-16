#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE ONLINE - Analyse Complete des Bugs de Menu
Analyse tous les handlers et trouve les problemes
"""

import re
import json
from pathlib import Path
from datetime import datetime

GAME_PATH = Path(__file__).parent
SCRIPT_PATH = GAME_PATH / "external" / "script"
MODS_PATH = GAME_PATH / "external" / "mods"
DATA_PATH = GAME_PATH / "data"
REPORT_PATH = GAME_PATH / "menu_test_reports"
REPORT_PATH.mkdir(exist_ok=True)

class MenuBugAnalyzer:
    def __init__(self):
        self.menu_items = {}  # Items definis dans system.def
        self.handlers = {}     # Handlers definis dans les .lua
        self.bugs = []
        self.warnings = []

    def parse_system_def(self):
        """Parse system.def pour trouver tous les items de menu"""
        system_def = DATA_PATH / "system.def"
        if not system_def.exists():
            self.bugs.append({"type": "CRITICAL", "msg": "system.def not found"})
            return

        with open(system_def, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Trouver tous les menu.itemname.xxx = "YYY"
        pattern = r'menu\.itemname\.(\w+)\s*=\s*"([^"]+)"'
        matches = re.findall(pattern, content)

        for item_name, display_name in matches:
            self.menu_items[item_name] = {
                "display": display_name,
                "handler_needed": self.get_handler_name(item_name),
                "found_handler": False
            }

        print(f"Found {len(self.menu_items)} menu items in system.def")

    def get_handler_name(self, item_name):
        """Determine le nom du handler necessaire"""
        # Les items avec prefixe (netplay_xxx) ont besoin du handler sans prefixe
        prefixes = ["netplay_", "options_", "select_"]
        for prefix in prefixes:
            if item_name.startswith(prefix):
                return item_name[len(prefix):]
        return item_name

    def parse_lua_handlers(self):
        """Parse tous les fichiers Lua pour trouver les handlers"""
        lua_files = list(SCRIPT_PATH.glob("*.lua")) + list(MODS_PATH.glob("*.lua"))

        for lua_file in lua_files:
            try:
                with open(lua_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Pattern pour main.t_itemname['xxx'] = function
                pattern1 = r"main\.t_itemname\['(\w+)'\]\s*=\s*function"
                # Pattern pour main.t_itemname.xxx = function
                pattern2 = r"main\.t_itemname\.(\w+)\s*=\s*function"
                # Pattern pour main.t_itemname['xxx'] = main.t_itemname['yyy']
                pattern3 = r"main\.t_itemname\['(\w+)'\]\s*=\s*main\.t_itemname\['(\w+)'\]"

                for match in re.finditer(pattern1, content):
                    handler_name = match.group(1)
                    self.handlers[handler_name] = {
                        "file": str(lua_file.relative_to(GAME_PATH)),
                        "type": "function"
                    }

                for match in re.finditer(pattern2, content):
                    handler_name = match.group(1)
                    if handler_name not in self.handlers:
                        self.handlers[handler_name] = {
                            "file": str(lua_file.relative_to(GAME_PATH)),
                            "type": "function"
                        }

                for match in re.finditer(pattern3, content):
                    handler_name = match.group(1)
                    alias_to = match.group(2)
                    self.handlers[handler_name] = {
                        "file": str(lua_file.relative_to(GAME_PATH)),
                        "type": "alias",
                        "alias_to": alias_to
                    }

            except Exception as e:
                self.warnings.append(f"Could not parse {lua_file}: {e}")

        print(f"Found {len(self.handlers)} handlers in Lua files")

    def check_handler_issues(self):
        """Verifie les problemes avec les handlers"""

        # 1. Items de menu sans handler
        for item_name, item_data in self.menu_items.items():
            handler_name = item_data["handler_needed"]

            if handler_name in self.handlers:
                item_data["found_handler"] = True
                item_data["handler_info"] = self.handlers[handler_name]
            elif item_name in self.handlers:
                # Peut-etre que le handler utilise le nom complet
                item_data["found_handler"] = True
                item_data["handler_info"] = self.handlers[item_name]
            else:
                # Special cases - built-in handlers
                builtin = ["back", "joinadd", "serverconnect"]
                if handler_name not in builtin and item_name not in builtin:
                    self.bugs.append({
                        "type": "MISSING_HANDLER",
                        "item": item_name,
                        "display": item_data["display"],
                        "expected_handler": handler_name,
                        "msg": f"Menu item '{item_data['display']}' ({item_name}) has no handler '{handler_name}'"
                    })

        # 2. Handlers qui sont des alias vers des handlers manquants
        for handler_name, handler_data in self.handlers.items():
            if handler_data["type"] == "alias":
                alias_to = handler_data["alias_to"]
                if alias_to not in self.handlers:
                    self.bugs.append({
                        "type": "BROKEN_ALIAS",
                        "handler": handler_name,
                        "alias_to": alias_to,
                        "file": handler_data["file"],
                        "msg": f"Handler '{handler_name}' is alias to non-existent '{alias_to}'"
                    })

    def check_empty_handlers(self):
        """Verifie les handlers vides"""
        lua_files = list(SCRIPT_PATH.glob("*.lua")) + list(MODS_PATH.glob("*.lua"))

        for lua_file in lua_files:
            try:
                with open(lua_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Pattern pour fonction vide: ['xxx'] = function() end
                pattern = r"\['(\w+)'\]\s*=\s*function\s*\([^)]*\)\s*\n?\s*end"
                for match in re.finditer(pattern, content):
                    handler_name = match.group(1)
                    self.bugs.append({
                        "type": "EMPTY_HANDLER",
                        "handler": handler_name,
                        "file": str(lua_file.relative_to(GAME_PATH)),
                        "msg": f"Handler '{handler_name}' is empty (does nothing)"
                    })

            except Exception as e:
                pass

    def check_return_values(self):
        """Verifie que les handlers retournent les bonnes valeurs"""
        main_lua = SCRIPT_PATH / "main.lua"

        if not main_lua.exists():
            return

        with open(main_lua, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Les handlers de mode de jeu doivent retourner start.f_selectMode
        game_modes = ["arcade", "versus", "survival", "training", "teamarcade",
                     "teamversus", "teamcoop", "survivalcoop", "trials"]

        for mode in game_modes:
            # Chercher le handler
            pattern = rf"\['{mode}'\]\s*=\s*function.*?(?=\['\w+'\]\s*=\s*function|\Z)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                handler_code = match.group(0)
                if "return start.f_selectMode" not in handler_code and "return nil" not in handler_code:
                    if "return" not in handler_code:
                        self.warnings.append({
                            "type": "NO_RETURN",
                            "handler": mode,
                            "msg": f"Handler '{mode}' may not return a value"
                        })

    def generate_report(self):
        """Genere le rapport"""
        report = {
            "date": datetime.now().isoformat(),
            "menu_items_count": len(self.menu_items),
            "handlers_count": len(self.handlers),
            "bugs": self.bugs,
            "warnings": self.warnings,
            "menu_items": self.menu_items,
            "handlers": self.handlers
        }

        # JSON report
        json_path = REPORT_PATH / "menu_bug_analysis.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Markdown report
        md_path = REPORT_PATH / "MENU_BUG_ANALYSIS.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# KOF Ultimate Online - Analyse des Bugs de Menu\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Resume\n\n")
            f.write(f"- Items de menu: {len(self.menu_items)}\n")
            f.write(f"- Handlers trouves: {len(self.handlers)}\n")
            f.write(f"- **BUGS: {len(self.bugs)}**\n")
            f.write(f"- Warnings: {len(self.warnings)}\n\n")

            if self.bugs:
                f.write("## BUGS CRITIQUES\n\n")
                f.write("| Type | Item/Handler | Message |\n")
                f.write("|------|--------------|----------|\n")
                for bug in self.bugs:
                    item = bug.get("item") or bug.get("handler") or "N/A"
                    f.write(f"| {bug['type']} | {item} | {bug['msg']} |\n")
                f.write("\n")

            if self.warnings:
                f.write("## Warnings\n\n")
                for warn in self.warnings:
                    if isinstance(warn, dict):
                        f.write(f"- [{warn['type']}] {warn['msg']}\n")
                    else:
                        f.write(f"- {warn}\n")
                f.write("\n")

            f.write("## Items de Menu\n\n")
            f.write("| Item | Display | Handler | Status |\n")
            f.write("|------|---------|---------|--------|\n")
            for item_name, data in sorted(self.menu_items.items()):
                status = "OK" if data["found_handler"] else "MISSING"
                handler = data["handler_needed"]
                f.write(f"| {item_name} | {data['display']} | {handler} | {status} |\n")

            f.write("\n---\n*Analyse statique sans lancement du jeu*\n")

        print(f"\nRapport genere: {md_path}")
        return md_path

    def run(self):
        """Execute l'analyse complete"""
        print("="*60)
        print("ANALYSE DES BUGS DE MENU")
        print("="*60)

        self.parse_system_def()
        self.parse_lua_handlers()
        self.check_handler_issues()
        self.check_empty_handlers()
        self.check_return_values()

        print(f"\nBugs trouves: {len(self.bugs)}")
        print(f"Warnings: {len(self.warnings)}")

        return self.generate_report()


if __name__ == "__main__":
    analyzer = MenuBugAnalyzer()
    analyzer.run()
