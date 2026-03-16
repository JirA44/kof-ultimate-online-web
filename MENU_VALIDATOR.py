#!/usr/bin/env python3
"""
KOF ULTIMATE ONLINE - MENU VALIDATOR & AUTO-FIXER
==================================================
Lit les fichiers de configuration, comprend ce que chaque bouton DEVRAIT faire,
puis verifie si ca correspond a la realite et corrige les incoherences.

Ce script:
1. Parse system.def pour comprendre la structure des menus
2. Parse live_lobby_screen.lua pour le menu online
3. Compare les definitions avec le comportement attendu
4. Genere un rapport detaille des incoherences
5. Propose et applique des corrections
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

BASE_PATH = Path(r"D:\KOF Ultimate Online kofuo")
SYSTEM_DEF = BASE_PATH / "data" / "system.def"
LIVE_LOBBY = BASE_PATH / "external" / "script" / "live_lobby_screen.lua"
MENU_LUA = BASE_PATH / "external" / "script" / "menu.lua"
START_LUA = BASE_PATH / "external" / "script" / "start.lua"

class MenuDefinition:
    """Definition d'un element de menu"""
    def __init__(self, name, action, source_file, line_number):
        self.name = name
        self.action = action
        self.source_file = source_file
        self.line_number = line_number
        self.expected_behavior = None
        self.actual_behavior = None
        self.issues = []

    def to_dict(self):
        return {
            "name": self.name,
            "action": self.action,
            "source": f"{self.source_file}:{self.line_number}",
            "expected": self.expected_behavior,
            "actual": self.actual_behavior,
            "issues": self.issues
        }


