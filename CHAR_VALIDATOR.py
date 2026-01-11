#!/usr/bin/env python3
"""
KOF Ultimate Online - Character Validator
Scanne tous les personnages et identifie les problemes potentiels
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

CHARS_DIR = Path("chars")
DATA_DIR = Path("data")
RESULTS_FILE = "char_validation_results.json"

# Problemes connus qui causent des crashes
CRASH_PATTERNS = {
    'missing_sff': "Fichier .sff manquant",
    'missing_air': "Fichier .air manquant",
    'missing_def': "Fichier .def manquant",
    'missing_cmd': "Fichier .cmd manquant",
    'missing_cns': "Fichier .cns/.cns.zss manquant",
    'invalid_anim': "Animation reference invalide",
    'missing_sprite': "Sprite reference manquant",
    'clsn_error': "Erreur CLSN (collision box)",
    'state_error': "StateController invalide",
    'triggerall_error': "TriggerAll/Trigger error",
    'helper_error': "Helper mal configure",
    'explod_error': "Explod mal configure",
    'projectile_error': "Projectile mal configure"
}

def scan_def_file(def_path):
    """Analyse le fichier .def du personnage"""
    issues = []
    required_files = {}

    try:
        with open(def_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()

        # Extraire les fichiers references
        patterns = {
            'sprite': r'sprite\s*=\s*(.+\.sff)',
            'anim': r'anim\s*=\s*(.+\.air)',
            'cmd': r'cmd\s*=\s*(.+\.cmd)',
            'cns': r'cns\s*=\s*(.+\.cns)',
            'sound': r'sound\s*=\s*(.+\.snd)',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                required_files[key] = match.group(1).strip()

    except Exception as e:
        issues.append(f"Erreur lecture .def: {e}")

    return required_files, issues

def check_file_exists(char_dir, filename):
    """Verifie si un fichier existe dans le dossier du personnage"""
    if not filename:
        return False
    filepath = char_dir / filename
    return filepath.exists()

def scan_air_file(air_path):
    """Analyse le fichier .air pour les erreurs"""
    issues = []
    animations_count = 0

    try:
        with open(air_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Compter les animations
        animations = re.findall(r'\[Begin Action (\d+)\]', content, re.IGNORECASE)
        animations_count = len(animations)

        # Chercher les erreurs CLSN courantes
        if 'clsn2default:' in content.lower() or 'clsn1default:' in content.lower():
            # Verifier les CLSN mal formees
            clsn_errors = re.findall(r'clsn\d+\[\d+\]\s*=\s*[^\d\-]', content, re.IGNORECASE)
            if clsn_errors:
                issues.append("CLSN mal formatees detectees")

        # Verifier les sprites references
        sprite_refs = re.findall(r'^\s*(\d+)\s*,\s*(\d+)\s*,', content, re.MULTILINE)

    except Exception as e:
        issues.append(f"Erreur lecture .air: {e}")

    return animations_count, issues

def scan_cns_file(cns_path):
    """Analyse le fichier .cns pour les erreurs"""
    issues = []
    states_count = 0

    try:
        with open(cns_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Compter les states
        states = re.findall(r'\[State(?:def)?\s+(-?\d+)', content, re.IGNORECASE)
        states_count = len(states)

        # Chercher les erreurs courantes
        error_patterns = [
            (r'trigger\d+\s*=\s*$', "Trigger vide"),
            (r'value\s*=\s*$', "Value vide"),
            (r'anim\s*=\s*[^\d\-\n]', "Anim invalide"),
        ]

        for pattern, msg in error_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                issues.append(msg)

    except Exception as e:
        issues.append(f"Erreur lecture .cns: {e}")

    return states_count, issues

def validate_character(char_name):
    """Valide un personnage complet"""
    char_dir = CHARS_DIR / char_name
    result = {
        'name': char_name,
        'status': 'unknown',
        'issues': [],
        'warnings': [],
        'files': {},
        'stats': {}
    }

    if not char_dir.exists():
        result['status'] = 'missing'
        result['issues'].append("Dossier personnage manquant")
        return result

    # Trouver le fichier .def principal
    def_files = list(char_dir.glob('*.def'))
    if not def_files:
        result['status'] = 'broken'
        result['issues'].append("Aucun fichier .def trouve")
        return result

    # Utiliser le .def qui correspond au nom du dossier ou le premier trouve
    main_def = None
    for def_file in def_files:
        if def_file.stem.lower() == char_name.lower():
            main_def = def_file
            break
    if not main_def:
        main_def = def_files[0]

    result['files']['def'] = main_def.name

    # Analyser le .def
    required_files, def_issues = scan_def_file(main_def)
    result['issues'].extend(def_issues)

    # Verifier les fichiers requis
    critical_missing = []

    # SFF (sprites)
    sff_files = list(char_dir.glob('*.sff'))
    if not sff_files:
        critical_missing.append('missing_sff')
    else:
        result['files']['sff'] = sff_files[0].name

    # AIR (animations)
    air_files = list(char_dir.glob('*.air'))
    if not air_files:
        critical_missing.append('missing_air')
    else:
        result['files']['air'] = air_files[0].name
        anim_count, air_issues = scan_air_file(air_files[0])
        result['stats']['animations'] = anim_count
        result['warnings'].extend(air_issues)

    # CNS (states)
    cns_files = list(char_dir.glob('*.cns')) + list(char_dir.glob('*.cns.zss'))
    if not cns_files:
        critical_missing.append('missing_cns')
    else:
        result['files']['cns'] = cns_files[0].name
        states_count, cns_issues = scan_cns_file(cns_files[0])
        result['stats']['states'] = states_count
        result['warnings'].extend(cns_issues)

    # CMD (commands)
    cmd_files = list(char_dir.glob('*.cmd'))
    if not cmd_files:
        result['warnings'].append("Fichier .cmd manquant (peut utiliser celui par defaut)")
    else:
        result['files']['cmd'] = cmd_files[0].name

    # SND (sounds) - optionnel
    snd_files = list(char_dir.glob('*.snd'))
    if snd_files:
        result['files']['snd'] = snd_files[0].name

    # Determiner le status
    if critical_missing:
        result['status'] = 'broken'
        for issue_key in critical_missing:
            result['issues'].append(CRASH_PATTERNS.get(issue_key, issue_key))
    elif result['warnings']:
        result['status'] = 'warning'
    else:
        result['status'] = 'ok'

    return result

def main():
    print("=" * 60)
    print("   KOF ULTIMATE ONLINE - CHARACTER VALIDATOR")
    print("=" * 60)
    print()

    if not CHARS_DIR.exists():
        print(f"ERREUR: Dossier chars non trouve: {CHARS_DIR}")
        return

    # Scanner tous les personnages
    char_folders = [d for d in CHARS_DIR.iterdir() if d.is_dir()]
    total = len(char_folders)

    print(f"Scanning {total} personnages...\n")

    results = {
        'scan_date': datetime.now().isoformat(),
        'total_chars': total,
        'ok': [],
        'warning': [],
        'broken': [],
        'details': {}
    }

    for i, char_folder in enumerate(sorted(char_folders), 1):
        char_name = char_folder.name
        print(f"[{i:3}/{total}] {char_name[:40]:<40}", end=" ")

        result = validate_character(char_name)
        results['details'][char_name] = result

        if result['status'] == 'ok':
            results['ok'].append(char_name)
            print("[OK]")
        elif result['status'] == 'warning':
            results['warning'].append(char_name)
            print("[WARNING]")
        else:
            results['broken'].append(char_name)
            print("[BROKEN]")

    # Sauvegarder les resultats
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Afficher le resume
    print("\n" + "=" * 60)
    print("   RESULTATS")
    print("=" * 60)
    print(f"\n   OK:      {len(results['ok']):3} personnages")
    print(f"   WARNING: {len(results['warning']):3} personnages")
    print(f"   BROKEN:  {len(results['broken']):3} personnages")
    print()

    if results['broken']:
        print("PERSONNAGES CASSES (causent des crashes):")
        for char in results['broken'][:20]:
            detail = results['details'][char]
            print(f"  - {char}: {', '.join(detail['issues'][:2])}")
        if len(results['broken']) > 20:
            print(f"  ... et {len(results['broken'])-20} autres")

    print(f"\nResultats sauvegardes dans: {RESULTS_FILE}")

    # Generer select.def safe
    generate_safe_select(results)

def generate_safe_select(results):
    """Genere un select.def avec uniquement les personnages stables"""
    safe_chars = results['ok'] + results['warning']

    output = """; IKEMEN GO Select.def - AUTO-GENERATED SAFE ROSTER
