#!/usr/bin/env python3
"""
Genere un select.def ultra-stable en combinant:
1. Validation des fichiers (CHAR_VALIDATOR)
2. Tests de crash en combat (test_jouabilite_results.json)
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")

# Personnages qui crashent EN COMBAT (d'apres les tests precedents)
COMBAT_CRASHERS = [
    "03-A-Kyo LV2",
    "Choi_XI",
    "D.Yashiro.Rhythm(Dusk)1.x",
    "D_DisciplineGirl",
    "Daisu",
    "DF-Sula",
    "Element Ash",
    "Garnet 1.1",
    "GOD_ADEL(2012-01-28 Trial)",
    "Kasim_LV2-CKOFM[v0.40]",
    "robo-kyo-kofa",
    "Rugal7th",
    "vandals",
    "WatchTV",
    # Ajoutes manuellement (reports utilisateur)
    "Athena",
    "boss-orochi",
    "Viper",
    "Rose",
    "akuma",
    "Final-IGNIZ",
    "god_orochi",
]

# Personnages avec fichiers manquants (du CHAR_VALIDATOR)
FILE_BROKEN = [
    "ABYSS'Mega's",
    "Alfred_WLS",
    "AngusPurple-KOFM",
    "Another Scarlet",
    "Arctic Emperor",
    "BLAKE V3-1.1",
    "BW-Meiling",
    "C.Kyo.Blood-KOFM",
    "Carlin.Blood-CKOFM",
    "Caser.Yashiro",
    "ccihinako",
    "ccijhun",
    "cciking",
    "D=Rockula",
    "Error Zero",
    "Flamme(S)",
    "HIEL-KOFM",
    "Hiyoi",
    "Infernal_Wind",
    "Kartis",
    "Kevenoce",
    "Keyser-Aunthmer",
    "Kotone",
    "Kyaga-KOFM",
    "Lane.Blood-CKOFM",
    "Littledevil-Phoenix",
    "LUMIEL",
    "New_Kyouki",
    "Noa_MK",
    "Olivia",
    "Orochi.Yamazaki-CKOFM",
    "Psyche_42-1.1",
    "Psyche_57-1.1",
    "R.S.P",
    "Raika",
    "Rinne-RH",
    "Rocken",
    "Samael",
    "Sasin",
    "Sonic Vanesa",
    "Tenrou_Kunagi",
    "ThunderMiss.Shermie",
    "VladRose",
    "Voltage Zeroko-Pre",
    "Yamazaki.Blood",
    "Yuri_SV",
]

# Combiner toutes les exclusions
ALL_EXCLUDED = set(COMBAT_CRASHERS + FILE_BROKEN)

def get_all_chars():
    """Liste tous les personnages disponibles"""
    chars_dir = Path("chars")
    if not chars_dir.exists():
        return []
    return [d.name for d in chars_dir.iterdir() if d.is_dir()]

def main():
    print("=" * 60)
    print("   GENERATION DU ROSTER ULTRA-STABLE")
    print("=" * 60)

    all_chars = get_all_chars()
    print(f"\nPersonnages totaux: {len(all_chars)}")
    print(f"Exclus (fichiers manquants): {len(FILE_BROKEN)}")
    print(f"Exclus (crashes combat): {len(COMBAT_CRASHERS)}")
    print(f"Total exclus: {len(ALL_EXCLUDED)}")

    # Filtrer les personnages stables
    stable_chars = [c for c in all_chars if c not in ALL_EXCLUDED]
    stable_chars.sort()

    print(f"\nPersonnages STABLES: {len(stable_chars)}")

    # Generer le select.def
    output = f"""; IKEMEN GO Select.def - ROSTER ULTRA-STABLE
; Genere le {datetime.now().strftime("%Y-%m-%d %H:%M")}
; {len(stable_chars)} personnages testes et confirmes stables
; {len(ALL_EXCLUDED)} personnages exclus (crashes fichiers + combat)

[Characters]
"""

    for char in stable_chars:
        output += f"{char}, stages/Abyss-Rugal-Palace.def\n"

    output += f"""
; === EXCLUS: FICHIERS MANQUANTS ({len(FILE_BROKEN)}) ===
"""
    for char in sorted(FILE_BROKEN):
        output += f"; {char}\n"

    output += f"""
; === EXCLUS: CRASHES EN COMBAT ({len(COMBAT_CRASHERS)}) ===
"""
    for char in sorted(COMBAT_CRASHERS):
        output += f"; {char}\n"

    output += """
[ExtraStages]
stages/Abyss-Rugal-Palace.def
stages/Anime Blu.def
stages/Anubis.def
stages/Arena.def

[Options]
arcade.maxmatches = 10,0,0,0,0,0,0,0,0,0
team.maxmatches = 4,0,0,0,0,0,0,0,0,0
"""

    # Sauvegarder
    output_file = DATA_DIR / "select_ultra_stable.def"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"\nFichier genere: {output_file}")

    # Appliquer comme select.def principal
    select_def = DATA_DIR / "select.def"
    backup = DATA_DIR / f"select_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.def"

    if select_def.exists():
        select_def.rename(backup)
        print(f"Backup: {backup}")

    with open(select_def, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"select.def mis a jour!")
    print(f"\n{'='*60}")
    print(f"   {len(stable_chars)} PERSONNAGES PRETS A JOUER")
    print(f"{'='*60}")

    # Afficher la liste
    print("\nPersonnages stables:")
    for i, char in enumerate(stable_chars, 1):
        print(f"  {i:3}. {char}")

if __name__ == "__main__":
    main()
