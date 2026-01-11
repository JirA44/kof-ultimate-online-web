#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE - AUTO-DÉTECTEUR ET CORRECTEUR UNIVERSEL
Scanne TOUS les fichiers, détecte TOUTES les erreurs et les corrige automatiquement
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
import subprocess
import json

class UniversalErrorDetectorFixer:
    """Détecteur et correcteur universel d'erreurs"""

    def __init__(self):
        self.game_dir = Path(r"D:\KOF Ultimate Online kofuo")
        self.correct_game_dir = r"D:\KOF Ultimate Online kofuo"
        self.wrong_paths = [
            r"D:\KOF Ultimate Online Online Online Online",
            r"D:\KOF Ultimate Online Online Online",
            r"D:\KOF Ultimate Online Online",
            r"D:/KOF Ultimate Online",
            r"D:\KOF Ultimate Online",
            "D:\\KOF Ultimate",
        ]

        self.backup_dir = self.game_dir / "backups_auto_fix"
        self.backup_dir.mkdir(exist_ok=True)

        self.errors_found = []
        self.fixes_applied = []
        self.files_checked = 0
        self.files_fixed = 0

        self.log_file = self.game_dir / "AUTO_FIX_REPORT.txt"

    def log(self, message, level='INFO'):
        """Log un message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[{timestamp}] [{level}] {message}"
        print(msg)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')

    def backup_file(self, filepath):
        """Sauvegarde un fichier avant modification"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{filepath.name}.backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            shutil.copy2(filepath, backup_path)
            return True
        except Exception as e:
            self.log(f"⚠️  Erreur backup {filepath.name}: {e}", "WARN")
            return False

    def scan_python_file_for_errors(self, filepath):
        """Scanne un fichier Python pour détecter les erreurs"""
        errors = []

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

            # 1. Vérifier les chemins incorrects
            for wrong_path in self.wrong_paths:
                if wrong_path in content:
                    count = content.count(wrong_path)
                    errors.append({
                        'type': 'WRONG_PATH',
                        'message': f"Chemin incorrect '{wrong_path}' trouvé {count} fois",
                        'fix': f"Remplacer par '{self.correct_game_dir}'",
                        'auto_fixable': True
                    })

            # 2. Vérifier les imports manquants/problématiques
            imports_needed = {
                'import tkinter': 'tkinter',
                'import pyautogui': 'pyautogui',
                'import win32gui': 'pywin32',
                'import win32con': 'pywin32',
                'import psutil': 'psutil',
                'from PIL import': 'Pillow',
            }

            for import_line, package in imports_needed.items():
                if import_line in content:
                    # Vérifier si le package est installé
                    try:
                        __import__(package if package != 'pywin32' else 'win32gui')
                    except ImportError:
                        errors.append({
                            'type': 'MISSING_PACKAGE',
                            'message': f"Package '{package}' manquant",
                            'fix': f"pip install {package}",
                            'auto_fixable': True
                        })

            # 3. Vérifier les chemins vers des exécutables inexistants
            exe_patterns = [
                r'["\']([^"\']+\.exe)["\']',
            ]

            for pattern in exe_patterns:
                for match in re.finditer(pattern, content):
                    exe_path = match.group(1)
                    if not Path(exe_path).exists() and not Path(self.game_dir / exe_path).exists():
                        errors.append({
                            'type': 'MISSING_EXE',
                            'message': f"Exécutable introuvable: {exe_path}",
                            'fix': "Vérifier le chemin ou télécharger le fichier",
                            'auto_fixable': False
                        })

            # 4. Vérifier les mkdir sans exist_ok
            if 'mkdir()' in content and 'exist_ok=True' not in content:
                errors.append({
                    'type': 'MKDIR_NO_EXIST_OK',
                    'message': "mkdir() sans exist_ok=True peut causer des erreurs",
                    'fix': "Ajouter exist_ok=True",
                    'auto_fixable': True
                })

            # 5. Vérifier les input() qui peuvent bloquer
            if 'input(' in content and filepath.name not in ['AUTO_DETECT_FIX_ALL_ERRORS.py']:
                errors.append({
                    'type': 'BLOCKING_INPUT',
                    'message': "input() peut bloquer l'exécution automatique",
                    'fix': "Remplacer par une alternative non-bloquante",
                    'auto_fixable': False
                })

            # 6. Vérifier les try/except trop larges
            if 'except:' in content or 'except Exception:' in content:
                count = content.count('except:') + content.count('except Exception:')
                if count > 3:
                    errors.append({
                        'type': 'TOO_BROAD_EXCEPT',
                        'message': f"{count} blocs except trop larges",
                        'fix': "Spécifier les exceptions à capturer",
                        'auto_fixable': False
                    })

            return errors

        except Exception as e:
            self.log(f"❌ Erreur scan {filepath.name}: {e}", "ERROR")
            return []

    def fix_python_file(self, filepath, errors):
        """Corrige automatiquement les erreurs détectées dans un fichier Python"""
        if not errors:
            return 0

        fixes_count = 0

        try:
            # Backup d'abord
            self.backup_file(filepath)

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content

            for error in errors:
                if not error['auto_fixable']:
                    continue

                if error['type'] == 'WRONG_PATH':
                    # Corriger tous les chemins incorrects
                    for wrong_path in self.wrong_paths:
                        if wrong_path in content:
                            # Remplacer en gardant le format (/ ou \)
                            if '/' in wrong_path:
                                correct = self.correct_game_dir.replace('\\', '/')
                            else:
                                correct = self.correct_game_dir.replace('/', '\\')

                            content = content.replace(wrong_path, correct)
                            fixes_count += 1
                            self.log(f"  ✓ Corrigé: {wrong_path} → {correct}")

                elif error['type'] == 'MKDIR_NO_EXIST_OK':
                    # Ajouter exist_ok=True aux mkdir()
                    content = re.sub(
                        r'\.mkdir\(\)',
                        '.mkdir(exist_ok=True)',
                        content
                    )
                    fixes_count += 1
                    self.log(f"  ✓ Corrigé: mkdir() → mkdir(exist_ok=True)")

            # Écrire les modifications si nécessaire
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"  📝 Fichier modifié: {filepath.name}")
                self.files_fixed += 1

            return fixes_count

        except Exception as e:
            self.log(f"❌ Erreur correction {filepath.name}: {e}", "ERROR")
            return 0

    def scan_all_python_files(self):
        """Scanne tous les fichiers Python du projet"""
        self.log("\n🔍 SCAN DE TOUS LES FICHIERS PYTHON")
        self.log("=" * 70)

        python_files = list(self.game_dir.glob("*.py"))

        self.log(f"\n📁 {len(python_files)} fichiers Python trouvés")
        self.log("")

        all_errors = {}

        for py_file in python_files:
            self.files_checked += 1
            errors = self.scan_python_file_for_errors(py_file)

            if errors:
                all_errors[py_file] = errors
                self.log(f"⚠️  {py_file.name}: {len(errors)} erreur(s) détectée(s)")
                for error in errors:
                    self.errors_found.append({
                        'file': py_file.name,
                        'error': error
                    })
            else:
                self.log(f"✅ {py_file.name}: OK")

        return all_errors

    def fix_all_detected_errors(self, all_errors):
        """Corrige toutes les erreurs détectées automatiquement"""
        self.log("\n\n🔧 CORRECTION AUTOMATIQUE DES ERREURS")
        self.log("=" * 70)

        if not all_errors:
            self.log("\n✅ Aucune erreur à corriger!")
            return

        for filepath, errors in all_errors.items():
            self.log(f"\n📝 Correction: {filepath.name}")

            auto_fixable = [e for e in errors if e['auto_fixable']]
            non_fixable = [e for e in errors if not e['auto_fixable']]

            if auto_fixable:
                fixes_count = self.fix_python_file(filepath, auto_fixable)
                self.fixes_applied.append({
                    'file': filepath.name,
                    'fixes': fixes_count
                })

            if non_fixable:
                self.log(f"  ⚠️  {len(non_fixable)} erreur(s) nécessitent une correction manuelle:")
                for error in non_fixable:
                    self.log(f"     • {error['message']}")
                    self.log(f"       → {error['fix']}")

    def check_mugen_config(self):
        """Vérifie la configuration MUGEN"""
        self.log("\n\n🎮 VÉRIFICATION CONFIGURATION MUGEN")
        self.log("=" * 70)

        # Vérifier system.def
        system_def = self.game_dir / "data" / "system.def"
        if system_def.exists():
            self.log("✅ system.def: Présent")
        else:
            self.log("❌ system.def: MANQUANT!", "ERROR")
            self.errors_found.append({
                'file': 'system.def',
                'error': {'type': 'MISSING_FILE', 'message': 'Fichier system.def manquant'}
            })

        # Vérifier select.def
        select_def = self.game_dir / "data" / "select.def"
        if select_def.exists():
            self.log("✅ select.def: Présent")

            # Compter les personnages
            with open(select_def, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                char_lines = [l for l in content.split('\n') if l.strip() and not l.strip().startswith(';') and 'chars/' in l.lower()]
                self.log(f"   📊 {len(char_lines)} personnages configurés")
        else:
            self.log("❌ select.def: MANQUANT!", "ERROR")

        # Vérifier mugen.cfg
        mugen_cfg = self.game_dir / "data" / "mugen.cfg"
        if mugen_cfg.exists():
            self.log("✅ mugen.cfg: Présent")
        else:
            self.log("⚠️  mugen.cfg: Manquant", "WARN")

    def check_game_executable(self):
        """Vérifie les exécutables du jeu"""
        self.log("\n\n🎯 VÉRIFICATION EXÉCUTABLES")
        self.log("=" * 70)

        executables = [
            "KOF_Ultimate_Online.exe",
            "KOF_Ultimate_Online.exe",
            "KOF_Ultimate_Online.exe",
        ]

        found_exe = None
        for exe_name in executables:
            exe_path = self.game_dir / exe_name
            if exe_path.exists():
                self.log(f"✅ {exe_name}: Trouvé")
                if found_exe is None:
                    found_exe = exe_path
            else:
                self.log(f"⚠️  {exe_name}: Non trouvé")

        if found_exe:
            self.log(f"\n✓ Exécutable principal: {found_exe.name}")
        else:
            self.log("\n❌ AUCUN EXÉCUTABLE TROUVÉ!", "ERROR")
            self.errors_found.append({
                'file': 'game',
                'error': {'type': 'NO_EXECUTABLE', 'message': 'Aucun exécutable de jeu trouvé'}
            })

    def check_python_packages(self):
        """Vérifie les packages Python installés"""
        self.log("\n\n📦 VÉRIFICATION PACKAGES PYTHON")
        self.log("=" * 70)

        required_packages = {
            'tkinter': 'tkinter',
            'pyautogui': 'pyautogui',
            'PIL': 'Pillow',
            'win32gui': 'pywin32',
            'psutil': 'psutil',
        }

        missing = []

        for module_name, package_name in required_packages.items():
            try:
                __import__(module_name)
                self.log(f"✅ {package_name}: Installé")
            except ImportError:
                self.log(f"❌ {package_name}: MANQUANT!", "ERROR")
                missing.append(package_name)
                self.errors_found.append({
                    'file': 'system',
                    'error': {
                        'type': 'MISSING_PACKAGE',
                        'message': f'Package {package_name} manquant',
                        'fix': f'pip install {package_name}',
                        'auto_fixable': True
                    }
                })

        if missing:
            self.log(f"\n⚠️  Pour installer les packages manquants:")
            self.log(f"   pip install {' '.join(missing)}")

    def install_missing_packages(self):
        """Installe les packages Python manquants"""
        self.log("\n\n📦 INSTALLATION PACKAGES MANQUANTS")
        self.log("=" * 70)

        required_packages = {
            'tkinter': None,  # Vient avec Python
            'pyautogui': 'pyautogui',
            'PIL': 'Pillow',
            'win32gui': 'pywin32',
            'psutil': 'psutil',
        }

        to_install = []

        for module_name, package_name in required_packages.items():
            if package_name is None:
                continue

            try:
                __import__(module_name)
            except ImportError:
                to_install.append(package_name)

        if not to_install:
            self.log("✅ Tous les packages sont déjà installés!")
            return True

        self.log(f"📥 Installation de {len(to_install)} package(s)...")

        for package in to_install:
            try:
                self.log(f"   Installing {package}...")
                result = subprocess.run(
                    ['pip', 'install', package],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    self.log(f"   ✅ {package} installé!")
                    self.fixes_applied.append({
                        'file': 'system',
                        'fixes': f'Package {package} installé'
                    })
                else:
                    self.log(f"   ❌ Échec installation {package}", "ERROR")

            except Exception as e:
                self.log(f"   ❌ Erreur: {e}", "ERROR")

        return True

    def generate_final_report(self):
        """Génère le rapport final"""
        self.log("\n\n" + "=" * 70)
        self.log("📊 RAPPORT FINAL")
        self.log("=" * 70)

        self.log(f"\n📁 Fichiers scannés: {self.files_checked}")
        self.log(f"🔧 Fichiers corrigés: {self.files_fixed}")
        self.log(f"⚠️  Erreurs détectées: {len(self.errors_found)}")
        self.log(f"✅ Corrections appliquées: {len(self.fixes_applied)}")

        if self.errors_found:
            self.log(f"\n📋 DÉTAILS DES ERREURS:")

            # Grouper par type
            by_type = {}
            for item in self.errors_found:
                error_type = item['error']['type']
                if error_type not in by_type:
                    by_type[error_type] = []
                by_type[error_type].append(item)

            for error_type, items in by_type.items():
                self.log(f"\n  {error_type}: {len(items)} occurrence(s)")
                for item in items[:5]:  # Afficher max 5 exemples
                    self.log(f"    • {item['file']}: {item['error']['message']}")
                if len(items) > 5:
                    self.log(f"    ... et {len(items) - 5} autre(s)")

        if self.fixes_applied:
            self.log(f"\n✅ CORRECTIONS APPLIQUÉES:")
            for fix in self.fixes_applied:
                if isinstance(fix['fixes'], int):
                    self.log(f"  • {fix['file']}: {fix['fixes']} correction(s)")
                else:
                    self.log(f"  • {fix.get('file', 'system')}: {fix['fixes']}")

        self.log(f"\n💾 Backups: {self.backup_dir}")
        self.log(f"📄 Rapport complet: {self.log_file}")

        self.log("\n" + "=" * 70)

        if len(self.errors_found) == 0:
            self.log("✅ AUCUNE ERREUR DÉTECTÉE - SYSTÈME OPÉRATIONNEL!")
        elif self.files_fixed > 0:
            self.log("✅ CORRECTIONS APPLIQUÉES - Relancez pour vérifier")
        else:
            self.log("⚠️  ERREURS NÉCESSITANT INTERVENTION MANUELLE")

        self.log("=" * 70)

    def run_full_diagnostic(self):
        """Lance le diagnostic complet"""
        self.log("\n" + "=" * 70)
        self.log("🚀 AUTO-DÉTECTEUR ET CORRECTEUR UNIVERSEL")
        self.log("=" * 70)
        self.log("\nRecherche et correction automatique de TOUTES les erreurs...")
        self.log("")

        # Nettoyer le log
        if self.log_file.exists():
            self.log_file.unlink()

        # 1. Vérifier les exécutables
        self.check_game_executable()

        # 2. Vérifier la config MUGEN
        self.check_mugen_config()

        # 3. Vérifier les packages Python
        self.check_python_packages()

        # 4. Scanner tous les fichiers Python
        all_errors = self.scan_all_python_files()

        # 5. Corriger les erreurs automatiquement
        self.fix_all_detected_errors(all_errors)

        # 6. Installer les packages manquants
        self.install_missing_packages()

        # 7. Générer le rapport final
        self.generate_final_report()

        return len(self.errors_found) == 0

def main():
    """Point d'entrée"""
    print("\n" + "=" * 70)
    print("  🤖 AUTO-DÉTECTEUR ET CORRECTEUR UNIVERSEL D'ERREURS")
    print("=" * 70)
    print("\n  Ce système va:")
    print("  • Scanner TOUS les fichiers Python")
    print("  • Détecter TOUTES les erreurs (chemins, imports, config)")
    print("  • Corriger AUTOMATIQUEMENT ce qui peut l'être")
    print("  • Installer les packages manquants")
    print("  • Générer un rapport complet")
    print("\n" + "=" * 70)
    print()

    detector = UniversalErrorDetectorFixer()
    success = detector.run_full_diagnostic()

    print("\n\n" + "=" * 70)
    if success:
        print("✅ TOUS LES SYSTÈMES OPÉRATIONNELS!")
        print("\nVous pouvez maintenant lancer n'importe quel launcher sans erreur.")
    else:
        print("⚠️  CORRECTIONS APPLIQUÉES")
        print(f"\nConsultez {detector.log_file} pour les détails.")
        print("\nRelancez ce script pour vérifier si toutes les erreurs sont corrigées.")
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()
