#!/usr/bin/env python3
"""
Correction massive de tous les personnages problematiques
"""

import os
import glob
import re
import shutil

def fix_all_characters(game_path):
    chars_path = os.path.join(game_path, 'Ikemen_GO', 'chars')
    fixed_count = 0
    disabled_count = 0

    print("=" * 60)
    print("  CORRECTION MASSIVE DES PERSONNAGES")
    print("=" * 60)

    for char_name in os.listdir(chars_path):
        char_path = os.path.join(chars_path, char_name)
        if not os.path.isdir(char_path):
            continue

        def_files = glob.glob(os.path.join(char_path, '*.def'))
        char_fixed = False

        for def_file in def_files:
            try:
                with open(def_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                original = content

                # Fix 1: Comment out stcommon references
                content = re.sub(
                    r'^(\s*stcommon\s*=.*)$',
                    r'; \1 ; AUTO-FIXED-v2',
                    content,
                    flags=re.MULTILINE | re.IGNORECASE
                )

                # Fix 2: Comment out common.const references
                content = re.sub(
                    r'^(\s*const\s*=.*common\.const.*)$',
                    r'; \1 ; AUTO-FIXED-v2',
                    content,
                    flags=re.MULTILINE | re.IGNORECASE
                )

                # Fix 3: Comment out common.air references in statedef
                content = re.sub(
                    r'^(\s*common\.air.*)$',
                    r'; \1 ; AUTO-FIXED-v2',
                    content,
                    flags=re.MULTILINE | re.IGNORECASE
                )

                if content != original:
                    with open(def_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    char_fixed = True

            except Exception as e:
                print(f"  ❌ Erreur {char_name}: {e}")

        # Check for missing sprite files
        sff_files = glob.glob(os.path.join(char_path, '*.sff'))
        if not sff_files:
            # Disable character by renaming folder
            disabled_path = char_path + '_DISABLED'
            if not os.path.exists(disabled_path):
                try:
                    # Just create a marker file instead of renaming
                    marker = os.path.join(char_path, '_DISABLED_NO_SPRITES')
                    with open(marker, 'w') as f:
                        f.write('This character has no sprites and is disabled')
                    disabled_count += 1
                    print(f"  ⚠️ Desactive (pas de sprites): {char_name}")
                except:
                    pass

        if char_fixed:
            fixed_count += 1
            print(f"  ✅ Corrige: {char_name}")

    print("\n" + "=" * 60)
    print(f"  RESULTAT:")
    print(f"  ✅ Personnages corriges: {fixed_count}")
    print(f"  ⚠️ Personnages desactives: {disabled_count}")
    print("=" * 60)

    return fixed_count, disabled_count


def update_select_def(game_path):
    """Met a jour select.def pour exclure les personnages desactives"""
    select_path = os.path.join(game_path, 'Ikemen_GO', 'data', 'select.def')
    chars_path = os.path.join(game_path, 'Ikemen_GO', 'chars')

    # Get list of disabled characters
    disabled = []
    for char_name in os.listdir(chars_path):
        char_path = os.path.join(chars_path, char_name)
        if os.path.isdir(char_path):
            marker = os.path.join(char_path, '_DISABLED_NO_SPRITES')
            if os.path.exists(marker):
                disabled.append(char_name.lower())

    if not disabled:
        print("  Aucun personnage a desactiver dans select.def")
        return

    print(f"\n  Mise a jour select.def ({len(disabled)} a desactiver)...")

    with open(select_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    new_lines = []
    disabled_count = 0

    for line in lines:
        # Check if line contains a disabled character
        should_disable = False
        for char in disabled:
            if char in line.lower() and not line.strip().startswith(';'):
                should_disable = True
                break

        if should_disable:
            new_lines.append('; ' + line.rstrip() + ' ; DISABLED-NO-SPRITES\n')
            disabled_count += 1
        else:
            new_lines.append(line)

    with open(select_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"  ✅ {disabled_count} personnages desactives dans select.def")


if __name__ == '__main__':
    game_path = 'D:/KOF Ultimate Online'
    fix_all_characters(game_path)
    update_select_def(game_path)
