"""
🤖 AI PERMANENT BUG HUNTER - Système de test continu esport-ready
Objectif : Passer de 2/20 à 18/20+ en détectant tous les bugs
"""
import subprocess
import time
import json
import os
import sys
import psutil
import threading
from datetime import datetime
from pathlib import Path
import re

class BugHunter:
    def __init__(self):
        self.game_dir = Path(__file__).parent
        self.bug_report = self.game_dir / "BUG_REPORTS" / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.bug_report.parent.mkdir(exist_ok=True)

        self.bugs_found = {
            "critical": [],
            "major": [],
            "minor": [],
            "visual": []
        }

        self.test_config = {
            "test_duration_hours": 24,  # Tests 24/7
            "profiles": [
                {"name": "RUSHDOWN", "playstyle": "aggressive", "combo_frequency": 0.8},
                {"name": "DEFENSIVE", "playstyle": "defensive", "combo_frequency": 0.3},
                {"name": "BALANCED", "playstyle": "balanced", "combo_frequency": 0.5},
                {"name": "TECHNICAL", "playstyle": "technical", "combo_frequency": 0.9},
                {"name": "RANDOM", "playstyle": "random", "combo_frequency": 0.5}
            ],
            "tests_per_profile": 100,
            "check_multiplayer": True,
            "check_portraits": True,
            "check_icons": True,
            "check_crashes": True,
            "check_visual_bugs": True,
            "check_input_bugs": True
        }

        self.running = True
        self.current_test = 0
        self.total_tests = len(self.test_config["profiles"]) * self.test_config["tests_per_profile"]

    def log_bug(self, severity, category, description, details=None):
        """Enregistre un bug détecté"""
        bug = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "description": description,
            "details": details or {},
            "test_number": self.current_test
        }
        self.bugs_found[severity].append(bug)

        # Log immédiat
        print(f"\n🐛 BUG {severity.upper()} détecté:")
        print(f"   Catégorie: {category}")
        print(f"   Description: {description}")
        if details:
            print(f"   Détails: {json.dumps(details, indent=2)}")

        # Sauvegarde
        self.save_report()

    def check_game_exe(self):
        """Vérifie que l'exe du jeu existe"""
        possible_exes = [
            self.game_dir / "KOF_Ultimate_Online.exe",
            self.game_dir / "Ikemen_GO.exe",
            self.game_dir / "mugen.exe"
        ]

        for exe in possible_exes:
            if exe.exists():
                return exe

        self.log_bug("critical", "INSTALLATION",
                    "Aucun exécutable de jeu trouvé",
                    {"searched_paths": [str(p) for p in possible_exes]})
        return None

    def check_select_def(self):
        """Vérifie la configuration du roster"""
        select_def = self.game_dir / "data" / "select.def"

        if not select_def.exists():
            self.log_bug("critical", "CONFIG", "select.def manquant")
            return False

        try:
            content = select_def.read_text(encoding='utf-8', errors='ignore')

            # Compte les personnages
            char_lines = [l for l in content.split('\n')
                         if l.strip() and not l.strip().startswith(';')
                         and ',' in l and '[Characters]' not in l]

            if len(char_lines) < 2:
                self.log_bug("critical", "ROSTER",
                           "Roster insuffisant pour esport (< 2 personnages)",
                           {"char_count": len(char_lines)})
                return False

            if len(char_lines) < 10:
                self.log_bug("major", "ROSTER",
                           "Roster limité pour esport (< 10 personnages)",
                           {"char_count": len(char_lines)})

            return True

        except Exception as e:
            self.log_bug("critical", "CONFIG", f"Erreur lecture select.def: {e}")
            return False

    def check_character_portraits(self):
        """Vérifie que les portraits des personnages existent"""
        chars_dir = self.game_dir / "chars"

        if not chars_dir.exists():
            self.log_bug("critical", "INSTALLATION", "Dossier chars/ manquant")
            return

        char_folders = [d for d in chars_dir.iterdir() if d.is_dir()]

        missing_portraits = []
        missing_def = []

        for char_folder in char_folders:
            # Vérifie .def
            def_files = list(char_folder.glob("*.def"))
            if not def_files:
                missing_def.append(char_folder.name)
                continue

            # Vérifie portrait (plusieurs formats possibles)
            portrait_patterns = ["portrait.sff", "*.sff", "portrait.png", "portrait.jpg"]
            has_portrait = False

            for pattern in portrait_patterns:
                if list(char_folder.glob(pattern)):
                    has_portrait = True
                    break

            if not has_portrait:
                missing_portraits.append(char_folder.name)

        if missing_def:
            self.log_bug("critical", "CHARACTERS",
                       "Personnages sans fichier .def",
                       {"characters": missing_def[:10]})

        if missing_portraits:
            self.log_bug("major", "VISUAL",
                       "Personnages sans portrait",
                       {"characters": missing_portraits[:10]})

    def check_character_icons(self):
        """Vérifie que les icônes des personnages sont valides"""
        select_def = self.game_dir / "data" / "select.def"

        if not select_def.exists():
            return

        try:
            content = select_def.read_text(encoding='utf-8', errors='ignore')
            char_lines = [l.strip() for l in content.split('\n')
                         if l.strip() and not l.strip().startswith(';')
                         and ',' in l and '[Characters]' not in l]

            mismatched = []

            for line in char_lines:
                char_name = line.split(',')[0].strip()
                char_folder = self.game_dir / "chars" / char_name

                if not char_folder.exists():
                    mismatched.append({
                        "char": char_name,
                        "issue": "Dossier inexistant"
                    })

            if mismatched:
                self.log_bug("critical", "ROSTER_ICONS",
                           "Personnages dans select.def sans dossier correspondant",
                           {"mismatches": mismatched[:10]})

        except Exception as e:
            self.log_bug("major", "CONFIG", f"Erreur vérification icônes: {e}")

    def check_multiplayer_config(self):
        """Vérifie la configuration multijoueur"""
        # Cherche fichiers de config réseau
        network_configs = [
            self.game_dir / "data" / "network.json",
            self.game_dir / "save" / "network.json",
            self.game_dir / "config.json"
        ]

        has_network = False
        for config in network_configs:
            if config.exists():
                has_network = True
                try:
                    data = json.loads(config.read_text())
                    if "network" in data or "multiplayer" in data:
                        return True
                except:
                    pass

        if not has_network:
            self.log_bug("critical", "MULTIPLAYER",
                       "Aucune configuration multijoueur trouvée")

        return has_network

    def run_ai_match_test(self, profile1, profile2):
        """Lance un match IA vs IA et surveille les bugs"""
        print(f"\n🎮 Test {self.current_test}/{self.total_tests}: {profile1['name']} vs {profile2['name']}")

        game_exe = self.check_game_exe()
        if not game_exe:
            return False

        # Lance le jeu en mode IA vs IA
        log_file = self.game_dir / "test_match.log"

        try:
            # Lance avec timeout
            process = subprocess.Popen(
                [str(game_exe), "-ai1", profile1["playstyle"], "-ai2", profile2["playstyle"]],
                cwd=str(self.game_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            start_time = time.time()
            timeout = 120  # 2 minutes max par match

            # Monitore le processus
            while process.poll() is None:
                if time.time() - start_time > timeout:
                    process.kill()
                    self.log_bug("major", "PERFORMANCE",
                               "Match dépassé timeout de 2 minutes",
                               {"profile1": profile1["name"], "profile2": profile2["name"]})
                    return False

                # Vérifie utilisation mémoire
                try:
                    proc_info = psutil.Process(process.pid)
                    mem_mb = proc_info.memory_info().rss / 1024 / 1024

                    if mem_mb > 2000:  # > 2GB
                        self.log_bug("major", "MEMORY_LEAK",
                                   f"Utilisation mémoire excessive: {mem_mb:.0f}MB",
                                   {"profile1": profile1["name"], "profile2": profile2["name"]})
                except:
                    pass

                time.sleep(0.5)

            # Vérifie le code de sortie
            if process.returncode != 0:
                stdout, stderr = process.communicate()
                self.log_bug("critical", "CRASH",
                           f"Jeu crashé (code {process.returncode})",
                           {
                               "profile1": profile1["name"],
                               "profile2": profile2["name"],
                               "stderr": stderr.decode('utf-8', errors='ignore')[:500]
                           })
                return False

            return True

        except Exception as e:
            self.log_bug("critical", "EXECUTION",
                       f"Erreur lancement match: {e}",
                       {"profile1": profile1["name"], "profile2": profile2["name"]})
            return False

    def save_report(self):
        """Sauvegarde le rapport de bugs"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "tests_completed": self.current_test,
            "total_tests": self.total_tests,
            "bugs": self.bugs_found,
            "summary": {
                "critical": len(self.bugs_found["critical"]),
                "major": len(self.bugs_found["major"]),
                "minor": len(self.bugs_found["minor"]),
                "visual": len(self.bugs_found["visual"])
            },
            "score": self.calculate_score()
        }

        self.bug_report.write_text(json.dumps(report, indent=2, ensure_ascii=False))

        # Crée aussi un rapport lisible
        self.generate_readable_report(report)

    def calculate_score(self):
        """Calcule le score de qualité du jeu /20"""
        base_score = 20

        # Pénalités
        base_score -= len(self.bugs_found["critical"]) * 5  # -5 par bug critique
        base_score -= len(self.bugs_found["major"]) * 2    # -2 par bug majeur
        base_score -= len(self.bugs_found["minor"]) * 0.5  # -0.5 par bug mineur
        base_score -= len(self.bugs_found["visual"]) * 0.2 # -0.2 par bug visuel

        return max(0, min(20, base_score))

    def generate_readable_report(self, report):
        """Génère un rapport markdown lisible"""
        md_path = self.bug_report.parent / f"REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        md = f"""# 🎮 RAPPORT BUG HUNTER - KOF Ultimate Online

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Tests effectués**: {report['tests_completed']}/{report['total_tests']}
**SCORE QUALITÉ**: {report['score']:.1f}/20

## 📊 Résumé des bugs

- 🔴 **CRITIQUE**: {report['summary']['critical']} bugs
- 🟠 **MAJEUR**: {report['summary']['major']} bugs
- 🟡 **MINEUR**: {report['summary']['minor']} bugs
- 🔵 **VISUEL**: {report['summary']['visual']} bugs

---

## 🔴 BUGS CRITIQUES (Bloquants esport)

"""

        for bug in self.bugs_found["critical"]:
            md += f"""### {bug['category']}
**Description**: {bug['description']}
**Test**: #{bug['test_number']}
**Timestamp**: {bug['timestamp']}
**Détails**:
```json
{json.dumps(bug['details'], indent=2)}
```

---

"""

        md += "\n## 🟠 BUGS MAJEURS\n\n"
        for bug in self.bugs_found["major"][:10]:  # Top 10
            md += f"- **{bug['category']}**: {bug['description']}\n"

        md += "\n## 🟡 BUGS MINEURS\n\n"
        for bug in self.bugs_found["minor"][:10]:
            md += f"- **{bug['category']}**: {bug['description']}\n"

        md += f"""

## 🎯 PRIORITÉS DE CORRECTION

### 🚨 URGENT (Bloquants esport)
"""

        urgent = []
        if any("MULTIPLAYER" in b["category"] for b in self.bugs_found["critical"]):
            urgent.append("- Réparer le système multijoueur")
        if any("ROSTER" in b["category"] for b in self.bugs_found["critical"]):
            urgent.append("- Corriger le roster et les icônes de personnages")
        if any("CRASH" in b["category"] for b in self.bugs_found["critical"]):
            urgent.append("- Éliminer les crashs")

        md += "\n".join(urgent) if urgent else "- Aucune priorité critique"

        md += f"""

### 📈 IMPORTANT (Qualité esport)
- Augmenter le roster (minimum 20 personnages)
- Ajouter tous les portraits et icônes manquants
- Optimiser les performances (éliminer memory leaks)
- Valider tous les fichiers .def des personnages

## 🔧 RECOMMANDATIONS

1. **Tests automatisés**: Lancer ce script 24/7 pour détecter tous les bugs
2. **Profils IA variés**: Tester avec tous les styles de jeu (rushdown, défensif, technique)
3. **Stress tests**: Matchs longues durées pour détecter memory leaks
4. **Validation complète**: Vérifier TOUS les fichiers avant release esport

---

*Rapport généré automatiquement par AI Bug Hunter*
*Prochaine analyse dans 1 heure*
"""

        md_path.write_text(md, encoding='utf-8')
        print(f"\n📄 Rapport sauvegardé: {md_path}")

    def run_continuous_tests(self):
        """Lance les tests en continu"""
        print("🚀 DÉMARRAGE BUG HUNTER - Tests 24/7")
        print("=" * 60)

        # Phase 1: Vérifications statiques
        print("\n📋 PHASE 1: Vérifications statiques")
        self.check_game_exe()
        self.check_select_def()
        self.check_character_portraits()
        self.check_character_icons()
        self.check_multiplayer_config()

        # Phase 2: Tests dynamiques (matchs IA)
        print("\n🎮 PHASE 2: Tests dynamiques (matchs IA)")

        profiles = self.test_config["profiles"]

        while self.running and self.current_test < self.total_tests:
            # Choisit 2 profils différents
            import random
            p1, p2 = random.sample(profiles, 2)

            self.current_test += 1
            self.run_ai_match_test(p1, p2)

            # Sauvegarde tous les 10 tests
            if self.current_test % 10 == 0:
                self.save_report()
                score = self.calculate_score()
                print(f"\n📊 Progression: {self.current_test}/{self.total_tests} - Score: {score:.1f}/20")

            # Petite pause pour ne pas saturer
            time.sleep(2)

        # Rapport final
        print("\n✅ TESTS TERMINÉS")
        self.save_report()

        final_score = self.calculate_score()
        print(f"\n🏆 SCORE FINAL: {final_score:.1f}/20")

        if final_score < 10:
            print("❌ QUALITÉ INSUFFISANTE - Nombreux bugs critiques")
        elif final_score < 15:
            print("⚠️  QUALITÉ MOYENNE - Corrections nécessaires")
        elif final_score < 18:
            print("✅ BONNE QUALITÉ - Quelques améliorations possibles")
        else:
            print("🏆 EXCELLENTE QUALITÉ - Prêt pour esport!")

        return final_score

def main():
    hunter = BugHunter()

    try:
        score = hunter.run_continuous_tests()
        sys.exit(0 if score >= 15 else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️  Tests interrompus par l'utilisateur")
        hunter.save_report()
        sys.exit(0)

if __name__ == "__main__":
    main()
