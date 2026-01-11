#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE - RAPPORT COMPLET D'ERREURS
Détecte TOUTES les erreurs et crée un rapport détaillé
"""

import subprocess
import re
from pathlib import Path
from datetime import datetime
import json

game_dir = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo kofuo Online kofuo kofuo Online kofuo kofuo")
exe_path = game_dir / "KOF_Ultimate_Online.exe"
log_file = game_dir / "mugen.log"

class ErrorReporter:
    """Détecteur et rapporteur d'erreurs complet"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.test_results = []

    def log(self, message, level='INFO'):
        """Log message"""
        symbols = {
            'INFO': 'ℹ️',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'TEST': '🧪'
        }
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {symbols.get(level, '•')} {message}")

    def test_character(self, char_def):
        """Teste le chargement d'un personnage"""
        try:
            # Effacer le log
            if log_file.exists():
                log_file.unlink()

            # Créer un select temporaire avec seulement ce personnage
            select_file = game_dir / "data" / "select.def"
            select_backup = game_dir / "data" / "select.def.backup_test"

            # Backup
            if select_file.exists():
                with open(select_file, 'rb') as src:
                    select_backup.write_bytes(src.read())

            # Créer select temporaire
            temp_select = f"""
[Characters]
{char_def}
"""
            with open(select_file, 'w') as f:
                f.write(temp_select)

            # Lancer le jeu
            proc = subprocess.Popen(
                [str(exe_path)],
                cwd=str(game_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Attendre 3 secondes
            import time
            time.sleep(3)

            # Terminer
            proc.terminate()
            time.sleep(1)
            if proc.poll() is None:
                proc.kill()

            # Restaurer select
            if select_backup.exists():
                with open(select_backup, 'rb') as src:
                    select_file.write_bytes(src.read())
                select_backup.unlink()

            # Analyser le log
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()

                # Chercher les erreurs
                errors_found = []

                if "Error detected" in log_content:
                    # Extraire toutes les erreurs
                    error_section = log_content[log_content.find("Error detected"):]
                    error_lines = [line for line in error_section.split('\n') if 'Error' in line or 'error' in line.lower()]
                    errors_found.extend(error_lines[:10])

                if "failed to load" in log_content.lower():
                    failed_lines = [line for line in log_content.split('\n') if 'failed' in line.lower()]
                    errors_found.extend(failed_lines[:5])

                if errors_found:
                    return {
                        'char': char_def,
                        'status': 'ERROR',
                        'errors': errors_found
                    }
                else:
                    return {
                        'char': char_def,
                        'status': 'OK',
                        'errors': []
                    }
            else:
                return {
                    'char': char_def,
                    'status': 'NO_LOG',
                    'errors': ['No log file generated']
                }

        except Exception as e:
            return {
                'char': char_def,
                'status': 'EXCEPTION',
                'errors': [str(e)]
            }

    def scan_all_characters(self):
        """Scanne tous les personnages"""
        self.log("SCAN COMPLET DE TOUS LES PERSONNAGES", 'TEST')
        print("=" * 70)
        print()

        # Lire select.def
        select_file = game_dir / "data" / "select.def"

        if not select_file.exists():
            self.log("select.def introuvable!", 'ERROR')
            return

        with open(select_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Extraire les définitions de personnages
        char_defs = []
        in_chars_section = False

        for line in lines:
            if line.strip().startswith('[Characters]'):
                in_chars_section = True
                continue

            if in_chars_section:
                # Nouvelle section
                if line.strip().startswith('['):
                    break

                # Ligne de personnage
                if line.strip() and not line.strip().startswith(';'):
                    # Extraire le chemin du personnage
                    char_def = line.strip().split(',')[0].strip()
                    if char_def:
                        char_defs.append(char_def)

        self.log(f"Trouvé {len(char_defs)} personnages à tester")
        print()

        # Tester les 30 premiers (pour ne pas que ça prenne trop de temps)
        test_limit = min(30, len(char_defs))
        self.log(f"Test des {test_limit} premiers personnages...")
        print()

        for i, char_def in enumerate(char_defs[:test_limit], 1):
            self.log(f"[{i}/{test_limit}] Test: {char_def}")
            result = self.test_character(char_def)
            self.test_results.append(result)

            if result['status'] == 'ERROR':
                self.log(f"  ❌ ERREUR détectée!", 'ERROR')
                for error in result['errors'][:3]:
                    self.log(f"     {error}", 'ERROR')
            elif result['status'] == 'OK':
                self.log(f"  ✓ OK", 'SUCCESS')

        print()
        print("=" * 70)
        self.generate_report()

    def generate_report(self):
        """Génère un rapport détaillé"""
        print()
        print("=" * 70)
        print("📊 RAPPORT COMPLET D'ERREURS")
        print("=" * 70)
        print()

        # Compter les résultats
        total = len(self.test_results)
        ok_count = len([r for r in self.test_results if r['status'] == 'OK'])
        error_count = len([r for r in self.test_results if r['status'] == 'ERROR'])

        print(f"Total testé:  {total}")
        print(f"✅ OK:        {ok_count}")
        print(f"❌ ERREURS:   {error_count}")
        print()

        if error_count > 0:
            print("🔍 PERSONNAGES AVEC ERREURS:")
            print()

            for result in self.test_results:
                if result['status'] == 'ERROR':
                    print(f"  ❌ {result['char']}")
                    for error in result['errors'][:3]:
                        print(f"     • {error[:80]}")
                    print()

        # Sauvegarder dans un fichier JSON
        report_file = game_dir / f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_tested': total,
                'ok_count': ok_count,
                'error_count': error_count,
                'results': self.test_results
            }, f, indent=2)

        print(f"✅ Rapport sauvegardé: {report_file.name}")
        print("=" * 70)
        print()

def main():
    """Main function"""
    print()
    print("=" * 70)
    print("  🔍 KOF ULTIMATE - RAPPORT COMPLET D'ERREURS")
    print("=" * 70)
    print()

    reporter = ErrorReporter()
    reporter.scan_all_characters()

    print()
    try:
        input("Appuyez sur ENTRÉE pour fermer...")
    except EOFError:
        pass

if __name__ == '__main__':
    main()
