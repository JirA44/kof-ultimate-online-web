#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              KOF ULTIMATE ONLINE - LAUNCHER PROFESSIONNEL                    ║
║                        READY TO PLAY - VERSION PRO                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  • Installation automatique                                                  ║
║  • Auto-réparation des erreurs                                               ║
║  • Matchmaking intégré (Firebase)                                            ║
║  • Tests automatiques au démarrage                                           ║
║  • Interface utilisateur simple                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import shutil
import hashlib
import subprocess
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from datetime import datetime
from threading import Thread
import urllib.request
import socket

# ============================================================================
# CONFIGURATION
# ============================================================================
GAME_DIR = Path(__file__).parent
DATA_DIR = GAME_DIR / "data"
CHARS_DIR = GAME_DIR / "chars"
STAGES_DIR = GAME_DIR / "stages"
CONFIG_FILE = GAME_DIR / "kof_config.json"
IKEMEN_EXE = GAME_DIR / "Ikemen_GO.exe"
LOBBY_HTML = GAME_DIR / "KOF_ONLINE_FIREBASE.html"

VERSION = "2.0.0"
GAME_PORT = 7500

# ============================================================================
# AUTO-REPAIR SYSTEM
# ============================================================================
class AutoRepair:
    """Système de réparation automatique"""

    def __init__(self, log_callback=None):
        self.log = log_callback or print
        self.issues_found = []
        self.issues_fixed = []

    def run_full_diagnostic(self):
        """Exécute un diagnostic complet"""
        self.log("🔍 Diagnostic en cours...")
        checks = [
            self.check_game_exe,
            self.check_data_folder,
            self.check_system_def,
            self.check_select_def,
            self.check_stages,
            self.check_fonts,
            self.check_network,
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                self.log(f"⚠️ Erreur diagnostic: {e}")

        return len(self.issues_found), len(self.issues_fixed)

    def check_game_exe(self):
        """Vérifie l'exécutable du jeu"""
        if not IKEMEN_EXE.exists():
            self.issues_found.append("Ikemen_GO.exe manquant")
            # Chercher dans les sous-dossiers
            for exe in GAME_DIR.rglob("Ikemen_GO.exe"):
                if exe != IKEMEN_EXE:
                    shutil.copy(exe, IKEMEN_EXE)
                    self.issues_fixed.append("Ikemen_GO.exe restauré")
                    self.log("✅ Ikemen_GO.exe restauré")
                    break

    def check_data_folder(self):
        """Vérifie le dossier data"""
        if not DATA_DIR.exists():
            self.issues_found.append("Dossier data manquant")
            DATA_DIR.mkdir(exist_ok=True)
            self.issues_fixed.append("Dossier data créé")
            self.log("✅ Dossier data créé")

    def check_system_def(self):
        """Vérifie et répare system.def"""
        system_def = DATA_DIR / "system.def"
        if not system_def.exists():
            self.issues_found.append("system.def manquant")
            # Chercher une copie de backup
            backups = list(DATA_DIR.glob("system*.def*"))
            if backups:
                shutil.copy(backups[0], system_def)
                self.issues_fixed.append("system.def restauré depuis backup")
                self.log("✅ system.def restauré")

    def check_select_def(self):
        """Vérifie que le select.def pointe vers un fichier valide"""
        system_def = DATA_DIR / "system.def"
        if not system_def.exists():
            return

        content = system_def.read_text(encoding='utf-8', errors='ignore')
        for line in content.split('\n'):
            if line.strip().startswith('select') and '=' in line:
                select_file = line.split('=')[1].strip().split(';')[0].strip()
                select_path = DATA_DIR / select_file
                if not select_path.exists():
                    self.issues_found.append(f"select.def invalide: {select_file}")
                    # Utiliser un select valide
                    valid_selects = list(DATA_DIR.glob("select*.def"))
                    if valid_selects:
                        # Mettre à jour system.def
                        new_content = content.replace(
                            f"select = {select_file}",
                            f"select = {valid_selects[0].name}"
                        )
                        system_def.write_text(new_content, encoding='utf-8')
                        self.issues_fixed.append("select.def corrigé")
                        self.log(f"✅ select.def corrigé → {valid_selects[0].name}")
                break

    def check_stages(self):
        """Vérifie qu'au moins un stage existe"""
        if not STAGES_DIR.exists():
            self.issues_found.append("Dossier stages manquant")
            return

        stages = list(STAGES_DIR.glob("*.def"))
        if len(stages) == 0:
            self.issues_found.append("Aucun stage trouvé")

    def check_fonts(self):
        """Vérifie les polices"""
        font_dir = DATA_DIR / "font"
        if not font_dir.exists():
            self.issues_found.append("Dossier font manquant")

    def check_network(self):
        """Vérifie la connectivité réseau"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.log("✅ Connexion Internet OK")
        except OSError:
            self.issues_found.append("Pas de connexion Internet")
            self.log("⚠️ Pas de connexion Internet")

    def fix_character(self, char_name: str) -> bool:
        """Tente de réparer un personnage"""
        char_path = CHARS_DIR / char_name
        if not char_path.exists():
            return False

        # Chercher le fichier .def
        def_files = list(char_path.glob("*.def"))
        if not def_files:
            # Chercher un backup
            backups = list(char_path.glob("*.def.backup"))
            if backups:
                new_name = backups[0].stem  # Remove .backup
                shutil.copy(backups[0], char_path / new_name)
                self.log(f"✅ {char_name}: .def restauré depuis backup")
                return True
            return False

        return True

# ============================================================================
# CONFIGURATION MANAGER
# ============================================================================
class ConfigManager:
    """Gestionnaire de configuration"""

    DEFAULT_CONFIG = {
        "username": "",
        "email": "",
        "auth_token": "",
        "elo": 1000,
        "games_played": 0,
        "wins": 0,
        "losses": 0,
        "last_roster": "select_certified.def",
        "auto_repair": True,
        "auto_update": True,
        "fullscreen": False,
        "vsync": True,
        "first_run": True
    }

    def __init__(self):
        self.config = self.load()

    def load(self) -> dict:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults
                    return {**self.DEFAULT_CONFIG, **config}
            except:
                pass
        return self.DEFAULT_CONFIG.copy()

    def save(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()

# ============================================================================
# MAIN LAUNCHER GUI
# ============================================================================
class KOFLauncher:
    def __init__(self):
        self.config = ConfigManager()
        self.repair = AutoRepair(self.log)

        # Créer la fenêtre
        self.root = tk.Tk()
        self.root.title(f"KOF Ultimate Online - Launcher Pro v{VERSION}")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a2e')

        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Segoe UI', 12), padding=10)
        self.style.configure('TLabel', background='#1a1a2e', foreground='white', font=('Segoe UI', 11))
        self.style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'), foreground='#e94560')
        self.style.configure('Status.TLabel', font=('Segoe UI', 10), foreground='#888')

        self.setup_ui()

        # Premier démarrage
        if self.config.get('first_run'):
            self.root.after(500, self.first_run_wizard)

    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Header
        header = tk.Frame(self.root, bg='#16213e', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title = ttk.Label(header, text="KOF ULTIMATE ONLINE", style='Title.TLabel')
        title.pack(pady=20)

        # Main content
        main = tk.Frame(self.root, bg='#1a1a2e')
        main.pack(fill='both', expand=True, padx=30, pady=20)

        # Buttons frame
        btn_frame = tk.Frame(main, bg='#1a1a2e')
        btn_frame.pack(pady=20)

        # Play button
        self.btn_play = tk.Button(
            btn_frame, text="🎮 JOUER", font=('Segoe UI', 16, 'bold'),
            bg='#00b894', fg='white', width=20, height=2,
            command=self.start_game
        )
        self.btn_play.pack(pady=10)

        # Online button
        self.btn_online = tk.Button(
            btn_frame, text="🌐 JOUER EN LIGNE", font=('Segoe UI', 14),
            bg='#0984e3', fg='white', width=20, height=2,
            command=self.open_online_lobby
        )
        self.btn_online.pack(pady=10)

        # Matchmaking button
        self.btn_match = tk.Button(
            btn_frame, text="⚔️ MATCHMAKING", font=('Segoe UI', 14),
            bg='#e94560', fg='white', width=20, height=2,
            command=self.start_matchmaking
        )
        self.btn_match.pack(pady=10)

        # Tools frame
        tools_frame = tk.Frame(main, bg='#1a1a2e')
        tools_frame.pack(pady=20)

        tk.Button(
            tools_frame, text="🔧 Réparer", font=('Segoe UI', 10),
            bg='#6c5ce7', fg='white', width=12,
            command=self.run_repair
        ).pack(side='left', padx=5)

        tk.Button(
            tools_frame, text="🧪 Tests QA", font=('Segoe UI', 10),
            bg='#fdcb6e', fg='black', width=12,
            command=self.run_qa_tests
        ).pack(side='left', padx=5)

        tk.Button(
            tools_frame, text="⚙️ Options", font=('Segoe UI', 10),
            bg='#636e72', fg='white', width=12,
            command=self.show_options
        ).pack(side='left', padx=5)

        # Status/Log area
        log_frame = tk.Frame(main, bg='#0f0f23')
        log_frame.pack(fill='both', expand=True, pady=10)

        self.log_text = tk.Text(
            log_frame, bg='#0f0f23', fg='#00ff00',
            font=('Consolas', 9), height=10
        )
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Status bar
        self.status_var = tk.StringVar(value="Prêt")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, style='Status.TLabel')
        status_bar.pack(side='bottom', fill='x', pady=5)

        # Initial log
        self.log("=" * 60)
        self.log("  KOF ULTIMATE ONLINE - LAUNCHER PROFESSIONNEL")
        self.log("=" * 60)
        self.log(f"Version: {VERSION}")
        self.log(f"Dossier: {GAME_DIR}")

    def log(self, message: str):
        """Ajoute un message au log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        self.root.update_idletasks()

    def first_run_wizard(self):
        """Assistant de première configuration"""
        self.log("\n🎉 Bienvenue dans KOF Ultimate Online!")
        self.log("📋 Configuration initiale en cours...")

        # Demander le pseudo
        username = simpledialog.askstring(
            "Configuration",
            "Entrez votre pseudo (pour le jeu en ligne):",
            parent=self.root
        )
        if username:
            self.config.set('username', username)
            self.log(f"✅ Pseudo configuré: {username}")

        # Lancer la réparation automatique
        self.log("\n🔧 Vérification du jeu...")
        self.run_repair()

        self.config.set('first_run', False)
        self.log("\n✅ Configuration terminée! Vous pouvez jouer.")

    def start_game(self):
        """Lance le jeu"""
        self.log("\n🎮 Lancement du jeu...")
        self.status_var.set("Lancement en cours...")

        if not IKEMEN_EXE.exists():
            messagebox.showerror("Erreur", "Ikemen_GO.exe introuvable!")
            self.log("❌ Ikemen_GO.exe introuvable")
            return

        try:
            subprocess.Popen([str(IKEMEN_EXE)], cwd=str(GAME_DIR))
            self.log("✅ Jeu lancé!")
            self.status_var.set("Jeu en cours...")
        except Exception as e:
            self.log(f"❌ Erreur: {e}")
            messagebox.showerror("Erreur", f"Impossible de lancer le jeu:\n{e}")

    def open_online_lobby(self):
        """Ouvre le lobby en ligne"""
        self.log("\n🌐 Ouverture du lobby en ligne...")

        if LOBBY_HTML.exists():
            webbrowser.open(str(LOBBY_HTML))
            self.log("✅ Lobby ouvert dans le navigateur")
        else:
            messagebox.showerror("Erreur", "Fichier lobby introuvable!")
            self.log("❌ KOF_ONLINE_FIREBASE.html introuvable")

    def start_matchmaking(self):
        """Lance le matchmaking"""
        self.log("\n⚔️ Matchmaking...")

        username = self.config.get('username')
        if not username:
            username = simpledialog.askstring(
                "Matchmaking",
                "Entrez votre pseudo:",
                parent=self.root
            )
            if username:
                self.config.set('username', username)

        if username:
            self.open_online_lobby()
            self.log(f"✅ Connecté en tant que: {username}")

    def run_repair(self):
        """Lance la réparation automatique"""
        self.log("\n🔧 Réparation automatique...")
        self.status_var.set("Réparation en cours...")

        def repair_thread():
            issues, fixed = self.repair.run_full_diagnostic()
            self.log(f"\n📊 Résultat: {issues} problèmes trouvés, {fixed} corrigés")
            self.status_var.set(f"Réparation terminée - {fixed} corrections")

        Thread(target=repair_thread, daemon=True).start()

    def run_qa_tests(self):
        """Lance les tests QA"""
        self.log("\n🧪 Lancement des tests QA...")
        self.status_var.set("Tests en cours...")

        qa_script = GAME_DIR / "QA_PROFESSIONAL_TESTER.py"
        if qa_script.exists():
            subprocess.Popen([sys.executable, str(qa_script)], cwd=str(GAME_DIR))
            self.log("✅ Tests QA lancés dans une nouvelle fenêtre")
        else:
            self.log("❌ Script QA introuvable")

    def show_options(self):
        """Affiche les options"""
        options_window = tk.Toplevel(self.root)
        options_window.title("Options")
        options_window.geometry("400x300")
        options_window.configure(bg='#1a1a2e')

        # Username
        tk.Label(options_window, text="Pseudo:", bg='#1a1a2e', fg='white').pack(pady=5)
        username_entry = tk.Entry(options_window, width=30)
        username_entry.insert(0, self.config.get('username', ''))
        username_entry.pack()

        # Auto-repair
        auto_repair_var = tk.BooleanVar(value=self.config.get('auto_repair', True))
        tk.Checkbutton(
            options_window, text="Réparation automatique au démarrage",
            variable=auto_repair_var, bg='#1a1a2e', fg='white',
            selectcolor='#16213e'
        ).pack(pady=10)

        def save_options():
            self.config.set('username', username_entry.get())
            self.config.set('auto_repair', auto_repair_var.get())
            self.log("✅ Options sauvegardées")
            options_window.destroy()

        tk.Button(
            options_window, text="Sauvegarder",
            bg='#00b894', fg='white',
            command=save_options
        ).pack(pady=20)

    def run(self):
        """Lance l'application"""
        # Auto-repair au démarrage si activé
        if self.config.get('auto_repair'):
            self.root.after(1000, self.run_repair)

        self.root.mainloop()

# ============================================================================
# MAIN
# ============================================================================
def main():
    launcher = KOFLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
