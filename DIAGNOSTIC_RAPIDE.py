#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 DIAGNOSTIC RAPIDE - Analyse immédiate des problèmes
Vérifie tous les fichiers critiques
"""

from pathlib import Path
import json

def diagnostic_rapide():
    """Diagnostic rapide des problèmes"""
    game_dir = Path(__file__).parent

    print("="*70)
    print("🔍 DIAGNOSTIC RAPIDE DU JEU")
    print("="*70)

    problems = []

    # 1. Vérifier exécutable
    print("\n1️⃣ Vérification exécutable...")
    exes = [
        game_dir / "KOF_Ultimate_Online.exe",
        game_dir / "Ikemen_GO.exe",
        game_dir / "mugen.exe"
    ]

    exe_found = False
    for exe in exes:
        if exe.exists():
            print(f"   ✅ Trouvé: {exe.name}")
            exe_found = True
            break

    if not exe_found:
        print("   ❌ AUCUN EXÉCUTABLE TROUVÉ!")
        problems.append("Pas d'exécutable de jeu")

    # 2. Vérifier select.def
    print("\n2️⃣ Vérification select.def...")
    select_def = game_dir / "data" / "select.def"

    if not select_def.exists():
        print("   ❌ select.def MANQUANT!")
        problems.append("select.def manquant")
    else:
        print(f"   ✅ select.def existe")

        # Analyser le contenu
        try:
            content = select_def.read_text(encoding='utf-8', errors='ignore')

            # Compter personnages actifs
            char_lines = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith(';') and ',' in line:
                    if not any(x in line.lower() for x in ['[characters]', '[extrastages]', '[stages]', '[options]']):
                        char_lines.append(line)

            print(f"   📊 Personnages trouvés: {len(char_lines)}")

            if len(char_lines) == 0:
                print("   ❌ AUCUN PERSONNAGE ACTIF!")
                problems.append("Aucun personnage dans select.def")
            elif len(char_lines) == 1:
                print("   ⚠️  Un seul personnage (minimal)")
                char_name = char_lines[0].split(',')[0].strip()
                print(f"   👤 Personnage: {char_name}")
            else:
                print(f"   ✅ {len(char_lines)} personnages")

        except Exception as e:
            print(f"   ❌ Erreur lecture: {e}")
            problems.append(f"Erreur select.def: {e}")

    # 3. Vérifier dossier chars
    print("\n3️⃣ Vérification dossier chars/...")
    chars_dir = game_dir / "chars"

    if not chars_dir.exists():
        print("   ❌ Dossier chars/ MANQUANT!")
        problems.append("Dossier chars/ manquant")
    else:
        char_folders = [d for d in chars_dir.iterdir() if d.is_dir()]
        print(f"   📁 {len(char_folders)} dossiers de personnages")

        # Vérifier fichiers .def
        chars_with_def = 0
        chars_without_def = []

        for char_folder in char_folders[:10]:  # Vérifier les 10 premiers
            def_files = list(char_folder.glob("*.def"))
            if def_files:
                chars_with_def += 1
            else:
                chars_without_def.append(char_folder.name)

        if chars_without_def:
            print(f"   ⚠️  {len(chars_without_def)} personnages sans .def")
            for char in chars_without_def[:5]:
                print(f"      - {char}")
        else:
            print(f"   ✅ Tous les personnages ont un .def")

    # 4. Vérifier stages
    print("\n4️⃣ Vérification stages/...")
    stages_dir = game_dir / "stages"

    if not stages_dir.exists():
        print("   ❌ Dossier stages/ MANQUANT!")
        problems.append("Dossier stages/ manquant")
    else:
        stage_files = list(stages_dir.glob("*.def"))
        print(f"   📁 {len(stage_files)} stages trouvés")

        if len(stage_files) == 0:
            print("   ❌ AUCUN STAGE!")
            problems.append("Aucun stage")
        else:
            print(f"   ✅ {len(stage_files)} stages disponibles")

    # 5. Vérifier data/
    print("\n5️⃣ Vérification data/...")
    data_dir = game_dir / "data"

    if not data_dir.exists():
        print("   ❌ Dossier data/ MANQUANT!")
        problems.append("Dossier data/ manquant")
    else:
        print("   ✅ Dossier data/ existe")

        # Fichiers critiques
        critical_files = ["common1.cns", "fight.def"]
        for file in critical_files:
            file_path = data_dir / file
            if file_path.exists():
                print(f"   ✅ {file}")
            else:
                print(f"   ⚠️  {file} manquant")

    # RÉSUMÉ
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DIAGNOSTIC")
    print("="*70)

    if not problems:
        print("\n✅ Aucun problème critique détecté")
        print("\n💡 Si le jeu crash quand même:")
        print("   1. Lancez: python TEST_MANUAL_SIMPLE.py")
        print("   2. Le crash est probablement dans un fichier .def corrompu")
    else:
        print(f"\n❌ {len(problems)} PROBLÈMES DÉTECTÉS:\n")
        for i, problem in enumerate(problems, 1):
            print(f"   {i}. {problem}")

        print("\n🔧 ACTIONS RECOMMANDÉES:")

        if "Aucun personnage dans select.def" in problems:
            print("\n   1. Ouvrir data/select.def")
            print("   2. Ajouter au moins un personnage dans [Characters]")
            print("   3. Format: nom_personnage, stages/nom_stage.def")

        if "Aucun stage" in problems:
            print("\n   1. Télécharger des stages MUGEN")
            print("   2. Les placer dans stages/")
            print("   3. Ajouter dans data/select.def")

    print("\n" + "="*70)

    return len(problems) == 0

if __name__ == "__main__":
    diagnostic_rapide()
