#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE ONLINE - FLY-AWAY FIX
Fixes air states with no physics that cause characters to fly away
"""

import os
import re
from pathlib import Path

GAME_DIR = Path(__file__).parent
CHARS_DIR = GAME_DIR / "chars"
DATA_DIR = GAME_DIR / "data"

stats = {'fixed': 0, 'states_fixed': 0}

def read_file(path):
    for enc in ['utf-8', 'latin-1', 'cp1252', 'shift-jis']:
        try:
            return path.read_text(encoding=enc, errors='ignore')
        except:
            continue
    return ""

def write_file(path, content):
    path.write_text(content, encoding='utf-8', errors='ignore')

def fix_air_physics(cns_path):
    """Fix air states that have physics = N"""
    content = read_file(cns_path)
    original = content
    fixes = 0

    # Pattern to find StateDef blocks
    # Looking for: [Statedef X] followed by type = A and physics = N

    # Split by StateDef
    parts = re.split(r'(\[Statedef\s+-?\d+[^\]]*\])', content, flags=re.IGNORECASE)

    new_parts = []
    i = 0
    while i < len(parts):
        part = parts[i]

        # Check if this is a StateDef header
        statedef_match = re.match(r'\[Statedef\s+(-?\d+)', part, re.IGNORECASE)
        if statedef_match and i + 1 < len(parts):
            state_num = statedef_match.group(1)
            new_parts.append(part)
            i += 1

            # Get the state content (until next StateDef or State)
            state_content = parts[i] if i < len(parts) else ""

            # Check if this is an air state with no physics
            is_air = bool(re.search(r'(?:state)?type\s*=\s*A', state_content, re.IGNORECASE))
            has_no_physics = bool(re.search(r'physics\s*=\s*N', state_content, re.IGNORECASE))

            if is_air and has_no_physics:
                # Change physics = N to physics = A (air physics)
                state_content = re.sub(
                    r'physics\s*=\s*N',
                    'physics = A',
                    state_content,
                    flags=re.IGNORECASE
                )
                fixes += 1

            new_parts.append(state_content)
        else:
            new_parts.append(part)
        i += 1

    content = ''.join(new_parts)

    if content != original:
        write_file(cns_path, content)
        return fixes
    return 0

def fix_character(char_path):
    """Fix all CNS files in a character folder"""
    total_fixes = 0

    cns_files = list(char_path.glob("*.cns")) + list(char_path.glob("**/*.cns"))

    for cns in cns_files:
        try:
            fixes = fix_air_physics(cns)
            total_fixes += fixes
        except Exception as e:
            pass

    return total_fixes

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              KOF ULTIMATE ONLINE - FLY-AWAY FIX                               ║
║          Fixing air states with no physics                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Read roster
    roster_path = DATA_DIR / "select_optimized.def"
    roster_content = read_file(roster_path)

    chars_in_roster = []
    for line in roster_content.split('\n'):
        line = line.strip()
        if line and not line.startswith(';') and not line.startswith('[') and ',' in line:
            char_name = line.split(',')[0].strip()
            if char_name and not char_name.startswith('arcade'):
                chars_in_roster.append(char_name)

    print(f"Fixing {len(chars_in_roster)} characters...\n")

    total_fixes = 0
    chars_fixed = 0

    for i, char_name in enumerate(sorted(chars_in_roster), 1):
        char_path = CHARS_DIR / char_name

        if not char_path.exists():
            continue

        fixes = fix_character(char_path)

        if fixes > 0:
            print(f"[{i:3d}/{len(chars_in_roster)}] Fixed {char_name}: +{fixes} physics fixes")
            chars_fixed += 1
            total_fixes += fixes
        else:
            print(f"[{i:3d}/{len(chars_in_roster)}] OK: {char_name}")

    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        FLY-AWAY FIX COMPLETE                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Characters processed: {len(chars_in_roster):<52}║
║  Characters fixed: {chars_fixed:<55}║
║  Physics fixes applied: {total_fixes:<51}║
║                                                                              ║
║  Air states now have proper physics!                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    main()
