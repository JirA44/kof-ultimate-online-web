#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE - Character Dashboard
Interface de visualisation complète des personnages et leurs coups
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path
import re

class CharacterDashboard:
    """Dashboard pour visualiser tous les personnages et leurs coups"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KOF Ultimate - Character Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0e27')

        self.game_dir = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo kofuo Online kofuo kofuo Online kofuo kofuo")
        self.chars_dir = self.game_dir / "chars"
        self.characters = []

        self.load_characters()
        self.setup_ui()

    def load_characters(self):
        """Charge la liste des personnages depuis select.def"""
        select_file = self.game_dir / "data" / "select.def"

        if not select_file.exists():
            return

        with open(select_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        in_chars_section = False
        for line in lines:
            line = line.strip()

            if line == "[Characters]":
                in_chars_section = True
                continue
            elif line.startswith('['):
                in_chars_section = False

            if in_chars_section and line and not line.startswith(';'):
                char_name = line.split(',')[0].strip()
                if char_name:
                    self.characters.append(char_name)

    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Header
        header = tk.Frame(self.root, bg='#1a1f3a', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="👤 CHARACTER DASHBOARD",
            font=('Consolas', 24, 'bold'),
            fg='#FFD700',
            bg='#1a1f3a'
        )
        title.pack(pady=20)

        # Container principal
        main_container = tk.Frame(self.root, bg='#0a0e27')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Panneau gauche - Liste des personnages
        left_panel = tk.Frame(main_container, bg='#1b263b', width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_panel.pack_propagate(False)

        # Recherche
        search_frame = tk.Frame(left_panel, bg='#1b263b')
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            search_frame,
            text="🔍 Rechercher:",
            font=('Consolas', 10, 'bold'),
            bg='#1b263b',
            fg='#00d9ff'
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_characters)

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Consolas', 10),
            bg='#2d3561',
            fg='#ffffff',
            insertbackground='#ffffff'
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Stats
        stats_frame = tk.Frame(left_panel, bg='#1b263b')
        stats_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.stats_label = tk.Label(
            stats_frame,
            text=f"📊 Total: {len(self.characters)} personnages",
            font=('Consolas', 10, 'bold'),
            bg='#1b263b',
            fg='#00ff88'
        )
        self.stats_label.pack()

        # Liste des personnages avec scrollbar
        list_frame = tk.Frame(left_panel, bg='#1b263b')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.char_listbox = tk.Listbox(
            list_frame,
            font=('Consolas', 10),
            bg='#2d3561',
            fg='#ffffff',
            selectbackground='#00d9ff',
            selectforeground='#000000',
            yscrollcommand=scrollbar.set,
            activestyle='none'
        )
        self.char_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.char_listbox.yview)

        # Remplir la liste
        for char in sorted(self.characters):
            self.char_listbox.insert(tk.END, char)

        # Bind de sélection
        self.char_listbox.bind('<<ListboxSelect>>', self.on_character_select)

        # Boutons d'action
        action_frame = tk.Frame(left_panel, bg='#1b263b')
        action_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(
            action_frame,
            text="🎮 Jouer avec ce perso",
            font=('Consolas', 10, 'bold'),
            bg='#00cc44',
            fg='#000000',
            cursor='hand2',
            command=self.play_character,
            pady=8
        ).pack(fill=tk.X, pady=5)

        tk.Button(
            action_frame,
            text="📁 Ouvrir dossier",
            font=('Consolas', 10),
            bg='#2d3561',
            fg='#c0c0c0',
            cursor='hand2',
            command=self.open_character_folder,
            pady=5
        ).pack(fill=tk.X)

        # Panneau droit - Détails du personnage
        right_panel = tk.Frame(main_container, bg='#0d1b2a')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tabs pour organiser les infos
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Informations générales
        info_tab = tk.Frame(notebook, bg='#0d1b2a')
        notebook.add(info_tab, text="ℹ Informations")

        self.info_text = scrolledtext.ScrolledText(
            info_tab,
            font=('Consolas', 10),
            bg='#1a1f3a',
            fg='#ffffff',
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 2: Coups spéciaux
        moves_tab = tk.Frame(notebook, bg='#0d1b2a')
        notebook.add(moves_tab, text="⚡ Coups Spéciaux")

        self.moves_text = scrolledtext.ScrolledText(
            moves_tab,
            font=('Consolas', 10),
            bg='#1a1f3a',
            fg='#00ff88',
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.moves_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 3: Stats
        stats_tab = tk.Frame(notebook, bg='#0d1b2a')
        notebook.add(stats_tab, text="📊 Statistiques")

        self.stats_text = scrolledtext.ScrolledText(
            stats_tab,
            font=('Consolas', 10),
            bg='#1a1f3a',
            fg='#ffaa00',
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 4: Fichier .def brut
        def_tab = tk.Frame(notebook, bg='#0d1b2a')
        notebook.add(def_tab, text="📄 Fichier .def")

        self.def_text = scrolledtext.ScrolledText(
            def_tab,
            font=('Consolas', 9),
            bg='#1a1f3a',
            fg='#c0c0c0',
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.def_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text=f"⚡ {len(self.characters)} personnages chargés",
            font=('Consolas', 10, 'bold'),
            bg='#1a1f3a',
            fg='#00ff88',
            anchor=tk.W,
            padx=15,
            pady=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def filter_characters(self, *args):
        """Filtre la liste des personnages"""
        search_term = self.search_var.get().lower()

        self.char_listbox.delete(0, tk.END)

        filtered_chars = [c for c in sorted(self.characters) if search_term in c.lower()]

        for char in filtered_chars:
            self.char_listbox.insert(tk.END, char)

        self.stats_label.config(text=f"📊 Affichage: {len(filtered_chars)}/{len(self.characters)} personnages")

    def on_character_select(self, event):
        """Gère la sélection d'un personnage"""
        selection = self.char_listbox.curselection()
        if not selection:
            return

        char_name = self.char_listbox.get(selection[0])
        self.load_character_info(char_name)

    def load_character_info(self, char_name):
        """Charge les informations d'un personnage"""
        self.status_bar.config(text=f"📂 Chargement de {char_name}...")

        char_dir = self.chars_dir / char_name

        if not char_dir.exists():
            self.show_error(f"Dossier non trouvé: {char_dir}")
            return

        # Charger le fichier .def
        def_file = self.find_def_file(char_dir)

        if not def_file:
            self.show_error(f"Fichier .def non trouvé pour {char_name}")
            return

        # Lire le .def
        try:
            with open(def_file, 'r', encoding='utf-8', errors='ignore') as f:
                def_content = f.read()

            self.display_info(char_name, def_content)
            self.display_moves(char_name, char_dir, def_content)
            self.display_stats(char_name, def_content)
            self.display_def_file(def_content)

            self.status_bar.config(text=f"✓ {char_name} chargé")

        except Exception as e:
            self.show_error(f"Erreur lecture: {e}")

    def find_def_file(self, char_dir):
        """Trouve le fichier .def principal du personnage"""
        # Chercher un fichier .def dans le dossier
        def_files = list(char_dir.glob("*.def"))

        if not def_files:
            return None

        # Prioriser le fichier portant le nom du dossier
        char_name = char_dir.name
        for def_file in def_files:
            if def_file.stem.lower() == char_name.lower():
                return def_file

        # Sinon, prendre le premier
        return def_files[0]

    def display_info(self, char_name, def_content):
        """Affiche les informations générales"""
        self.info_text.delete('1.0', tk.END)

        # Extraire les infos du .def
        info_section = self.extract_section(def_content, 'Info')

        self.info_text.insert(tk.END, f"{'='*80}\n", 'header')
        self.info_text.insert(tk.END, f"  {char_name}\n", 'title')
        self.info_text.insert(tk.END, f"{'='*80}\n\n", 'header')

        if info_section:
            for line in info_section.split('\n'):
                if '=' in line and not line.strip().startswith(';'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    if key.lower() in ['name', 'displayname', 'author', 'versiondate']:
                        self.info_text.insert(tk.END, f"  {key:20s}: {value}\n")

        self.info_text.insert(tk.END, f"\n{'─'*80}\n\n")
        self.info_text.insert(tk.END, "📁 Fichiers:\n\n")

        char_dir = self.chars_dir / char_name
        if char_dir.exists():
            # Lister les fichiers principaux
            important_files = {
                '*.def': '🔧 Définition',
                '*.cns': '📜 Constants',
                '*.cmd': '🎮 Commandes',
                '*.st': '🎭 États',
                '*.air': '🎬 Animations',
                '*.sff': '🖼️  Sprites',
                '*.snd': '🔊 Sons',
                '*.act': '🎨 Palettes'
            }

            for pattern, label in important_files.items():
                files = list(char_dir.glob(pattern))
                if files:
                    self.info_text.insert(tk.END, f"  {label:12s}: {len(files)} fichier(s)\n")

    def display_moves(self, char_name, char_dir, def_content):
        """Affiche les coups spéciaux"""
        self.moves_text.delete('1.0', tk.END)

        self.moves_text.insert(tk.END, f"⚡ COUPS SPÉCIAUX - {char_name}\n", 'header')
        self.moves_text.insert(tk.END, f"{'='*80}\n\n", 'header')

        # Chercher le fichier .cmd
        cmd_files = list(char_dir.glob("*.cmd"))

        if not cmd_files:
            self.moves_text.insert(tk.END, "⚠ Fichier .cmd non trouvé\n\n")
            self.moves_text.insert(tk.END, "Les coups spéciaux sont définis dans le fichier .cmd\n")
            return

        cmd_file = cmd_files[0]

        try:
            with open(cmd_file, 'r', encoding='utf-8', errors='ignore') as f:
                cmd_content = f.read()

            # Extraire les commandes
            moves = self.extract_moves(cmd_content)

            if moves:
                for move_name, move_command in moves:
                    self.moves_text.insert(tk.END, f"🔸 {move_name}\n")
                    self.moves_text.insert(tk.END, f"   Command: {move_command}\n\n")
            else:
                self.moves_text.insert(tk.END, "Aucun coup spécial trouvé dans le fichier .cmd\n")

        except Exception as e:
            self.moves_text.insert(tk.END, f"✗ Erreur lecture .cmd: {e}\n")

    def extract_moves(self, cmd_content):
        """Extrait les coups spéciaux du fichier .cmd"""
        moves = []

        # Pattern pour trouver les définitions de coups
        # Format: [Command]
        #         name = "nom_du_coup"
        #         command = ~D, DF, F, a

        lines = cmd_content.split('\n')
        current_name = None
        current_command = None

        for line in lines:
            line = line.strip()

            if line.startswith('name') and '=' in line:
                current_name = line.split('=', 1)[1].strip().strip('"\'')

            elif line.startswith('command') and '=' in line and current_name:
                current_command = line.split('=', 1)[1].strip()

                # Ne garder que les coups avec des directions (pas les simples boutons)
                if any(d in current_command for d in ['D,', 'F,', 'B,', 'U,', 'DF', 'DB', 'UF', 'UB']):
                    moves.append((current_name, current_command))

                current_name = None
                current_command = None

        return moves[:30]  # Limiter à 30 coups pour ne pas surcharger

    def display_stats(self, char_name, def_content):
        """Affiche les statistiques"""
        self.stats_text.delete('1.0', tk.END)

        self.stats_text.insert(tk.END, f"📊 STATISTIQUES - {char_name}\n", 'header')
        self.stats_text.insert(tk.END, f"{'='*80}\n\n", 'header')

        # Extraire les sections [Data] et [Size]
        data_section = self.extract_section(def_content, 'Data')
        size_section = self.extract_section(def_content, 'Size')

        if data_section:
            self.stats_text.insert(tk.END, "⚔️  Données de Combat:\n\n")

            stats_to_show = ['life', 'power', 'attack', 'defence', 'fall.defence_up', 'liedown.time', 'airjuggle', 'sparkno', 'guard.sparkno', 'ko.echo']

            for line in data_section.split('\n'):
                if '=' in line and not line.strip().startswith(';'):
                    key, value = line.split('=', 1)
                    key = key.strip().lower()
                    value = value.split(';')[0].strip()  # Enlever les commentaires

                    if key in stats_to_show:
                        self.stats_text.insert(tk.END, f"  {key:20s}: {value}\n")

        if size_section:
            self.stats_text.insert(tk.END, f"\n{'─'*80}\n\n")
            self.stats_text.insert(tk.END, "📏 Dimensions:\n\n")

            for line in size_section.split('\n'):
                if '=' in line and not line.strip().startswith(';'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.split(';')[0].strip()

                    self.stats_text.insert(tk.END, f"  {key:20s}: {value}\n")

    def display_def_file(self, def_content):
        """Affiche le contenu brut du fichier .def"""
        self.def_text.delete('1.0', tk.END)
        self.def_text.insert(tk.END, def_content)

    def extract_section(self, content, section_name):
        """Extrait une section d'un fichier .def/.cmd"""
        pattern = rf'\[{section_name}\](.*?)(?=\[|$)'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)

        if match:
            return match.group(1).strip()

        return None

    def show_error(self, message):
        """Affiche un message d'erreur"""
        self.info_text.delete('1.0', tk.END)
        self.info_text.insert(tk.END, f"✗ Erreur:\n\n{message}")

        self.moves_text.delete('1.0', tk.END)
        self.stats_text.delete('1.0', tk.END)
        self.def_text.delete('1.0', tk.END)

    def play_character(self):
        """Lance le jeu avec ce personnage"""
        selection = self.char_listbox.curselection()
        if not selection:
            self.status_bar.config(text="⚠ Sélectionnez un personnage d'abord")
            return

        char_name = self.char_listbox.get(selection[0])
        self.status_bar.config(text=f"🎮 Fonctionnalité à venir: Jouer avec {char_name}")

    def open_character_folder(self):
        """Ouvre le dossier du personnage"""
        selection = self.char_listbox.curselection()
        if not selection:
            self.status_bar.config(text="⚠ Sélectionnez un personnage d'abord")
            return

        char_name = self.char_listbox.get(selection[0])
        char_dir = self.chars_dir / char_name

        if char_dir.exists():
            import os
            os.startfile(str(char_dir))
            self.status_bar.config(text=f"📁 Dossier ouvert: {char_name}")
        else:
            self.status_bar.config(text=f"✗ Dossier non trouvé: {char_name}")

    def run(self):
        """Lance le dashboard"""
        self.root.mainloop()

def main():
    """Point d'entrée principal"""
    dashboard = CharacterDashboard()
    dashboard.run()

if __name__ == '__main__':
    main()
