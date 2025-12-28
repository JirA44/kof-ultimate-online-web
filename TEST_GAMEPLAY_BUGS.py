#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST DE BUGS GAMEPLAY - KOF Ultimate Online
Détecte les personnages avec des bugs de state/physics
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Set

GAME_DIR = Path(__file__).parent
CHARS_DIR = GAME_DIR / "chars"
DATA_DIR = GAME_DIR / "data"

# Patterns de bugs connus
BUG_PATTERNS = {
    # State loops infinis
    'infinite_loop': [
        r'changestate\s*=\s*(\d+).*\n.*\n.*changestate\s*=\s*\1',  # même state
        r'velset\s*=\s*0\s*,\s*-9999',  # vélocité Y extrême
        r'velset\s*=\s*0\s*,\s*9999',
        r'posadd\s*=\s*0\s*,\s*-9999',  # position Y extrême
    ],
    # Physics cassée
    'broken_physics': [
        r'physics\s*=\s*N',  # No physics peut causer des problèmes
        r'velset\s*=\s*[^,]+,\s*-[5-9]\d{2,}',  # vélocité Y très négative
    ],
    # States dangereux
    'dangerous_states': [
        r'\[State\s+-2',  # State -2 mal configuré
        r'triggerall\s*=\s*1\s*\n\s*changestate',  # toujours changestate
    ],
    # Helpers infinis
    'infinite_helpers': [
        r'helper.*\n.*helpertype\s*=\s*normal.*\n.*(?!destroytime)',
    ]
}

# States qui peuvent causer "fly away"
FLYAWAY_STATES = [
    'air', 'airjuggle', 'hitfall', 'liedown', 'getup'
]

@dataclass
class CharBugReport:
    name: str
    folder: str
    bugs_found: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    safe: bool = True
    flyaway_risk: bool = False

def read_file_safe(path: Path) -> str:
    """Lit un fichier avec gestion des encodages"""
    for encoding in ['utf-8', 'latin-1', 'cp1252', 'shift-jis']:
        try:
            return path.read_text(encoding=encoding, errors='ignore')
        except:
            continue
    return ""

def analyze_cns_file(cns_path: Path) -> List[str]:
    """Analyse un fichier CNS pour les bugs"""
    bugs = []
    content = read_file_safe(cns_path)
    content_lower = content.lower()

    # Vérifier les patterns de bugs
    for bug_type, patterns in BUG_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content_lower, re.IGNORECASE | re.MULTILINE):
                bugs.append(f"{bug_type}: pattern détecté dans {cns_path.name}")

    # Vérifier les vélocités extrêmes
    vel_matches = re.findall(r'vel\s*[xy]\s*=\s*(-?\d+)', content_lower)
    for vel in vel_matches:
        try:
            if abs(int(vel)) > 50:
                bugs.append(f"Vélocité extrême: {vel} dans {cns_path.name}")
        except:
            pass

    # Vérifier les ChangeState sans condition
    changestate_count = len(re.findall(r'changestate\s*=', content_lower))
    trigger_count = len(re.findall(r'trigger', content_lower))
    if changestate_count > 0 and trigger_count < changestate_count:
        bugs.append(f"ChangeState sans trigger suffisant dans {cns_path.name}")

    return bugs

def analyze_character(char_path: Path) -> CharBugReport:
    """Analyse complète d'un personnage pour les bugs gameplay"""
    report = CharBugReport(
        name=char_path.name,
        folder=str(char_path)
    )

    # Trouver tous les fichiers CNS
    cns_files = list(char_path.glob("*.cns")) + list(char_path.glob("**/*.cns"))

    if not cns_files:
        report.warnings.append("Aucun fichier CNS trouvé")
        return report

    for cns_file in cns_files:
        bugs = analyze_cns_file(cns_file)
        report.bugs_found.extend(bugs)

    # Vérifier les states de vol
    for cns_file in cns_files:
        content = read_file_safe(cns_file).lower()
        for state in FLYAWAY_STATES:
            if f'statetype = {state[0]}' in content:
                # Vérifier si physics est bien configurée
                if 'physics = n' in content and state in ['air', 'airjuggle']:
                    report.flyaway_risk = True
                    report.warnings.append(f"Risque fly-away: {state} avec physics=N")

    # Déterminer si le personnage est safe
    report.safe = len(report.bugs_found) == 0 and not report.flyaway_risk

    return report