; Genere le {date}
; {ok} personnages OK, {warn} avec warnings
; {broken} personnages exclus (crashes)

[Characters]
""".format(
        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        ok=len(results['ok']),
        warn=len(results['warning']),
        broken=len(results['broken'])
    )

    # Ajouter les personnages OK d'abord
    output += "; === PERSONNAGES STABLES ===\n"
    for char in sorted(results['ok']):
        output += f"{char}, stages/Abyss-Rugal-Palace.def\n"

    # Ajouter les warnings (commentes pour review)
    if results['warning']:
        output += "\n; === PERSONNAGES AVEC WARNINGS (a tester) ===\n"
        for char in sorted(results['warning']):
            output += f";{char}, stages/Abyss-Rugal-Palace.def\n"

    # Lister les exclus en commentaire
    if results['broken']:
        output += "\n; === EXCLUS (CRASHES) ===\n"
        for char in sorted(results['broken']):
            output += f"; {char} - CRASH\n"

    output += """
[ExtraStages]
stages/Abyss-Rugal-Palace.def

[Options]
arcade.maxmatches = 10,0,0,0,0,0,0,0,0,0
team.maxmatches = 4,0,0,0,0,0,0,0,0,0
"""

    safe_select_path = DATA_DIR / "select_validated.def"
    with open(safe_select_path, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"\nSelect.def safe genere: {safe_select_path}")
    print(f"  -> {len(results['ok'])} personnages actives")

if __name__ == "__main__":
    main()
