#!/usr/bin/env python3
"""
Manage characters with missing sprites
Options: list, download placeholders, or remove from selection
"""
import os
import shutil
from pathlib import Path

GAME_PATH = Path(__file__).parent
CHARS_PATH = GAME_PATH / "chars"

def get_disabled_chars():
    """Get all characters marked as disabled (no sprites)"""
    disabled = []
    for d in CHARS_PATH.iterdir():
        if d.is_dir() and (d / "_DISABLED_NO_SPRITES").exists():
            disabled.append(d)
    return disabled

def get_char_info(char_path):
    """Get info about a character"""
    def_files = list(char_path.glob("*.def"))
    sff_files = list(char_path.glob("*.sff")) + list(char_path.rglob("*.sff"))
    air_files = list(char_path.glob("*.air")) + list(char_path.rglob("*.air"))

    return {
        "name": char_path.name,
        "has_def": len(def_files) > 0,
        "has_sff": len(sff_files) > 0,
        "has_air": len(air_files) > 0,
        "def_files": [f.name for f in def_files],
    }

def create_placeholder_info():
    """Create a placeholder info file for disabled chars"""
    disabled = get_disabled_chars()

    report = []
    report.append("=" * 60)
    report.append("PERSONNAGES SANS SPRITES - RAPPORT")
    report.append("=" * 60)
    report.append(f"\nTotal: {len(disabled)} personnages désactivés\n")

    for char in disabled:
        info = get_char_info(char)
        report.append(f"• {info['name']}")
        report.append(f"  DEF: {'✓' if info['has_def'] else '✗'}")
        report.append(f"  SFF: {'✓' if info['has_sff'] else '✗'}")
        report.append(f"  AIR: {'✓' if info['has_air'] else '✗'}")
        report.append("")

    report.append("\n" + "=" * 60)
    report.append("OPTIONS POUR CES PERSONNAGES:")
    report.append("=" * 60)
    report.append("1. Télécharger les sprites depuis des sites MUGEN")
    report.append("   - mugenarchive.com")
    report.append("   - mugenfreeforall.com")
    report.append("   - mugencharacters.org")
    report.append("")
    report.append("2. Supprimer définitivement ces personnages")
    report.append("3. Les garder désactivés pour référence future")

    return "\n".join(report)

def remove_disabled_chars():
    """Remove all disabled characters (move to backup folder)"""
    disabled = get_disabled_chars()
    backup_dir = GAME_PATH / "chars_backup_disabled"
    backup_dir.mkdir(exist_ok=True)

    moved = 0
    for char in disabled:
        try:
            dest = backup_dir / char.name
            shutil.move(str(char), str(dest))
            moved += 1
            print(f"  Déplacé: {char.name}")
        except Exception as e:
            print(f"  Erreur {char.name}: {e}")

    return moved

def main():
    print("\n" + "=" * 60)
    print("  GESTION DES PERSONNAGES SANS SPRITES")
    print("=" * 60 + "\n")

    disabled = get_disabled_chars()
    print(f"Personnages désactivés trouvés: {len(disabled)}\n")

    for char in disabled[:10]:
        print(f"  • {char.name}")
    if len(disabled) > 10:
        print(f"  ... et {len(disabled) - 10} autres")

    print("\n" + "-" * 60)
    print("Options:")
    print("  1. Générer un rapport détaillé")
    print("  2. Déplacer les persos désactivés vers backup")
    print("  3. Quitter")
    print("-" * 60)

    choice = input("\nChoix (1-3): ").strip()

    if choice == "1":
        report = create_placeholder_info()
        report_path = GAME_PATH / "RAPPORT_PERSOS_MANQUANTS.txt"
        report_path.write_text(report, encoding='utf-8')
        print(f"\n✅ Rapport généré: {report_path}")
        print("\n" + report)

    elif choice == "2":
        confirm = input("\n⚠️  Déplacer {len(disabled)} personnages vers backup? (oui/non): ")
        if confirm.lower() == "oui":
            moved = remove_disabled_chars()
            print(f"\n✅ {moved} personnages déplacés vers chars_backup_disabled/")
        else:
            print("Annulé.")

    else:
        print("Au revoir!")

if __name__ == "__main__":
    main()
