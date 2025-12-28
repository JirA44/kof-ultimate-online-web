#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE ONLINE - ADVANCED CHARACTER TESTER
Simulates gameplay scenarios and detects potential crash patterns
"""

import os
import re
from pathlib import Path
from datetime import datetime
import json

GAME_DIR = Path(__file__).parent
CHARS_DIR = GAME_DIR / "chars"
DATA_DIR = GAME_DIR / "data"

# Known crash patterns
CRASH_PATTERNS = {
    'infinite_loop': r'changestate\s*=\s*(\d+).*?trigger1\s*=\s*1\s*$',
    'extreme_vel_y': r'vel\s*y\s*=\s*(-?\d{3,})',
    'extreme_vel_x': r'vel\s*x\s*=\s*(-?\d{3,})',
    'no_physics_air': r'\[Statedef\s+-?\d+\].*?physics\s*=\s*N.*?type\s*=\s*A',
    'helper_spam': r'type\s*=\s*Helper(?!.*helperid)',
    'explod_no_remove': r'type\s*=\s*Explod(?!.*removetime)',
    'division_zero': r'/\s*0(?:\s|$)',
    'negative_anim': r'anim\s*=\s*-\d+',
    'huge_damage': r'damage\s*=\s*(\d{4,})',
    'self_state_loop': r'\[Statedef\s+(\d+)\].*?changestate\s*=\s*\1',
}

# Dangerous state combinations
DANGEROUS_STATES = {
    'air_no_landing': 'StateType = A without landing transition',
    'hit_no_recovery': 'HitDef without recovery states',
    'guard_infinite': 'GuardDist too high causing infinite block',
}

class CharacterTester:
    def __init__(self, char_path):
        self.char_path = char_path
        self.char_name = char_path.name
        self.issues = []
        self.warnings = []
        self.score = 100

    def read_file(self, path):
        for enc in ['utf-8', 'latin-1', 'cp1252', 'shift-jis']:
            try:
                return path.read_text(encoding=enc, errors='ignore')
            except:
                continue
        return ""

    def check_cns_files(self):
        """Analyze all CNS files for crash patterns"""
        cns_files = list(self.char_path.glob("*.cns")) + list(self.char_path.glob("**/*.cns"))

        for cns in cns_files:
            content = self.read_file(cns)

            # Check for crash patterns
            for pattern_name, pattern in CRASH_PATTERNS.items():
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                if matches:
                    if pattern_name in ['extreme_vel_y', 'extreme_vel_x', 'huge_damage']:
                        for m in matches:
                            try:
                                val = abs(int(m))
                                if val > 100:
                                    self.issues.append(f"{cns.name}: {pattern_name} = {m}")
                                    self.score -= 5
                            except:
                                pass
                    else:
                        self.warnings.append(f"{cns.name}: Potential {pattern_name}")
                        self.score -= 2

            # Check state definitions
            self.check_state_integrity(content, cns.name)

    def check_state_integrity(self, content, filename):
        """Check for state integrity issues"""
        # Find all StateDefs
        statedefs = re.findall(r'\[Statedef\s+(-?\d+)\](.*?)(?=\[Statedef|\[State\s|$)',
                               content, re.IGNORECASE | re.DOTALL)

        for state_num, state_content in statedefs:
            # Check air states have landing
            if 'type = a' in state_content.lower() or 'statetype = a' in state_content.lower():
                if 'pos y' not in state_content.lower() and 'changestate' not in state_content.lower():
                    # Air state without position check or state change
                    if 'physics = n' in state_content.lower():
                        self.issues.append(f"{filename}: State {state_num} - Air with no physics (fly-away risk)")
                        self.score -= 10

            # Check for infinite state loops
            state_changes = re.findall(r'changestate\s*=\s*(\d+)', state_content, re.IGNORECASE)
            for target in state_changes:
                if target == state_num:
                    # Self-referencing state - check for exit condition
                    if 'time >' not in state_content.lower() and 'animtime' not in state_content.lower():
                        self.issues.append(f"{filename}: State {state_num} - Potential infinite loop")
                        self.score -= 15

    def check_cmd_file(self):
        """Check CMD file for issues"""
        cmd_files = list(self.char_path.glob("*.cmd")) + list(self.char_path.glob("**/*.cmd"))

        for cmd in cmd_files:
            content = self.read_file(cmd)

            # Check command time
            times = re.findall(r'command\.time\s*=\s*(\d+)', content, re.IGNORECASE)
            for t in times:
                if int(t) > 60:
                    self.warnings.append(f"{cmd.name}: command.time too high ({t})")
                    self.score -= 1

    def check_def_file(self):
        """Check DEF file for completeness"""
        def_files = list(self.char_path.glob("*.def"))

        if not def_files:
            self.issues.append("Missing DEF file")
            self.score -= 50
            return

        content = self.read_file(def_files[0])

        required = ['cmd', 'cns', 'sprite', 'anim']
        for req in required:
            if f'{req} =' not in content.lower() and f'{req}=' not in content.lower():
                self.issues.append(f"Missing {req} in DEF file")
                self.score -= 10

    def check_sprite_size(self):
        """Check sprite file sizes"""
        sff_files = list(self.char_path.glob("*.sff")) + list(self.char_path.glob("**/*.sff"))

        for sff in sff_files:
            size_mb = sff.stat().st_size / (1024 * 1024)
            if size_mb > 100:
                self.issues.append(f"Sprite file too large: {size_mb:.0f}MB (may cause memory issues)")
                self.score -= 20
            elif size_mb > 50:
                self.warnings.append(f"Large sprite file: {size_mb:.0f}MB")
                self.score -= 5

    def run_all_tests(self):
        """Run all tests"""
        self.check_def_file()
        self.check_cns_files()
        self.check_cmd_file()
        self.check_sprite_size()

        # Ensure score stays in valid range
        self.score = max(0, min(100, self.score))

        return {
            'name': self.char_name,
            'score': self.score,
            'grade': self.get_grade(),
            'issues': self.issues,
            'warnings': self.warnings,
            'stable': self.score >= 60
        }

    def get_grade(self):
        if self.score >= 90: return 'A+'
        if self.score >= 80: return 'A'
        if self.score >= 70: return 'B'
        if self.score >= 60: return 'C'
        if self.score >= 50: return 'D'
        return 'F'


def test_all_characters():
    """Test all characters in the optimized roster"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║         KOF ULTIMATE ONLINE - ADVANCED CHARACTER TESTING                      ║
