#!/usr/bin/env python3
"""
=================================================================
  KOF ULTIMATE ONLINE - SUITE DE TESTS QA PROFESSIONNELLE
  Tests automatisés complets comme si le jeu était sorti
=================================================================
"""

import os
import sys
import json
import glob
import time
import subprocess
import re
from datetime import datetime
from pathlib import Path

class KOFQATester:
    def __init__(self, game_path):
        self.game_path = Path(game_path)
        self.ikemen_path = self.game_path / 'Ikemen_GO'
        self.report = {
            'test_date': datetime.now().isoformat(),
            'version': 'KOF Ultimate Online v2.0',
            'tests': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            },
            'critical_issues': [],
            'recommendations': []
        }

    def log(self, msg, level='INFO'):
        icons = {'INFO': 'ℹ️', 'OK': '✅', 'FAIL': '❌', 'WARN': '⚠️', 'TEST': '🧪'}
        print(f"  {icons.get(level, '•')} {msg}")

    def add_test_result(self, category, test_name, passed, details='', warning=False):
        if category not in self.report['tests']:
            self.report['tests'][category] = []

        self.report['tests'][category].append({
            'name': test_name,
            'passed': passed,
            'warning': warning,
            'details': details
        })

        self.report['summary']['total_tests'] += 1
        if passed:
            self.report['summary']['passed'] += 1
        elif warning:
            self.report['summary']['warnings'] += 1
        else:
            self.report['summary']['failed'] += 1

    # =========================================================
    # TEST 1: FICHIERS SYSTEME
    # =========================================================
    def test_system_files(self):
        print("\n" + "="*60)
        print("  🧪 TEST 1: FICHIERS SYSTEME")
        print("="*60)

        required_files = {
            'data/system.def': ('Configuration système', True),
            'data/select.def': ('Sélection personnages', True),
            'data/fight.def': ('Configuration combat', True),
            'data/common.const': ('Constantes communes', True),
            'data/common.air': ('Animations communes', False),
            'data/common.cmd': ('Commandes communes', True),
            'data/common.snd': ('Sons communs', True),
            'data/common1.cns': ('États communs', True),
            'data/functions.zss': ('Fonctions ZSS', True),
            'data/action.zss': ('Actions ZSS', True),
            'data/dizzy.zss': ('Système dizzy', False),
            'data/guardbreak.zss': ('Guard break', False),
            'data/score.zss': ('Système score', False),
            'data/tag.zss': ('Mode tag', False),
            'data/training.zss': ('Mode training', False),
            'Ikemen_GO.exe': ('Exécutable jeu', True),
        }

        for file_path, (desc, critical) in required_files.items():
            full_path = self.ikemen_path / file_path
            exists = full_path.exists()
            size = full_path.stat().st_size if exists else 0

            if exists and size > 0:
                self.log(f"{desc}: OK ({size:,} bytes)", 'OK')
                self.add_test_result('Fichiers Système', f"{desc} ({file_path})", True, f"{size:,} bytes")
            elif exists and size == 0:
                self.log(f"{desc}: VIDE!", 'WARN' if not critical else 'FAIL')
                self.add_test_result('Fichiers Système', f"{desc} ({file_path})", not critical, "Fichier vide", warning=not critical)
                if critical:
                    self.report['critical_issues'].append(f"Fichier vide: {file_path}")
            else:
                self.log(f"{desc}: MANQUANT!", 'FAIL' if critical else 'WARN')
                self.add_test_result('Fichiers Système', f"{desc} ({file_path})", not critical, "Fichier manquant", warning=not critical)
                if critical:
                    self.report['critical_issues'].append(f"Fichier manquant: {file_path}")

    # =========================================================
    # TEST 2: PERSONNAGES
    # =========================================================
    def test_characters(self):
        print("\n" + "="*60)
        print("  🧪 TEST 2: PERSONNAGES (Test individuel)")
        print("="*60)

        chars_path = self.ikemen_path / 'chars'
        if not chars_path.exists():
            self.log("Dossier chars introuvable!", 'FAIL')
            return

        char_dirs = [d for d in chars_path.iterdir() if d.is_dir()]
        total = len(char_dirs)
        working = 0
        issues = []

        print(f"  📊 Analyse de {total} personnages...")

        for char_dir in char_dirs:
            char_name = char_dir.name
            char_issues = []

            # Test 1: Fichier .def existe
            def_files = list(char_dir.glob('*.def'))
            if not def_files:
                char_issues.append('Pas de .def')
            else:
                # Test 2: Contenu du .def valide
                for def_file in def_files:
                    try:
                        content = def_file.read_text(encoding='utf-8', errors='ignore')

                        # Vérifier les sections obligatoires
                        if '[Info]' not in content:
                            char_issues.append('Section [Info] manquante')
                        if '[Files]' not in content:
                            char_issues.append('Section [Files] manquante')

                        # Vérifier les références problématiques
                        for line in content.split('\n'):
                            line_lower = line.lower().strip()
                            if line_lower.startswith('stcommon') and 'common1.cns' in line_lower:
                                if not line_lower.startswith(';'):
                                    char_issues.append('Référence stcommon invalide')
                                    break
                    except Exception as e:
                        char_issues.append(f'Erreur lecture: {str(e)[:20]}')

            # Test 3: Sprites existent
            sff_files = list(char_dir.glob('*.sff'))
            if not sff_files:
                char_issues.append('Pas de sprites (.sff)')

            # Test 4: Animations existent
            air_files = list(char_dir.glob('*.air'))
            if not air_files:
                char_issues.append('Pas d\'animations (.air)')

            # Test 5: États existent
            cns_files = list(char_dir.glob('*.cns'))
            if not cns_files:
                char_issues.append('Pas d\'états (.cns)')

            # Test 6: Commandes existent
            cmd_files = list(char_dir.glob('*.cmd'))
            if not cmd_files:
                char_issues.append('Pas de commandes (.cmd)')

            if char_issues:
                issues.append((char_name, char_issues))
            else:
                working += 1

        # Résumé
        broken = total - working
        success_rate = (working / total * 100) if total > 0 else 0

        print(f"\n  📊 Résultat: {working}/{total} personnages fonctionnels ({success_rate:.1f}%)")

        self.add_test_result('Personnages', f'Total personnages', True, f"{total} détectés")
        self.add_test_result('Personnages', f'Personnages fonctionnels', working >= total * 0.7, f"{working}/{total} ({success_rate:.1f}%)")

        if broken > 0:
            print(f"\n  ❌ {broken} personnages avec problèmes:")
            for char_name, char_issues in issues[:15]:
                print(f"     - {char_name}: {', '.join(char_issues)}")
                self.add_test_result('Personnages', f'Perso: {char_name}', False, ', '.join(char_issues))
            if len(issues) > 15:
                print(f"     ... et {len(issues) - 15} autres")

        if success_rate < 80:
            self.report['critical_issues'].append(f"Seulement {success_rate:.1f}% des personnages sont fonctionnels")

    # =========================================================
    # TEST 3: STAGES
    # =========================================================
    def test_stages(self):
        print("\n" + "="*60)
        print("  🧪 TEST 3: STAGES")
        print("="*60)

        stages_path = self.ikemen_path / 'stages'
        if not stages_path.exists():
            self.log("Dossier stages introuvable!", 'FAIL')
            return

        stage_files = list(stages_path.glob('*.def'))
        total = len(stage_files)
        working = 0
        issues = []

        for stage_file in stage_files:
            stage_name = stage_file.stem
            stage_issues = []

            # Test 1: Fichier .sff correspondant
            sff_file = stage_file.with_suffix('.sff')
            if not sff_file.exists():
                stage_issues.append('Pas de .sff')

            # Test 2: Taille du .def raisonnable
            size = stage_file.stat().st_size
            if size < 100:
                stage_issues.append('Fichier trop petit')

            # Test 3: Contenu valide
            try:
                content = stage_file.read_text(encoding='utf-8', errors='ignore')
                if '[Info]' not in content and '[BGdef]' not in content:
                    stage_issues.append('Format invalide')
            except:
                stage_issues.append('Erreur lecture')

            if stage_issues:
                issues.append((stage_name, stage_issues))
            else:
                working += 1

        success_rate = (working / total * 100) if total > 0 else 0
        print(f"  📊 Résultat: {working}/{total} stages fonctionnels ({success_rate:.1f}%)")

        self.add_test_result('Stages', 'Total stages', True, f"{total} détectés")
        self.add_test_result('Stages', 'Stages fonctionnels', working >= total * 0.8, f"{working}/{total}")

        if issues:
            print(f"\n  ⚠️ Stages avec problèmes:")
            for name, probs in issues[:5]:
                print(f"     - {name}: {', '.join(probs)}")

    # =========================================================
    # TEST 4: CONFIGURATION SELECT.DEF
    # =========================================================
    def test_select_def(self):
        print("\n" + "="*60)
        print("  🧪 TEST 4: CONFIGURATION SELECT.DEF")
        print("="*60)

        select_path = self.ikemen_path / 'data' / 'select.def'
        if not select_path.exists():
            self.log("select.def introuvable!", 'FAIL')
            return

        content = select_path.read_text(encoding='utf-8', errors='ignore')

        # Compter les personnages actifs
        chars_section = False
        stages_section = False
        active_chars = 0
        disabled_chars = 0
        active_stages = 0

        for line in content.split('\n'):
            line = line.strip()

            if '[Characters]' in line:
                chars_section = True
                stages_section = False
                continue
            elif '[Stages]' in line:
                chars_section = False
                stages_section = True
                continue
            elif line.startswith('['):
                chars_section = False
                stages_section = False
                continue

            if chars_section and line and not line.startswith(';'):
                if ',' in line:
                    active_chars += 1
            elif chars_section and line.startswith(';') and ',' in line:
                disabled_chars += 1

            if stages_section and line and not line.startswith(';'):
                if 'stages/' in line.lower():
                    active_stages += 1

        print(f"  📊 Personnages actifs: {active_chars}")
        print(f"  📊 Personnages désactivés: {disabled_chars}")
        print(f"  📊 Stages actifs: {active_stages}")

        self.add_test_result('Configuration', 'Personnages actifs', active_chars >= 50, f"{active_chars} personnages")
        self.add_test_result('Configuration', 'Stages actifs', active_stages >= 10, f"{active_stages} stages")

        if active_chars < 50:
            self.report['recommendations'].append(f"Ajouter plus de personnages (actuellement {active_chars})")

    # =========================================================
    # TEST 5: SONS ET MUSIQUE
    # =========================================================
    def test_audio(self):
        print("\n" + "="*60)
        print("  🧪 TEST 5: SONS ET MUSIQUE")
        print("="*60)

        sound_path = self.ikemen_path / 'sound'
        if not sound_path.exists():
            self.log("Dossier sound introuvable!", 'WARN')
            self.add_test_result('Audio', 'Dossier sound', False, 'Manquant')
            return

        # Compter les fichiers audio
        mp3_files = list(sound_path.glob('**/*.mp3'))
        ogg_files = list(sound_path.glob('**/*.ogg'))
        snd_files = list(sound_path.glob('**/*.snd'))

        total_audio = len(mp3_files) + len(ogg_files) + len(snd_files)

        print(f"  📊 Fichiers MP3: {len(mp3_files)}")
        print(f"  📊 Fichiers OGG: {len(ogg_files)}")
        print(f"  📊 Fichiers SND: {len(snd_files)}")

        self.add_test_result('Audio', 'Fichiers audio', total_audio > 0, f"{total_audio} fichiers")

        # Vérifier le son commun
        common_snd = self.ikemen_path / 'data' / 'common.snd'
        if common_snd.exists():
            size = common_snd.stat().st_size
            self.log(f"common.snd: {size:,} bytes", 'OK')
            self.add_test_result('Audio', 'common.snd', size > 1000, f"{size:,} bytes")

    # =========================================================
    # TEST 6: FONTS
    # =========================================================
    def test_fonts(self):
        print("\n" + "="*60)
        print("  🧪 TEST 6: POLICES")
        print("="*60)

        font_path = self.ikemen_path / 'font'
        if not font_path.exists():
            self.log("Dossier font introuvable!", 'WARN')
            return

        font_files = list(font_path.glob('*.def')) + list(font_path.glob('*.fnt'))

        print(f"  📊 Polices trouvées: {len(font_files)}")
        self.add_test_result('Polices', 'Fichiers police', len(font_files) >= 1, f"{len(font_files)} polices")

    # =========================================================
    # TEST 7: SAUVEGARDE ET PROFILS
    # =========================================================
    def test_save_system(self):
        print("\n" + "="*60)
        print("  🧪 TEST 7: SYSTEME DE SAUVEGARDE")
        print("="*60)

        save_path = self.ikemen_path / 'save'
        if not save_path.exists():
            self.log("Dossier save introuvable!", 'WARN')
            self.add_test_result('Sauvegarde', 'Dossier save', False, 'Manquant')
            return

        # Vérifier config.json
        config_file = save_path / 'config.json'
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text())
                self.log(f"config.json: Valide", 'OK')
                self.add_test_result('Sauvegarde', 'config.json', True, 'JSON valide')

                # Vérifier les paramètres importants
                checks = [
                    ('Difficulty', config.get('Difficulty', 0) > 0),
                    ('VolumeMaster', 'VolumeMaster' in config),
                    ('KeyConfig', 'KeyConfig' in config),
                    ('ListenPort', 'ListenPort' in config),
                ]
                for name, passed in checks:
                    self.add_test_result('Sauvegarde', f'Config: {name}', passed)

            except json.JSONDecodeError:
                self.log("config.json: JSON invalide!", 'FAIL')
                self.add_test_result('Sauvegarde', 'config.json', False, 'JSON invalide')
        else:
            self.log("config.json manquant", 'WARN')

        # Vérifier replays
        replays_path = save_path / 'replays'
        if replays_path.exists():
            replays = list(replays_path.glob('*.replay'))
            print(f"  📊 Replays sauvegardés: {len(replays)}")
            self.add_test_result('Sauvegarde', 'Système replay', True, f"{len(replays)} replays")

    # =========================================================
    # TEST 8: NETPLAY/ONLINE
    # =========================================================
    def test_netplay(self):
        print("\n" + "="*60)
        print("  🧪 TEST 8: CONFIGURATION NETPLAY")
        print("="*60)

        config_file = self.ikemen_path / 'save' / 'config.json'
        if not config_file.exists():
            self.log("Impossible de vérifier netplay (config manquante)", 'WARN')
            return

        try:
            config = json.loads(config_file.read_text())

            listen_port = config.get('ListenPort', 'Non défini')
            print(f"  📊 Port d'écoute: {listen_port}")
            self.add_test_result('Netplay', 'Port configuré', listen_port != 'Non défini', f"Port {listen_port}")

            # Vérifier si le mode netplay est dans le menu
            system_def = self.ikemen_path / 'data' / 'system.def'
            if system_def.exists():
                content = system_def.read_text(encoding='utf-8', errors='ignore')
                has_netplay = 'netplay' in content.lower()
                self.log(f"Menu Netplay: {'Présent' if has_netplay else 'Absent'}", 'OK' if has_netplay else 'WARN')
                self.add_test_result('Netplay', 'Menu Netplay', has_netplay)

        except Exception as e:
            self.log(f"Erreur: {e}", 'FAIL')

    # =========================================================
    # TEST 9: INTEGRATION COMPLETE
    # =========================================================
    def test_integration(self):
        print("\n" + "="*60)
        print("  🧪 TEST 9: TESTS D'INTEGRATION")
        print("="*60)

        # Test: Tous les personnages du select.def existent
        select_path = self.ikemen_path / 'data' / 'select.def'
        chars_path = self.ikemen_path / 'chars'

        if select_path.exists() and chars_path.exists():
            content = select_path.read_text(encoding='utf-8', errors='ignore')
            missing_chars = []

            in_chars_section = False
            for line in content.split('\n'):
                line = line.strip()
                if '[Characters]' in line:
                    in_chars_section = True
                    continue
                elif line.startswith('['):
                    in_chars_section = False
                    continue

                if in_chars_section and line and not line.startswith(';'):
                    # Extraire le nom du personnage
                    char_name = line.split(',')[0].strip()
                    if char_name:
                        # Vérifier si le dossier existe
                        char_dir = chars_path / char_name
                        if not char_dir.exists():
                            missing_chars.append(char_name)

            if missing_chars:
                print(f"  ⚠️ {len(missing_chars)} personnages dans select.def mais dossier manquant:")
                for char in missing_chars[:5]:
                    print(f"     - {char}")
                self.add_test_result('Intégration', 'Cohérence select.def/chars', False, f"{len(missing_chars)} manquants")
            else:
                self.log("Tous les personnages du select.def existent", 'OK')
                self.add_test_result('Intégration', 'Cohérence select.def/chars', True)

    # =========================================================
    # TEST 10: PERFORMANCE (simulation)
    # =========================================================
    def test_performance(self):
        print("\n" + "="*60)
        print("  🧪 TEST 10: ESTIMATION PERFORMANCE")
        print("="*60)

        # Calculer la taille totale des assets
        total_size = 0

        for folder in ['chars', 'stages', 'sound', 'font']:
            folder_path = self.ikemen_path / folder
            if folder_path.exists():
                for file in folder_path.rglob('*'):
                    if file.is_file():
                        total_size += file.stat().st_size

        total_mb = total_size / (1024 * 1024)
        print(f"  📊 Taille totale assets: {total_mb:.1f} MB")

        # Estimation RAM nécessaire (approximative)
        estimated_ram = total_mb * 0.3  # ~30% des assets en RAM
        print(f"  📊 RAM estimée nécessaire: {estimated_ram:.0f} MB")

        self.add_test_result('Performance', 'Taille assets', total_mb < 5000, f"{total_mb:.1f} MB")
        self.add_test_result('Performance', 'RAM estimée', estimated_ram < 1000, f"{estimated_ram:.0f} MB")

    # =========================================================
    # GENERATION RAPPORT
    # =========================================================
    def generate_report(self):
        print("\n" + "="*60)
        print("  📋 GENERATION DU RAPPORT QA")
        print("="*60)

        # Calculer le score
        total = self.report['summary']['total_tests']
        passed = self.report['summary']['passed']
        score = int((passed / total * 100)) if total > 0 else 0

        self.report['summary']['score'] = score

        # Déterminer le statut
        if score >= 90:
            status = "PRET POUR RELEASE"
            status_icon = "🟢"
        elif score >= 75:
            status = "CORRECTIONS MINEURES REQUISES"
            status_icon = "🟡"
        elif score >= 50:
            status = "CORRECTIONS MAJEURES REQUISES"
            status_icon = "🟠"
        else:
            status = "NON JOUABLE"
            status_icon = "🔴"

        self.report['summary']['status'] = status

        # Afficher le résumé
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    RAPPORT QA FINAL                          ║
╠══════════════════════════════════════════════════════════════╣
║  📊 Score Global: {score}/100
║  {status_icon} Statut: {status}
║
║  ✅ Tests réussis: {passed}/{total}
║  ❌ Tests échoués: {self.report['summary']['failed']}
║  ⚠️  Avertissements: {self.report['summary']['warnings']}
╚══════════════════════════════════════════════════════════════╝
""")

        if self.report['critical_issues']:
            print("  🚨 PROBLEMES CRITIQUES:")
            for issue in self.report['critical_issues']:
                print(f"     - {issue}")

        if self.report['recommendations']:
            print("\n  💡 RECOMMANDATIONS:")
            for rec in self.report['recommendations']:
                print(f"     - {rec}")

        # Sauvegarder le rapport
        report_path = self.game_path / 'QA_REPORT.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)

        print(f"\n  📄 Rapport sauvegardé: QA_REPORT.json")

        return score

    # =========================================================
    # EXECUTION COMPLETE
    # =========================================================
    def run_all_tests(self):
        print("\n" + "="*60)
        print("  🎮 KOF ULTIMATE ONLINE - SUITE QA COMPLETE")
        print("  📅 " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("="*60)

        self.test_system_files()
        self.test_characters()
        self.test_stages()
        self.test_select_def()
        self.test_audio()
        self.test_fonts()
        self.test_save_system()
        self.test_netplay()
        self.test_integration()
        self.test_performance()

        return self.generate_report()


if __name__ == '__main__':
    tester = KOFQATester('D:/KOF Ultimate Online')
    score = tester.run_all_tests()

    print(f"\n{'='*60}")
    print(f"  Tests terminés avec un score de {score}/100")
    print(f"{'='*60}\n")
