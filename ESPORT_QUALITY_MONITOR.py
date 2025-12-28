#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESPORT QUALITY MONITOR - Système de monitoring qualité en temps réel
Analyse continue du jeu et génère des métriques de qualité esport
"""

import os
import sys
import json
import time
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class EsportQualityMonitor:
    """Moniteur de qualité pour niveau esport"""

    def __init__(self):
        self.base_path = Path(r"D:\KOF Ultimate Online")
        self.game_exe = self.base_path / "KOF_Ultimate_Online.exe"
        self.chars_path = self.base_path / "chars"
        self.data_path = self.base_path / "data"
        self.logs_path = self.base_path / "logs"

        # Créer les dossiers nécessaires
        self.logs_path.mkdir(exist_ok=True)

        # Métriques de qualité
        self.metrics = {
            "quality_score": 2.0,
            "critical_bugs": [],
            "major_bugs": [],
            "minor_bugs": [],
            "roster_count": 0,
            "crash_count": 0,
            "tests_run": 0,
            "multiplayer_status": "NON_FONCTIONNEL",
            "portrait_issues": 0,
            "icon_issues": 0,
            "ai_status": "STOPPED",
            "last_update": None
        }

        # Critères esport
        self.esport_criteria = {
            "min_roster": 20,
            "max_critical_bugs": 0,
            "max_major_bugs": 2,
            "min_tests": 100,
            "required_features": [
                "multiplayer_working",
                "portraits_working",
                "icons_working",
                "no_crashes",
                "balanced_roster"
            ]
        }

    def log(self, message, level="INFO"):
        """Log avec icônes"""
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "SCAN": "🔍",
            "METRIC": "📊"
        }
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {icons.get(level, '')} {message}")

    def scan_roster(self):
        """Scanner le nombre de personnages disponibles"""
        self.log("Scan du roster...", "SCAN")

        try:
            if not self.chars_path.exists():
                self.log("Dossier chars introuvable!", "ERROR")
                return 0

            # Compter les dossiers de personnages
            char_folders = [d for d in self.chars_path.iterdir() if d.is_dir()]
            count = len(char_folders)

            self.metrics["roster_count"] = count
            self.log(f"Personnages détectés: {count}", "SUCCESS")

            # Vérifier si on atteint le minimum esport
            min_required = self.esport_criteria["min_roster"]
            if count < min_required:
                self.log(f"⚠️ Roster insuffisant! Minimum: {min_required}, Actuel: {count}", "WARNING")
                self.metrics["critical_bugs"].append(f"Roster trop petit: {count}/{min_required}")

            return count

        except Exception as e:
            self.log(f"Erreur scan roster: {e}", "ERROR")
            return 0

    def check_portraits(self):
        """Vérifier l'état des portraits"""
        self.log("Vérification des portraits...", "SCAN")

        issues = 0
        try:
            if not self.chars_path.exists():
                return issues

            for char_folder in self.chars_path.iterdir():
                if not char_folder.is_dir():
                    continue

                # Chercher le fichier de portrait
                portrait_found = False
                for portrait_file in ["portrait.png", "portrait.pcx", "portrait.sff"]:
                    if (char_folder / portrait_file).exists():
                        portrait_found = True
                        break

                if not portrait_found:
                    issues += 1
                    self.log(f"Portrait manquant: {char_folder.name}", "WARNING")

            self.metrics["portrait_issues"] = issues

            if issues > 0:
                bug_msg = f"{issues} portraits manquants/corrompus"
                if bug_msg not in self.metrics["critical_bugs"]:
                    self.metrics["critical_bugs"].append(bug_msg)

            self.log(f"Issues portraits: {issues}", "SUCCESS" if issues == 0 else "WARNING")

        except Exception as e:
            self.log(f"Erreur check portraits: {e}", "ERROR")

        return issues

    def check_multiplayer(self):
        """Vérifier le système multijoueur"""
        self.log("Vérification système multijoueur...", "SCAN")

        status = "NON_FONCTIONNEL"
        issues = []

        try:
            # Vérifier serveur matchmaking
            matchmaking_server = self.base_path / "matchmaking_server.py"
            if not matchmaking_server.exists():
                issues.append("Serveur matchmaking manquant")

            # Vérifier client matchmaking
            matchmaking_client = self.base_path / "matchmaking_client.py"
            if not matchmaking_client.exists():
                issues.append("Client matchmaking manquant")

            # Vérifier config réseau dans mugen.cfg
            mugen_cfg = self.data_path / "mugen.cfg"
            if mugen_cfg.exists():
                content = mugen_cfg.read_text(encoding='latin-1', errors='ignore')
                if 'Network' not in content:
                    issues.append("Config réseau manquante")
            else:
                issues.append("mugen.cfg manquant")

            if len(issues) == 0:
                status = "FONCTIONNEL"
            elif len(issues) <= 1:
                status = "PARTIEL"

            self.metrics["multiplayer_status"] = status

            if issues:
                bug_msg = f"Multijoueur {status}: {', '.join(issues)}"
                if bug_msg not in self.metrics["critical_bugs"]:
                    self.metrics["critical_bugs"].append(bug_msg)
                self.log(f"Issues multijoueur: {len(issues)}", "WARNING")
            else:
                self.log("Système multijoueur OK", "SUCCESS")

        except Exception as e:
            self.log(f"Erreur check multijoueur: {e}", "ERROR")

        return status

    def check_crashes(self):
        """Analyser les logs pour détecter les crashs"""
        self.log("Analyse des crashs...", "SCAN")

        crash_count = 0
        try:
            # Vérifier mugen.log
            mugen_log = self.base_path / "mugen.log"
            if mugen_log.exists():
                content = mugen_log.read_text(encoding='utf-8', errors='ignore')

                # Chercher les indicateurs de crash
                crash_keywords = ['crash', 'fatal', 'exception', 'segmentation fault', 'access violation']
                for keyword in crash_keywords:
                    crash_count += content.lower().count(keyword)

            self.metrics["crash_count"] = crash_count

            if crash_count > 0:
                bug_msg = f"{crash_count} crashs détectés"
                if bug_msg not in self.metrics["critical_bugs"]:
                    self.metrics["critical_bugs"].append(bug_msg)
                self.log(f"⚠️ {crash_count} crashs détectés!", "WARNING")
            else:
                self.log("Aucun crash détecté", "SUCCESS")

        except Exception as e:
            self.log(f"Erreur check crashes: {e}", "ERROR")

        return crash_count

    def check_ai_tests(self):
        """Vérifier si les tests IA sont actifs"""
        self.log("Vérification tests IA...", "SCAN")

        is_running = False
        tests_count = 0

        try:
            # Vérifier si un processus de test tourne
            for proc in psutil.process_iter(['name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info.get('cmdline', []))
                    if 'AUTO_TEST' in cmdline or 'ai_player' in cmdline:
                        is_running = True
                        break
                except:
                    pass

            # Compter les logs de test
            if self.logs_path.exists():
                test_logs = list(self.logs_path.glob("test_*.log"))
                tests_count = len(test_logs)

            self.metrics["ai_status"] = "RUNNING" if is_running else "STOPPED"
            self.metrics["tests_run"] = tests_count

            if is_running:
                self.log(f"Tests IA actifs - {tests_count} tests effectués", "SUCCESS")
            else:
                self.log("Tests IA arrêtés", "WARNING")

        except Exception as e:
            self.log(f"Erreur check AI: {e}", "ERROR")

        return is_running

    def calculate_quality_score(self):
        """Calculer le score de qualité global (0-20)"""
        self.log("Calcul du score qualité...", "METRIC")

        score = 20.0  # Commencer au maximum

        # Pénalités pour bugs critiques (-3 points chacun)
        critical_count = len(self.metrics["critical_bugs"])
        score -= critical_count * 3.0

        # Pénalités pour bugs majeurs (-1 point chacun)
        major_count = len(self.metrics["major_bugs"])
        score -= major_count * 1.0

        # Bonus pour roster suffisant (+2 points)
        if self.metrics["roster_count"] >= self.esport_criteria["min_roster"]:
            score += 2.0
        else:
            score -= 2.0

        # Bonus pour tests effectués (+1 point si >= 100 tests)
        if self.metrics["tests_run"] >= self.esport_criteria["min_tests"]:
            score += 1.0

        # Bonus multijoueur fonctionnel (+3 points)
        if self.metrics["multiplayer_status"] == "FONCTIONNEL":
            score += 3.0
        elif self.metrics["multiplayer_status"] == "PARTIEL":
            score += 1.0

        # Bonus aucun crash (+2 points)
        if self.metrics["crash_count"] == 0:
            score += 2.0

        # Limiter entre 0 et 20
        score = max(0.0, min(20.0, score))

        self.metrics["quality_score"] = round(score, 1)
        self.log(f"Score qualité: {score}/20", "METRIC")

        return score

    def generate_report(self):
        """Générer un rapport JSON des métriques"""
        self.log("Génération du rapport...", "INFO")

        self.metrics["last_update"] = datetime.now().isoformat()

        report_file = self.base_path / "esport_quality_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2, ensure_ascii=False)

            self.log(f"Rapport sauvegardé: {report_file.name}", "SUCCESS")

        except Exception as e:
            self.log(f"Erreur génération rapport: {e}", "ERROR")

    def display_summary(self):
        """Afficher un résumé des métriques"""
        print("\n" + "="*60)
        print("📊 RAPPORT QUALITÉ ESPORT - KOF ULTIMATE ONLINE")
        print("="*60)
        print(f"\n🎯 SCORE GLOBAL: {self.metrics['quality_score']}/20")
        print(f"   Objectif esport: 18+/20")
        print(f"   Progression: {(self.metrics['quality_score']/20*100):.0f}%")

        print(f"\n📈 MÉTRIQUES:")
        print(f"   👥 Roster: {self.metrics['roster_count']} personnages (min: {self.esport_criteria['min_roster']})")
        print(f"   🧪 Tests effectués: {self.metrics['tests_run']}")
        print(f"   💥 Crashs détectés: {self.metrics['crash_count']}")
        print(f"   🌐 Multijoueur: {self.metrics['multiplayer_status']}")
        print(f"   🤖 Tests IA: {self.metrics['ai_status']}")

        print(f"\n🔴 BUGS CRITIQUES ({len(self.metrics['critical_bugs'])}):")
        if self.metrics['critical_bugs']:
            for bug in self.metrics['critical_bugs']:
                print(f"   - {bug}")
        else:
            print("   ✅ Aucun bug critique!")

        print(f"\n🟠 BUGS MAJEURS ({len(self.metrics['major_bugs'])}):")
        if self.metrics['major_bugs']:
            for bug in self.metrics['major_bugs']:
                print(f"   - {bug}")
        else:
            print("   ✅ Aucun bug majeur!")

        print(f"\n🎨 PROBLÈMES VISUELS:")
        print(f"   - Portraits: {self.metrics['portrait_issues']} issues")
        print(f"   - Icônes: {self.metrics['icon_issues']} issues")

        print("\n" + "="*60)

    def run_full_audit(self):
        """Exécuter un audit complet"""
        print("\n🔍 DÉMARRAGE AUDIT QUALITÉ ESPORT")
        print("="*60 + "\n")

        # Effectuer toutes les vérifications
        self.scan_roster()
        self.check_portraits()
        self.check_multiplayer()
        self.check_crashes()
        self.check_ai_tests()

        # Calculer le score
        self.calculate_quality_score()

        # Générer le rapport
        self.generate_report()

        # Afficher le résumé
        self.display_summary()

        return self.metrics["quality_score"]

    def continuous_monitor(self, interval=60):
        """Monitoring continu avec intervalle (en secondes)"""
        print(f"\n🔄 DÉMARRAGE MONITORING CONTINU (intervalle: {interval}s)")
        print("Appuyez sur Ctrl+C pour arrêter\n")

        try:
            while True:
                self.run_full_audit()
                print(f"\n⏳ Prochaine analyse dans {interval} secondes...\n")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring arrêté par l'utilisateur")
            self.log("Monitoring terminé", "INFO")


def main():
    """Point d'entrée principal"""
    monitor = EsportQualityMonitor()

    # Vérifier les arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--continuous':
            # Mode monitoring continu
            interval = 60 if len(sys.argv) <= 2 else int(sys.argv[2])
            monitor.continuous_monitor(interval)
        elif sys.argv[1] == '--help':
            print("ESPORT QUALITY MONITOR - Système de monitoring qualité")
            print("\nUtilisation:")
            print("  python ESPORT_QUALITY_MONITOR.py              # Audit unique")
            print("  python ESPORT_QUALITY_MONITOR.py --continuous # Monitoring continu (60s)")
            print("  python ESPORT_QUALITY_MONITOR.py --continuous 120 # Monitoring (120s)")
            return
    else:
        # Mode audit unique
        monitor.run_full_audit()


if __name__ == "__main__":
    main()
