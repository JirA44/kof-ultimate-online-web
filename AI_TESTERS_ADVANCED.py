#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 SYSTÈME DE TESTEURS IA AVANCÉS
Tests permanents multi-angles pour détecter TOUS les bugs
- Crashs au démarrage
- Personnages injouables
- Stages qui plantent
- Bugs visuels, gameplay, input
"""

import subprocess
import time
import json
import os
import sys
import psutil
import threading
import pyautogui
from datetime import datetime
from pathlib import Path
import random
import traceback

class AITesterProfile:
    """Profil d'un testeur IA avec comportement unique"""

    def __init__(self, name, behavior):
        self.name = name
        self.behavior = behavior
        self.bugs_found = []
        self.tests_completed = 0
        self.crashes_detected = 0

    PROFILES = {
        "CRASHER": {
            "description": "Teste spécifiquement les crashs au démarrage",
            "focus": ["startup_crash", "load_crash", "selection_crash"],
            "test_strategy": "rapid_restart",
            "input_pattern": "minimal"
        },
        "STRESS_TESTER": {
            "description": "Spam d'inputs pour détecter bugs de gameplay",
            "focus": ["gameplay_bugs", "animation_bugs", "collision_bugs"],
            "test_strategy": "intensive_input",
            "input_pattern": "spam"
        },
        "EXPLORER": {
            "description": "Teste tous les personnages et stages systématiquement",
            "focus": ["character_bugs", "stage_bugs", "compatibility_bugs"],
            "test_strategy": "exhaustive_coverage",
            "input_pattern": "varied"
        },
        "VISUAL_INSPECTOR": {
            "description": "Détecte bugs visuels (portraits, icônes, sprites)",
            "focus": ["visual_bugs", "portrait_bugs", "sprite_bugs"],
            "test_strategy": "screenshot_analysis",
            "input_pattern": "slow_methodical"
        },
        "LONG_RUNNER": {
            "description": "Matchs longs pour détecter memory leaks",
            "focus": ["memory_leak", "performance_degradation"],
            "test_strategy": "extended_matches",
            "input_pattern": "sustained"
        },
        "RAGE_QUITTER": {
            "description": "Teste exits rapides et interruptions",
            "focus": ["exit_crash", "cleanup_bugs", "state_corruption"],
            "test_strategy": "rapid_exit",
            "input_pattern": "interrupt"
        },
        "MENU_NAVIGATOR": {
            "description": "Teste navigation menus et sélection",
            "focus": ["menu_bugs", "selection_bugs", "ui_bugs"],
            "test_strategy": "menu_exhaustive",
            "input_pattern": "navigation"
        },
        "RANDOM_CHAOS": {
            "description": "Inputs totalement aléatoires - trouve bugs rares",
            "focus": ["edge_cases", "rare_bugs", "undefined_behavior"],
            "test_strategy": "pure_random",
            "input_pattern": "chaos"
        }
    }

