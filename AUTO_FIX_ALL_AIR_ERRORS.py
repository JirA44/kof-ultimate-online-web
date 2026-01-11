#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-CORRECTEUR D'ERREURS .AIR
Détecte et corrige automatiquement toutes les erreurs dans les fichiers .air
"""

import re
from pathlib import Path
import shutil

class AirErrorFixer:
    def __init__(self, game_dir):
        self.game_dir = Path(game_dir)
        self.chars_dir = self.game_dir / "chars"
        self.errors_found = []
        self.errors_fixed = []

    def find_all_air_files(self):
        """Trouve tous les fichiers .air"""
        air_files = list(self.chars_dir.glob("**/*.air"))
        print(f"🔍 {len(air_files)} fichiers .air trouvés")
        return air_files

    def backup_file(self, file_path):
        """Crée un backup du fichier"""
        backup_path = file_path.with_suffix('.air.backup_autofix')
        if not backup_path.exists():
            shutil.copy2(file_path, backup_path)

    def fix_clsn_errors(self, content, file_path):
        """Corrige les erreurs Clsn"""
        fixed = False
        lines = content.split('\n')
        new_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Détecter [Begin Action XXX]
            if line.strip().startswith('[Begin Action'):
                new_lines.append(line)
                i += 1

                # Chercher la ligne Clsn1: ou Clsn2:
                while i < len(lines) and not lines[i].strip().startswith('['):
                    current = lines[i].strip()

                    # Si on trouve Clsn2: 0 ou Clsn1: 0 sans définitions
                    if re.match(r'(Clsn[12]):\s*0\s*$', current):
                        # Vérifier la ligne suivante
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            # Si la ligne suivante est une image (commence par un chiffre)
                            if re.match(r'^\d+,', next_line):
                                # Ajouter une Clsn valide
                                clsn_type = re.match(r'(Clsn[12]):', current).group(1)
                                new_lines.append(f"{clsn_type}: 1")
                                new_lines.append(f"{clsn_type}[0] = -10, -90, 10, 0")
                                fixed = True
                                self.errors_fixed.append(f"{file_path.name}:{i+1} - Fixed empty {clsn_type}")
                                i += 1
                                continue

                    # Si on trouve Clsn2[0] suivi d'une image au lieu d'autre Clsn
                    if re.match(r'Clsn[12]\[\d+\]\s*=', current):
                        new_lines.append(lines[i])
                        i += 1
                        # Vérifier si les Clsn suivantes sont complètes
                        while i < len(lines):
                            next_line = lines[i].strip()
                            # Si on trouve une image alors qu'on attend encore des Clsn
                            if re.match(r'^\d+,', next_line):
                                # Vérifier s'il y a "Loopstart" mal placé
                                if 'Loopstart' in next_line or 'LoopStart' in next_line:
                                    # Séparer Loopstart et mettre sur ligne suivante
                                    cleaned = re.sub(r'\s*(Loopstart|LoopStart)\s*', '', next_line, flags=re.IGNORECASE)
                                    new_lines.append(cleaned)
                                    new_lines.append("Loopstart")
                                    fixed = True
                                    self.errors_fixed.append(f"{file_path.name}:{i+1} - Fixed Loopstart placement")
                                    i += 1
                                    continue
                                break
                            elif re.match(r'Clsn[12]\[\d+\]\s*=', next_line):
                                new_lines.append(lines[i])
                                i += 1
                            else:
                                break
                        continue

                    new_lines.append(lines[i])
                    i += 1
                continue

            new_lines.append(line)
            i += 1

        return '\n'.join(new_lines), fixed

    def fix_file(self, file_path):
        """Corrige un fichier .air"""
        try:
            # Lire le fichier avec différents encodages
            content = None
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'shift-jis']:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    break
                except:
                    continue

            if content is None:
                return False

            # Backup
            self.backup_file(file_path)

            # Corriger les erreurs Clsn
            new_content, fixed = self.fix_clsn_errors(content, file_path)

            if fixed:
                # Sauvegarder
                with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(new_content)
                return True

            return False

        except Exception as e:
            print(f"❌ Erreur sur {file_path.name}: {e}")
            return False

    def scan_mugen_log(self):
        """Scanne mugen.log pour trouver les fichiers avec erreurs"""
        log_file = self.game_dir / "mugen.log"
        if not log_file.exists():
            return []

        error_files = []
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Trouver toutes les erreurs .air
            pattern = r'Error in ([^\s:]+\.air):(\d+)'
            matches = re.findall(pattern, content)

            for air_file, line_num in matches:
                error_files.append((air_file, line_num))
                print(f"⚠️  Erreur détectée: {air_file}:{line_num}")

        except Exception as e:
            print(f"❌ Erreur lecture log: {e}")

        return error_files

    def fix_all(self):
        """Corrige tous les fichiers avec erreurs"""
        print("=" * 80)
        print(" " * 20 + "🔧 AUTO-CORRECTEUR D'ERREURS .AIR")
        print("=" * 80)
        print()

        # 1. Scanner le log pour trouver les fichiers avec erreurs
        print("📋 Analyse du mugen.log...")
        error_files = self.scan_mugen_log()

        if error_files:
            print(f"\n✓ {len(error_files)} fichiers avec erreurs détectés\n")

            # Corriger ces fichiers spécifiques
            for air_filename, line_num in error_files:
                # Trouver le fichier
                matches = list(self.chars_dir.glob(f"**/{air_filename}"))
                for file_path in matches:
                    print(f"🔧 Correction de {file_path.name}...")
                    if self.fix_file(file_path):
                        print(f"  ✅ Corrigé!")
                    else:
                        print(f"  ℹ️  Aucune correction nécessaire")
        else:
            print("✓ Aucune erreur détectée dans le log\n")

        # 2. Scanner TOUS les fichiers .air pour prévenir d'autres erreurs
        print("\n🔍 Scan préventif de tous les fichiers .air...")
        all_files = self.find_all_air_files()

        fixed_count = 0
        for file_path in all_files:
            if self.fix_file(file_path):
                fixed_count += 1

        print(f"\n✅ {fixed_count} fichiers corrigés en mode préventif")

        # Résumé
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DES CORRECTIONS")
        print("=" * 80)
        print(f"Total fichiers scannés: {len(all_files)}")
        print(f"Fichiers corrigés: {len(self.errors_fixed)}")
        print()

        if self.errors_fixed:
            print("Détails des corrections:")
            for error in self.errors_fixed[:20]:  # Afficher max 20
                print(f"  • {error}")
            if len(self.errors_fixed) > 20:
                print(f"  ... et {len(self.errors_fixed) - 20} autres")

        print("\n✅ CORRECTION AUTOMATIQUE TERMINÉE!\n")

def main():
    game_dir = r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo"
    fixer = AirErrorFixer(game_dir)
    fixer.fix_all()

if __name__ == '__main__':
    main()
