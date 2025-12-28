#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE ONLINE - COMBAT SIMULATOR
Simulates fights and detects potential issues
"""

import os
import re
import random
import json
from pathlib import Path
from datetime import datetime

GAME_DIR = Path(__file__).parent
CHARS_DIR = GAME_DIR / "chars"
DATA_DIR = GAME_DIR / "data"

def read_file(path):
    for enc in ['utf-8', 'latin-1', 'cp1252', 'shift-jis']:
        try:
            return path.read_text(encoding=enc, errors='ignore')
        except:
            continue
    return ""

class CombatSimulator:
    def __init__(self):
        self.results = []
        self.issues = []

    def analyze_character_combat(self, char_path):
        """Analyze character for combat readiness"""
        char_name = char_path.name
        score = 100
        problems = []

        # Check all CNS files
        cns_files = list(char_path.glob("*.cns")) + list(char_path.glob("**/*.cns"))

        total_states = 0
        air_states = 0
        ground_states = 0
        attack_states = 0
        has_idle = False
        has_walk = False
        has_jump = False
        has_crouch = False
        has_guard = False
        has_hit = False
        has_getup = False

        for cns in cns_files:
            content = read_file(cns)

            # Count states
            states = re.findall(r'\[Statedef\s+(-?\d+)\]', content, re.IGNORECASE)
            total_states += len(states)

            for state_num in states:
                num = int(state_num)

                # Basic states check
                if num == 0:
                    has_idle = True
                elif num in [20, 21]:
                    has_walk = True
                elif num in [40, 45, 50]:
                    has_jump = True
                elif num in [10, 11]:
                    has_crouch = True
                elif num in [120, 130, 131, 132]:
                    has_guard = True
                elif num in [5000, 5010, 5020]:
                    has_hit = True
                elif num in [5120, 5200, 5210]:
                    has_getup = True

            # Check for air states
            air_matches = re.findall(r'statetype\s*=\s*A', content, re.IGNORECASE)
            air_states += len(air_matches)

            # Check for standing states
            stand_matches = re.findall(r'statetype\s*=\s*S', content, re.IGNORECASE)
            ground_states += len(stand_matches)

            # Check for attacks
            hitdef_matches = re.findall(r'type\s*=\s*HitDef', content, re.IGNORECASE)
            attack_states += len(hitdef_matches)

            # Check for dangerous patterns

            # 1. Infinite damage
            damages = re.findall(r'damage\s*=\s*(\d+)', content, re.IGNORECASE)
            for d in damages:
                if int(d) > 500:
                    problems.append(f"Very high damage: {d}")
                    score -= 5

            # 2. Missing physics in air
            air_no_physics = re.findall(
                r'\[Statedef[^\]]*\].*?statetype\s*=\s*A.*?physics\s*=\s*N',
                content, re.IGNORECASE | re.DOTALL
            )
            if air_no_physics:
                problems.append(f"Air states without physics: {len(air_no_physics)}")
                score -= len(air_no_physics) * 2

            # 3. State loops (same state calling itself without time check)
            # Already fixed by previous scripts

            # 4. Extreme velocities
            extreme_vel = re.findall(r'vel\s*[xy]\s*=\s*(-?\d{3,})', content, re.IGNORECASE)
            if extreme_vel:
                problems.append(f"Extreme velocities found: {len(extreme_vel)}")
                score -= len(extreme_vel)

        # Check basic states exist
        if not has_idle:
            problems.append("Missing idle state (0)")
            score -= 10
        if not has_walk:
            problems.append("Missing walk states")
            score -= 5
        if not has_jump:
            problems.append("Missing jump states")
            score -= 5
        if not has_guard:
            problems.append("Missing guard states")
            score -= 5
        if not has_hit:
            problems.append("Missing hit reaction states")
            score -= 10
        if not has_getup:
            problems.append("Missing getup states")
            score -= 5

        # Check attack count
        if attack_states < 5:
            problems.append(f"Very few attacks: {attack_states}")
            score -= 10
        elif attack_states < 10:
            problems.append(f"Few attacks: {attack_states}")
            score -= 5

        score = max(0, min(100, score))

        return {
            'name': char_name,
            'score': score,
            'total_states': total_states,
            'attacks': attack_states,
            'problems': problems,
            'combat_ready': score >= 70
        }

    def simulate_matchup(self, char1_data, char2_data):
        """Simulate a matchup between two characters"""
        # Simple simulation based on stats
        score1 = char1_data['score']
        score2 = char2_data['score']
        attacks1 = char1_data['attacks']
        attacks2 = char2_data['attacks']

        # Calculate win probability
        total = score1 + score2
        if total == 0:
            win_prob = 0.5
        else:
            win_prob = score1 / total

        # Add attack factor
        attack_total = attacks1 + attacks2
        if attack_total > 0:
            attack_factor = attacks1 / attack_total
            win_prob = (win_prob + attack_factor) / 2

        # Simulate 10 rounds
        wins1 = 0
        wins2 = 0
        for _ in range(10):
            if random.random() < win_prob:
                wins1 += 1
            else:
                wins2 += 1

        return {
            'char1': char1_data['name'],
            'char2': char2_data['name'],
            'wins1': wins1,
            'wins2': wins2,
            'predicted_winner': char1_data['name'] if wins1 > wins2 else char2_data['name']
        }

    def run_full_test(self):
        """Run full combat simulation test"""
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              KOF ULTIMATE ONLINE - COMBAT SIMULATOR                           ║
║                   Testing all characters for combat                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)

        # Load roster
        roster_path = DATA_DIR / "select_pro.def"
        if not roster_path.exists():
            roster_path = DATA_DIR / "select_optimized.def"

        roster_content = read_file(roster_path)

        chars = []
        for line in roster_content.split('\n'):
            line = line.strip()
            if line and not line.startswith(';') and not line.startswith('[') and ',' in line:
                char_name = line.split(',')[0].strip()
                if char_name and not char_name.startswith('arcade'):
                    chars.append(char_name)

        print(f"Testing {len(chars)} characters for combat readiness...\n")

        # Analyze each character
        char_data = []
        combat_ready = []
        not_ready = []

        for i, char_name in enumerate(chars, 1):
            char_path = CHARS_DIR / char_name
            if not char_path.exists():
                continue

            result = self.analyze_character_combat(char_path)
            char_data.append(result)

            if result['combat_ready']:
                combat_ready.append(result)
                status = "READY"
            else:
                not_ready.append(result)
                status = "ISSUES"

            problems_str = f" ({len(result['problems'])} issues)" if result['problems'] else ""
            print(f"[{i:3d}/{len(chars)}] {status:6} {result['name']:<35} Score:{result['score']:3} Attacks:{result['attacks']:3}{problems_str}")

        print(f"\n{'='*80}")
        print(f"COMBAT READINESS SUMMARY")
        print(f"{'='*80}")
        print(f"  Combat Ready: {len(combat_ready)}/{len(char_data)} ({100*len(combat_ready)/len(char_data):.1f}%)")
        print(f"  Need Work: {len(not_ready)}/{len(char_data)}")

        # Run some matchup simulations
        print(f"\n{'='*80}")
        print(f"MATCHUP SIMULATIONS (Random samples)")
        print(f"{'='*80}")

        if len(combat_ready) >= 2:
            for _ in range(10):
                c1, c2 = random.sample(combat_ready, 2)
                matchup = self.simulate_matchup(c1, c2)
                print(f"  {matchup['char1']:<30} vs {matchup['char2']:<30} | {matchup['wins1']}-{matchup['wins2']} -> {matchup['predicted_winner']}")

        # Characters with most issues
        if not_ready:
            print(f"\n{'='*80}")
            print(f"CHARACTERS WITH ISSUES (Top 10)")
            print(f"{'='*80}")
            not_ready.sort(key=lambda x: x['score'])
            for r in not_ready[:10]:
                print(f"\n  {r['name']} (Score: {r['score']})")
                for p in r['problems'][:3]:
                    print(f"    - {p}")

        # Save results
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tested': len(char_data),
            'combat_ready': len(combat_ready),
            'characters': char_data
        }

        with open(GAME_DIR / "combat_test_results.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*80}")
        print(f"  Results saved to: combat_test_results.json")
        print(f"{'='*80}")

        return char_data, combat_ready, not_ready

if __name__ == "__main__":
    sim = CombatSimulator()
    sim.run_full_test()