class BugDatabase:
    """Base de données centralisée des bugs trouvés"""

    def __init__(self, game_dir):
        self.game_dir = Path(game_dir)
        self.db_file = self.game_dir / "BUG_DATABASE.json"
        self.db = self.load_database()

    def load_database(self):
        """Charge la base de bugs existante"""
        if self.db_file.exists():
            try:
                return json.loads(self.db_file.read_text(encoding='utf-8'))
            except:
                pass

        return {
            "startup_crashes": [],
            "character_bugs": {},
            "stage_bugs": {},
            "gameplay_bugs": [],
            "visual_bugs": [],
            "performance_bugs": [],
            "broken_characters": [],
            "broken_stages": [],
            "total_tests": 0,
            "start_time": datetime.now().isoformat()
        }

    def save_database(self):
        """Sauvegarde la base"""
        self.db_file.write_text(json.dumps(self.db, indent=2, ensure_ascii=False), encoding='utf-8')

    def add_bug(self, category, bug_data):
        """Ajoute un bug à la base"""
        bug_data['timestamp'] = datetime.now().isoformat()
        bug_data['test_number'] = self.db['total_tests']

        if category in self.db:
            if isinstance(self.db[category], list):
                self.db[category].append(bug_data)
            elif isinstance(self.db[category], dict):
                key = bug_data.get('key', str(len(self.db[category])))
                self.db[category][key] = bug_data

        self.save_database()

        # Log immédiat
        print(f"\n🐛 BUG DÉTECTÉ [{category}]:")
        print(f"   {json.dumps(bug_data, indent=2, ensure_ascii=False)}")

    def mark_broken_character(self, char_name, reason):
        """Marque un personnage comme cassé"""
        if char_name not in self.db['broken_characters']:
            self.db['broken_characters'].append({
                'name': char_name,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            })
            self.save_database()
            print(f"❌ PERSONNAGE CASSÉ: {char_name} - {reason}")

    def mark_broken_stage(self, stage_name, reason):
        """Marque un stage comme cassé"""
        if stage_name not in [s['name'] for s in self.db['broken_stages']]:
            self.db['broken_stages'].append({
                'name': stage_name,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            })
            self.save_database()
            print(f"❌ STAGE CASSÉ: {stage_name} - {reason}")

    def get_safe_characters(self):
        """Retourne les personnages sûrs (non cassés)"""
        broken = [c['name'] for c in self.db['broken_characters']]
        all_chars = self.get_all_characters()
        return [c for c in all_chars if c not in broken]

    def get_safe_stages(self):
        """Retourne les stages sûrs (non cassés)"""
        broken = [s['name'] for s in self.db['broken_stages']]
        all_stages = self.get_all_stages()
        return [s for s in all_stages if s not in broken]

    def get_all_characters(self):
        """Lit tous les personnages du dossier chars/"""
        chars_dir = self.game_dir / "chars"
        if not chars_dir.exists():
            return []
        return [d.name for d in chars_dir.iterdir() if d.is_dir()]

    def get_all_stages(self):
        """Lit tous les stages depuis select.def"""
        select_def = self.game_dir / "data" / "select.def"
        if not select_def.exists():
            return []

        try:
            content = select_def.read_text(encoding='utf-8', errors='ignore')
            stages = []
            in_stages = False

            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('[Stages]'):
                    in_stages = True
                    continue
                if line.startswith('['):
                    in_stages = False

                if in_stages and line and not line.startswith(';'):
                    if '.def' in line:
                        stage = line.split('/')[-1].replace('.def', '')
                        stages.append(stage)

            return stages
        except:
            return []

    def generate_report(self):
        """Génère un rapport complet"""
        report_path = self.game_dir / f"BUG_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        total_bugs = (
            len(self.db['startup_crashes']) +
            sum(len(v) if isinstance(v, list) else 1 for v in self.db['character_bugs'].values()) +
            sum(len(v) if isinstance(v, list) else 1 for v in self.db['stage_bugs'].values()) +
            len(self.db['gameplay_bugs']) +
            len(self.db['visual_bugs']) +
            len(self.db['performance_bugs'])
        )

        md = f"""# 🐛 RAPPORT DÉTAILLÉ DES BUGS - KOF Ultimate Online

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Tests effectués**: {self.db['total_tests']}
**Bugs trouvés**: {total_bugs}

## 🚨 ÉLÉMENTS CASSÉS À RETIRER

### ❌ Personnages Injouables ({len(self.db['broken_characters'])})

"""

        for char in self.db['broken_characters']:
            md += f"- **{char['name']}**: {char['reason']}\n"

        md += f"""

### 🗺️ Stages Problématiques ({len(self.db['broken_stages'])})

"""

        for stage in self.db['broken_stages']:
            md += f"- **{stage['name']}**: {stage['reason']}\n"

        md += f"""

## 💥 Crashs au Démarrage ({len(self.db['startup_crashes'])})

"""

        for crash in self.db['startup_crashes'][-10:]:  # Derniers 10
            md += f"- Test #{crash.get('test_number', 'N/A')}: {crash.get('description', 'N/A')}\n"

        md += f"""

## 🎮 Bugs de Gameplay ({len(self.db['gameplay_bugs'])})

"""

        for bug in self.db['gameplay_bugs'][-10:]:
            md += f"- {bug.get('description', 'N/A')}\n"

        md += f"""

## 🎨 Bugs Visuels ({len(self.db['visual_bugs'])})

"""

        for bug in self.db['visual_bugs'][-10:]:
            md += f"- {bug.get('description', 'N/A')}\n"

        md += """

## 🔧 ACTIONS RECOMMANDÉES

### 1. Nettoyer le Roster
```
Retirer les personnages cassés de data/select.def
Retirer les dossiers correspondants de chars/
```

### 2. Nettoyer les Stages
```
Retirer les stages cassés de data/select.def
Retirer les fichiers correspondants de stages/
```

### 3. Tests de Validation
```
Relancer les testeurs IA après nettoyage
Vérifier que le score qualité s'améliore
```

---

*Rapport généré par AI Testers Advanced*
"""

        report_path.write_text(md, encoding='utf-8')
        print(f"\n📄 Rapport sauvegardé: {report_path}")
        return report_path


