#!/usr/bin/env python3
"""
AUDIT PROFESSIONNEL - KOF ULTIMATE ONLINE
Test complet de tous les composants du jeu
"""

import os
import glob
import json
from datetime import datetime

class GameAuditor:
    def __init__(self, game_path):
        self.game_path = game_path
        self.ikemen_path = os.path.join(game_path, 'Ikemen_GO')
        self.report = {
            'date': datetime.now().isoformat(),
            'system_files': {},
            'characters': {'total': 0, 'working': 0, 'broken': [], 'warnings': []},
            'stages': {'total': 0, 'working': 0, 'broken': []},
            'critical_bugs': [],
            'warnings': [],
            'score': 0
        }

    def check_system_files(self):
        """Verifie les fichiers systeme essentiels"""
        print("\n[1/5] VERIFICATION FICHIERS SYSTEME")
        print("=" * 50)

        required_files = [
            ('data/common.const', True),
            ('data/common.air', True),
            ('data/common.cmd', True),
            ('data/common.snd', True),
            ('data/common1.cns', False),
            ('data/system.def', True),
            ('data/select.def', True),
            ('data/fight.def', True),
        ]

        for file_path, critical in required_files:
            full_path = os.path.join(self.ikemen_path, file_path)
            exists = os.path.exists(full_path)
            size = os.path.getsize(full_path) if exists else 0

            status = 'OK' if exists and size > 0 else 'MISSING' if not exists else 'EMPTY'

            self.report['system_files'][file_path] = {
                'exists': exists,
                'size': size,
                'status': status,
                'critical': critical
            }

            icon = '✅' if status == 'OK' else '❌' if critical else '⚠️'
            print(f"  {icon} {file_path}: {status} ({size} bytes)")

            if status != 'OK' and critical:
                self.report['critical_bugs'].append(f"Fichier manquant: {file_path}")

    def check_characters(self):
        """Verifie tous les personnages"""
        print("\n[2/5] VERIFICATION PERSONNAGES")
        print("=" * 50)

        chars_path = os.path.join(self.ikemen_path, 'chars')
        if not os.path.exists(chars_path):
            print("  ❌ Dossier chars introuvable!")
            return

        char_dirs = [d for d in os.listdir(chars_path) if os.path.isdir(os.path.join(chars_path, d))]
        self.report['characters']['total'] = len(char_dirs)

        for char_name in char_dirs:
            char_path = os.path.join(chars_path, char_name)
            issues = []

            # Check for .def file
            def_files = glob.glob(os.path.join(char_path, '*.def'))
            if not def_files:
                issues.append('No .def file')
            else:
                # Check def content
                for def_file in def_files:
                    try:
                        with open(def_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        # Check for problematic references
                        if 'stcommon' in content.lower():
                            for line in content.split('\n'):
                                if 'stcommon' in line.lower() and not line.strip().startswith(';'):
                                    if 'common1.cns' in line or 'common.cns' in line:
                                        issues.append('Invalid stcommon reference')
                                        break

                        if 'common.const' in content.lower():
                            issues.append('References common.const')

                    except Exception as e:
                        issues.append(f'Read error: {str(e)[:30]}')

            # Check for .sff (sprite) file
            sff_files = glob.glob(os.path.join(char_path, '*.sff'))
            if not sff_files:
                issues.append('No sprite file')

            if issues:
                self.report['characters']['broken'].append({
                    'name': char_name,
                    'issues': issues
                })
            else:
                self.report['characters']['working'] += 1

        working = self.report['characters']['working']
        total = self.report['characters']['total']
        broken = len(self.report['characters']['broken'])

        print(f"  📊 Total: {total} personnages")
        print(f"  ✅ Fonctionnels: {working}")
        print(f"  ❌ Problematiques: {broken}")

        if broken > 0:
            print(f"\n  Personnages a corriger:")
            for char in self.report['characters']['broken'][:10]:
                print(f"    - {char['name']}: {', '.join(char['issues'])}")
            if broken > 10:
                print(f"    ... et {broken - 10} autres")

    def check_stages(self):
        """Verifie tous les stages"""
        print("\n[3/5] VERIFICATION STAGES")
        print("=" * 50)

        stages_path = os.path.join(self.ikemen_path, 'stages')
        if not os.path.exists(stages_path):
            print("  ❌ Dossier stages introuvable!")
            return

        stage_files = glob.glob(os.path.join(stages_path, '*.def'))
        self.report['stages']['total'] = len(stage_files)

        for stage_file in stage_files:
            stage_name = os.path.basename(stage_file)
            issues = []

            # Check for corresponding .sff
            sff_file = stage_file.replace('.def', '.sff')
            if not os.path.exists(sff_file):
                issues.append('Missing .sff file')

            # Check def file content
            try:
                with open(stage_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if len(content) < 100:
                    issues.append('File too small')
            except:
                issues.append('Read error')

            if issues:
                self.report['stages']['broken'].append({
                    'name': stage_name,
                    'issues': issues
                })
            else:
                self.report['stages']['working'] += 1

        print(f"  📊 Total: {self.report['stages']['total']} stages")
        print(f"  ✅ Fonctionnels: {self.report['stages']['working']}")
        print(f"  ❌ Problematiques: {len(self.report['stages']['broken'])}")

    def check_config(self):
        """Verifie la configuration"""
        print("\n[4/5] VERIFICATION CONFIGURATION")
        print("=" * 50)

        # Check select.def
        select_def = os.path.join(self.ikemen_path, 'data', 'select.def')
        if os.path.exists(select_def):
            with open(select_def, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Count enabled characters
            char_lines = [l for l in content.split('\n') if l.strip() and not l.strip().startswith(';') and ',' in l]
            print(f"  📋 Personnages dans select.def: {len(char_lines)}")

        # Check system.def
        system_def = os.path.join(self.ikemen_path, 'data', 'system.def')
        if os.path.exists(system_def):
            print(f"  ✅ system.def present")
        else:
            print(f"  ❌ system.def manquant")
            self.report['critical_bugs'].append("system.def manquant")

    def check_logs(self):
        """Analyse les logs d'erreur"""
        print("\n[5/5] ANALYSE DES LOGS")
        print("=" * 50)

        log_file = os.path.join(self.ikemen_path, 'Ikemen.log')
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract errors
            errors = []
            for line in content.split('\n'):
                if 'error' in line.lower() or 'cannot find' in line.lower():
                    errors.append(line.strip()[:80])

            if errors:
                print(f"  ⚠️ {len(errors)} erreurs dans le log")
                for err in errors[:5]:
                    print(f"    - {err}")
            else:
                print(f"  ✅ Pas d'erreurs recentes")
        else:
            print(f"  ℹ️ Pas de fichier log")

    def calculate_score(self):
        """Calcule un score de qualite"""
        score = 100

        # Penalite fichiers systeme
        for file_info in self.report['system_files'].values():
            if file_info['status'] != 'OK' and file_info['critical']:
                score -= 15

        # Penalite personnages
        broken_ratio = len(self.report['characters']['broken']) / max(1, self.report['characters']['total'])
        score -= int(broken_ratio * 30)

        # Penalite stages
        broken_stages = len(self.report['stages']['broken']) / max(1, self.report['stages']['total'])
        score -= int(broken_stages * 10)

        # Penalite bugs critiques
        score -= len(self.report['critical_bugs']) * 10

        self.report['score'] = max(0, score)
        return self.report['score']

    def run_audit(self):
        """Execute l'audit complet"""
        print("\n" + "=" * 60)
        print("  AUDIT PROFESSIONNEL - KOF ULTIMATE ONLINE")
        print("=" * 60)

        self.check_system_files()
        self.check_characters()
        self.check_stages()
        self.check_config()
        self.check_logs()

        score = self.calculate_score()

        print("\n" + "=" * 60)
        print("  RESULTAT DE L'AUDIT")
        print("=" * 60)

        print(f"\n  📊 SCORE QUALITE: {score}/100")

        if score >= 80:
            print("  ✅ Statut: PRET POUR RELEASE")
        elif score >= 60:
            print("  ⚠️ Statut: CORRECTIONS NECESSAIRES")
        elif score >= 40:
            print("  🔧 Statut: TRAVAIL SIGNIFICATIF REQUIS")
        else:
            print("  ❌ Statut: NON JOUABLE")

        # Save report
        report_path = os.path.join(self.game_path, 'AUDIT_REPORT.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)

        print(f"\n  📄 Rapport sauvegarde: AUDIT_REPORT.json")

        return self.report


if __name__ == '__main__':
    auditor = GameAuditor('D:/KOF Ultimate Online')
    auditor.run_audit()
