#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE - Auto Test Infini
Lance le jeu + IAs en boucle et détecte TOUTES les erreurs
"""

import subprocess
import time
import win32gui
import pyautogui
from pathlib import Path
from datetime import datetime
import random

class InfiniteAutoTester:
    """Teste le jeu en boucle infinie avec clics automatiques"""

    def __init__(self):
        self.game_dir = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo kofuo Online kofuo kofuo Online kofuo kofuo")
        self.exe_path = self.game_dir / "KOF_Ultimate_Online.exe"
        self.process = None
        self.window_handle = None
        self.iteration = 0
        self.total_clicks = 0
        self.errors_log = self.game_dir / "errors_auto_detected.txt"

    def log(self, message):
        """Log avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[{timestamp}] {message}"
        print(msg)

        # Logger dans fichier
        with open(self.errors_log, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')

    def find_game_window(self):
        """Trouve la fenêtre du jeu"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "mugen" in title.lower() or "kof" in title.lower():
                    windows.append(hwnd)
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)

        if windows:
            self.window_handle = windows[0]
            return True
        return False

    def focus_and_click(self, key):
        """Focus et clique"""
        if self.window_handle:
            try:
                win32gui.SetForegroundWindow(self.window_handle)
                time.sleep(0.1)
                pyautogui.press(key)
                self.total_clicks += 1
                return True
            except:
                return False
        return False

    def launch_game(self):
        """Lance le jeu"""
        self.log(f"\n🚀 LANCEMENT #{self.iteration} du jeu...")

        try:
            self.process = subprocess.Popen(
                [str(self.exe_path)],
                cwd=str(self.game_dir)
            )

            self.log(f"✅ Jeu lancé (PID: {self.process.pid})")

            # Attendre la fenêtre
            for i in range(30):
                time.sleep(0.5)
                if self.find_game_window():
                    self.log("✅ Fenêtre trouvée!")
                    return True

            self.log("❌ Fenêtre non trouvée")
            return False

        except Exception as e:
            self.log(f"❌ ERREUR lancement: {e}")
            return False

    def random_navigation_sequence(self):
        """Séquence de navigation aléatoire"""
        self.log("\n🎯 Séquence de navigation aléatoire...")

        # Passer l'écran de titre
        time.sleep(3)
        self.focus_and_click('enter')
        time.sleep(1.5)

        # Navigation aléatoire intense
        actions = []

        # 1. Explorer les menus
        for _ in range(random.randint(3, 8)):
            actions.append(('down', 0.4))
            actions.append(('enter', 1.5))
            actions.append(('escape', 1))

        # 2. Entrer en mode arcade et tester persos
        actions.append(('enter', 2))  # Mode Arcade

        # 3. Naviguer dans la grille de persos
        for _ in range(random.randint(15, 30)):
            direction = random.choice(['up', 'down', 'left', 'right'])
            actions.append((direction, 0.3))

        # 4. Sélectionner un perso
        actions.append(('enter', 1.5))
        actions.append(('enter', 2))  # Confirmer

        # 5. Attendre le combat
        time.sleep(3)

        # 6. Spam de touches en combat
        combat_keys = ['a', 's', 'd', 'j', 'k', 'l', 'space']
        for _ in range(random.randint(20, 40)):
            key = random.choice(combat_keys)
            actions.append((key, 0.2))

        # 7. Quitter
        for _ in range(5):
            actions.append(('escape', 0.8))

        # Exécuter toutes les actions
        for i, (key, wait) in enumerate(actions):
            if not self.find_game_window():
                self.log(f"⚠️ Jeu fermé à l'action {i}/{len(actions)}")
                return False

            self.focus_and_click(key)
            self.log(f"  [{i+1}/{len(actions)}] Touche: {key} | Total clics: {self.total_clicks}")
            time.sleep(wait)

        return True

    def check_for_errors(self):
        """Vérifie les erreurs dans mugen.log"""
        mugen_log = self.game_dir / "mugen.log"

        if not mugen_log.exists():
            return []

        errors = []

        with open(mugen_log, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['error', 'failed', 'crash', 'invalid', 'warning']):
                errors.append(line.strip())

        return errors

    def run_infinite_test(self):
        """Lance les tests en boucle infinie"""
        self.log("\n" + "=" * 80)
        self.log("  KOF ULTIMATE - AUTO TEST INFINI")
        self.log("  Les IAs vont tester en boucle et trouver TOUS les bugs!")
        self.log("=" * 80)

        while True:
            self.iteration += 1

            self.log("\n" + "=" * 80)
            self.log(f"  ITÉRATION #{self.iteration}")
            self.log("=" * 80)

            # Lancer le jeu
            if not self.launch_game():
                self.log("❌ Échec lancement, on réessaie dans 5s...")
                time.sleep(5)
                continue

            # Navigation aléatoire
            success = self.random_navigation_sequence()

            # Vérifier les erreurs
            errors = self.check_for_errors()

            if errors:
                self.log(f"\n⚠️ {len(errors)} ERREURS DÉTECTÉES:")
                for error in errors[:10]:  # Max 10 premières erreurs
                    self.log(f"  - {error}")

            # Rapport itération
            self.log(f"\n📊 STATS ITÉRATION #{self.iteration}:")
            self.log(f"  Clics cette itération: {self.total_clicks}")
            self.log(f"  Erreurs trouvées: {len(errors)}")
            self.log(f"  Status: {'✅ OK' if success else '❌ Problème'}")

            # Fermer le jeu
            try:
                if self.process:
                    self.process.terminate()
                    self.process.wait(timeout=3)
            except:
                try:
                    self.process.kill()
                except:
                    pass

            # Pause entre iterations
            self.log(f"\n⏸️ Pause 5s avant itération #{self.iteration + 1}...")
            time.sleep(5)

def main():
    """Point d'entrée"""
    tester = InfiniteAutoTester()
    tester.run_infinite_test()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Arrêt manuel - Tests terminés")