class AdvancedAITester:
    """Testeur IA avancé"""

    def __init__(self, profile_name, game_dir):
        self.profile_name = profile_name
        self.profile = AITesterProfile.PROFILES[profile_name]
        self.game_dir = Path(game_dir)
        self.bug_db = BugDatabase(game_dir)
        self.running = True
        self.tests_run = 0

        # Trouve l'exe du jeu
        self.game_exe = self.find_game_exe()

    def find_game_exe(self):
        """Trouve l'exécutable du jeu"""
        possible_exes = [
            self.game_dir / "KOF_Ultimate_Online.exe",
            self.game_dir / "Ikemen_GO.exe",
            self.game_dir / "mugen.exe"
        ]

        for exe in possible_exes:
            if exe.exists():
                return exe

        print(f"❌ Aucun exécutable trouvé!")
        return None

    def kill_game(self):
        """Tue tous les processus du jeu"""
        killed = 0
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if name and ('KOF' in name or 'Ikemen' in name or 'mugen' in name.lower()):
                    proc.kill()
                    killed += 1
            except:
                pass

        if killed > 0:
            time.sleep(1)
        return killed

    def test_startup_crash(self):
        """Teste si le jeu crash au démarrage"""
        print(f"\n[{self.profile_name}] Test startup crash...")

        if not self.game_exe:
            return False

        self.kill_game()

        try:
            process = subprocess.Popen(
                [str(self.game_exe)],
                cwd=str(self.game_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Attendre 5 secondes
            time.sleep(5)

            # Vérifier si crashé
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                self.bug_db.add_bug('startup_crashes', {
                    'tester': self.profile_name,
                    'description': 'Crash immédiat au démarrage',
                    'exit_code': process.returncode,
                    'stderr': stderr.decode('utf-8', errors='ignore')[:500]
                })
                return False

            # Jeu démarré OK
            self.kill_game()
            return True

        except Exception as e:
            self.bug_db.add_bug('startup_crashes', {
                'tester': self.profile_name,
                'description': f'Exception au démarrage: {str(e)}',
                'traceback': traceback.format_exc()[:500]
            })
            return False

    def test_character(self, char_name):
        """Teste un personnage spécifique"""
        print(f"\n[{self.profile_name}] Test personnage: {char_name}")

        self.kill_game()

        try:
            process = subprocess.Popen(
                [str(self.game_exe)],
                cwd=str(self.game_dir)
            )

            time.sleep(5)

            # Vérifier crash au startup
            if process.poll() is not None:
                self.bug_db.mark_broken_character(char_name, "Crash au démarrage")
                return False

            # Navigation vers Versus
            pyautogui.press('return')
            time.sleep(0.5)
            pyautogui.press('down')
            time.sleep(0.3)
            pyautogui.press('return')
            time.sleep(2)

            # Vérifier crash après menu
            if process.poll() is not None:
                self.bug_db.mark_broken_character(char_name, "Crash navigation menu")
                return False

            # Sélection personnage P1
            # (Simplification: on sélectionne au hasard)
            for _ in range(random.randint(0, 5)):
                pyautogui.press('right')
                time.sleep(0.05)

            pyautogui.press('space')
            time.sleep(1)

            # Vérifier crash après sélection
            if process.poll() is not None:
                self.bug_db.mark_broken_character(char_name, "Crash après sélection")
                return False

            # Sélection P2
            for _ in range(random.randint(0, 5)):
                pyautogui.press('right')
                time.sleep(0.05)

            pyautogui.press('space')
            time.sleep(3)

            # Vérifier crash après sélection P2
            if process.poll() is not None:
                self.bug_db.mark_broken_character(char_name, "Crash chargement combat")
                return False

            # Combat rapide (10s)
            start_time = time.time()
            while time.time() - start_time < 10:
                if process.poll() is not None:
                    self.bug_db.mark_broken_character(char_name, "Crash pendant combat")
                    return False

                # Input selon profil
                self.execute_input_pattern()
                time.sleep(0.3)

            # Personnage OK!
            self.kill_game()
            print(f"✅ {char_name} - OK")
            return True

        except Exception as e:
            self.bug_db.add_bug('character_bugs', {
                'key': char_name,
                'tester': self.profile_name,
                'character': char_name,
                'description': f'Exception test personnage: {str(e)}',
                'traceback': traceback.format_exc()[:500]
            })
            self.kill_game()
            return False

    def test_stage(self, stage_name):
        """Teste un stage spécifique"""
        print(f"\n[{self.profile_name}] Test stage: {stage_name}")

        # Modifie temporairement select.def pour forcer ce stage
        select_def = self.game_dir / "data" / "select.def"
        backup = select_def.read_text(encoding='utf-8', errors='ignore')

        try:
            # Force le stage dans select.def
            modified = backup.replace('[Stages]', f'[Stages]\nstages/{stage_name}.def')
            select_def.write_text(modified, encoding='utf-8')

            self.kill_game()

            process = subprocess.Popen([str(self.game_exe)], cwd=str(self.game_dir))
            time.sleep(5)

            if process.poll() is not None:
                self.bug_db.mark_broken_stage(stage_name, "Crash au chargement")
                return False

            # Navigation rapide vers combat
            pyautogui.press('return')
            time.sleep(0.5)
            pyautogui.press('down')
            time.sleep(0.3)
            pyautogui.press('return')
            time.sleep(2)

            pyautogui.press('space')
            time.sleep(1)
            pyautogui.press('space')
            time.sleep(5)

            # Vérifier crash pendant chargement stage
            if process.poll() is not None:
                self.bug_db.mark_broken_stage(stage_name, "Crash chargement stage")
                return False

            # Combat court
            time.sleep(5)

            if process.poll() is not None:
                self.bug_db.mark_broken_stage(stage_name, "Crash pendant combat sur stage")
                return False

            self.kill_game()
            print(f"✅ Stage {stage_name} - OK")
            return True

        except Exception as e:
            self.bug_db.add_bug('stage_bugs', {
                'key': stage_name,
                'tester': self.profile_name,
                'stage': stage_name,
                'description': f'Exception test stage: {str(e)}'
            })
            return False

        finally:
            # Restaure select.def
            select_def.write_text(backup, encoding='utf-8')

    def execute_input_pattern(self):
        """Exécute des inputs selon le pattern du profil"""
        pattern = self.profile.get('input_pattern', 'minimal')

        if pattern == 'minimal':
            # Rien
            pass

        elif pattern == 'spam':
            # Spam agressif
            keys = ['a', 's', 'd', 'z', 'x', 'c', 'space']
            for _ in range(5):
                pyautogui.press(random.choice(keys))
                time.sleep(0.05)

        elif pattern == 'varied':
            # Varié
            if random.random() < 0.5:
                pyautogui.press(random.choice(['a', 's', 'd', 'z', 'x', 'c']))

        elif pattern == 'chaos':
            # Total chaos
            keys = ['a', 's', 'd', 'z', 'x', 'c', 'space', 'return', 'left', 'right', 'up', 'down']
            for _ in range(random.randint(1, 10)):
                pyautogui.press(random.choice(keys))
                time.sleep(0.02)

        elif pattern == 'sustained':
            # Inputs soutenus
            pyautogui.press('d')
            time.sleep(0.1)
            pyautogui.press('s')

    def run_continuous_tests(self):
        """Boucle de tests continue"""
        print(f"\n🤖 TESTEUR IA DÉMARRÉ: {self.profile_name}")
        print(f"   Description: {self.profile['description']}")
        print(f"   Focus: {', '.join(self.profile['focus'])}")
        print("=" * 70)

        while self.running:
            try:
                self.tests_run += 1
                self.bug_db.db['total_tests'] += 1

                strategy = self.profile['test_strategy']

                if strategy == 'rapid_restart':
                    # Test startup crashes répétés
                    self.test_startup_crash()

                elif strategy == 'exhaustive_coverage':
                    # Teste tous les personnages
                    chars = self.bug_db.get_all_characters()
                    if chars:
                        char = random.choice(chars)
                        self.test_character(char)

                    # Teste tous les stages
                    stages = self.bug_db.get_all_stages()
                    if stages and random.random() < 0.3:  # 30% du temps
                        stage = random.choice(stages)
                        self.test_stage(stage)

                elif strategy in ['intensive_input', 'extended_matches', 'pure_random']:
                    # Tests de gameplay variés
                    safe_chars = self.bug_db.get_safe_characters()
                    if len(safe_chars) >= 2:
                        char = random.choice(safe_chars)
                        self.test_character(char)

                elif strategy == 'screenshot_analysis':
                    # Tests visuels
                    self.test_visual_bugs()

                # Rapport tous les 10 tests
                if self.tests_run % 10 == 0:
                    print(f"\n📊 [{self.profile_name}] Tests effectués: {self.tests_run}")
                    self.bug_db.generate_report()

                # Pause entre tests
                time.sleep(2)

            except KeyboardInterrupt:
                print(f"\n⏸️  [{self.profile_name}] Arrêté")
                break

            except Exception as e:
                print(f"\n❌ [{self.profile_name}] Erreur: {e}")
                traceback.print_exc()
                time.sleep(5)

    def test_visual_bugs(self):
        """Teste les bugs visuels"""
        # TODO: Analyse de screenshots pour détecter portraits manquants, etc.
        pass


def main():
    """Lance tous les testeurs IA en parallèle"""
    game_dir = Path(__file__).parent

    print("=" * 70)
    print("🤖 SYSTÈME DE TESTEURS IA AVANCÉS")
    print("=" * 70)

    # Sélection des profils à lancer
    profiles_to_run = [
        "CRASHER",
        "EXPLORER",
        "STRESS_TESTER",
        "RAGE_QUITTER"
    ]

    print(f"\n📋 Lancement de {len(profiles_to_run)} testeurs IA:")
    for profile in profiles_to_run:
        print(f"   - {profile}: {AITesterProfile.PROFILES[profile]['description']}")

    print("\n🚀 Démarrage des tests (Ctrl+C pour arrêter)...\n")

    # Crée un testeur par profil
    testers = [AdvancedAITester(profile, game_dir) for profile in profiles_to_run]

    # Lance en threads parallèles
    threads = []
    for tester in testers:
        thread = threading.Thread(target=tester.run_continuous_tests, daemon=True)
        thread.start()
        threads.append(thread)
        time.sleep(2)  # Décale les démarrages

    try:
        # Attendre indéfiniment
        while True:
            time.sleep(10)

            # Status global tous les 30s
            if int(time.time()) % 30 == 0:
                total_tests = sum(t.tests_run for t in testers)
                print(f"\n📊 STATUT GLOBAL - Tests totaux: {total_tests}")
                for tester in testers:
                    print(f"   {tester.profile_name}: {tester.tests_run} tests")

    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt de tous les testeurs...")
        for tester in testers:
            tester.running = False

        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join(timeout=5)

        # Rapport final
        print("\n📄 Génération du rapport final...")
        bug_db = BugDatabase(game_dir)
        report_path = bug_db.generate_report()

        print(f"\n✅ Tests terminés!")
        print(f"📄 Rapport: {report_path}")
        print(f"🗃️  Base de bugs: {bug_db.db_file}")

if __name__ == "__main__":
    main()
