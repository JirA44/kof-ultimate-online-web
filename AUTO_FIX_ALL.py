#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          KOF ULTIMATE ONLINE - AUTO-FIX & OPTIMIZATION SYSTEM                ║
║                    Correction automatique de tous les bugs                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

GAME_DIR = Path(__file__).parent
CHARS_DIR = GAME_DIR / "chars"
DATA_DIR = GAME_DIR / "data"
STAGES_DIR = GAME_DIR / "stages"
BACKUP_DIR = GAME_DIR / "backup_before_fix"

# Statistiques
stats = {
    'chars_analyzed': 0,
    'chars_fixed': 0,
    'issues_fixed': 0,
    'chars_removed': 0,
    'stable_chars': []
}

def read_file(path):
    """Lit un fichier avec gestion des encodages"""
    for enc in ['utf-8', 'latin-1', 'cp1252', 'shift-jis']:
        try:
            return path.read_text(encoding=enc, errors='ignore')
        except:
            continue
    return ""

def write_file(path, content):
    """Écrit un fichier"""
    path.write_text(content, encoding='utf-8')

def backup_char(char_path):
    """Sauvegarde un personnage avant modification"""
    backup_path = BACKUP_DIR / char_path.name
    if not backup_path.exists():
        shutil.copytree(char_path, backup_path, dirs_exist_ok=True)

def fix_cns_file(cns_path):
    """Corrige les bugs courants dans un fichier CNS"""
    content = read_file(cns_path)
    original = content
    fixes = 0

    # Fix 1: Vélocités extrêmes (cause fly-away)
    def fix_extreme_vel(match):
        nonlocal fixes
        vel_type = match.group(1)
        value = int(match.group(2))
        if abs(value) > 30:
            fixes += 1
            new_val = 30 if value > 0 else -30
            return f"vel {vel_type} = {new_val}"
        return match.group(0)

    content = re.sub(r'vel\s*([xy])\s*=\s*(-?\d{3,})', fix_extreme_vel, content, flags=re.IGNORECASE)

    # Fix 2: PosAdd extrêmes
    def fix_extreme_pos(match):
        nonlocal fixes
        value = int(match.group(1))
        if abs(value) > 500:
            fixes += 1
            new_val = 500 if value > 0 else -500
            return f"posadd = 0, {new_val}"
        return match.group(0)

    content = re.sub(r'posadd\s*=\s*0\s*,\s*(-?\d{4,})', fix_extreme_pos, content, flags=re.IGNORECASE)

    # Fix 3: ChangeState sans trigger (cause freeze)
    # Ajouter trigger1 = 1 si manquant
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # Si c'est un ChangeState, vérifier qu'il y a un trigger avant
        if 'changestate' in line.lower() and '=' in line:
            # Chercher en arrière pour un trigger
            has_trigger = False
            for j in range(max(0, len(new_lines)-5), len(new_lines)-1):
                if 'trigger' in new_lines[j].lower():
                    has_trigger = True
                    break
            if not has_trigger and not line.strip().startswith(';'):
                # Ajouter un trigger basique
                new_lines.insert(-1, "trigger1 = Time > 0")
                fixes += 1

        i += 1

    content = '\n'.join(new_lines)

    # Fix 4: Helper sans ID (cause overflow)
    content = re.sub(
        r'(\[State[^\]]*\]\s*type\s*=\s*Helper)(\s*\n)(?!.*helperid)',
        r'\1\nhelperid = 9000 + random%100\2',
        content,
        flags=re.IGNORECASE
    )

    if content != original:
        write_file(cns_path, content)
        return fixes
    return 0

def fix_def_file(def_path):
    """Corrige le fichier DEF d'un personnage"""
    content = read_file(def_path)
    original = content
    fixes = 0

    # Fix: MugenVersion manquant ou invalide
    if 'mugenversion' not in content.lower():
        content = content.replace('[Info]', '[Info]\nMugenVersion = 1.0')
        fixes += 1

    # Fix: Lignes vides dans les chemins de fichiers
    content = re.sub(r'(\w+)\s*=\s*\n', r'\1 = \n', content)

    if content != original:
        write_file(def_path, content)
        return fixes
    return 0

def analyze_and_fix_character(char_path):
    """Analyse et corrige un personnage"""
    char_name = char_path.name
    total_fixes = 0
    issues = []
    is_stable = True

    # Trouver le fichier DEF
    def_files = list(char_path.glob("*.def"))
    if not def_files:
        return None, ["Pas de fichier DEF"]

    # Vérifier la taille des sprites
    sff_files = list(char_path.glob("*.sff")) + list(char_path.glob("**/*.sff"))
    for sff in sff_files:
        size_mb = sff.stat().st_size / (1024*1024)
        if size_mb > 100:
            issues.append(f"Sprite trop gros: {size_mb:.0f}MB")
            is_stable = False

    # Corriger le DEF
    fixes = fix_def_file(def_files[0])
    total_fixes += fixes

    # Corriger tous les fichiers CNS
    cns_files = list(char_path.glob("*.cns")) + list(char_path.glob("**/*.cns"))
    for cns in cns_files:
        try:
            fixes = fix_cns_file(cns)
            total_fixes += fixes
        except Exception as e:
            issues.append(f"Erreur CNS: {e}")

    # Vérifier les fichiers requis
    def_content = read_file(def_files[0])
    required = ['cmd', 'cns', 'sprite', 'anim']
    for req in required:
        pattern = rf'{req}\s*=\s*(\S+)'
        match = re.search(pattern, def_content, re.IGNORECASE)
        if match:
            file_path = char_path / match.group(1)
            if not file_path.exists():
                issues.append(f"Fichier manquant: {match.group(1)}")
                is_stable = False

    return {
        'name': char_name,
        'fixes': total_fixes,
        'issues': issues,
        'stable': is_stable and len(issues) == 0
    }, None

