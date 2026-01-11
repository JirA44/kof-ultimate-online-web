"""
KOF Ultimate - Character Balancer
Outil d'équilibrage automatique des personnages
"""
import os
import re
import json
from pathlib import Path
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class CharacterBalancer:
    """Analyseur et équilibreur de personnages MUGEN"""

    def __init__(self):
        self.game_path = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo kofuo Online kofuo kofuo Online kofuo kofuo")
        self.chars_path = self.game_path / "chars"
        self.characters = []
        self.stats = {}

        # Valeurs cibles pour l'équilibrage
        self.target_stats = {
            'life': 1000,
            'attack': 100,
            'defence': 100,
            'walk.fwd': 2.5,
            'walk.back': -2.2,
            'run.fwd.x': 4.5,
            'run.fwd.y': 0,
            'run.back.x': -4.5,
            'run.back.y': -4,
            'jump.neu.y': -8.4,
            'jump.back.x': -2.55,
            'jump.fwd.x': 2.5
        }

    def scan_characters(self):
        """Scanne tous les personnages"""
        if not self.chars_path.exists():
            return []

        chars = []
        for char_dir in self.chars_path.iterdir():
            if char_dir.is_dir():
                # Chercher le fichier .def
                def_files = list(char_dir.glob("*.def"))
                if def_files:
                    chars.append({
                        'name': char_dir.name,
                        'path': char_dir,
                        'def_file': def_files[0]
                    })

        self.characters = chars
        return chars

    def parse_def_file(self, def_file):
        """Parse un fichier .def pour trouver le fichier .cns"""
        cns_file = None
        try:
            with open(def_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.strip().startswith('st ='):
                        # st = character.cns
                        cns_name = line.split('=')[1].strip()
                        cns_file = def_file.parent / cns_name
                        break
        except Exception as e:
            print(f"Erreur lecture {def_file}: {e}")

        return cns_file

    def parse_cns_file(self, cns_file):
        """Parse un fichier .cns pour extraire les stats"""
        stats = {}

        if not cns_file or not cns_file.exists():
            return stats

        try:
            with open(cns_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                # Section [Data]
                data_section = re.search(r'\[Data\](.*?)(?=\[|\Z)', content, re.DOTALL | re.IGNORECASE)
                if data_section:
                    data_content = data_section.group(1)

                    # Extraire life
                    life_match = re.search(r'life\s*=\s*(\d+)', data_content, re.IGNORECASE)
                    if life_match:
                        stats['life'] = int(life_match.group(1))

                    # Extraire attack
                    attack_match = re.search(r'attack\s*=\s*(\d+)', data_content, re.IGNORECASE)
                    if attack_match:
                        stats['attack'] = int(attack_match.group(1))

                    # Extraire defence
                    defence_match = re.search(r'defence\s*=\s*(\d+)', data_content, re.IGNORECASE)
                    if defence_match:
                        stats['defence'] = int(defence_match.group(1))

                # Section [Velocity]
                velocity_section = re.search(r'\[Velocity\](.*?)(?=\[|\Z)', content, re.DOTALL | re.IGNORECASE)
                if velocity_section:
                    vel_content = velocity_section.group(1)

                    # Extraire vitesses
                    vel_params = ['walk.fwd', 'walk.back', 'run.fwd.x', 'run.fwd.y',
                                  'run.back.x', 'run.back.y', 'jump.neu.y', 'jump.back.x', 'jump.fwd.x']

                    for param in vel_params:
                        pattern = param.replace('.', r'\.') + r'\s*=\s*([-\d.]+)'
                        match = re.search(pattern, vel_content, re.IGNORECASE)
                        if match:
                            stats[param] = float(match.group(1))

        except Exception as e:
            print(f"Erreur parse {cns_file}: {e}")

        return stats

    def analyze_all_characters(self):
        """Analyse tous les personnages"""
        self.scan_characters()
        print(f"Analyse de {len(self.characters)} personnages...")

        for char in self.characters:
            cns_file = self.parse_def_file(char['def_file'])
            stats = self.parse_cns_file(cns_file)

            self.stats[char['name']] = {
                'stats': stats,
                'cns_file': cns_file,
                'balanced': False
            }

        return self.stats

    def calculate_balance_score(self, stats):
        """Calcule un score d'équilibre (0-100)"""
        if not stats:
            return 0

        score = 100
        penalties = 0

        # Vérifier life
        if 'life' in stats:
            life_diff = abs(stats['life'] - self.target_stats['life'])
            penalties += min(life_diff / 10, 30)  # Max 30 points de pénalité

        # Vérifier attack
        if 'attack' in stats:
            attack_diff = abs(stats['attack'] - self.target_stats['attack'])
            penalties += min(attack_diff / 5, 30)

        # Vérifier defence
        if 'defence' in stats:
            defence_diff = abs(stats['defence'] - self.target_stats['defence'])
            penalties += min(defence_diff / 5, 30)

        return max(0, score - penalties)

    def balance_character(self, char_name):
        """Équilibre un personnage spécifique"""
        if char_name not in self.stats:
            return False

        char_data = self.stats[char_name]
        cns_file = char_data['cns_file']

        if not cns_file or not cns_file.exists():
            return False

        try:
            # Lire le fichier
            with open(cns_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Créer une sauvegarde
            backup_file = cns_file.with_suffix('.cns.backup')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Appliquer les modifications
            modified = False

            # Ajuster life
            if 'life' in char_data['stats']:
                current_life = char_data['stats']['life']
                if abs(current_life - self.target_stats['life']) > 100:
                    content = re.sub(
                        r'(life\s*=\s*)\d+',
                        f'life = {self.target_stats["life"]}',
                        content,
                        flags=re.IGNORECASE
                    )
                    modified = True

            # Ajuster attack
            if 'attack' in char_data['stats']:
                current_attack = char_data['stats']['attack']
                if abs(current_attack - self.target_stats['attack']) > 20:
                    content = re.sub(
                        r'(attack\s*=\s*)\d+',
                        f'attack = {self.target_stats["attack"]}',
                        content,
                        flags=re.IGNORECASE
                    )
                    modified = True

            # Ajuster defence
            if 'defence' in char_data['stats']:
                current_defence = char_data['stats']['defence']
                if abs(current_defence - self.target_stats['defence']) > 20:
                    content = re.sub(
                        r'(defence\s*=\s*)\d+',
                        f'defence = {self.target_stats["defence"]}',
                        content,
                        flags=re.IGNORECASE
                    )
                    modified = True

            if modified:
                # Écrire les modifications
                with open(cns_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                char_data['balanced'] = True
                return True

        except Exception as e:
            print(f"Erreur équilibrage {char_name}: {e}")
            return False

        return False

    def balance_all_characters(self, progress_callback=None):
        """Équilibre tous les personnages"""
        balanced_count = 0
        total = len(self.stats)

        for i, char_name in enumerate(self.stats.keys()):
            if progress_callback:
                progress_callback(i + 1, total, char_name)

            if self.balance_character(char_name):
                balanced_count += 1

        return balanced_count

    def generate_report(self):
        """Génère un rapport d'équilibrage"""
        report = []
        report.append("=" * 60)
        report.append("RAPPORT D'ÉQUILIBRAGE DES PERSONNAGES")
        report.append("=" * 60)
        report.append("")

        for char_name, data in sorted(self.stats.items()):
            stats = data['stats']
            score = self.calculate_balance_score(stats)

            report.append(f"Personnage: {char_name}")
            report.append(f"  Score d'équilibre: {score:.1f}/100")

            if stats:
                report.append(f"  Vie: {stats.get('life', 'N/A')}")
                report.append(f"  Attaque: {stats.get('attack', 'N/A')}")
                report.append(f"  Défense: {stats.get('defence', 'N/A')}")

            report.append(f"  Équilibré: {'✓' if data.get('balanced') else '✗'}")
            report.append("")

        return "\n".join(report)

class BalancerGUI:
    """Interface graphique pour l'équilibreur"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KOF Ultimate - Équilibreur de Personnages")
        self.root.geometry("900x700")

        self.balancer = CharacterBalancer()
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface"""
        # Frame supérieur - Contrôles
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        ttk.Button(control_frame, text="🔍 Analyser", command=self.analyze).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="⚖ Équilibrer Tout", command=self.balance_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📊 Rapport", command=self.show_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="💾 Sauvegarder", command=self.save_config).pack(side=tk.LEFT, padx=5)

        # Barre de progression
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        self.progress_label = ttk.Label(self.root, text="Prêt")
        self.progress_label.pack()

        # Tableau des personnages
        columns = ('Personnage', 'Vie', 'Attaque', 'Défense', 'Score', 'État')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, pady=10)

        # Zone de texte pour les logs
        log_frame = ttk.LabelFrame(self.root, text="Console", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        """Ajoute un message au log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def analyze(self):
        """Lance l'analyse"""
        self.log("🔍 Analyse des personnages en cours...")
        self.tree.delete(*self.tree.get_children())

        stats = self.balancer.analyze_all_characters()
        self.log(f"✓ {len(stats)} personnages analysés")

        for char_name, data in sorted(stats.items()):
            char_stats = data['stats']
            score = self.balancer.calculate_balance_score(char_stats)

            self.tree.insert('', tk.END, values=(
                char_name,
                char_stats.get('life', 'N/A'),
                char_stats.get('attack', 'N/A'),
                char_stats.get('defence', 'N/A'),
                f"{score:.1f}",
                '✓' if data.get('balanced') else '✗'
            ))

        self.log("✓ Analyse terminée")

    def balance_all(self):
        """Équilibre tous les personnages"""
        response = messagebox.askyesno(
            "Confirmation",
            "Cela va modifier les fichiers des personnages.\n"
            "Des sauvegardes seront créées (.cns.backup).\n\n"
            "Continuer?"
        )

        if not response:
            return

        self.log("⚖ Équilibrage en cours...")

        def progress_callback(current, total, char_name):
            progress = (current / total) * 100
            self.progress_var.set(progress)
            self.progress_label.config(text=f"Équilibrage: {char_name} ({current}/{total})")
            self.root.update()

        balanced_count = self.balancer.balance_all_characters(progress_callback)

        self.log(f"✓ {balanced_count} personnages équilibrés")
        self.progress_label.config(text="✓ Équilibrage terminé")
        self.analyze()  # Rafraîchir l'affichage

    def show_report(self):
        """Affiche le rapport"""
        report = self.balancer.generate_report()

        # Créer une nouvelle fenêtre
        report_window = tk.Toplevel(self.root)
        report_window.title("Rapport d'équilibrage")
        report_window.geometry("800x600")

        text = scrolledtext.ScrolledText(report_window, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, report)

        # Sauvegarder le rapport
        report_file = self.balancer.game_path / "balance_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        self.log(f"📊 Rapport sauvegardé: {report_file}")

    def save_config(self):
        """Sauvegarde la configuration"""
        config = {
            'target_stats': self.balancer.target_stats,
            'balanced_characters': [name for name, data in self.balancer.stats.items() if data.get('balanced')]
        }

        config_file = self.balancer.game_path / "balance_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        self.log(f"💾 Configuration sauvegardée: {config_file}")
        messagebox.showinfo("Succès", f"Configuration sauvegardée dans:\n{config_file}")

    def run(self):
        """Lance l'interface"""
        self.log("🎮 KOF Ultimate - Équilibreur de Personnages")
        self.log("Cliquez sur 'Analyser' pour commencer")
        self.root.mainloop()

if __name__ == "__main__":
    app = BalancerGUI()
    app.run()
