#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYSTÈME 100% AUTOMATIQUE
- Lance le jeu
- Détecte les crashes
- Lit les erreurs
- Répare automatiquement
- Recommence jusqu'à stabilité
"""
import os
import re
import time
import subprocess
import psutil
from pathlib import Path
import shutil
import signal

class AutoGameTester:
    def __init__(self):
        self.base_path = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo")
        self.game_exe = self.base_path / "KOF_Ultimate_Online.exe"

        # Chercher l'exe
        if not self.game_exe.exists():
            self.game_exe = self.base_path / "Ikemen_GO.exe"
        if not self.game_exe.exists():
            # Chercher n'importe quel .exe
            exe_files = list(self.base_path.glob("*.exe"))
            if exe_files:
                self.game_exe = exe_files[0]

        self.log_file = self.base_path / "mugen.log"
        self.errors_file = self.base_path / "auto_errors_detected.txt"
        self.fixed_count = 0

    def kill_game_processes(self):
        """Tue tous les processus du jeu"""
        killed = 0
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name'].lower()
                if 'kof' in name or 'mugen' in name or 'ikemen' in name:
                    proc.kill()
                    killed += 1
            except:
                pass

        if killed > 0:
            print(f"  ✓ {killed} processus de jeu arrêtés")
            time.sleep(2)

    def launch_game_and_wait_crash(self, timeout=30):
        """Lance le jeu et attend qu'il crash ou timeout"""
        print(f"\n🎮 Lancement du jeu: {self.game_exe.name}")
        print(f"   Timeout: {timeout}s")

        # Sauvegarder taille actuelle du log
        log_size_before = self.log_file.stat().st_size if self.log_file.exists() else 0

        try:
            # Lancer le jeu
            process = subprocess.Popen(
                [str(self.game_exe)],
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            start_time = time.time()

            while time.time() - start_time < timeout:
                # Vérifier si le processus est mort (crash)
                if process.poll() is not None:
                    print(f"  ⚠️  Jeu crashé après {int(time.time() - start_time)}s")
                    return True  # Crash détecté

                # Vérifier si le log a changé (erreur détectée)
                if self.log_file.exists():
                    log_size_now = self.log_file.stat().st_size
                    if log_size_now > log_size_before:
                        # Le log a grossi, vérifier s'il y a des erreurs
                        with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            new_content = f.read()[log_size_before:]
                            if 'Error' in new_content or 'error' in new_content:
                                print(f"  ⚠️  Erreur détectée dans le log")
                                # Tuer le processus
                                process.kill()
                                return True

                time.sleep(0.5)

            # Timeout atteint - jeu encore en cours
            print(f"  ✓ Jeu stable pendant {timeout}s!")
            process.kill()
            return False

        except Exception as e:
            print(f"  ❌ Erreur lancement: {e}")
            return False

    def extract_errors_from_log(self):
        """Extrait les dernières erreurs du log"""
        if not self.log_file.exists():
            return []

        errors = []

        try:
            with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Prendre seulement la fin du log (dernier lancement)
            lines = content.split('\n')
            recent_lines = lines[-200:]  # 200 dernières lignes
            recent_content = '\n'.join(recent_lines)

            # Chercher erreurs CLSN
            clsn_errors = re.findall(
                r'Error in clsn([12]) in \[Begin Action (\d+)\]',
                recent_content,
                re.IGNORECASE
            )

            for clsn_type, action_num in clsn_errors:
                errors.append({
                    'type': 'clsn',
                    'clsn_type': clsn_type,
                    'action': action_num
                })

            # Chercher fichiers .air avec erreurs
            air_errors = re.findall(
                r'Error in (.+?\.air):(\d+)',
                recent_content
            )

            for air_file, line_num in air_errors:
                errors.append({
                    'type': 'air_file',
                    'file': air_file.strip(),
                    'line': int(line_num)
                })

            # Chercher storyboards manquants
            sb_errors = re.findall(
                r'Error loading storyboard: (.+)',
                recent_content
            )

            for sb_path in sb_errors:
                errors.append({
                    'type': 'storyboard',
                    'path': sb_path.strip()
                })

            # Chercher personnages qui ne chargent pas
            char_errors = re.findall(
                r'Error loading chars/([^/]+)/',
                recent_content
            )

            for char_name in set(char_errors):  # Dédupliquer
                errors.append({
                    'type': 'character',
                    'name': char_name.strip()
                })

        except Exception as e:
            print(f"  ❌ Erreur lecture log: {e}")

        return errors

    def fix_storyboard_error(self, error):
        """Crée un storyboard manquant"""
        sb_path = self.base_path / error['path']

        if sb_path.exists():
            return False

        try:
            char_match = re.search(r'chars/([^/]+)/', error['path'])
            if not char_match:
                return False

            char_name = char_match.group(1)
            char_path = self.base_path / 'chars' / char_name

            # Trouver sprite file
            def_files = list(char_path.glob("*.def"))
            spr_file = "sprite.sff"

            if def_files:
                with open(def_files[0], 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                spr_match = re.search(r'sprite\s*=\s*(.+)', content, re.IGNORECASE)
                if spr_match:
                    spr_file = spr_match.group(1).strip().strip('"')

            # Créer storyboard
            sb_path.parent.mkdir(parents=True, exist_ok=True)

            sb_type = 'intro' if 'intro' in sb_path.name.lower() else 'ending'

            sb_content = f"""; Auto-generated {sb_type} storyboard
; Created by AUTO_TEST_AND_FIX

[SceneDef]
spr = {spr_file}
"""

            with open(sb_path, 'w', encoding='utf-8') as f:
                f.write(sb_content)

            print(f"    ✅ Créé: {error['path']}")
            return True

        except Exception as e:
            print(f"    ❌ Erreur: {e}")
            return False

    def fix_air_clsn_errors(self, air_file_path):
        """Répare toutes les erreurs CLSN dans un fichier .air"""
        fixed = 0

        try:
            with open(air_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            modified = False
            i = 0

            while i < len(lines):
                line = lines[i].strip()

                clsn_match = re.match(r'(Clsn[12]):\s*(\d+)', line, re.IGNORECASE)
                if clsn_match:
                    clsn_type = clsn_match.group(1)
                    declared_count = int(clsn_match.group(2))

                    # Compter les CLSN réelles
                    actual_count = 0
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if re.match(rf'{clsn_type}\[\d+\]', next_line, re.IGNORECASE):
                            actual_count += 1
                            j += 1
                        else:
                            break

                    if declared_count != actual_count:
                        lines[i] = f"{clsn_type}: {actual_count}\n"
                        modified = True
                        fixed += 1

                i += 1

            if modified:
                # Backup
                backup = air_file_path.parent / f"{air_file_path.name}.backup_auto"
                if not backup.exists():
                    shutil.copy(air_file_path, backup)

                # Sauvegarder
                with open(air_file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

                print(f"    ✅ {air_file_path.name}: {fixed} erreurs CLSN réparées")
                return True

        except Exception as e:
            print(f"    ❌ Erreur: {e}")

        return False

    def remove_problematic_character(self, char_name):
        """Retire un personnage du roster"""
        select_def = self.base_path / "data" / "select.def"

        try:
            with open(select_def, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            modified = False
            for i, line in enumerate(lines):
                if line.strip().startswith(char_name + ','):
                    lines[i] = f"; AUTO-RETIRÉ (Erreurs): {line}"
                    modified = True
                    break

            if modified:
                # Backup
                backup = select_def.parent / f"select.def.backup_auto_{int(time.time())}"
                shutil.copy(select_def, backup)

                with open(select_def, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

                print(f"    ✅ {char_name} retiré du roster")
                return True

        except Exception as e:
            print(f"    ❌ Erreur: {e}")

        return False

    def run_auto_test_loop(self, max_iterations=20):
        """Boucle principale de test automatique"""
        print("="*70)
        print("🤖 SYSTÈME DE TEST ET RÉPARATION 100% AUTOMATIQUE")
        print("="*70)
        print(f"\n⚙️  Configuration:")
        print(f"   Jeu: {self.game_exe.name}")
        print(f"   Itérations max: {max_iterations}")
        print(f"   Timeout par test: 30s")
        print("\n🎯 Objectif: Rendre le jeu stable automatiquement")
        print("\n" + "="*70)

        for iteration in range(1, max_iterations + 1):
            print(f"\n🔄 ITÉRATION {iteration}/{max_iterations}")
            print("-" * 70)

            # Tuer les processus existants
            self.kill_game_processes()

            # Lancer le jeu et attendre
            crashed = self.launch_game_and_wait_crash(timeout=30)

            if not crashed:
                print("\n" + "="*70)
                print("✅ SUCCÈS! Le jeu est stable!")
                print("="*70)
                print(f"\nItérations: {iteration}")
                print(f"Réparations: {self.fixed_count}")
                print("\n🎉 Le jeu devrait maintenant fonctionner!")
                break

            # Extraire les erreurs
            print("\n📋 Analyse des erreurs...")
            errors = self.extract_errors_from_log()

            if not errors:
                print("  ⚠️  Crash détecté mais aucune erreur lisible dans le log")
                print("  Peut-être un problème système ou de mémoire")
                continue

            print(f"  ✓ {len(errors)} erreur(s) détectée(s)")

            # Sauvegarder les erreurs
            with open(self.errors_file, 'a', encoding='utf-8') as f:
                f.write(f"\n=== ITÉRATION {iteration} ===\n")
                for err in errors:
                    f.write(f"{err}\n")

            # Grouper par type
            storyboard_errors = [e for e in errors if e['type'] == 'storyboard']
            air_errors = [e for e in errors if e['type'] == 'air_file']
            char_errors = [e for e in errors if e['type'] == 'character']

            # Réparer
            print("\n🔧 Réparation...")

            # 1. Storyboards
            if storyboard_errors:
                print(f"\n  📝 {len(storyboard_errors)} storyboard(s) manquant(s)")
                for err in storyboard_errors:
                    if self.fix_storyboard_error(err):
                        self.fixed_count += 1

            # 2. Fichiers .air
            if air_errors:
                print(f"\n  🔧 {len(air_errors)} fichier(s) .air avec erreurs")
                air_files = set([e['file'] for e in air_errors])

                for air_filename in air_files:
                    # Chercher le fichier
                    air_paths = list(self.base_path.glob(f"**/{air_filename}"))

                    if air_paths:
                        if self.fix_air_clsn_errors(air_paths[0]):
                            self.fixed_count += 1

            # 3. Personnages problématiques (après 3 essais)
            if char_errors and iteration >= 3:
                print(f"\n  ⚠️  {len(char_errors)} personnage(s) toujours problématique(s)")
                for err in char_errors:
                    if self.remove_problematic_character(err['name']):
                        self.fixed_count += 1

            print(f"\n  ✅ Réparations appliquées (Total: {self.fixed_count})")

        else:
            print("\n" + "="*70)
            print("⚠️  LIMITE D'ITÉRATIONS ATTEINTE")
            print("="*70)
            print(f"\nItérations: {max_iterations}")
            print(f"Réparations: {self.fixed_count}")
            print("\n💡 Le jeu peut encore avoir des problèmes")
            print("   Consultez auto_errors_detected.txt pour détails")

        # Nettoyage final
        self.kill_game_processes()

        print("\n" + "="*70)
        print("📊 RAPPORT FINAL")
        print("="*70)
        print(f"\nTotal réparations: {self.fixed_count}")
        print(f"Log des erreurs: {self.errors_file.name}")

def main():
    tester = AutoGameTester()
    tester.run_auto_test_loop(max_iterations=20)

    input("\nAppuyez sur ENTRÉE pour fermer...")

if __name__ == "__main__":
    main()
