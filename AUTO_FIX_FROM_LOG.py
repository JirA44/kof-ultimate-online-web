#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE - AUTO-CORRECTEUR À PARTIR DES LOGS
Lit mugen.log, détecte les erreurs, et les corrige automatiquement
"""

import re
from pathlib import Path
from datetime import datetime
import shutil

game_dir = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo kofuo Online kofuo kofuo Online kofuo kofuo")
log_file = game_dir / "mugen.log"
chars_dir = game_dir / "chars"

class LogBasedFixer:
    """Correcteur automatique basé sur mugen.log"""

    def __init__(self):
        self.fixed_count = 0
        self.iteration = 0
        self.backup_dir = game_dir / "air_backups_from_log" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.errors_fixed = []

    def log(self, message, level='INFO'):
        """Log message"""
        symbols = {
            'INFO': 'ℹ️',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'FIX': '🔧'
        }
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {symbols.get(level, '•')} {message}")

    def read_log_errors(self):
        """Lit mugen.log et extrait toutes les erreurs"""
        if not log_file.exists():
            self.log("mugen.log introuvable", 'WARNING')
            return []

        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        errors = []

        # Pattern 1: Error in xxx.air:line
        air_errors = re.findall(r'Error in ([^\s:]+\.air):(\d+)', content)
        for air_file, line_num in air_errors:
            errors.append({
                'type': 'AIR_ERROR',
                'file': air_file,
                'line': int(line_num),
                'message': f"Error in {air_file} at line {line_num}"
            })

        # Pattern 2: Error in clsn2 in [Begin Action X] elem Y
        clsn_errors = re.findall(r'Error in (clsn\d+) in \[Begin Action (\d+)\] elem (\d+)', content)
        for clsn_type, action, elem in clsn_errors:
            errors.append({
                'type': 'CLSN_ERROR',
                'clsn_type': clsn_type,
                'action': int(action),
                'elem': int(elem),
                'message': f"Error in {clsn_type} in Action {action} elem {elem}"
            })

        # Pattern 3: Character xxx.def failed to load
        char_errors = re.findall(r'Character ([^\s]+\.def) failed to load', content)
        for char_def in char_errors:
            errors.append({
                'type': 'CHAR_FAILED',
                'file': char_def,
                'message': f"Character {char_def} failed to load"
            })

        self.log(f"Trouvé {len(errors)} erreurs dans mugen.log")
        return errors

    def find_air_file(self, air_filename):
        """Trouve un fichier AIR dans le dossier chars"""
        matches = list(chars_dir.rglob(air_filename))
        return matches[0] if matches else None

    def backup_file(self, file_path):
        """Crée un backup"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = self.backup_dir / file_path.name
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            self.log(f"Erreur backup: {e}", 'ERROR')
            return False

    def fix_air_file_at_line(self, air_path, line_num):
        """Corrige un fichier AIR à une ligne spécifique"""
        try:
            with open(air_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num > len(lines):
                self.log(f"Ligne {line_num} hors limites", 'WARNING')
                return False

            # Analyser la ligne problématique
            problem_line = lines[line_num - 1]

            # Vérifier si c'est un problème de Clsn
            if re.match(r'^\s*Clsn[12]:\s*\d+', problem_line):
                # Trouver l'action contenant cette ligne
                action_num = None
                for i in range(line_num - 1, -1, -1):
                    match = re.match(r'^\s*\[Begin Action (\d+)\]', lines[i])
                    if match:
                        action_num = int(match.group(1))
                        action_start = i
                        break

                if action_num is not None:
                    # Compter les Clsn boxes
                    clsn1_boxes = []
                    clsn2_boxes = []
                    clsn1_declared = 0
                    clsn2_declared = 0

                    # Parcourir l'action
                    for i in range(action_start, len(lines)):
                        line = lines[i]

                        # Nouvelle action = fin
                        if i > action_start and re.match(r'^\s*\[Begin Action', line):
                            break

                        # Déclarations Clsn
                        match = re.match(r'^\s*Clsn1:\s*(\d+)', line)
                        if match:
                            clsn1_declared = int(match.group(1))

                        match = re.match(r'^\s*Clsn2:\s*(\d+)', line)
                        if match:
                            clsn2_declared = int(match.group(1))

                        # Boxes Clsn
                        if re.match(r'^\s*Clsn1\[\d+\]', line):
                            clsn1_boxes.append(line)
                        elif re.match(r'^\s*Clsn2\[\d+\]', line):
                            clsn2_boxes.append(line)

                    # Corriger les déclarations
                    fixed = False
                    for i in range(action_start, len(lines)):
                        if i > action_start and re.match(r'^\s*\[Begin Action', lines[i]):
                            break

                        if re.match(r'^\s*Clsn1:\s*\d+', lines[i]):
                            if clsn1_declared != len(clsn1_boxes):
                                lines[i] = f"Clsn1: {len(clsn1_boxes)}\n"
                                fixed = True

                        if re.match(r'^\s*Clsn2:\s*\d+', lines[i]):
                            if clsn2_declared != len(clsn2_boxes):
                                lines[i] = f"Clsn2: {len(clsn2_boxes)}\n"
                                fixed = True

                    if fixed:
                        # Backup et sauvegarder
                        self.backup_file(air_path)

                        with open(air_path, 'w', encoding='utf-8') as f:
                            f.writelines(lines)

                        self.fixed_count += 1
                        self.log(f"Corrigé Action {action_num} dans {air_path.name}", 'FIX')
                        return True

            return False

        except Exception as e:
            self.log(f"Erreur correction: {e}", 'ERROR')
            return False

    def fix_all_errors_from_log(self):
        """Corrige toutes les erreurs trouvées dans mugen.log"""
        print()
        print("=" * 70)
        print("  🔧 AUTO-CORRECTEUR À PARTIR DES LOGS")
        print("=" * 70)
        print()

        while True:
            self.iteration += 1
            self.log(f"ITÉRATION #{self.iteration}", 'TEST')
            print()

            # Lire les erreurs
            errors = self.read_log_errors()

            if not errors:
                self.log("Aucune erreur trouvée dans mugen.log!", 'SUCCESS')
                break

            # Grouper les erreurs par fichier
            air_files = {}
            for error in errors:
                if error['type'] == 'AIR_ERROR' and 'file' in error:
                    air_file = error['file']
                    if air_file not in air_files:
                        air_files[air_file] = []
                    air_files[air_file].append(error)

            self.log(f"Fichiers AIR à corriger: {len(air_files)}")
            print()

            if not air_files:
                self.log("Aucun fichier AIR à corriger", 'WARNING')
                break

            # Corriger chaque fichier
            fixed_this_iteration = 0
            for air_filename, file_errors in air_files.items():
                air_path = self.find_air_file(air_filename)

                if not air_path:
                    self.log(f"Fichier introuvable: {air_filename}", 'WARNING')
                    continue

                self.log(f"Correction de {air_filename}...")

                for error in file_errors:
                    if 'line' in error:
                        if self.fix_air_file_at_line(air_path, error['line']):
                            fixed_this_iteration += 1
                            self.errors_fixed.append(error['message'])

            if fixed_this_iteration == 0:
                self.log("Aucune correction possible", 'WARNING')
                break

            self.log(f"Corrections cette itération: {fixed_this_iteration}", 'SUCCESS')
            print()

            # Limiter à 10 itérations pour éviter boucle infinie
            if self.iteration >= 10:
                self.log("Limite de 10 itérations atteinte", 'WARNING')
                break

        print()
        print("=" * 70)
        print("📊 RAPPORT FINAL")
        print("=" * 70)
        print(f"Itérations:        {self.iteration}")
        print(f"Corrections:       {self.fixed_count}")
        print(f"Erreurs corrigées: {len(self.errors_fixed)}")
        print()

        if self.errors_fixed:
            print("🔧 ERREURS CORRIGÉES:")
            for i, error in enumerate(self.errors_fixed[:10], 1):
                print(f"  {i}. {error}")
            if len(self.errors_fixed) > 10:
                print(f"  ... et {len(self.errors_fixed) - 10} autres")
            print()

        if self.fixed_count > 0:
            print(f"✅ Backups sauvegardés dans:")
            print(f"   {self.backup_dir}")

        print("=" * 70)
        print()

def main():
    """Main function"""
    print()
    print("=" * 70)
    print("  🔍 KOF ULTIMATE - AUTO-CORRECTEUR À PARTIR DES LOGS")
    print("=" * 70)
    print()

    fixer = LogBasedFixer()
    fixer.fix_all_errors_from_log()

    print()
    try:
        input("Appuyez sur ENTRÉE pour fermer...")
    except EOFError:
        pass

if __name__ == '__main__':
    main()
