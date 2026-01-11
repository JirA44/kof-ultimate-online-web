#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour vérifier quels personnages ont des portraits (9000,0 et 9000,1)
"""
import os
import re

CHARS_DIR = r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo\chars"
SELECT_DEF = r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo\data\select.def"

def read_select_def():
    """Lit le select.def et extrait la liste des personnages"""
    chars = []
    with open(SELECT_DEF, 'r', encoding='utf-8') as f:
        in_chars = False
        for line in f:
            line = line.strip()
            if line == '[Characters]':
                in_chars = True
                continue
            if in_chars:
                if line.startswith('['):
                    break
                if line and not line.startswith(';'):
                    chars.append(line)
    return chars

def check_portrait_files(char_name):
    """Vérifie si un personnage a des fichiers de portrait"""
    char_dir = os.path.join(CHARS_DIR, char_name)
    if not os.path.exists(char_dir):
        return {'mini': False, 'big': False, 'reason': 'DIR_NOT_FOUND'}

    # Chercher récursivement les fichiers 9000,0.* et 9000,1.*
    mini_found = False
    big_found = False

    for root, dirs, files in os.walk(char_dir):
        for file in files:
            if file.startswith('9000,0.') or file.startswith('9000_0.'):
                mini_found = True
            if file.startswith('9000,1.') or file.startswith('9000_1.'):
                big_found = True

    reason = None
    if not mini_found and not big_found:
        reason = 'NO_PORTRAITS'
    elif not mini_found:
        reason = 'NO_MINI'
    elif not big_found:
        reason = 'NO_BIG'

    return {'mini': mini_found, 'big': big_found, 'reason': reason}

def main():
    print("=== VÉRIFICATION DES PORTRAITS ===\n")

    chars = read_select_def()
    print(f"Total personnages dans select.def: {len(chars)}\n")

    stats = {
        'with_both': [],
        'with_mini_only': [],
        'with_big_only': [],
        'without_portraits': [],
        'dir_not_found': []
    }

    for char in chars:
        result = check_portrait_files(char)

        if result['reason'] == 'DIR_NOT_FOUND':
            stats['dir_not_found'].append(char)
        elif result['mini'] and result['big']:
            stats['with_both'].append(char)
        elif result['mini'] and not result['big']:
            stats['with_mini_only'].append(char)
        elif not result['mini'] and result['big']:
            stats['with_big_only'].append(char)
        else:
            stats['without_portraits'].append(char)

    # Affichage des résultats
    print(f"✅ Avec portraits complets (mini + big): {len(stats['with_both'])}")
    print(f"⚠️  Avec mini uniquement: {len(stats['with_mini_only'])}")
    print(f"⚠️  Avec big uniquement: {len(stats['with_big_only'])}")
    print(f"❌ Sans portraits: {len(stats['without_portraits'])}")
    print(f"❌ Dossier introuvable: {len(stats['dir_not_found'])}")
    print()

    # Détails des personnages sans portraits
    if stats['without_portraits']:
        print("PERSONNAGES SANS PORTRAITS:")
        for char in stats['without_portraits']:
            print(f"  - {char}")
        print()

    if stats['dir_not_found']:
        print("DOSSIERS INTROUVABLES:")
        for char in stats['dir_not_found']:
            print(f"  - {char}")
        print()

    # Sauvegarder un rapport
    report_path = r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo\PORTRAIT_REPORT.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=== RAPPORT PORTRAITS KOF ULTIMATE ===\n\n")
        f.write(f"Total personnages: {len(chars)}\n")
        f.write(f"Avec portraits complets: {len(stats['with_both'])}\n")
        f.write(f"Avec mini uniquement: {len(stats['with_mini_only'])}\n")
        f.write(f"Avec big uniquement: {len(stats['with_big_only'])}\n")
        f.write(f"Sans portraits: {len(stats['without_portraits'])}\n")
        f.write(f"Dossier introuvable: {len(stats['dir_not_found'])}\n\n")

        f.write("\n=== PERSONNAGES SANS PORTRAITS ===\n")
        for char in stats['without_portraits']:
            f.write(f"{char}\n")

        f.write("\n=== DOSSIERS INTROUVABLES ===\n")
        for char in stats['dir_not_found']:
            f.write(f"{char}\n")

    print(f"Rapport sauvegardé: {report_path}")

if __name__ == '__main__':
    main()
