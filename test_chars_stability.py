#!/usr/bin/env python3
"""
Test de stabilité des personnages KOF Ultimate Online
Vérifie que chaque personnage a tous les fichiers requis
"""

import os
import json
from pathlib import Path

CHARS_DIR = Path(__file__).parent / "chars"
STAGES_DIR = Path(__file__).parent / "stages"

def check_character(char_path):
    """Vérifie si un personnage a tous les fichiers requis"""
    issues = []
    char_name = char_path.name

    # Chercher le fichier .def principal
    def_files = list(char_path.glob("*.def"))
    if not def_files:
        return None, ["Pas de fichier .def"]

    def_file = def_files[0]

    # Lire le .def pour trouver les fichiers requis
    try:
        content = def_file.read_text(encoding='utf-8', errors='ignore')
    except:
        try:
            content = def_file.read_text(encoding='latin-1', errors='ignore')
        except:
            return None, ["Impossible de lire le .def"]

    required_files = {}
    for line in content.split('\n'):
        line = line.strip()
        if '=' in line and not line.startswith(';'):
            parts = line.split('=', 1)
            key = parts[0].strip().lower()
            value = parts[1].split(';')[0].strip().strip('"')

            if key in ['cmd', 'cns', 'st', 'sprite', 'anim', 'sound']:
                required_files[key] = value

    # Vérifier les fichiers essentiels
    for key in ['cmd', 'cns', 'sprite', 'anim']:
        if key in required_files:
            file_path = char_path / required_files[key]
            if not file_path.exists():
                issues.append(f"Manquant: {required_files[key]}")

    # Vérifier la taille des fichiers sprite (sff)
    if 'sprite' in required_files:
        sff_path = char_path / required_files['sprite']
        if sff_path.exists():
            size_mb = sff_path.stat().st_size / (1024*1024)
            if size_mb > 100:
                issues.append(f"Sprite trop gros: {size_mb:.1f}MB")

    return def_file.stem, issues

def main():
    print("=" * 60)
    print("TEST DE STABILITÉ DES PERSONNAGES")
    print("=" * 60)

    stable_chars = []
    unstable_chars = []

    char_folders = sorted([d for d in CHARS_DIR.iterdir() if d.is_dir()])
    total = len(char_folders)

    for i, char_path in enumerate(char_folders, 1):
        char_name = char_path.name

        # Skip certains dossiers
        if char_name in ['ai', 'data', 'backup']:
            continue

        name, issues = check_character(char_path)

        if issues:
            unstable_chars.append((char_name, issues))
            status = "❌"
        else:
            stable_chars.append(char_name)
            status = "✅"

        print(f"[{i}/{total}] {status} {char_name}")

    print("\n" + "=" * 60)
    print(f"RÉSULTATS: {len(stable_chars)}/{total} personnages stables")
    print("=" * 60)

    # Créer un select.def avec les personnages stables
    select_content = """; IKEMEN GO Select.def
; ROSTER AUTO-TESTÉ - Personnages avec fichiers complets
; Généré automatiquement

[Characters]
"""

    # Ajouter les 50 premiers personnages stables
    for char in stable_chars[:50]:
        select_content += f"{char}, stages/Abyss-Rugal-Palace.def\n"

    select_content += """
[ExtraStages]
stages/Abyss-Rugal-Palace.def

[Options]
"""

    # Sauvegarder
    select_path = Path(__file__).parent / "data" / "select_tested.def"
    select_path.write_text(select_content, encoding='utf-8')

    print(f"\n✅ Créé: data/select_tested.def ({len(stable_chars[:50])} personnages)")

    # Afficher les personnages problématiques
    if unstable_chars:
        print(f"\n⚠️ {len(unstable_chars)} personnages avec problèmes:")
        for char, issues in unstable_chars[:10]:
            print(f"  - {char}: {', '.join(issues)}")

if __name__ == "__main__":
    main()
