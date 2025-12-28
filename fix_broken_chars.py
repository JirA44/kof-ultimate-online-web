#!/usr/bin/env python3
"""
Désactive tous les personnages problématiques dans select.def
"""

import os
from pathlib import Path

def get_broken_characters(game_path):
    """Identifie tous les personnages cassés"""
    ikemen_path = Path(game_path) / 'Ikemen_GO'
    chars_path = ikemen_path / 'chars'

    broken = []

    for char_dir in chars_path.iterdir():
        if not char_dir.is_dir():
            continue

        char_name = char_dir.name
        issues = []

        # Check .def
        def_files = list(char_dir.glob('*.def'))
        if not def_files:
            issues.append('no_def')
        else:
            for def_file in def_files:
                try:
                    content = def_file.read_text(encoding='utf-8', errors='ignore')
                    if '[Info]' not in content:
                        issues.append('no_info')
                    if '[Files]' not in content:
                        issues.append('no_files')
                except:
                    issues.append('read_error')

        # Check .sff (sprites)
        if not list(char_dir.glob('*.sff')):
            issues.append('no_sff')

        # Check .air (animations)
        if not list(char_dir.glob('*.air')):
            issues.append('no_air')

        # Check .cns (states)
        if not list(char_dir.glob('*.cns')):
            issues.append('no_cns')

        # Check .cmd (commands)
        if not list(char_dir.glob('*.cmd')):
            issues.append('no_cmd')

        if issues:
            broken.append(char_name)

    return broken

def disable_in_select_def(game_path, broken_chars):
    """Désactive les personnages cassés dans select.def"""
    select_path = Path(game_path) / 'Ikemen_GO' / 'data' / 'select.def'

    content = select_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.split('\n')

    new_lines = []
    disabled_count = 0

    broken_lower = [c.lower() for c in broken_chars]

    for line in lines:
        line_stripped = line.strip()

        # Skip already commented lines
        if line_stripped.startswith(';'):
            new_lines.append(line)
            continue

        # Check if this line contains a broken character
        should_disable = False
        for broken in broken_lower:
            if broken in line_stripped.lower() and ',' in line_stripped:
                should_disable = True
                break

        if should_disable:
            new_lines.append('; ' + line + ' ; DISABLED-BY-QA')
            disabled_count += 1
        else:
            new_lines.append(line)

    # Write back
    select_path.write_text('\n'.join(new_lines), encoding='utf-8')

    return disabled_count

def disable_broken_stages(game_path):
    """Désactive les stages cassés dans select.def"""
    ikemen_path = Path(game_path) / 'Ikemen_GO'
    stages_path = ikemen_path / 'stages'
    select_path = ikemen_path / 'data' / 'select.def'

    # Find broken stages (no .sff)
    broken_stages = []
    for stage_def in stages_path.glob('*.def'):
        sff_file = stage_def.with_suffix('.sff')
        if not sff_file.exists():
            broken_stages.append(stage_def.stem)

    if not broken_stages:
        return 0

    # Disable in select.def
    content = select_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.split('\n')

    new_lines = []
    disabled_count = 0

    for line in lines:
        should_disable = False
        for stage in broken_stages:
            if stage.lower() in line.lower() and 'stages/' in line.lower():
                if not line.strip().startswith(';'):
                    should_disable = True
                    break

        if should_disable:
            new_lines.append('; ' + line + ' ; DISABLED-NO-SFF')
            disabled_count += 1
        else:
            new_lines.append(line)

    select_path.write_text('\n'.join(new_lines), encoding='utf-8')
    return disabled_count


if __name__ == '__main__':
    game_path = 'D:/KOF Ultimate Online'

    print("="*60)
    print("  CORRECTION AUTOMATIQUE - KOF ULTIMATE ONLINE")
    print("="*60)

    # Step 1: Find broken characters
    print("\n[1/3] Recherche des personnages cassés...")
    broken_chars = get_broken_characters(game_path)
    print(f"      Trouvé: {len(broken_chars)} personnages problématiques")

    # Step 2: Disable in select.def
    print("\n[2/3] Désactivation dans select.def...")
    disabled_chars = disable_in_select_def(game_path, broken_chars)
    print(f"      Désactivé: {disabled_chars} personnages")

    # Step 3: Disable broken stages
    print("\n[3/3] Désactivation des stages cassés...")
    disabled_stages = disable_broken_stages(game_path)
    print(f"      Désactivé: {disabled_stages} stages")

    print("\n" + "="*60)
    print(f"  ✅ CORRECTION TERMINÉE")
    print(f"  - {disabled_chars} personnages désactivés")
    print(f"  - {disabled_stages} stages désactivés")
    print("="*60)