║                   Simulating gameplay scenarios                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Read roster
    roster_path = DATA_DIR / "select_optimized.def"
    roster_content = roster_path.read_text(encoding='utf-8', errors='ignore')

    chars_in_roster = []
    for line in roster_content.split('\n'):
        line = line.strip()
        if line and not line.startswith(';') and not line.startswith('[') and ',' in line:
            char_name = line.split(',')[0].strip()
            if char_name and not char_name.startswith('arcade'):
                chars_in_roster.append(char_name)

    print(f"Testing {len(chars_in_roster)} characters...\n")

    results = []
    problematic = []

    for i, char_name in enumerate(sorted(chars_in_roster), 1):
        char_path = CHARS_DIR / char_name

        if not char_path.exists():
            print(f"[{i:3d}/{len(chars_in_roster)}] MISSING: {char_name}")
            continue

        tester = CharacterTester(char_path)
        result = tester.run_all_tests()
        results.append(result)

        # Display result
        grade = result['grade']
        score = result['score']

        if score >= 80:
            status = "OK"
        elif score >= 60:
            status = "WARN"
        else:
            status = "FAIL"
            problematic.append(result)

        issues_count = len(result['issues'])
        warns_count = len(result['warnings'])

        print(f"[{i:3d}/{len(chars_in_roster)}] {status:4} {char_name:<40} Score:{score:3} Grade:{grade} Issues:{issues_count} Warns:{warns_count}")

    # Summary
    stable_count = len([r for r in results if r['stable']])
    avg_score = sum(r['score'] for r in results) / len(results) if results else 0

    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           TEST RESULTS SUMMARY                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Characters Tested: {len(results):<54}║
║  Stable Characters: {stable_count:<54}║
║  Problematic: {len(problematic):<60}║
║  Average Score: {avg_score:.1f}/100{' '*50}║
║                                                                              ║
║  Grade Distribution:                                                         ║
║    A+: {len([r for r in results if r['grade'] == 'A+']):<4} A: {len([r for r in results if r['grade'] == 'A']):<4} B: {len([r for r in results if r['grade'] == 'B']):<4} C: {len([r for r in results if r['grade'] == 'C']):<4} D: {len([r for r in results if r['grade'] == 'D']):<4} F: {len([r for r in results if r['grade'] == 'F']):<4}                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Show problematic characters
    if problematic:
        print("\n⚠️  PROBLEMATIC CHARACTERS (Score < 60):")
        for p in problematic:
            print(f"\n  {p['name']} (Score: {p['score']}, Grade: {p['grade']})")
            for issue in p['issues'][:5]:
                print(f"    - {issue}")

    # Save detailed report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tested': len(results),
        'stable_count': stable_count,
        'average_score': avg_score,
        'results': results
    }

    report_path = GAME_DIR / "test_results.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\n📄 Detailed report saved: {report_path}")

    return results, problematic


if __name__ == "__main__":
    results, problematic = test_all_characters()