def get_def_info(char_path: Path) -> dict:
    """Récupère les infos du fichier DEF"""
    def_files = list(char_path.glob("*.def"))
    if not def_files:
        return {}

    content = read_file_safe(def_files[0])
    info = {}

    for line in content.split('\n'):
        if '=' in line and not line.strip().startswith(';'):
            parts = line.split('=', 1)
            key = parts[0].strip().lower()
            value = parts[1].split(';')[0].strip().strip('"')
            info[key] = value

    return info

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              TEST DE BUGS GAMEPLAY - KOF ULTIMATE ONLINE                     ║
║                    Détection des personnages bugués                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    char_folders = sorted([d for d in CHARS_DIR.iterdir()
                          if d.is_dir() and d.name not in ['ai', 'data', 'backup']])

    total = len(char_folders)
    safe_chars = []
    buggy_chars = []
    flyaway_chars = []

    print(f"Analyse de {total} personnages pour bugs gameplay...\n")

    for i, char_path in enumerate(char_folders, 1):
        report = analyze_character(char_path)

        if report.flyaway_risk:
            flyaway_chars.append(report)
            status = "🚀"
        elif not report.safe:
            buggy_chars.append(report)
            status = "❌"
        else:
            safe_chars.append(report)
            status = "✅"

        # Progress
        if i % 20 == 0 or i == total:
            print(f"[{i}/{total}] {status} {report.name}")

    # Résultats
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              RÉSULTATS                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ✅ Personnages safe: {len(safe_chars):<52}║
║  🚀 Risque fly-away: {len(flyaway_chars):<53}║
║  ❌ Bugs détectés: {len(buggy_chars):<55}║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Afficher les personnages à risque de fly-away
    if flyaway_chars:
        print("\n🚀 PERSONNAGES À RISQUE DE FLY-AWAY (à retirer du roster):")
        print("-" * 60)
        for report in flyaway_chars:
            print(f"  - {report.name}")
            for warning in report.warnings[:2]:
                print(f"      {warning}")

    # Afficher les personnages bugués
    if buggy_chars:
        print("\n❌ PERSONNAGES AVEC BUGS:")
        print("-" * 60)
        for report in buggy_chars[:10]:
            print(f"  - {report.name}")
            for bug in report.bugs_found[:2]:
                print(f"      {bug}")

    # Créer un roster sans les personnages bugués
    print("\n📝 Création du roster ULTRA-SAFE...")

    safe_names = [r.name for r in safe_chars]

    # Lire le roster certifié actuel
    certified_path = DATA_DIR / "select_certified.def"
    if certified_path.exists():
        content = certified_path.read_text(encoding='utf-8')

        # Filtrer les personnages bugués
        new_lines = []
        removed = 0
        flyaway_names = [r.name for r in flyaway_chars]
        buggy_names = [r.name for r in buggy_chars]

        for line in content.split('\n'):
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith(';'):
                # Vérifier si c'est un personnage
                char_name = line_stripped.split(',')[0].strip()
                if char_name in flyaway_names or char_name in buggy_names:
                    new_lines.append(f"; RETIRÉ (BUG): {line}")
                    removed += 1
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Sauvegarder le nouveau roster
        ultra_safe_path = DATA_DIR / "select_ultra_safe.def"
        ultra_safe_path.write_text('\n'.join(new_lines), encoding='utf-8')

        print(f"✅ Créé: select_ultra_safe.def ({removed} personnages retirés)")

    # Liste des personnages à retirer
    all_problematic = flyaway_chars + buggy_chars
    if all_problematic:
        print(f"\n⚠️ {len(all_problematic)} personnages problématiques identifiés")
        print("   Pour appliquer le roster ultra-safe, exécutez:")
        print("   python -c \"import os; os.system('sed -i s/select_certified/select_ultra_safe/ data/system.def')\"")

if __name__ == "__main__":
    main()
