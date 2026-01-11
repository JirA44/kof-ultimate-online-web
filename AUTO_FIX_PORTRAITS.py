#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO FIX PORTRAITS - Réparation automatique des portraits manquants
Génère des portraits par défaut ou extrait depuis les .sff
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

class PortraitFixer:
    """Réparateur automatique de portraits"""

    def __init__(self):
        self.base_path = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo")
        self.chars_path = self.base_path / "chars"
        self.backup_path = self.base_path / "portraits_backup"
        self.fixed_count = 0
        self.error_count = 0

    def log(self, message, level="INFO"):
        """Log avec icônes"""
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "FIX": "🔧"
        }
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {icons.get(level, '')} {message}")

    def create_backup(self):
        """Créer un backup des portraits existants"""
        self.log("Création backup des portraits existants...", "INFO")

        if self.backup_path.exists():
            self.log("Backup existant trouvé, skip", "INFO")
            return

        self.backup_path.mkdir(exist_ok=True)
        self.log(f"Backup créé: {self.backup_path}", "SUCCESS")

    def generate_default_portrait(self, char_name, output_path, size=(150, 150)):
        """Générer un portrait par défaut avec le nom du personnage"""
        try:
            # Créer une image avec fond dégradé
            img = Image.new('RGB', size, color='#1a1a2e')
            draw = ImageDraw.Draw(img)

            # Fond dégradé simple
            for i in range(size[1]):
                darkness = int(26 + (i / size[1]) * 40)
                color = (darkness, darkness, darkness + 20)
                draw.line([(0, i), (size[0], i)], fill=color)

            # Bordure
            draw.rectangle([0, 0, size[0]-1, size[1]-1], outline='#667eea', width=3)

            # Texte avec le nom du personnage
            text = char_name[:15]  # Limiter à 15 chars

            # Essayer d'utiliser une police système
            try:
                font = ImageFont.truetype("arial.ttf", 14)
            except:
                font = ImageFont.load_default()

            # Centrer le texte
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2

            # Ombre du texte
            draw.text((x+2, y+2), text, fill='#000000', font=font)
            # Texte principal
            draw.text((x, y), text, fill='#667eea', font=font)

            # Icône "?" en haut
            draw.text((size[0]//2-10, 10), "?", fill='#feca57', font=font)

            # Sauvegarder
            img.save(output_path)
            return True

        except Exception as e:
            self.log(f"Erreur génération portrait {char_name}: {e}", "ERROR")
            return False

    def check_and_fix_portrait(self, char_folder):
        """Vérifier et réparer le portrait d'un personnage"""
        char_name = char_folder.name

        # Extensions possibles pour les portraits
        portrait_extensions = ['.png', '.pcx', '.sff']
        portrait_found = False

        # Vérifier si un portrait existe déjà
        for ext in portrait_extensions:
            portrait_file = char_folder / f"portrait{ext}"
            if portrait_file.exists():
                portrait_found = True
                break

        if portrait_found:
            return False  # Pas besoin de réparer

        # Générer un portrait par défaut
        portrait_path = char_folder / "portrait.png"

        if self.generate_default_portrait(char_name, portrait_path):
            self.log(f"Portrait créé: {char_name}", "FIX")
            self.fixed_count += 1
            return True
        else:
            self.error_count += 1
            return False

    def fix_all_portraits(self):
        """Réparer tous les portraits manquants"""
        self.log("Démarrage réparation des portraits...", "INFO")
        print("\n" + "="*60)

        if not self.chars_path.exists():
            self.log("Dossier chars introuvable!", "ERROR")
            return

        # Créer backup
        self.create_backup()

        # Parcourir tous les personnages
        char_folders = [d for d in self.chars_path.iterdir() if d.is_dir()]
        total = len(char_folders)

        self.log(f"Scan de {total} personnages...", "INFO")
        print()

        for i, char_folder in enumerate(char_folders, 1):
            # Afficher progression
            progress = (i / total) * 100
            print(f"\rProgression: [{i}/{total}] {progress:.1f}%", end='', flush=True)

            self.check_and_fix_portrait(char_folder)

        print("\n")
        print("="*60)
        self.log(f"Réparation terminée!", "SUCCESS")
        self.log(f"Portraits créés: {self.fixed_count}", "SUCCESS")
        self.log(f"Erreurs: {self.error_count}", "ERROR" if self.error_count > 0 else "INFO")
        print("="*60 + "\n")

    def generate_report(self):
        """Générer un rapport de réparation"""
        report_path = self.base_path / "portrait_fix_report.txt"

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("RAPPORT DE RÉPARATION DES PORTRAITS\n")
                f.write("="*60 + "\n\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Portraits créés: {self.fixed_count}\n")
                f.write(f"Erreurs: {self.error_count}\n\n")
                f.write("="*60 + "\n")

            self.log(f"Rapport sauvegardé: {report_path.name}", "SUCCESS")

        except Exception as e:
            self.log(f"Erreur génération rapport: {e}", "ERROR")


def main():
    """Point d'entrée principal"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "AUTO FIX PORTRAITS v1.0" + " "*20 + "║")
    print("║" + " "*10 + "Réparation automatique des portraits" + " "*11 + "║")
    print("╚" + "="*58 + "╝")
    print("\n")

    fixer = PortraitFixer()

    # Demander confirmation
    print("⚠️  Ce script va générer des portraits par défaut pour tous")
    print("   les personnages qui n'en ont pas.\n")

    choice = input("Continuer? (O/N): ").strip().upper()

    if choice != 'O':
        print("\n❌ Opération annulée par l'utilisateur\n")
        return

    print("\n")

    # Lancer la réparation
    fixer.fix_all_portraits()

    # Générer le rapport
    fixer.generate_report()

    print("\n✅ Opération terminée!")
    print("\n💡 Conseil: Relancez l'audit qualité pour voir l'amélioration:")
    print("   python ESPORT_QUALITY_MONITOR.py\n")


if __name__ == "__main__":
    main()
