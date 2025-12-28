#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE ONLINE - CHARACTER POWER RANKING
Analyzes characters and ranks them by power level
"""

import os
import re
from pathlib import Path
import json

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

def analyze_character_power(char_path):
    """Analyze character power based on various metrics"""
    char_name = char_path.name

    power_score = 50  # Base score
    metrics = {
        'life': 1000,
        'attack': 100,
        'defence': 100,
        'max_damage': 0,
        'super_count': 0,
        'helper_count': 0,
        'projectile_count': 0,
        'combo_potential': 0
    }

    # Read DEF file for base stats
    def_files = list(char_path.glob("*.def"))
    if def_files:
        def_content = read_file(def_files[0])

        # Life
        life_match = re.search(r'life\s*=\s*(\d+)', def_content, re.IGNORECASE)
        if life_match:
            metrics['life'] = int(life_match.group(1))

        # Attack
        attack_match = re.search(r'attack\s*=\s*(\d+)', def_content, re.IGNORECASE)
        if attack_match:
            metrics['attack'] = int(attack_match.group(1))

        # Defence
        defence_match = re.search(r'defence\s*=\s*(\d+)', def_content, re.IGNORECASE)
        if defence_match:
            metrics['defence'] = int(defence_match.group(1))

    # Analyze CNS files for damage, supers, etc.
    cns_files = list(char_path.glob("*.cns")) + list(char_path.glob("**/*.cns"))

    all_damages = []
    super_states = set()
    helper_states = set()
    projectile_states = set()

    for cns in cns_files:
        content = read_file(cns)

        # Find all damage values
        damages = re.findall(r'damage\s*=\s*(\d+)', content, re.IGNORECASE)
        for d in damages:
            all_damages.append(int(d))

        # Count super moves (typically states 3000+)
        super_matches = re.findall(r'\[Statedef\s+(3\d{3})\]', content, re.IGNORECASE)
        super_states.update(super_matches)

        # Count helpers
        helper_matches = re.findall(r'type\s*=\s*Helper', content, re.IGNORECASE)
        metrics['helper_count'] += len(helper_matches)

        # Count projectiles
        projectile_matches = re.findall(r'type\s*=\s*Projectile', content, re.IGNORECASE)
        metrics['projectile_count'] += len(projectile_matches)

        # Count HitDefs (combo potential)
        hitdef_matches = re.findall(r'type\s*=\s*HitDef', content, re.IGNORECASE)
        metrics['combo_potential'] += len(hitdef_matches)

    if all_damages:
        metrics['max_damage'] = max(all_damages)
        avg_damage = sum(all_damages) / len(all_damages)
    else:
        avg_damage = 50

    metrics['super_count'] = len(super_states)

    # Calculate power score
    # Life factor (higher = tankier)
    if metrics['life'] > 1000:
        power_score += (metrics['life'] - 1000) / 50
    elif metrics['life'] < 1000:
        power_score -= (1000 - metrics['life']) / 100

    # Attack factor
    if metrics['attack'] > 100:
        power_score += (metrics['attack'] - 100) / 5
    elif metrics['attack'] < 100:
        power_score -= (100 - metrics['attack']) / 10

    # Max damage factor
    if metrics['max_damage'] > 100:
        power_score += min(20, (metrics['max_damage'] - 100) / 10)

    # Super moves factor
    power_score += min(15, metrics['super_count'] * 2)

    # Helper factor (assistants)
    power_score += min(10, metrics['helper_count'] / 5)

    # Projectile factor
    power_score += min(10, metrics['projectile_count'] / 3)

    # Combo potential
    power_score += min(10, metrics['combo_potential'] / 20)

    # Normalize to 0-100
    power_score = max(0, min(100, power_score))

    # Determine tier
    if power_score >= 85:
        tier = 'S'
        tier_name = 'GOD TIER'
    elif power_score >= 75:
        tier = 'A'
        tier_name = 'TOP TIER'
    elif power_score >= 65:
        tier = 'B'
        tier_name = 'HIGH TIER'
    elif power_score >= 55:
        tier = 'C'
        tier_name = 'MID TIER'
    elif power_score >= 45:
        tier = 'D'
        tier_name = 'LOW TIER'
    else:
        tier = 'F'
        tier_name = 'BOTTOM'

    return {
        'name': char_name,
        'power': round(power_score, 1),
        'tier': tier,
        'tier_name': tier_name,
        'life': metrics['life'],
        'attack': metrics['attack'],
        'defence': metrics['defence'],
        'max_damage': metrics['max_damage'],
        'supers': metrics['super_count'],
        'helpers': metrics['helper_count'],
        'projectiles': metrics['projectile_count']
    }

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              KOF ULTIMATE ONLINE - POWER RANKING                              ║
║                   Character Tier List Analysis                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Read stable roster
    roster_path = DATA_DIR / "select_pro.def"
    if not roster_path.exists():
        roster_path = DATA_DIR / "select_optimized.def"

    roster_content = read_file(roster_path)

    chars_in_roster = []
    for line in roster_content.split('\n'):
        line = line.strip()
        if line and not line.startswith(';') and not line.startswith('[') and ',' in line:
            char_name = line.split(',')[0].strip()
            if char_name and not char_name.startswith('arcade'):
                chars_in_roster.append(char_name)

    print(f"Analyzing {len(chars_in_roster)} characters...\n")

    results = []

    for char_name in chars_in_roster:
        char_path = CHARS_DIR / char_name
        if char_path.exists():
            try:
                result = analyze_character_power(char_path)
                results.append(result)
            except Exception as e:
                pass

    # Sort by power
    results.sort(key=lambda x: x['power'], reverse=True)

    # Display by tier
    tiers = {'S': [], 'A': [], 'B': [], 'C': [], 'D': [], 'F': []}
    for r in results:
        tiers[r['tier']].append(r)

    print("=" * 80)
    print("                           TIER LIST")
    print("=" * 80)

    tier_colors = {
        'S': 'GOD TIER',
        'A': 'TOP TIER',
        'B': 'HIGH TIER',
        'C': 'MID TIER',
        'D': 'LOW TIER',
        'F': 'BOTTOM TIER'
    }

    for tier in ['S', 'A', 'B', 'C', 'D', 'F']:
        if tiers[tier]:
            print(f"\n{'='*80}")
            print(f"  [{tier}] {tier_colors[tier]} ({len(tiers[tier])} characters)")
            print(f"{'='*80}")
            for r in tiers[tier]:
                stats = f"Life:{r['life']} Atk:{r['attack']} Def:{r['defence']}"
                extras = f"Supers:{r['supers']} MaxDmg:{r['max_damage']}"
                print(f"  {r['power']:5.1f} | {r['name']:<35} | {stats} | {extras}")

    # Save to file
    output = []
    output.append("=" * 80)
    output.append("         KOF ULTIMATE ONLINE - CHARACTER POWER RANKING")
    output.append("=" * 80)
    output.append("")

    for tier in ['S', 'A', 'B', 'C', 'D', 'F']:
        if tiers[tier]:
            output.append(f"\n[{tier}] {tier_colors[tier]} ({len(tiers[tier])} characters)")
            output.append("-" * 60)
            for r in tiers[tier]:
                output.append(f"  {r['power']:5.1f} - {r['name']}")

    output.append("\n" + "=" * 80)
    output.append("LEGEND:")
    output.append("  S = God Tier (85-100) - Extremely powerful, boss-level")
    output.append("  A = Top Tier (75-84) - Very strong, tournament viable")
    output.append("  B = High Tier (65-74) - Strong, competitive")
    output.append("  C = Mid Tier (55-64) - Balanced, average")
    output.append("  D = Low Tier (45-54) - Below average")
    output.append("  F = Bottom (0-44) - Weak")
    output.append("=" * 80)

    with open(GAME_DIR / "TIER_LIST.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    # Save JSON for detailed data
    with open(GAME_DIR / "power_ranking.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"  SUMMARY")
    print(f"{'='*80}")
    print(f"  S Tier: {len(tiers['S'])} characters")
    print(f"  A Tier: {len(tiers['A'])} characters")
    print(f"  B Tier: {len(tiers['B'])} characters")
    print(f"  C Tier: {len(tiers['C'])} characters")
    print(f"  D Tier: {len(tiers['D'])} characters")
    print(f"  F Tier: {len(tiers['F'])} characters")
    print(f"\n  Saved: TIER_LIST.txt, power_ranking.json")

if __name__ == "__main__":
    main()
