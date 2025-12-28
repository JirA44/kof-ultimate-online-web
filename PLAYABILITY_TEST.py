#!/usr/bin/env python3
"""
=================================================================
  TEST DE JOUABILITE REELLE - KOF ULTIMATE ONLINE
  Teste uniquement ce qui est ACTUELLEMENT JOUABLE
=================================================================
"""

import os
import json
from pathlib import Path
from datetime import datetime

class PlayabilityTester:
    def __init__(self, game_path):
        self.game_path = Path(game_path)
        self.ikemen_path = self.game_path / 'Ikemen_GO'
        self.results = {
            'date': datetime.now().isoformat(),
            'playable_chars': [],
            'playable_stages': [],
            'issues': [],
            'score': 0
        }

    def get_active_characters(self):
        """Récupère uniquement les personnages ACTIFS dans select.def"""
        select_path = self.ikemen_path / 'data' / 'select.def'
        content = select_path.read_text(encoding='utf-8', errors='ignore')

        active = []
        in_chars = False

        for line in content.split('\n'):
            line = line.strip()
            if '[Characters]' in line:
                in_chars = True
                continue
            elif line.startswith('['):
                in_chars = False
                continue

            if in_chars and line and not line.startswith(';') and ',' in line:
                char_name = line.split(',')[0].strip()
                if char_name:
                    active.append(char_name)

        return active

    def get_active_stages(self):
        """Récupère uniquement les stages ACTIFS dans select.def"""
        select_path = self.ikemen_path / 'data' / 'select.def'
        content = select_path.read_text(encoding='utf-8', errors='ignore')

        active = []
        in_stages = False

        for line in content.split('\n'):
            line = line.strip()
            if '[Stages]' in line:
                in_stages = True
                continue
            elif line.startswith('['):
                in_stages = False
                continue

            if in_stages and line and not line.startswith(';'):
                if 'stages/' in line.lower():
                    # Extract stage name
                    stage = line.split('/')[-1].replace('.def', '').strip()
                    active.append(stage)

        return active

    def test_character(self, char_name):
        """Teste si un personnage est vraiment jouable"""
        char_path = self.ikemen_path / 'chars' / char_name
        if not char_path.exists():
            return False, "Dossier manquant"

        # Check essential files
        has_def = len(list(char_path.glob('*.def'))) > 0
        has_sff = len(list(char_path.glob('*.sff'))) > 0
        has_air = len(list(char_path.glob('*.air'))) > 0
        has_cns = len(list(char_path.glob('*.cns'))) > 0

        if not has_def:
            return False, "Pas de .def"
        if not has_sff:
            return False, "Pas de sprites"
        if not has_air:
            return False, "Pas d'animations"
        if not has_cns:
            return False, "Pas d'états"

        return True, "OK"

    def test_stage(self, stage_name):
        """Teste si un stage est vraiment jouable"""
        stages_path = self.ikemen_path / 'stages'

        def_file = stages_path / f"{stage_name}.def"
        sff_file = stages_path / f"{stage_name}.sff"

        if not def_file.exists():
            return False, "DEF manquant"
        if not sff_file.exists():
            return False, "SFF manquant"

        return True, "OK"

    def run_playability_test(self):
        print("\n" + "="*60)
        print("  🎮 TEST DE JOUABILITE REELLE")
        print("  (Uniquement le contenu ACTIF)")
        print("="*60)

        # Test characters
        print("\n[1/2] TEST DES PERSONNAGES ACTIFS")
        print("-"*40)

        active_chars = self.get_active_characters()
        playable_chars = 0
        char_issues = []

        for char in active_chars:
            playable, reason = self.test_character(char)
            if playable:
                playable_chars += 1
                self.results['playable_chars'].append(char)
            else:
                char_issues.append((char, reason))

        char_rate = (playable_chars / len(active_chars) * 100) if active_chars else 0

        print(f"  📊 Personnages actifs dans select.def: {len(active_chars)}")
        print(f"  ✅ Personnages jouables: {playable_chars}")
        print(f"  📈 Taux de réussite: {char_rate:.1f}%")

        if char_issues:
            print(f"\n  ⚠️ Personnages actifs mais non jouables:")
            for char, reason in char_issues[:10]:
                print(f"     - {char}: {reason}")
                self.results['issues'].append(f"Personnage {char}: {reason}")

        # Test stages
        print("\n[2/2] TEST DES STAGES ACTIFS")
        print("-"*40)

        active_stages = self.get_active_stages()
        playable_stages = 0
        stage_issues = []

        for stage in active_stages:
            playable, reason = self.test_stage(stage)
            if playable:
                playable_stages += 1
                self.results['playable_stages'].append(stage)
            else:
                stage_issues.append((stage, reason))

        stage_rate = (playable_stages / len(active_stages) * 100) if active_stages else 0

        print(f"  📊 Stages actifs dans select.def: {len(active_stages)}")
        print(f"  ✅ Stages jouables: {playable_stages}")
        print(f"  📈 Taux de réussite: {stage_rate:.1f}%")

        if stage_issues:
            print(f"\n  ⚠️ Stages actifs mais non jouables:")
            for stage, reason in stage_issues:
                print(f"     - {stage}: {reason}")
                self.results['issues'].append(f"Stage {stage}: {reason}")

        # Calculate overall score
        overall_score = int((char_rate + stage_rate) / 2)
        self.results['score'] = overall_score

        # Final summary
        print("\n" + "="*60)
        print("  📋 RESULTAT JOUABILITE")
        print("="*60)

        if overall_score >= 95:
            status = "🟢 EXCELLENT - Prêt pour release"
        elif overall_score >= 85:
            status = "🟡 BON - Quelques corrections mineures"
        elif overall_score >= 70:
            status = "🟠 MOYEN - Corrections recommandées"
        else:
            status = "🔴 INSUFFISANT - Corrections requises"

        print(f"""
  ╔════════════════════════════════════════════════╗
  ║  SCORE JOUABILITE: {overall_score}/100
  ║  {status}
  ║
  ║  Personnages jouables: {playable_chars}/{len(active_chars)}
  ║  Stages jouables: {playable_stages}/{len(active_stages)}
  ╚════════════════════════════════════════════════╝
""")

        # Save results
        report_path = self.game_path / 'PLAYABILITY_REPORT.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"  📄 Rapport: PLAYABILITY_REPORT.json")

        return overall_score


if __name__ == '__main__':
    tester = PlayabilityTester('D:/KOF Ultimate Online')
    score = tester.run_playability_test()
