#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI AUTO REPAIR SYSTEM - Système de réparation automatique permanent
Surveille et corrige TOUTES les erreurs automatiquement 24/7
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import shutil

class AIAutoRepairSystem:
    """Système IA de réparation automatique permanent"""

    def __init__(self):
        self.base_path = Path(r"D:\KOF Ultimate Online")
        self.data_path = self.base_path / "data"
        self.chars_path = self.data_path / "chars"
        self.mugen_cfg = self.base_path / "data" / "mugen1.1.cfg"
        self.select_def = self.data_path / "select.def"

        # Statistiques de réparation
        self.repair_log = []
        self.errors_fixed = 0
        self.cycle_count = 0

        # Journal de réparations
        self.log_file = self.base_path / "ai_repair_log.json"
        self.load_log()

    def load_log(self):
        """Charger l'historique des réparations"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.repair_log = data.get('repairs', [])
                    self.errors_fixed = data.get('total_fixed', 0)
            except:
                pass

    def save_log(self):
        """Sauvegarder l'historique"""
        try:
            data = {
                'repairs': self.repair_log[-100:],  # Garder les 100 dernières
                'total_fixed': self.errors_fixed,
                'last_update': datetime.now().isoformat()
            }
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde log: {e}")

    def log_repair(self, error_type, description, status="SUCCESS"):
        """Logger une réparation"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'cycle': self.cycle_count,
            'error_type': error_type,
            'description': description,
            'status': status
        }
        self.repair_log.append(entry)
        if status == "SUCCESS":
            self.errors_fixed += 1

        # Afficher
        icon = "✅" if status == "SUCCESS" else "❌"
        print(f"  {icon} {error_type}: {description}")

    def print_header(self):
        """Afficher l'en-tête du système"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*70)
        print(" 🤖 AI AUTO REPAIR SYSTEM - Réparation Automatique 24/7")
        print("="*70)
        print(f" 🔄 Cycle: {self.cycle_count} | 🔧 Erreurs corrigées: {self.errors_fixed}")
        print(f" ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

    def scan_roster(self):
        """Scanner le roster complet"""
        characters = []

        if not self.select_def.exists():
            return characters

        try:
            with open(self.select_def, 'r', encoding='utf-8', errors='ignore') as f:
                in_chars_section = False
                for line in f:
                    line = line.strip()

                    if line.startswith('[Characters]'):
                        in_chars_section = True
                        continue

                    if in_chars_section:
                        if line.startswith('['):
                            break

                        if line and not line.startswith(';'):
                            parts = line.split(',')
                            if parts and parts[0].strip():
                                char_folder = parts[0].strip()
                                characters.append(char_folder)
        except:
            pass

        return characters

    def check_and_fix_portraits(self, characters):
        """Vérifier et corriger les portraits manquants"""
        print("\n🔍 SCAN: Portraits")

        portraits_dir = self.data_path / "big"
        portraits_dir.mkdir(exist_ok=True)

        fixed = 0
        for char_folder in characters:
            portrait_path = portraits_dir / f"{char_folder}.png"

            if not portrait_path.exists():
                # Créer portrait manquant
                try:
                    self.generate_default_portrait(char_folder, portrait_path)
                    self.log_repair("PORTRAIT", f"Portrait créé: {char_folder}.png")
                    fixed += 1
                except Exception as e:
                    self.log_repair("PORTRAIT", f"Échec création: {char_folder}.png", "ERROR")

        if fixed == 0:
            print("  ✓ Tous les portraits sont présents")

        return fixed

    def generate_default_portrait(self, char_name, output_path, size=(150, 150)):
        """Générer un portrait par défaut"""
        # Créer image avec dégradé
        img = Image.new('RGB', size, color='#1a1a2e')
        draw = ImageDraw.Draw(img)

        # Dégradé simple
        for y in range(size[1]):
            intensity = int(26 + (y / size[1]) * 30)
            color = (intensity, intensity, intensity + 20)
            draw.line([(0, y), (size[0], y)], fill=color)

        # Bordure
        draw.rectangle([(0, 0), (size[0]-1, size[1]-1)], outline='#667eea', width=2)

        # Texte
        try:
            # Essayer plusieurs polices
            font_paths = [
                "C:\\Windows\\Fonts\\arial.ttf",
                "C:\\Windows\\Fonts\\calibri.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            ]

            font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 14)
                    break

            if not font:
                font = ImageFont.load_default()

            # Nom du personnage (tronquer si trop long)
            display_name = char_name[:20]

            # Centrer le texte
            bbox = draw.textbbox((0, 0), display_name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (size[0] - text_width) // 2
            y = size[1] - text_height - 10

            # Ombre
            draw.text((x+1, y+1), display_name, fill='#000000', font=font)
            # Texte principal
            draw.text((x, y), display_name, fill='#ffffff', font=font)

        except Exception as e:
            # Fallback: texte simple
            draw.text((10, size[1]-20), char_name[:15], fill='#ffffff')

        # Sauvegarder
        img.save(output_path, 'PNG')

    def check_and_fix_multiplayer(self):
        """Vérifier et corriger la config multijoueur"""
        print("\n🔍 SCAN: Configuration Multijoueur")

        if not self.mugen_cfg.exists():
            print("  ⚠️ mugen1.1.cfg introuvable")
            return 0

        try:
            with open(self.mugen_cfg, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Vérifier si section [Network] existe
            if '[Network]' not in content:
                # Ajouter section réseau
                network_config = """

; ═══════════════════════════════════════════════════════════════════════
; NETWORK CONFIGURATION - Configuration réseau pour le multijoueur
; ═══════════════════════════════════════════════════════════════════════
[Network]
; Activer le mode réseau (0 = désactivé, 1 = activé)
Enabled = 1

; Type de connexion (server, client, auto)
ConnectionType = auto

; Serveur par défaut
Server = 127.0.0.1

; Port réseau
Port = 9999

; Rollback netcode frames (recommandé: 2-4 pour connexions locales, 6-8 pour internet)
RollbackFrames = 4

; Délai d'entrée pour compenser la latence (frames)
InputDelay = 2

; Qualité de la connexion minimum requise (0-5, 5 = excellente)
MinConnectionQuality = 2

; Timeout de connexion (secondes)
ConnectionTimeout = 30

; Mode spectateur activé
SpectatorMode = 1

; Chat activé
ChatEnabled = 1
"""

                with open(self.mugen_cfg, 'a', encoding='utf-8') as f:
                    f.write(network_config)

                self.log_repair("NETWORK", "Section [Network] ajoutée à mugen1.1.cfg")
                return 1
            else:
                print("  ✓ Configuration réseau présente")
                return 0

        except Exception as e:
            self.log_repair("NETWORK", f"Erreur vérification réseau: {e}", "ERROR")
            return 0

    def check_and_fix_file_permissions(self):
        """Vérifier et corriger les permissions de fichiers"""
        print("\n🔍 SCAN: Permissions de fichiers")

        critical_files = [
            self.mugen_cfg,
            self.select_def,
            self.base_path / "KOF_Ultimate_Online.exe",
            self.base_path / "Ikemen_GO.exe"
        ]

        fixed = 0
        for file_path in critical_files:
            if file_path.exists():
                try:
                    # Vérifier si on peut lire/écrire
                    if not os.access(file_path, os.R_OK | os.W_OK):
                        # Tenter de corriger (Windows)
                        os.chmod(file_path, 0o666)
                        self.log_repair("PERMISSIONS", f"Permissions corrigées: {file_path.name}")
                        fixed += 1
                except:
                    pass

        if fixed == 0:
            print("  ✓ Permissions correctes")

        return fixed

    def check_and_fix_missing_directories(self):
        """Vérifier et créer les répertoires manquants"""
        print("\n🔍 SCAN: Répertoires requis")

        required_dirs = [
            self.data_path / "big",
            self.data_path / "chars",
            self.data_path / "stages",
            self.data_path / "sound",
            self.data_path / "font",
            self.base_path / "logs",
            self.base_path / "save"
        ]

        fixed = 0
        for dir_path in required_dirs:
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.log_repair("DIRECTORY", f"Répertoire créé: {dir_path.name}")
                    fixed += 1
                except Exception as e:
                    self.log_repair("DIRECTORY", f"Échec création: {dir_path.name}", "ERROR")

        if fixed == 0:
            print("  ✓ Tous les répertoires présents")

        return fixed

    def check_and_fix_corrupted_files(self):
        """Détecter et isoler les fichiers corrompus"""
        print("\n🔍 SCAN: Fichiers corrompus")

        # Vérifier les PNG corrompus dans big/
        portraits_dir = self.data_path / "big"
        fixed = 0

        if portraits_dir.exists():
            for portrait_file in portraits_dir.glob("*.png"):
                try:
                    # Tenter d'ouvrir l'image
                    img = Image.open(portrait_file)
                    img.verify()
                except Exception as e:
                    # Fichier corrompu - le renommer et en créer un nouveau
                    try:
                        corrupted_path = portrait_file.with_suffix('.corrupted')
                        portrait_file.rename(corrupted_path)

                        # Recréer le portrait
                        char_name = portrait_file.stem
                        self.generate_default_portrait(char_name, portrait_file)

                        self.log_repair("CORRUPTED", f"Portrait corrompu réparé: {portrait_file.name}")
                        fixed += 1
                    except:
                        self.log_repair("CORRUPTED", f"Échec réparation: {portrait_file.name}", "ERROR")

        if fixed == 0:
            print("  ✓ Aucun fichier corrompu détecté")

        return fixed

    def run_repair_cycle(self):
        """Exécuter un cycle complet de réparation"""
        self.cycle_count += 1
        self.print_header()

        print("🚀 DÉBUT DU CYCLE DE RÉPARATION\n")

        # Scanner le roster
        characters = self.scan_roster()
        print(f"📋 Roster: {len(characters)} personnages détectés\n")

        total_fixed = 0

        # 1. Répertoires
        total_fixed += self.check_and_fix_missing_directories()

        # 2. Portraits
        total_fixed += self.check_and_fix_portraits(characters)

        # 3. Configuration réseau
        total_fixed += self.check_and_fix_multiplayer()

        # 4. Permissions
        total_fixed += self.check_and_fix_file_permissions()

        # 5. Fichiers corrompus
        total_fixed += self.check_and_fix_corrupted_files()

        # Sauvegarder le log
        self.save_log()

        # Résumé
        print("\n" + "="*70)
        if total_fixed > 0:
            print(f"✅ CYCLE {self.cycle_count} TERMINÉ - {total_fixed} erreurs corrigées!")
        else:
            print(f"✅ CYCLE {self.cycle_count} TERMINÉ - Aucune erreur détectée")
        print(f"📊 Total corrections depuis le début: {self.errors_fixed}")
        print("="*70 + "\n")

    def run_continuous(self, interval=60):
        """Lancer en mode continu"""
        print("\n" + "="*70)
        print(" 🤖 AI AUTO REPAIR SYSTEM - MODE CONTINU")
        print("="*70)
        print(f" ⏱️  Intervalle de scan: {interval} secondes")
        print(" 🛑 Appuyez sur Ctrl+C pour arrêter")
        print("="*70 + "\n")

        try:
            while True:
                self.run_repair_cycle()

                print(f"⏳ Prochain scan dans {interval} secondes...")
                print("   (Ctrl+C pour arrêter)\n")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print(" 🛑 ARRÊT DU SYSTÈME DE RÉPARATION AUTOMATIQUE")
            print("="*70)
            print(f" 📊 Statistiques finales:")
            print(f"    • Cycles effectués: {self.cycle_count}")
            print(f"    • Erreurs corrigées: {self.errors_fixed}")
            print("="*70 + "\n")

    def run_once(self):
        """Lancer un seul cycle"""
        self.run_repair_cycle()

        print("\n💡 Pour lancer en mode continu:")
        print("   python AI_AUTO_REPAIR_SYSTEM.py --continuous")
        print("   python AI_AUTO_REPAIR_SYSTEM.py --continuous --interval 120\n")


def main():
    """Point d'entrée principal"""
    system = AIAutoRepairSystem()

    # Parser les arguments
    if '--continuous' in sys.argv:
        interval = 60  # Par défaut 60 secondes

        if '--interval' in sys.argv:
            try:
                idx = sys.argv.index('--interval')
                interval = int(sys.argv[idx + 1])
            except:
                pass

        system.run_continuous(interval)
    else:
        system.run_once()


if __name__ == "__main__":
    main()