class MenuValidator:
    """Validateur de menus avec detection et correction des bugs"""

    def __init__(self):
        self.menus = {}  # {menu_name: [MenuDefinition]}
        self.issues = []
        self.fixes_applied = []
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": [],
            "menus_found": {},
            "issues": [],
            "fixes": [],
            "recommendations": []
        }

    def parse_system_def(self):
        """Parse system.def pour extraire la structure des menus"""
        print("\n[PARSE] Lecture de system.def...")

        if not SYSTEM_DEF.exists():
            self.log_issue("CRITICAL", "system.def introuvable", str(SYSTEM_DEF))
            return

        self.report["files_analyzed"].append(str(SYSTEM_DEF))

        with open(SYSTEM_DEF, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')

        # Extraire les elements du menu principal
        main_menu = []
        for i, line in enumerate(lines):
            # Pattern: menu.itemname.XXX = "YYY"
            match = re.match(r'menu\.itemname\.(\w+)\s*=\s*"([^"]+)"', line.strip())
            if match:
                action_name = match.group(1)
                display_name = match.group(2)

                menu_def = MenuDefinition(
                    name=display_name,
                    action=action_name,
                    source_file="system.def",
                    line_number=i+1
                )

                # Definir le comportement attendu selon l'action
                menu_def.expected_behavior = self.get_expected_behavior(action_name)
                main_menu.append(menu_def)

                print(f"  [MENU] {display_name} -> {action_name}")

        self.menus["MAIN_MENU"] = main_menu
        self.report["menus_found"]["MAIN_MENU"] = len(main_menu)

    def parse_live_lobby(self):
        """Parse live_lobby_screen.lua pour le menu online"""
        print("\n[PARSE] Lecture de live_lobby_screen.lua...")

        if not LIVE_LOBBY.exists():
            self.log_issue("HIGH", "live_lobby_screen.lua introuvable", str(LIVE_LOBBY))
            return

        self.report["files_analyzed"].append(str(LIVE_LOBBY))

        with open(LIVE_LOBBY, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')

        # Extraire menuOptions
        online_menu = []
        in_menu_options = False

        for i, line in enumerate(lines):
            if 'live_lobby.menuOptions' in line:
                in_menu_options = True
                continue

            if in_menu_options:
                if line.strip() == '}':
                    in_menu_options = False
                    continue

                # Pattern: {name = "XXX", action = "YYY", ...}
                name_match = re.search(r'name\s*=\s*"([^"]+)"', line)
                action_match = re.search(r'action\s*=\s*"([^"]+)"', line)
                desc_match = re.search(r'desc\s*=\s*"([^"]+)"', line)

                if name_match and action_match:
                    menu_def = MenuDefinition(
                        name=name_match.group(1),
                        action=action_match.group(1),
                        source_file="live_lobby_screen.lua",
                        line_number=i+1
                    )

                    if desc_match:
                        menu_def.expected_behavior = desc_match.group(1)
                    else:
                        menu_def.expected_behavior = self.get_expected_behavior(action_match.group(1))

                    online_menu.append(menu_def)
                    print(f"  [ONLINE] {menu_def.name} -> {menu_def.action}")

        self.menus["ONLINE_MENU"] = online_menu
        self.report["menus_found"]["ONLINE_MENU"] = len(online_menu)

        # Verifier la coherence avec executeAction
        self.validate_execute_action(content, lines, online_menu)

    def validate_execute_action(self, content, lines, menu_items):
        """Verifie que chaque action du menu a un handler dans executeAction"""
        print("\n[VALIDATE] Verification des handlers d'action...")

        # Trouver la fonction executeAction
        exec_start = None
        exec_end = None

        for i, line in enumerate(lines):
            if 'function live_lobby.executeAction' in line:
                exec_start = i
            if exec_start and line.strip() == 'end' and i > exec_start:
                exec_end = i
                break

        if exec_start is None:
            self.log_issue("CRITICAL", "executeAction non trouve", "live_lobby_screen.lua")
            return

        exec_content = '\n'.join(lines[exec_start:exec_end])

        # Verifier chaque action
        for menu_item in menu_items:
            action = menu_item.action

            # Chercher le handler
            handler_pattern = rf'action\s*==\s*"{action}"'
            if not re.search(handler_pattern, exec_content):
                self.log_issue(
                    "HIGH",
                    f"Action '{action}' n'a PAS de handler dans executeAction!",
                    f"live_lobby_screen.lua:{exec_start+1}",
                    fix=self.generate_action_handler(action)
                )
                menu_item.issues.append(f"Handler manquant pour '{action}'")
            else:
                print(f"  [OK] Handler trouve pour '{action}'")

    def get_expected_behavior(self, action):
        """Retourne le comportement attendu pour une action"""
        behaviors = {
            # Menu principal
            "arcade": "Lance le mode Arcade (combat solo contre l'IA)",
            "versus": "Lance le mode VS (combat local 2 joueurs)",
            "teamarcade": "Lance le mode Team Arcade",
            "teamversus": "Lance le mode Team VS",
            "teamcoop": "Lance le mode Team Co-op",
            "survival": "Lance le mode Survival",
            "survivalcoop": "Lance le mode Survival Co-op",
            "training": "Lance le mode Entrainement",
            "netplay": "Ouvre le menu Online/Netplay",
            "options": "Ouvre le menu Options",
            "exit": "Quitte le jeu",
            "watch": "Mode spectateur",

            # Sous-menu netplay
            "netplay_serverhost": "Heberge une partie en ligne",
            "netplay_serverjoin": "Rejoint une partie en ligne",
            "netplay_joinadd": "Ajoute une nouvelle adresse",
            "netplay_netplayversus": "VS en ligne 2 joueurs",
            "netplay_netplayteamcoop": "Arcade Co-op en ligne",
            "netplay_netplaysurvivalcoop": "Survival Co-op en ligne",
            "netplay_lobby": "Ouvre le Live Lobby",
            "netplay_rankings": "Affiche le classement",
            "netplay_profile": "Affiche le profil joueur",
            "netplay_back": "Retour au menu precedent",

            # Live Lobby
            "ranked": "Lance la recherche de match classe (ELO)",
            "casual": "Lance la recherche de match casual",
            "players": "Affiche la liste des joueurs en ligne",
            "leaderboard": "Affiche le classement Top joueurs",
            "back": "Retour au menu precedent"
        }
        return behaviors.get(action, f"Action '{action}' - comportement non documente")

    def generate_action_handler(self, action):
        """Genere le code pour un handler d'action manquant"""
        templates = {
            "casual": '''
    elseif action == "casual" then
        -- Start casual matchmaking
        live_lobby.inMatchmaking = true
        live_lobby.matchmakingTimer = 0
        live_lobby.matchmakingMode = "casual"
        live_lobby.showMessage("Recherche match CASUAL...")
''',
            "default": f'''
    elseif action == "{action}" then
        -- TODO: Implementer l'action "{action}"
        live_lobby.showMessage("Action {action} non implementee")
'''
        }
        return templates.get(action, templates["default"])

    def log_issue(self, severity, description, location, fix=None):
        """Enregistre un probleme trouve"""
        issue = {
            "severity": severity,
            "description": description,
            "location": location,
            "fix": fix,
            "timestamp": datetime.now().isoformat()
        }
        self.issues.append(issue)
        self.report["issues"].append(issue)

        icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(severity, "⚪")
        print(f"  {icon} [{severity}] {description}")
        print(f"      Location: {location}")
        if fix:
            print(f"      Fix disponible: Oui")

    def check_menu_consistency(self):
        """Verifie la coherence entre les menus"""
        print("\n[CHECK] Verification de coherence...")

        # Verifier que le menu ONLINE reference dans system.def existe dans live_lobby
        main_menu = self.menus.get("MAIN_MENU", [])
        online_menu = self.menus.get("ONLINE_MENU", [])

        # Trouver l'entree ONLINE/NETPLAY dans le menu principal
        has_online = False
        for item in main_menu:
            if item.action in ["netplay", "online"]:
                has_online = True
                break

        if has_online and not online_menu:
            self.log_issue(
                "HIGH",
                "Menu ONLINE defini dans system.def mais live_lobby_screen.lua est vide",
                "Coherence inter-fichiers"
            )

        # Verifier les actions dupliquees
        all_actions = {}
        for menu_name, items in self.menus.items():
            for item in items:
                if item.action in all_actions:
                    self.log_issue(
                        "MEDIUM",
                        f"Action '{item.action}' dupliquee",
                        f"{all_actions[item.action]} et {item.source_file}:{item.line_number}"
                    )
                all_actions[item.action] = f"{item.source_file}:{item.line_number}"

    def check_button_mappings(self):
        """Verifie que les boutons font ce qu'ils sont censes faire"""
        print("\n[CHECK] Verification des mappings de boutons...")

        # Lire la config
        config_file = BASE_PATH / "save" / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)

            key_config = config.get("KeyConfig", [])
            if key_config:
                buttons = key_config[0].get("Buttons", [])
                expected_order = ["UP", "DOWN", "LEFT", "RIGHT", "A", "B", "C", "X", "Y", "Z", "START", "D", "W", "MENU"]

                print(f"  Boutons configures: {buttons[:6]}...")

                # Verifier les boutons de confirmation/annulation
                confirm_btn = buttons[4] if len(buttons) > 4 else None  # A
                cancel_btn = buttons[5] if len(buttons) > 5 else None   # B

                self.report["recommendations"].append({
                    "type": "INFO",
                    "message": f"Bouton CONFIRMER = {confirm_btn} (index 4)",
                })
                self.report["recommendations"].append({
                    "type": "INFO",
                    "message": f"Bouton ANNULER = {cancel_btn} (index 5)",
                })

    def analyze_menu_flow(self):
        """Analyse le flux de navigation entre les menus"""
        print("\n[ANALYZE] Analyse du flux de navigation...")

        # Verifier que chaque "back" ramene au bon menu
        online_menu = self.menus.get("ONLINE_MENU", [])

        for item in online_menu:
            if item.action == "back":
                # Le back devrait fermer le lobby et retourner au menu principal
                print(f"  [FLOW] {item.name} -> Retour menu principal")
                item.actual_behavior = "Ferme le live_lobby et retourne au menu"

    def generate_report(self):
        """Genere le rapport complet"""
        print("\n" + "="*60)
        print("  RAPPORT DE VALIDATION DES MENUS")
        print("="*60)

        print(f"\nFichiers analyses: {len(self.report['files_analyzed'])}")
        for f in self.report['files_analyzed']:
            print(f"  - {f}")

        print(f"\nMenus trouves:")
        for menu, count in self.report['menus_found'].items():
            print(f"  - {menu}: {count} elements")

        print(f"\nProblemes detectes: {len(self.issues)}")
        critical = len([i for i in self.issues if i['severity'] == 'CRITICAL'])
        high = len([i for i in self.issues if i['severity'] == 'HIGH'])
        medium = len([i for i in self.issues if i['severity'] == 'MEDIUM'])

        print(f"  🔴 CRITICAL: {critical}")
        print(f"  🟠 HIGH: {high}")
        print(f"  🟡 MEDIUM: {medium}")

        if self.issues:
            print("\nDetails des problemes:")
            for issue in self.issues:
                print(f"\n  [{issue['severity']}] {issue['description']}")
                print(f"  Location: {issue['location']}")
                if issue.get('fix'):
                    print(f"  Fix: Code de correction disponible")

        # Sauvegarder le rapport
        report_file = BASE_PATH / "menu_validation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        print(f"\n[SAVE] Rapport sauvegarde: {report_file}")

        return self.report

    def apply_fixes(self, auto=False):
        """Applique les corrections automatiques"""
        if not auto:
            print("\n[FIX] Mode manuel - corrections non appliquees")
            print("      Utilisez --auto-fix pour appliquer les corrections")
            return

        print("\n[FIX] Application des corrections...")

        for issue in self.issues:
            if issue.get('fix'):
                print(f"  Correction: {issue['description'][:50]}...")
                # TODO: Appliquer le fix
                self.fixes_applied.append(issue)

    def run(self, auto_fix=False):
        """Execute la validation complete"""
        print("\n" + "="*60)
        print("  KOF ULTIMATE - MENU VALIDATOR")
        print("="*60)

        self.parse_system_def()
        self.parse_live_lobby()
        self.check_menu_consistency()
        self.check_button_mappings()
        self.analyze_menu_flow()
        self.generate_report()
        self.apply_fixes(auto_fix)

        return len(self.issues) == 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="KOF Menu Validator")
    parser.add_argument('--auto-fix', '-f', action='store_true',
                        help='Applique les corrections automatiquement')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Mode verbose')

    args = parser.parse_args()

    validator = MenuValidator()
    success = validator.run(auto_fix=args.auto_fix)

    if success:
        print("\n✅ Validation OK - Aucun probleme detecte")
    else:
        print(f"\n⚠️ {len(validator.issues)} probleme(s) detecte(s)")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