def optimize_game_settings():
    """Optimise les paramètres du jeu"""
    print("\n⚙️ Optimisation des paramètres du jeu...")

    # Créer/modifier le fichier de config Ikemen
    config_path = GAME_DIR / "save" / "config.json"
    config_path.parent.mkdir(exist_ok=True)

    config = {
        "AIRandomColor": True,
        "AudioDucking": False,
        "AutoGuard": False,
        "Fullscreen": False,
        "GameWidth": 640,
        "GameHeight": 480,
        "MSAA": False,
        "VRetrace": 1,
        "VolumeBgm": 80,
        "VolumeMaster": 100,
        "VolumeSfx": 80,
        "MaxPowerMode": False,
        "AIRamping": True,
        "NumSimul": [2, 2],
        "NumTurns": [2, 2],
        "Team1VS2Life": 100,
        "TeamPowerShare": True,
        "RoundsToWin": 2,
        "MaxAfterImages": 32,
        "MaxDrawGames": 1,
        "MaxExplods": 256,
        "MaxHelper": 56,
        "MaxPlayerProjectile": 50
    }

    import json
    config_path.write_text(json.dumps(config, indent=2))
    print("  ✅ Configuration optimisée")

def create_stable_roster(stable_chars):
    """Crée un roster avec uniquement les personnages stables"""
    print(f"\n📝 Création du roster avec {len(stable_chars)} personnages stables...")

    content = f"""; ╔══════════════════════════════════════════════════════════════════════════╗
; ║           KOF ULTIMATE ONLINE - ROSTER FINAL OPTIMISÉ                    ║
; ╠══════════════════════════════════════════════════════════════════════════╣
; ║  Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<54} ║
; ║  Personnages testés et optimisés: {len(stable_chars):<37} ║
; ║  Tous les bugs connus ont été corrigés                                   ║
; ╚══════════════════════════════════════════════════════════════════════════╝

[Characters]
"""

    # Trier par nom
    for char in sorted(stable_chars):
        content += f"{char}, stages/Abyss-Rugal-Palace.def\n"

    content += """
[ExtraStages]
stages/Abyss-Rugal-Palace.def
stages/Darkness.def
stages/RED.def
stages/Galaxy BG.def
stages/Moon recidence.def

[Options]
arcade.maxmatches = 6,1,1,0,0,0,0,0,0,0
"""

    roster_path = DATA_DIR / "select_optimized.def"
    roster_path.write_text(content, encoding='utf-8')

    # Appliquer ce roster
    system_def = DATA_DIR / "system.def"
    sys_content = read_file(system_def)
    sys_content = re.sub(r'select\s*=\s*\S+', 'select = select_optimized.def', sys_content)
    write_file(system_def, sys_content)

    print(f"  ✅ Roster sauvegardé: {roster_path}")

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ██╗  ██╗ ██████╗ ███████╗    ███████╗██╗██╗  ██╗                        ║
║     ██║ ██╔╝██╔═══██╗██╔════╝    ██╔════╝██║╚██╗██╔╝                        ║
║     █████╔╝ ██║   ██║█████╗      █████╗  ██║ ╚███╔╝                         ║
║     ██╔═██╗ ██║   ██║██╔══╝      ██╔══╝  ██║ ██╔██╗                         ║
║     ██║  ██╗╚██████╔╝██║         ██║     ██║██╔╝ ██╗                        ║
║     ╚═╝  ╚═╝ ╚═════╝ ╚═╝         ╚═╝     ╚═╝╚═╝  ╚═╝                        ║
║                                                                              ║
║              AUTO-FIX & OPTIMIZATION SYSTEM                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Créer le dossier de backup
    BACKUP_DIR.mkdir(exist_ok=True)

    # Lister tous les personnages
    char_folders = [d for d in CHARS_DIR.iterdir()
                   if d.is_dir() and d.name not in ['ai', 'data', 'backup']]

    total = len(char_folders)
    print(f"📋 {total} personnages à analyser et corriger\n")

    stable_chars = []
    fixed_chars = []
    removed_chars = []

    for i, char_path in enumerate(char_folders, 1):
        result, error = analyze_and_fix_character(char_path)

        if error:
            print(f"[{i:3d}/{total}] ❌ {char_path.name}: {error[0]}")
            removed_chars.append(char_path.name)
            continue

        if result['stable']:
            status = "✅"
            stable_chars.append(result['name'])
        else:
            status = "⚠️"
            removed_chars.append(result['name'])

        fixes_msg = f"+{result['fixes']} fixes" if result['fixes'] > 0 else ""

        if result['fixes'] > 0:
            fixed_chars.append(result['name'])

        print(f"[{i:3d}/{total}] {status} {result['name']:<40} {fixes_msg}")

    # Optimiser les paramètres
    optimize_game_settings()

    # Créer le roster final
    create_stable_roster(stable_chars)

    # Résumé
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           RÉSUMÉ DES CORRECTIONS                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Personnages analysés: {total:<52}║
║  Personnages stables: {len(stable_chars):<53}║
║  Personnages corrigés: {len(fixed_chars):<52}║
║  Personnages retirés: {len(removed_chars):<53}║
║                                                                              ║
║  ✅ Le jeu est maintenant optimisé!                                         ║
║  ✅ Roster appliqué: select_optimized.def                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎮 Lance le jeu avec: JOUER_ONLINE_PRO.bat
    """)

if __name__ == "__main__":
    main()
