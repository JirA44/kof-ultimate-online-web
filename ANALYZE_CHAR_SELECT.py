#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse du Character Select Screen
Identifie les problèmes d'affichage et génère une configuration optimale
"""

from pathlib import Path
import re

def analyze_select_def():
    """Analyse select.def pour compter les personnages et détecter les problèmes"""

    select_file = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo\data\select.def")

    if not select_file.exists():
        print(f"❌ {select_file} n'existe pas!")
        return None

    with open(select_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    in_characters = False
    characters = []
    blank_lines = 0

    for line in lines:
        stripped = line.strip()

        if stripped == "[Characters]":
            in_characters = True
            continue

        if in_characters:
            if stripped.startswith('['):
                break

            if stripped and not stripped.startswith(';'):
                characters.append(stripped)
            elif not stripped:
                blank_lines += 1

    return {
        'total': len(characters),
        'blank_lines': blank_lines,
        'characters': characters
    }

def analyze_system_def():
    """Analyse system.def pour la configuration actuelle"""

    system_file = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo\data\system.def")

    with open(system_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Extraire [Select Info]
    select_info = {}
    in_select_info = False

    for line in content.split('\n'):
        stripped = line.strip()

        if stripped == "[Select Info]":
            in_select_info = True
            continue

        if in_select_info:
            if stripped.startswith('['):
                break

            if '=' in stripped and not stripped.startswith(';'):
                key, value = stripped.split('=', 1)
                select_info[key.strip()] = value.strip()

    return select_info

def calculate_optimal_grid(num_chars):
    """Calcule la configuration de grille optimale"""

    # Options de configuration testées
    configs = []

    # Pour 195 caractères, on veut une grille qui:
    # 1. A assez de slots (195+)
    # 2. Minimise l'espace vide
    # 3. A des cellules assez grandes pour les portraits

    # Configuration 1: Grille large avec cellules moyennes
    configs.append({
        'name': 'Large Grid (13×15)',
        'rows': 13,
        'columns': 15,
        'cell_size': '35,35',
        'cell_spacing': 2,
        'pos': '8,55',
        'total_slots': 13 * 15,
        'unused_slots': (13 * 15) - num_chars,
        'width': 15 * 35 + 14 * 2,  # colonnes × taille + espacement
        'height': 13 * 35 + 12 * 2,
    })

    # Configuration 2: Grille très large avec petites cellules
    configs.append({
        'name': 'Wide Grid (11×18)',
        'rows': 11,
        'columns': 18,
        'cell_size': '33,33',
        'cell_spacing': 2,
        'pos': '5,55',
        'total_slots': 11 * 18,
        'unused_slots': (11 * 18) - num_chars,
        'width': 18 * 33 + 17 * 2,
        'height': 11 * 33 + 10 * 2,
    })

    # Configuration 3: Grille haute avec cellules moyennes
    configs.append({
        'name': 'Tall Grid (15×14)',
        'rows': 15,
        'columns': 14,
        'cell_size': '36,36',
        'cell_spacing': 2,
        'pos': '10,50',
        'total_slots': 15 * 14,
        'unused_slots': (15 * 14) - num_chars,
        'width': 14 * 36 + 13 * 2,
        'height': 15 * 36 + 14 * 2,
    })

    # Configuration 4: Grille équilibrée
    configs.append({
        'name': 'Balanced Grid (14×15)',
        'rows': 14,
        'columns': 15,
        'cell_size': '34,34',
        'cell_spacing': 2,
        'pos': '6,52',
        'total_slots': 14 * 15,
        'unused_slots': (14 * 15) - num_chars,
        'width': 15 * 34 + 14 * 2,
        'height': 14 * 34 + 13 * 2,
    })

    return configs

def main():
    print("="*70)
    print("  ANALYSE CHARACTER SELECT SCREEN")
    print("="*70)
    print()

    # Analyse select.def
    select_data = analyze_select_def()

    if not select_data:
        return

    print("📋 SELECT.DEF:")
    print(f"   Total personnages: {select_data['total']}")
    print(f"   Lignes vides: {select_data['blank_lines']}")
    print()

    # Analyse system.def
    system_data = analyze_system_def()

    print("⚙️  CONFIGURATION ACTUELLE (system.def):")
    for key, value in system_data.items():
        print(f"   {key} = {value}")

    # Calculer slots actuels
    current_rows = int(system_data.get('rows', 10))
    current_cols = int(system_data.get('columns', 20))
    current_slots = current_rows * current_cols

    print()
    print(f"   Slots actuels: {current_rows} × {current_cols} = {current_slots}")
    print(f"   Slots utilisés: {select_data['total']}")
    print(f"   Slots vides: {current_slots - select_data['total']}")
    print()

    # Analyser problèmes potentiels
    print("🔍 PROBLÈMES DÉTECTÉS:")

    cell_size = system_data.get('cell.size', '30,30').split(',')
    cell_w, cell_h = int(cell_size[0]), int(cell_size[1])

    if cell_w < 32 or cell_h < 32:
        print(f"   ⚠️  Cellules trop petites ({cell_w}×{cell_h})")
        print("       Les portraits risquent d'être coupés/écrasés")

    if current_slots - select_data['total'] > 50:
        print(f"   ⚠️  Trop de slots vides ({current_slots - select_data['total']})")
        print("       La grille est trop grande")

    spacing = int(system_data.get('cell.spacing', 1))
    if spacing < 2:
        print(f"   ⚠️  Espacement insuffisant ({spacing}px)")
        print("       Les cellules peuvent se toucher")

    # Vérifier largeur écran
    total_width = current_cols * cell_w + (current_cols - 1) * spacing
    if total_width > 630:  # gamewidth = 640
        print(f"   ❌ Grille trop large ({total_width}px > 630px)")
        print("       Dépasse la largeur d'écran!")

    print()

    # Proposer configurations optimales
    print("✅ CONFIGURATIONS RECOMMANDÉES:")
    print()

    configs = calculate_optimal_grid(select_data['total'])

    for i, config in enumerate(configs, 1):
        print(f"   {i}. {config['name']}")
        print(f"      rows = {config['rows']}")
        print(f"      columns = {config['columns']}")
        print(f"      cell.size = {config['cell_size']}")
        print(f"      cell.spacing = {config['cell_spacing']}")
        print(f"      pos = {config['pos']}")
        print(f"      → Slots: {config['total_slots']} ({config['unused_slots']} vides)")
        print(f"      → Taille: {config['width']}×{config['height']} px")
        print()

    print("="*70)
    print("  RECOMMANDATION")
    print("="*70)
    print()
    print("Configuration recommandée: #4 (Balanced Grid)")
    print()
    print("Raisons:")
    print("  ✓ 210 slots (195 chars + 15 vides)")
    print("  ✓ Cellules 34×34 (taille optimale pour portraits)")
    print("  ✓ Espacement de 2px (lisible)")
    print("  ✓ Largeur totale: 538px (dans 640px écran)")
    print("  ✓ Grille équilibrée (14×15)")
    print()
    print("Pour appliquer cette configuration, exécute:")
    print("  python APPLY_OPTIMAL_CHAR_SELECT.py")
    print()

if __name__ == "__main__":
    main()
