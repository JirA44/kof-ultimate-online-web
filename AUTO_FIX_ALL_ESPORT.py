#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO FIX ALL ESPORT - Réparation automatique complète
Répare TOUS les bugs critiques en un seul clic
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import time

class EsportAutoFixer:
    """Réparateur automatique complet pour niveau esport"""

    def __init__(self):
        self.base_path = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo")
        self.scripts = {
            "portraits": self.base_path / "AUTO_FIX_PORTRAITS.py",
            "multiplayer": self.base_path / "AUTO_FIX_MULTIPLAYER.py",
            "monitor": self.base_path / "ESPORT_QUALITY_MONITOR.py"
        }
        self.results = {}

    def log(self, message, level="INFO"):
        """Log avec icônes"""
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "FIX": "🔧",
            "SCAN": "🔍"
        }
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {icons.get(level, '')} {message}")

    def print_header(self):
        """Afficher l'en-tête"""
        print("\n")
        print("╔" + "="*68 + "╗")
        print("║" + " "*15 + "AUTO FIX ALL ESPORT v1.0" + " "*29 + "║")
        print("║" + " "*10 + "Réparation Automatique Complète" + " "*27 + "║")
        print("║" + " "*20 + "Vers le Niveau Esport!" + " "*25 + "║")
        print("╚" + "="*68 + "╝")
        print("\n")

    def print_section(self, title):
        """Afficher une section"""
        print("\n" + "="*70)
        print(f"🎯 {title}")
        print("="*70 + "\n")

    def run_initial_audit(self):
        """Exécuter l'audit initial"""
        self.print_section("PHASE 1: AUDIT INITIAL")
        self.log("Analyse de l'état actuel du jeu...", "SCAN")

        try:
            result = subprocess.run(
                [sys.executable, str(self.scripts["monitor"])],
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                timeout=60
            )

            # Extraire le score du résultat
            if "Score qualité:" in result.stdout:
                for line in result.stdout.split('\n'):
                    if "Score qualité:" in line:
                        score_line = line
                        break

            self.log("Audit initial terminé", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Erreur audit initial: {e}", "ERROR")
            return False

    def fix_portraits(self):
        """Réparer les portraits"""
        self.print_section("PHASE 2: RÉPARATION DES PORTRAITS")
        self.log("Démarrage réparation portraits...", "FIX")

        try:
            # Créer un fichier temporaire pour simuler l'input 'O'
            temp_input = self.base_path / "temp_input.txt"
            temp_input.write_text("O\n")

            with open(temp_input, 'r') as input_file:
                result = subprocess.run(
                    [sys.executable, str(self.scripts["portraits"])],
                    cwd=str(self.base_path),
                    stdin=input_file,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

            temp_input.unlink()  # Supprimer le fichier temporaire

            if result.returncode == 0:
                # Compter les portraits créés
                if "Portraits créés:" in result.stdout:
                    for line in result.stdout.split('\n'):
                        if "Portraits créés:" in line:
                            self.log(line.strip(), "SUCCESS")
                            break

                self.results["portraits"] = "SUCCESS"
                return True
            else:
                self.results["portraits"] = "ERROR"
                return False

        except Exception as e:
            self.log(f"Erreur réparation portraits: {e}", "ERROR")
            self.results["portraits"] = "ERROR"
            return False

    def fix_multiplayer(self):
        """Réparer le multijoueur"""
        self.print_section("PHASE 3: RÉPARATION SYSTÈME MULTIJOUEUR")
        self.log("Configuration du système réseau...", "FIX")

        try:
            # Créer input simulé
            temp_input = self.base_path / "temp_input.txt"
            temp_input.write_text("O\n")

            with open(temp_input, 'r') as input_file:
                result = subprocess.run(
                    [sys.executable, str(self.scripts["multiplayer"])],
                    cwd=str(self.base_path),
                    stdin=input_file,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

            temp_input.unlink()

            if result.returncode == 0:
                self.log("Configuration réseau ajoutée", "SUCCESS")
                self.results["multiplayer"] = "SUCCESS"
                return True
            else:
                self.results["multiplayer"] = "ERROR"
                return False

        except Exception as e:
            self.log(f"Erreur réparation multijoueur: {e}", "ERROR")
            self.results["multiplayer"] = "ERROR"
            return False

    def run_final_audit(self):
        """Exécuter l'audit final"""
        self.print_section("PHASE 4: AUDIT FINAL")
        self.log("Vérification des réparations...", "SCAN")

        try:
            result = subprocess.run(
                [sys.executable, str(self.scripts["monitor"])],
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                timeout=60
            )

            # Afficher les résultats
            print(result.stdout)

            self.log("Audit final terminé", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Erreur audit final: {e}", "ERROR")
            return False

    def display_summary(self):
        """Afficher le résumé final"""
        self.print_section("RÉSUMÉ DES RÉPARATIONS")

        repairs = {
            "portraits": "Réparation des portraits",
            "multiplayer": "Configuration multijoueur"
        }

        print("╔" + "="*68 + "╗")
        print("║" + " "*20 + "STATUT DES RÉPARATIONS" + " "*25 + "║")
        print("╠" + "="*68 + "╣")

        for key, description in repairs.items():
            status = self.results.get(key, "PENDING")
            if status == "SUCCESS":
                icon = "✅"
                status_text = "RÉUSSI"
            elif status == "ERROR":
                icon = "❌"
                status_text = "ÉCHEC"
            else:
                icon = "⏳"
                status_text = "EN ATTENTE"

            # Formater la ligne
            line = f"║ {icon} {description:<40} {status_text:>23} ║"
            print(line)

        print("╚" + "="*68 + "╝")

    def display_next_steps(self):
        """Afficher les prochaines étapes"""
        print("\n" + "="*70)
        print("🎯 PROCHAINES ÉTAPES RECOMMANDÉES")
        print("="*70)

        print("\n1. 🚀 Lancer le Bug Hunter 24/7")
        print("   → python AUTO_TEST_MINI_WINDOWS.py")
        print("   → Tests automatiques permanents")

        print("\n2. 🌐 Tester le système multijoueur")
        print("   → python matchmaking_server.py (dans un terminal)")
        print("   → Lancez le jeu et testez le mode réseau")

        print("\n3. 📊 Surveiller le dashboard qualité")
        print("   → start ESPORT_QUALITY_DASHBOARD.html")
        print("   → Suivez les métriques en temps réel")

        print("\n4. 🔄 Monitoring continu")
        print("   → python ESPORT_QUALITY_MONITOR.py --continuous")
        print("   → Audit automatique toutes les 60s")

        print("\n" + "="*70)

    def run_all(self):
        """Exécuter toutes les réparations"""
        self.print_header()

        print("⚠️  Ce script va réparer automatiquement:")
        print("   ✓ Tous les portraits manquants")
        print("   ✓ La configuration multijoueur")
        print("   ✓ Et relancer un audit complet")
        print()

        choice = input("🚀 Démarrer la réparation automatique? (O/N): ").strip().upper()

        if choice != 'O':
            print("\n❌ Opération annulée par l'utilisateur\n")
            return

        print("\n🎯 Début de la réparation automatique...\n")
        time.sleep(1)

        # Phase 1: Audit initial
        self.run_initial_audit()
        time.sleep(2)

        # Phase 2: Portraits
        self.fix_portraits()
        time.sleep(2)

        # Phase 3: Multijoueur
        self.fix_multiplayer()
        time.sleep(2)

        # Phase 4: Audit final
        self.run_final_audit()

        # Afficher le résumé
        self.display_summary()

        # Prochaines étapes
        self.display_next_steps()

        print("\n✅ RÉPARATION AUTOMATIQUE TERMINÉE!\n")
        print("🎮 Votre jeu est maintenant plus proche du niveau esport!\n")


def main():
    """Point d'entrée principal"""
    fixer = EsportAutoFixer()
    fixer.run_all()


if __name__ == "__main__":
    main()
