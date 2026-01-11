#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE - VALIDATEUR/TESTEUR AUTOMATIQUE COMPLET
Teste TOUT: menus, launchers, personnages, stages
"""

import subprocess
import time
import psutil
import re
from pathlib import Path
from datetime import datetime

game_dir = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo kofuo Online kofuo kofuo Online kofuo kofuo")
log_file = game_dir / "mugen.log"

class KOFValidator:
    """Validateur complet KOF Ultimate"""

    def __init__(self):
        self.game_dir = game_dir
        self.errors = []
        self.warnings = []
        self.tests_passed = 0
        self.tests_failed = 0

    def log(self, message, level='INFO'):
        """Log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbol = {
            'INFO': 'ℹ️',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'TEST': '🧪'
        }.get(level, '•')
        print(f"[{timestamp}] {symbol} {message}")

    def test_launchers(self):
        """Test tous les launchers"""
        self.log("TEST LAUNCHERS", 'TEST')
        print("=" * 70)

        launchers = [
            "launcher.py",
            "launcher_modern.py",
            "LAUNCHER_ULTIMATE.py",
            "LAUNCHER_ULTIMATE_V2.py",
            "character_dashboard.py",
            "visual_inspector.py"
        ]

        for launcher in launchers:
            launcher_path = self.game_dir / launcher
            if launcher_path.exists():
                self.log(f"Test: {launcher}")
                # Just check if file is valid Python
                try:
                    with open(launcher_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), launcher, 'exec')
                    self.log(f"  ✓ {launcher} - Syntaxe OK", 'SUCCESS')
                    self.tests_passed += 1
                except SyntaxError as e:
                    self.log(f"  ✗ {launcher} - Erreur syntaxe: {e}", 'ERROR')
                    self.errors.append(f"{launcher}: {e}")
                    self.tests_failed += 1
            else:
                self.log(f"  ! {launcher} - Introuvable", 'WARNING')
                self.warnings.append(f"{launcher} not found")

        print()

    def test_air_files(self):
        """Test tous les fichiers AIR"""
        self.log("TEST FICHIERS AIR", 'TEST')
        print("=" * 70)

        chars_dir = self.game_dir / "chars"
        air_files = list(chars_dir.rglob("*.air"))

        self.log(f"Trouvé {len(air_files)} fichiers AIR")

        errors_found = []

        for air_file in air_files:
            errors = self.validate_air_file(air_file)
            if errors:
                errors_found.append({
                    'file': air_file,
                    'errors': errors
                })

        if errors_found:
            self.log(f"Erreurs dans {len(errors_found)} fichiers", 'ERROR')
            self.tests_failed += len(errors_found)

            # Show first 10
            for item in errors_found[:10]:
                rel_path = item['file'].relative_to(self.game_dir)
                self.log(f"  ❌ {rel_path}")
                for err in item['errors'][:3]:
                    self.log(f"     • {err}", 'ERROR')

            if len(errors_found) > 10:
                self.log(f"  ... et {len(errors_found)-10} autres fichiers avec erreurs")
        else:
            self.log("Tous les AIR files sont valides!", 'SUCCESS')
            self.tests_passed += 1

        print()

    def validate_air_file(self, air_file):
        """Valide un fichier AIR"""
        errors = []

        try:
            with open(air_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            # Check for literal \n
            for i, line in enumerate(lines, 1):
                if r'\n' in line and not line.strip().startswith(';'):
                    errors.append(f"Line {i}: Literal \\n found")

            # Check for Clsn structure
            in_action = False
            clsn1_count = None
            clsn2_count = None
            clsn1_boxes = 0
            clsn2_boxes = 0
            action_num = None

            for i, line in enumerate(lines, 1):
                # Action start
                match = re.match(r'^\[Begin Action (\d+)\]', line, re.IGNORECASE)
                if match:
                    # Validate previous action
                    if in_action and action_num is not None:
                        if clsn1_count is not None and clsn1_boxes != clsn1_count:
                            errors.append(f"Action {action_num}: Clsn1 count mismatch (declared {clsn1_count}, found {clsn1_boxes})")
                        if clsn2_count is not None and clsn2_boxes != clsn2_count:
                            errors.append(f"Action {action_num}: Clsn2 count mismatch (declared {clsn2_count}, found {clsn2_boxes})")

                    # Reset
                    in_action = True
                    action_num = int(match.group(1))
                    clsn1_count = None
                    clsn2_count = None
                    clsn1_boxes = 0
                    clsn2_boxes = 0
                    continue

                # Clsn counters
                match = re.match(r'^\s*Clsn1:\s*(\d+)', line)
                if match:
                    count = int(match.group(1))
                    if clsn1_count is not None:
                        errors.append(f"Line {i}: Redundant Clsn1 counter")
                    clsn1_count = count

                match = re.match(r'^\s*Clsn2:\s*(\d+)', line)
                if match:
                    count = int(match.group(1))
                    if clsn2_count is not None:
                        errors.append(f"Line {i}: Redundant Clsn2 counter")
                    clsn2_count = count

                # Clsn boxes
                if re.match(r'^\s*Clsn1\[\d+\]', line):
                    clsn1_boxes += 1
                if re.match(r'^\s*Clsn2\[\d+\]', line):
                    clsn2_boxes += 1

        except Exception as e:
            errors.append(f"Failed to validate: {e}")

        return errors

    def test_game_launch(self):
        """Test lancement du jeu"""
        self.log("TEST LANCEMENT DU JEU", 'TEST')
        print("=" * 70)

        exe_path = self.game_dir / "KOF_Ultimate_Online.exe"

        if not exe_path.exists():
            self.log("KOF_Ultimate_Online.exe introuvable!", 'ERROR')
            self.tests_failed += 1
            return

        # Clear log
        if log_file.exists():
            log_file.unlink()

        self.log("Lancement du jeu...")

        try:
            proc = subprocess.Popen(
                [str(exe_path)],
                cwd=str(self.game_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait for log to be created
            time.sleep(5)

            # Check if still running
            if proc.poll() is None:
                self.log("Jeu lancé avec succès", 'SUCCESS')
                self.tests_passed += 1

                # Kill after 10 seconds
                time.sleep(10)
                proc.terminate()
                time.sleep(2)
                if proc.poll() is None:
                    proc.kill()

                # Check log
                if log_file.exists():
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()

                    # Check for errors
                    if "Error detected" in log_content or "failed to load" in log_content.lower():
                        self.log("ERREURS DÉTECTÉES dans mugen.log!", 'ERROR')
                        self.tests_failed += 1

                        # Extract errors
                        error_lines = [line for line in log_content.split('\n') if 'error' in line.lower()]
                        for err_line in error_lines[:5]:
                            self.log(f"  {err_line.strip()}", 'ERROR')
                    else:
                        self.log("Aucune erreur dans le log", 'SUCCESS')
                        self.tests_passed += 1
            else:
                self.log("Le jeu s'est arrêté immédiatement!", 'ERROR')
                self.tests_failed += 1

        except Exception as e:
            self.log(f"Erreur lors du test: {e}", 'ERROR')
            self.tests_failed += 1

        print()

    def generate_report(self):
        """Génère le rapport final"""
        print()
        print("=" * 70)
        print("📊 RAPPORT FINAL DE VALIDATION")
        print("=" * 70)
        print(f"✅ Tests réussis: {self.tests_passed}")
        print(f"❌ Tests échoués: {self.tests_failed}")
        print(f"⚠️  Avertissements: {len(self.warnings)}")
        print()

        if self.errors:
            print(f"ERREURS CRITIQUES ({len(self.errors)}):")
            for err in self.errors[:20]:
                print(f"  • {err}")
            if len(self.errors) > 20:
                print(f"  ... et {len(self.errors)-20} autres")
            print()

        total_tests = self.tests_passed + self.tests_failed
        if total_tests > 0:
            success_rate = (self.tests_passed / total_tests) * 100
            print(f"Taux de réussite: {success_rate:.1f}%")

        print("=" * 70)

        return len(self.errors) == 0 and self.tests_failed == 0

def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("  🔍 KOF ULTIMATE - VALIDATEUR/TESTEUR AUTOMATIQUE COMPLET")
    print("=" * 70)
    print()

    validator = KOFValidator()

    # Run all tests
    validator.test_launchers()
    validator.test_air_files()
    validator.test_game_launch()

    # Generate report
    success = validator.generate_report()

    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
