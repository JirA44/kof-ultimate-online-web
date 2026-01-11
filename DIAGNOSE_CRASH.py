#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNOSTIC COMPLET DES CRASHES
Identifie les personnages/stages qui causent des crashes
"""
import os
from pathlib import Path
import re

def check_file_exists(path):
    """Vérifie qu'un fichier existe"""
    return path.exists() if isinstance(path, Path) else Path(path).exists()

def analyze_character_def(char_path):
    """Analyse le fichier .def d'un personnage"""
    errors = []
    warnings = []

    # Chercher le .def
    def_files = list(char_path.glob("*.def"))
    if not def_files:
        errors.append("Aucun fichier .def trouvé")
        return errors, warnings

    def_file = def_files[0]

    try:
        with open(def_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Vérifier les fichiers référencés
        files_section = re.search(r'\[Files\](.*?)(?:\[|$)', content, re.DOTALL)
        if files_section:
            files_text = files_section.group(1)

            # Chercher les références de fichiers
            patterns = [
                (r'cmd\s*=\s*(.+)', 'CMD'),
                (r'cns\s*=\s*(.+)', 'CNS'),
                (r'st\s*=\s*(.+)', 'ST'),
                (r'stcommon\s*=\s*(.+)', 'ST Common'),
                (r'sprite\s*=\s*(.+)', 'Sprite'),
                (r'anim\s*=\s*(.+)', 'Animation'),
                (r'sound\s*=\s*(.+)', 'Sound'),
                (r'pal\d+\s*=\s*(.+)', 'Palette'),
            ]

            for pattern, file_type in patterns:
                matches = re.findall(pattern, files_text, re.IGNORECASE)
                for match in matches:
                    filename = match.strip().strip('"')
                    if filename and not filename.startswith(';'):
                        file_path = char_path / filename
                        if not file_path.exists():
                            errors.append(f"{file_type} manquant: {filename}")

        # Vérifier les storyboards
        if 'intro.storyboard' in content:
            intro_match = re.search(r'intro\.storyboard\s*=\s*(.+)', content)
            if intro_match:
                intro_file = intro_match.group(1).strip().strip('"')
                if intro_file and not (char_path / intro_file).exists():
                    warnings.append(f"Intro storyboard manquant: {intro_file}")

        if 'ending.storyboard' in content:
            ending_match = re.search(r'ending\.storyboard\s*=\s*(.+)', content)
            if ending_match:
                ending_file = ending_match.group(1).strip().strip('"')
                if ending_file and not (char_path / ending_file).exists():
                    warnings.append(f"Ending storyboard manquant: {ending_file}")

    except Exception as e:
        errors.append(f"Erreur lecture .def: {e}")

    return errors, warnings

def analyze_stage(stage_path):
    """Analyse un fichier de stage"""
    errors = []
    warnings = []

    if not stage_path.exists():
        errors.append(f"Stage introuvable: {stage_path}")
        return errors, warnings

    try:
        with open(stage_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Vérifier les fichiers référencés
        spr_match = re.search(r'spr\s*=\s*(.+)', content)
        if spr_match:
            spr_file = spr_match.group(1).strip().strip('"')
            if spr_file:
                spr_path = stage_path.parent / spr_file
                if not spr_path.exists():
                    errors.append(f"Stage sprite manquant: {spr_file}")

        # Vérifier BGM
        bgm_matches = re.findall(r'bgmusic\s*=\s*(.+)', content)
        for bgm_match in bgm_matches:
            bgm_file = bgm_match.strip().strip('"')
            if bgm_file and bgm_file.lower() not in ['none', '']:
                # Les BGM peuvent être dans data/musica ou ailleurs
                # C'est optionnel donc juste warning
                warnings.append(f"BGM référencé: {bgm_file}")

    except Exception as e:
        errors.append(f"Erreur lecture stage: {e}")

    return errors, warnings

def main():
    print("="*80)
    print("🔍 DIAGNOSTIC COMPLET - RECHERCHE DE LA CAUSE DU CRASH")
    print("="*80)

    base_path = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo")
    select_def = base_path / "data" / "select.def"

    # Lire select.def
    print("\n📋 Lecture du roster...")
    chars = []
    stages = []

    with open(select_def, 'r', encoding='utf-8') as f:
        in_chars_section = False
        in_stages_section = False

        for line in f:
            line = line.strip()

            if line.startswith('[Characters]'):
                in_chars_section = True
                in_stages_section = False
                continue
            elif line.startswith('[Stages]') or line.startswith('[ExtraStages]'):
                in_chars_section = False
                in_stages_section = True
                continue
            elif line.startswith('['):
                in_chars_section = False
                in_stages_section = False
                continue

            if in_chars_section and line and not line.startswith(';'):
                if ',' in line:
                    char_name = line.split(',')[0].strip()
                    stage_name = line.split(',')[1].strip() if len(line.split(',')) > 1 else None
                    if char_name:
                        chars.append(char_name)
                        if stage_name:
                            stages.append(stage_name)

            if in_stages_section and line and not line.startswith(';'):
                stages.append(line.strip())

    print(f"✓ {len(chars)} personnages trouvés")
    print(f"✓ {len(set(stages))} stages uniques trouvés")

    # Analyser chaque personnage
    print("\n" + "="*80)
    print("🎮 ANALYSE DES PERSONNAGES")
    print("="*80)

    total_errors = 0
    total_warnings = 0
    problematic_chars = []

    for i, char_name in enumerate(chars, 1):
        char_path = base_path / "chars" / char_name

        print(f"\n[{i}/{len(chars)}] {char_name}")

        if not char_path.exists():
            print(f"  ❌ CRITIQUE: Dossier introuvable!")
            problematic_chars.append((char_name, ["Dossier introuvable"]))
            total_errors += 1
            continue

        errors, warnings = analyze_character_def(char_path)

        if errors:
            print(f"  ❌ {len(errors)} erreur(s) CRITIQUE(S):")
            for error in errors:
                print(f"     - {error}")
            problematic_chars.append((char_name, errors))
            total_errors += len(errors)

        if warnings:
            print(f"  ⚠️  {len(warnings)} avertissement(s):")
            for warning in warnings[:3]:  # Limiter à 3
                print(f"     - {warning}")
            total_warnings += len(warnings)

        if not errors and not warnings:
            print(f"  ✅ OK")

    # Analyser les stages
    print("\n" + "="*80)
    print("🏞️  ANALYSE DES STAGES")
    print("="*80)

    problematic_stages = []
    unique_stages = list(set(stages))

    for i, stage_name in enumerate(unique_stages[:10], 1):  # Limiter à 10 premiers
        stage_path = base_path / stage_name

        print(f"\n[{i}/{min(10, len(unique_stages))}] {stage_name}")

        errors, warnings = analyze_stage(stage_path)

        if errors:
            print(f"  ❌ {len(errors)} erreur(s):")
            for error in errors:
                print(f"     - {error}")
            problematic_stages.append((stage_name, errors))
            total_errors += len(errors)

        if warnings:
            print(f"  ⚠️  {len(warnings)} avertissement(s)")
            total_warnings += len(warnings)

        if not errors and not warnings:
            print(f"  ✅ OK")

    # Rapport final
    print("\n" + "="*80)
    print("📊 RAPPORT FINAL")
    print("="*80)

    print(f"\nErreurs critiques:  {total_errors}")
    print(f"Avertissements:     {total_warnings}")

    if problematic_chars:
        print(f"\n❌ PERSONNAGES PROBLÉMATIQUES ({len(problematic_chars)}):")
        for char_name, errors in problematic_chars:
            print(f"  - {char_name}: {errors[0]}")

    if problematic_stages:
        print(f"\n❌ STAGES PROBLÉMATIQUES ({len(problematic_stages)}):")
        for stage_name, errors in problematic_stages:
            print(f"  - {stage_name}: {errors[0]}")

    # Recommandations
    print("\n" + "="*80)
    print("💡 RECOMMANDATIONS")
    print("="*80)

    if total_errors > 0:
        print("\n🔧 ACTIONS URGENTES:")

        if problematic_chars:
            print(f"\n1. RETIRER les {len(problematic_chars)} personnages problématiques du roster")
            print("   Créer un nouveau select.def sans ces personnages")

        if problematic_stages:
            print(f"\n2. CORRIGER ou REMPLACER les {len(problematic_stages)} stages défectueux")
            print("   Utiliser un stage par défaut fiable (ex: stages/kfm.def)")

    else:
        print("\n✅ Aucune erreur critique détectée dans les fichiers!")
        print("\nSi le jeu crash quand même, le problème vient probablement de:")
        print("  1. Contenu corrompu dans les fichiers .sff/.snd/.air")
        print("  2. Incompatibilités entre versions MUGEN/Ikemen")
        print("  3. Problème dans les CNS/ST (states code)")
        print("\nRecommandation: Utiliser UNIQUEMENT des personnages KOF officiels")

    # Créer un roster minimal ultra-safe
    print("\n" + "="*80)
    print("🛡️  CRÉATION ROSTER MINIMAL ULTRA-SAFE")
    print("="*80)

    safe_chars = [char for char in chars if char not in [pc[0] for pc in problematic_chars]]

    if len(safe_chars) < len(chars):
        print(f"\n✓ {len(safe_chars)} personnages sûrs identifiés (sur {len(chars)})")

        select_minimal = base_path / "data" / "select_minimal_safe.def"

        with open(select_def, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Copier l'en-tête
        new_content = []
        in_chars = False

        for line in original_content.split('\n'):
            if line.strip().startswith('[Characters]'):
                in_chars = True
                new_content.append(line)
                new_content.append(f"; AUTO-GÉNÉRÉ - {len(safe_chars)} PERSONNAGES SÛRS UNIQUEMENT")
                new_content.append(";")
                continue

            if in_chars:
                if line.strip().startswith('['):
                    in_chars = False
                    new_content.append(";")
                    new_content.append("; === FIN PERSONNAGES SÛRS ===")
                    new_content.append(line)
                    continue

                if line.strip() and not line.strip().startswith(';'):
                    char_name = line.split(',')[0].strip()
                    if char_name in safe_chars:
                        new_content.append(line)
                    else:
                        new_content.append(f"; RETIRÉ (PROBLÉMATIQUE): {line}")
                else:
                    new_content.append(line)
            else:
                new_content.append(line)

        with open(select_minimal, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_content))

        print(f"✓ Créé: {select_minimal.name}")
        print(f"\n💡 Pour utiliser ce roster:")
        print(f"   1. Renommer data/select.def → data/select_old.def")
        print(f"   2. Renommer {select_minimal.name} → select.def")
        print(f"   3. Relancer le jeu")

    print("\n" + "="*80)
    print("✅ DIAGNOSTIC TERMINÉ")
    print("="*80)

    input("\nAppuyez sur ENTRÉE pour fermer...")

if __name__ == "__main__":
    main()
