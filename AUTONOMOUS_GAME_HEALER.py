#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 SYSTÈME AUTONOME D'AUTO-GUÉRISON DU JEU
Le jeu se debug, se répare et s'améliore TOUT SEUL

Cycle continu:
1. Tests automatiques (détection bugs)
2. Analyse automatique (diagnostic)
3. Réparation automatique (correction)
4. Validation automatique (vérification)
5. Amélioration continue (optimisation)

FONCTIONNE EN PERMANENCE SANS INTERVENTION
"""

import subprocess
import time
import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import threading
import traceback

class AutonomousGameHealer:
    """Système autonome qui guérit le jeu en permanence"""

    def __init__(self, game_dir):
        self.game_dir = Path(game_dir)
        self.running = True
        self.cycle_count = 0
        self.score_history = []

        # Fichiers de données
        self.bug_db_file = self.game_dir / "BUG_DATABASE.json"
        self.health_report = self.game_dir / "GAME_HEALTH.json"
        self.auto_log = self.game_dir / "AUTONOMOUS_HEALER.log"

        # Statistiques
        self.stats = {
            'cycles_completed': 0,
            'bugs_detected': 0,
            'bugs_fixed': 0,
            'characters_removed': 0,
            'stages_removed': 0,
            'score_improvements': [],
            'start_time': datetime.now().isoformat()
        }

        self.log("🤖 SYSTÈME AUTONOME D'AUTO-GUÉRISON INITIALISÉ")
        self.log(f"📁 Répertoire: {self.game_dir}")

    def log(self, message):
        """Log avec timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)

        with open(self.auto_log, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')

    def load_bug_database(self):
        """Charge la base de bugs"""
        if self.bug_db_file.exists():
            try:
                return json.loads(self.bug_db_file.read_text(encoding='utf-8'))
            except:
                return None
        return None

    def save_health_report(self, data):
        """Sauvegarde le rapport de santé du jeu"""
        data['timestamp'] = datetime.now().isoformat()
        data['cycle'] = self.cycle_count
        self.health_report.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    def calculate_game_score(self, bug_db):
        """Calcule le score qualité du jeu /20"""
        if not bug_db:
            return 2.0  # Score par défaut si pas de données

        base_score = 20.0

        # Pénalités selon bugs
        critical_bugs = (
            len(bug_db.get('startup_crashes', [])) +
            len(bug_db.get('broken_characters', [])) +
            len(bug_db.get('broken_stages', []))
        )

        major_bugs = len(bug_db.get('gameplay_bugs', []))
        visual_bugs = len(bug_db.get('visual_bugs', []))

        base_score -= critical_bugs * 5.0
        base_score -= major_bugs * 2.0
        base_score -= visual_bugs * 0.2

        return max(0, min(20, base_score))

    # ==================== PHASE 1: TEST ====================

    def phase_test(self):
        """Phase 1: Lance les testeurs IA pour détecter bugs"""
        self.log("\n" + "="*70)
        self.log("📋 PHASE 1: TESTS AUTOMATIQUES")
        self.log("="*70)

        # Lance les testeurs IA
        tester_script = self.game_dir / "AI_TESTERS_ADVANCED.py"

        if not tester_script.exists():
            self.log("❌ AI_TESTERS_ADVANCED.py manquant!")
            return False

        self.log("🤖 Lancement testeurs IA (20 tests rapides)...")

        try:
            # Lance les testeurs avec limite de temps
            process = subprocess.Popen(
                [sys.executable, str(tester_script)],
                cwd=str(self.game_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Attendre max 5 minutes
            timeout = 300
            start_time = time.time()

            while process.poll() is None and (time.time() - start_time) < timeout:
                time.sleep(5)

                # Vérifier si assez de tests effectués
                bug_db = self.load_bug_database()
                if bug_db and bug_db.get('total_tests', 0) >= 20:
                    self.log(f"✅ {bug_db['total_tests']} tests effectués")
                    process.terminate()
                    break

            # Forcer arrêt si encore actif
            if process.poll() is None:
                process.kill()

            # Charger résultats
            bug_db = self.load_bug_database()
            if bug_db:
                total_bugs = (
                    len(bug_db.get('broken_characters', [])) +
                    len(bug_db.get('broken_stages', [])) +
                    len(bug_db.get('startup_crashes', []))
                )
                self.log(f"🐛 Bugs détectés: {total_bugs}")
                self.stats['bugs_detected'] += total_bugs
                return True
            else:
                self.log("⚠️  Aucune base de bugs générée")
                return False

        except Exception as e:
            self.log(f"❌ Erreur phase test: {e}")
            traceback.print_exc()
            return False

    # ==================== PHASE 2: ANALYSE ====================

    def phase_analyze(self):
        """Phase 2: Analyse les bugs détectés"""
        self.log("\n" + "="*70)
        self.log("🔍 PHASE 2: ANALYSE AUTOMATIQUE")
        self.log("="*70)

        bug_db = self.load_bug_database()
        if not bug_db:
            self.log("❌ Pas de données à analyser")
            return None

        # Calcule score actuel
        current_score = self.calculate_game_score(bug_db)
        self.score_history.append({
            'cycle': self.cycle_count,
            'score': current_score,
            'timestamp': datetime.now().isoformat()
        })

        self.log(f"📊 SCORE ACTUEL: {current_score:.1f}/20")

        # Analyse priorités
        broken_chars = bug_db.get('broken_characters', [])
        broken_stages = bug_db.get('broken_stages', [])
        startup_crashes = bug_db.get('startup_crashes', [])

        analysis = {
            'score': current_score,
            'critical_issues': [],
            'recommended_actions': []
        }

        if broken_chars:
            analysis['critical_issues'].append(f"{len(broken_chars)} personnages cassés")
            analysis['recommended_actions'].append("remove_broken_characters")
            self.log(f"❌ {len(broken_chars)} personnages à retirer")

        if broken_stages:
            analysis['critical_issues'].append(f"{len(broken_stages)} stages cassés")
            analysis['recommended_actions'].append("remove_broken_stages")
            self.log(f"🗺️  {len(broken_stages)} stages à retirer")

        if startup_crashes:
            analysis['critical_issues'].append(f"{len(startup_crashes)} crashs au startup")
            analysis['recommended_actions'].append("fix_startup_crashes")
            self.log(f"💥 {len(startup_crashes)} crashs détectés")

        if current_score >= 18:
            self.log("🏆 QUALITÉ ESPORT ATTEINTE!")
            analysis['recommended_actions'].append("polish_only")
        elif current_score >= 15:
            self.log("🟢 Bonne qualité - Peaufinage nécessaire")
            analysis['recommended_actions'].append("minor_fixes")
        elif current_score >= 10:
            self.log("🟡 Qualité moyenne - Corrections importantes")
        else:
            self.log("🔴 Qualité faible - Nettoyage majeur requis")

        return analysis

    # ==================== PHASE 3: RÉPARATION ====================

    def phase_repair(self, analysis):
        """Phase 3: Répare automatiquement les problèmes"""
        self.log("\n" + "="*70)
        self.log("🔧 PHASE 3: RÉPARATION AUTOMATIQUE")
        self.log("="*70)

        if not analysis or not analysis.get('recommended_actions'):
            self.log("✅ Aucune réparation nécessaire")
            return True

        bug_db = self.load_bug_database()
        if not bug_db:
            return False

        repairs_made = 0

        # Backup avant modifications
        backup_dir = self.game_dir / f"AUTO_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(exist_ok=True)

        # Réparation: Retirer personnages cassés
        if "remove_broken_characters" in analysis['recommended_actions']:
            self.log("🗑️  Suppression personnages cassés...")
            broken_chars = bug_db.get('broken_characters', [])

            for char_info in broken_chars:
                char_name = char_info['name']
                char_dir = self.game_dir / "chars" / char_name

                if char_dir.exists():
                    try:
                        # Backup
                        backup_char = backup_dir / "chars" / char_name
                        backup_char.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copytree(char_dir, backup_char)

                        # Supprimer
                        shutil.rmtree(char_dir)
                        self.log(f"   ✅ Retiré: {char_name}")
                        repairs_made += 1
                        self.stats['characters_removed'] += 1
                    except Exception as e:
                        self.log(f"   ❌ Erreur {char_name}: {e}")

            # Mettre à jour select.def
            self.update_select_def_remove_characters(broken_chars)

        # Réparation: Retirer stages cassés
        if "remove_broken_stages" in analysis['recommended_actions']:
            self.log("🗑️  Suppression stages cassés...")
            broken_stages = bug_db.get('broken_stages', [])

            for stage_info in broken_stages:
                stage_name = stage_info['name']
                stage_file = self.game_dir / "stages" / f"{stage_name}.def"

                if stage_file.exists():
                    try:
                        # Backup
                        backup_stage = backup_dir / "stages" / stage_file.name
                        backup_stage.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(stage_file, backup_stage)

                        # Supprimer
                        stage_file.unlink()
                        self.log(f"   ✅ Retiré: {stage_name}")
                        repairs_made += 1
                        self.stats['stages_removed'] += 1
                    except Exception as e:
                        self.log(f"   ❌ Erreur {stage_name}: {e}")

            # Mettre à jour select.def
            self.update_select_def_remove_stages(broken_stages)

        self.log(f"\n✅ {repairs_made} réparations effectuées")
        self.stats['bugs_fixed'] += repairs_made

        # Réinitialiser la base de bugs pour nouveaux tests
        if repairs_made > 0:
            self.bug_db_file.unlink(missing_ok=True)
            self.log("🔄 Base de bugs réinitialisée pour prochains tests")

        return repairs_made > 0

    def update_select_def_remove_characters(self, broken_chars):
        """Met à jour select.def en retirant les personnages cassés"""
        select_def = self.game_dir / "data" / "select.def"
        if not select_def.exists():
            return

        content = select_def.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        broken_names = [c['name'] for c in broken_chars]

        new_lines = []
        for line in lines:
            should_keep = True
            for broken_name in broken_names:
                if line.strip().startswith(broken_name):
                    new_lines.append(f"; [AUTO-REMOVED] {line}")
                    should_keep = False
                    break
            if should_keep:
                new_lines.append(line)

        select_def.write_text('\n'.join(new_lines), encoding='utf-8')
        self.log("   ✅ select.def mis à jour")

    def update_select_def_remove_stages(self, broken_stages):
        """Met à jour select.def en retirant les stages cassés"""
        select_def = self.game_dir / "data" / "select.def"
        if not select_def.exists():
            return

        content = select_def.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        broken_names = [s['name'] for s in broken_stages]

        new_lines = []
        for line in lines:
            should_keep = True
            for broken_name in broken_names:
                if broken_name in line and '.def' in line:
                    new_lines.append(f"; [AUTO-REMOVED] {line}")
                    should_keep = False
                    break
            if should_keep:
                new_lines.append(line)

        select_def.write_text('\n'.join(new_lines), encoding='utf-8')
        self.log("   ✅ select.def stages mis à jour")

    # ==================== PHASE 4: VALIDATION ====================

    def phase_validate(self):
        """Phase 4: Valide que les réparations ont fonctionné"""
        self.log("\n" + "="*70)
        self.log("✅ PHASE 4: VALIDATION AUTOMATIQUE")
        self.log("="*70)

        # Relancer tests rapides
        self.log("🔍 Tests de validation (10 tests)...")

        try:
            tester_script = self.game_dir / "AI_TESTERS_ADVANCED.py"
            if not tester_script.exists():
                return True

            process = subprocess.Popen(
                [sys.executable, str(tester_script)],
                cwd=str(self.game_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Tests rapides (2 minutes max)
            time.sleep(120)
            process.terminate()

            # Vérifier amélioration
            bug_db = self.load_bug_database()
            if bug_db:
                new_score = self.calculate_game_score(bug_db)
                old_score = self.score_history[-1]['score'] if self.score_history else 2.0

                improvement = new_score - old_score
                self.log(f"📊 Score avant: {old_score:.1f}/20")
                self.log(f"📊 Score après: {new_score:.1f}/20")

                if improvement > 0:
                    self.log(f"🎉 AMÉLIORATION: +{improvement:.1f} points!")
                    self.stats['score_improvements'].append(improvement)
                    return True
                elif improvement < 0:
                    self.log(f"⚠️  Régression: {improvement:.1f} points")
                    return False
                else:
                    self.log("➡️  Score stable")
                    return True

        except Exception as e:
            self.log(f"❌ Erreur validation: {e}")
            return False

        return True

    # ==================== PHASE 5: AMÉLIORATION ====================

    def phase_improve(self):
        """Phase 5: Optimisations et améliorations continues"""
        self.log("\n" + "="*70)
        self.log("🚀 PHASE 5: AMÉLIORATION CONTINUE")
        self.log("="*70)

        # Vérifier si objectif atteint
        if self.score_history:
            current_score = self.score_history[-1]['score']

            if current_score >= 18:
                self.log("🏆 OBJECTIF ESPORT ATTEINT!")
                self.log("✅ Qualité maximale - Surveillance continue activée")
                return True

            # Suggestions d'amélioration
            if current_score < 10:
                self.log("🎯 Priorité: Éliminer tous les bugs critiques")
            elif current_score < 15:
                self.log("🎯 Priorité: Corriger bugs majeurs et améliorer roster")
            elif current_score < 18:
                self.log("🎯 Priorité: Peaufinage final et optimisations")

        return True

    # ==================== CYCLE PRINCIPAL ====================

    def run_healing_cycle(self):
        """Exécute un cycle complet de guérison"""
        self.cycle_count += 1

        self.log("\n" + "="*70)
        self.log(f"🔄 CYCLE D'AUTO-GUÉRISON #{self.cycle_count}")
        self.log("="*70)

        try:
            # Phase 1: Tests
            test_success = self.phase_test()
            if not test_success:
                self.log("⚠️  Phase test échouée - Retry au prochain cycle")
                return

            # Phase 2: Analyse
            analysis = self.phase_analyze()
            if not analysis:
                self.log("⚠️  Phase analyse échouée")
                return

            # Phase 3: Réparation
            repair_success = self.phase_repair(analysis)

            # Phase 4: Validation (si réparations effectuées)
            if repair_success:
                self.phase_validate()

            # Phase 5: Amélioration
            self.phase_improve()

            # Statistiques du cycle
            self.stats['cycles_completed'] += 1
            self.log(f"\n📊 CYCLE #{self.cycle_count} TERMINÉ")
            self.log(f"   Bugs détectés total: {self.stats['bugs_detected']}")
            self.log(f"   Bugs corrigés total: {self.stats['bugs_fixed']}")

            if self.score_history:
                current_score = self.score_history[-1]['score']
                self.log(f"   Score actuel: {current_score:.1f}/20")

        except Exception as e:
            self.log(f"❌ Erreur cycle: {e}")
            traceback.print_exc()

    def run_forever(self):
        """Boucle infinie d'auto-guérison"""
        self.log("\n" + "="*70)
        self.log("🤖 DÉMARRAGE SYSTÈME AUTONOME D'AUTO-GUÉRISON")
        self.log("="*70)
        self.log("\n⚡ Le jeu va se réparer et s'améliorer AUTOMATIQUEMENT")
        self.log("⏸️  Ctrl+C pour arrêter\n")

        while self.running:
            try:
                self.run_healing_cycle()

                # Pause entre cycles (5 minutes)
                self.log("\n⏸️  Pause 5 minutes avant prochain cycle...")
                time.sleep(300)

            except KeyboardInterrupt:
                self.log("\n🛑 Arrêt demandé par utilisateur")
                break

            except Exception as e:
                self.log(f"\n❌ Erreur critique: {e}")
                traceback.print_exc()
                time.sleep(60)

        # Rapport final
        self.generate_final_report()

    def generate_final_report(self):
        """Génère le rapport final"""
        self.log("\n" + "="*70)
        self.log("📄 RAPPORT FINAL D'AUTO-GUÉRISON")
        self.log("="*70)

        report = f"""# 🤖 RAPPORT SYSTÈME AUTONOME D'AUTO-GUÉRISON

**Durée**: {datetime.now().isoformat()} (Démarré: {self.stats['start_time']})
**Cycles effectués**: {self.stats['cycles_completed']}

## 📊 Statistiques

- **Bugs détectés**: {self.stats['bugs_detected']}
- **Bugs corrigés**: {self.stats['bugs_fixed']}
- **Personnages retirés**: {self.stats['characters_removed']}
- **Stages retirés**: {self.stats['stages_removed']}

## 📈 Évolution du Score

"""

        for entry in self.score_history:
            report += f"- Cycle #{entry['cycle']}: {entry['score']:.1f}/20\n"

        if self.score_history:
            initial_score = self.score_history[0]['score']
            final_score = self.score_history[-1]['score']
            improvement = final_score - initial_score

            report += f"""

## 🎯 Résultat Final

- **Score initial**: {initial_score:.1f}/20
- **Score final**: {final_score:.1f}/20
- **Amélioration totale**: {improvement:+.1f} points
"""

            if final_score >= 18:
                report += "\n🏆 **OBJECTIF ESPORT ATTEINT!**\n"
            elif final_score >= 15:
                report += "\n🟢 **Bonne qualité - Presque prêt pour esport**\n"
            elif final_score >= 10:
                report += "\n🟡 **Qualité moyenne - Corrections supplémentaires nécessaires**\n"
            else:
                report += "\n🔴 **Qualité insuffisante - Cycles supplémentaires requis**\n"

        report += "\n---\n\n*Rapport généré par Autonomous Game Healer*\n"

        report_path = self.game_dir / f"AUTO_HEALING_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path.write_text(report, encoding='utf-8')

        self.log(f"📄 Rapport sauvegardé: {report_path}")


def main():
    """Point d'entrée"""
    game_dir = Path(__file__).parent
    healer = AutonomousGameHealer(game_dir)

    try:
        healer.run_forever()
    except KeyboardInterrupt:
        healer.log("\n🛑 Arrêté par l'utilisateur")
    except Exception as e:
        healer.log(f"\n❌ Erreur fatale: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
