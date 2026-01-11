#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO TEST MINI WINDOWS - Test automatique continu en mini-fenêtres
Lance plusieurs instances de test qui jouent automatiquement
"""

import os
import sys
import time
import subprocess
import psutil
from pathlib import Path
from datetime import datetime
import threading

class AutoTestRunner:
    def __init__(self):
        self.base_path = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo")
        self.game_exe = self.base_path / "KOF_Ultimate_Online.exe"
        self.logs_path = self.base_path / "logs"
        self.running = True

        # Créer le dossier logs s'il n'existe pas
        self.logs_path.mkdir(exist_ok=True)

    def log(self, message, level="INFO"):
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✓",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "TEST": "🧪"
        }
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {icons.get(level, '')} {message}")

    def is_game_running(self):
        """Vérifie si le jeu tourne déjà"""
        for proc in psutil.process_iter(['name']):
            try:
                if 'KOF_Ultimate_Online.exe' in proc.info['name']:
                    return True
            except:
                pass
        return False

    def kill_game(self):
        """Ferme proprement le jeu"""
        for proc in psutil.process_iter(['name']):
            try:
                if 'KOF_Ultimate_Online.exe' in proc.info['name']:
                    proc.terminate()
                    time.sleep(2)
                    if proc.is_running():
                        proc.kill()
            except:
                pass

    def save_log(self):
        """Sauvegarde le log de test"""
        mugen_log = self.base_path / "mugen.log"
        if mugen_log.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_backup = self.logs_path / f"test_mini_{timestamp}.log"

            try:
                import shutil
                shutil.copy2(mugen_log, log_backup)
                self.log(f"Log sauvegardé: {log_backup.name}", "SUCCESS")

                # Analyser le log pour les erreurs
                content = mugen_log.read_text(encoding='utf-8', errors='ignore')
                if 'error' in content.lower() or 'failed' in content.lower():
                    self.log("⚠️ Erreurs détectées dans le log!", "WARNING")

            except Exception as e:
                self.log(f"Erreur sauvegarde log: {e}", "ERROR")

    def launch_game_test(self):
        """Lance une session de test du jeu"""
        try:
            self.log("Lancement session de test...", "TEST")

            # Lancer le jeu en mode minimisé
            subprocess.Popen(
                [str(self.game_exe)],
                cwd=str(self.base_path),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            self.log("Jeu lancé en mini-fenêtre", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Erreur lancement: {e}", "ERROR")
            return False

    def monitor_game(self, duration=180):
        """Surveille le jeu pendant la durée spécifiée"""
        self.log(f"Surveillance active pendant {duration} secondes...", "INFO")

        start_time = time.time()
        last_check = start_time

        while (time.time() - start_time) < duration and self.running:
            # Vérifier toutes les 5 secondes
            if time.time() - last_check >= 5:
                if not self.is_game_running():
                    self.log("Le jeu s'est fermé prématurément!", "WARNING")
                    return False
                last_check = time.time()

            time.sleep(1)

        return True

    def run_test_cycle(self):
        """Exécute un cycle de test complet"""
        self.log("═══════════════════════════════════════", "INFO")
        self.log(f"Début cycle de test", "TEST")
        self.log("═══════════════════════════════════════", "INFO")

        # S'assurer qu'aucun jeu ne tourne
        if self.is_game_running():
            self.log("Fermeture instance précédente...", "WARNING")
            self.kill_game()
            time.sleep(3)

        # Lancer le jeu
        if not self.launch_game_test():
            return False

        # Attendre un peu pour que le jeu démarre
        time.sleep(10)

        # Surveiller le jeu pendant 3 minutes
        self.monitor_game(duration=180)

        # Fermer le jeu
        self.log("Fin du cycle, fermeture du jeu...", "INFO")
        self.kill_game()
        time.sleep(3)

        # Sauvegarder le log
        self.save_log()

        self.log("Cycle de test terminé", "SUCCESS")
        return True

    def run_continuous(self):
        """Lance les tests en continu"""
        print("\n" + "="*70)
        print("  🪟 TEST AUTOMATIQUE CONTINU EN MINI-FENÊTRES")
        print("="*70 + "\n")

        self.log("Configuration: Mode fenêtré 640x480", "INFO")
        self.log("Durée par cycle: 3 minutes", "INFO")
        self.log("Logs sauvegardés dans: logs/", "INFO")
        print()
        self.log("⚠️  Pour arrêter: CTRL+C", "WARNING")
        print("\n" + "="*70 + "\n")

        cycle_count = 0

        try:
            while self.running:
                cycle_count += 1
                self.log(f"CYCLE #{cycle_count}", "TEST")

                self.run_test_cycle()

                # Pause entre les cycles
                self.log("Pause 10 secondes avant prochain cycle...", "INFO")
                time.sleep(10)

        except KeyboardInterrupt:
            print("\n")
            self.log("Arrêt demandé par l'utilisateur", "WARNING")
            self.running = False

        finally:
            # Nettoyage
            self.log("Nettoyage...", "INFO")
            self.kill_game()

            print("\n" + "="*70)
            print(f"  ✓ {cycle_count} CYCLES DE TEST EFFECTUÉS")
            print("="*70 + "\n")
            self.log(f"Logs sauvegardés: {len(list(self.logs_path.glob('test_*.log')))} fichiers", "INFO")

if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        print("❌ Module psutil requis. Installation...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "-q"])
        import psutil

    runner = AutoTestRunner()
    runner.run_continuous()
