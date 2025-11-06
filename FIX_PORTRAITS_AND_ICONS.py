"""
🎨 RÉPARATEUR PORTRAITS & ICÔNES
Corrige tous les problèmes d'affichage des personnages
"""
from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFont
import json

class PortraitFixer:
    def __init__(self):
        self.game_dir = Path(__file__).parent
        self.chars_dir = self.game_dir / "chars"
        self.fixes_log = []

    def scan_all_characters(self):
        """Scanne tous les personnages et détecte les problèmes"""
        print("🔍 Scan de tous les personnages...")

        if not self.chars_dir.exists():
            print("❌ Dossier chars/ introuvable!")
            return []

        char_folders = [d for d in self.chars_dir.iterdir() if d.is_dir()]
        print(f"📁 {len(char_folders)} personnages trouvés")

        problems = []

        for char_folder in char_folders:
            char_name = char_folder.name
            issues = []

            # Vérifie .def
            def_files = list(char_folder.glob("*.def"))
            if not def_files:
                issues.append("NO_DEF")

            # Vérifie portrait
            portrait_files = list(char_folder.glob("portrait.*"))
            if not portrait_files:
                issues.append("NO_PORTRAIT")

            # Vérifie sprites
            sff_files = list(char_folder.glob("*.sff"))
            if not sff_files:
                issues.append("NO_SPRITES")

            if issues:
                problems.append({
                    "char": char_name,
                    "folder": char_folder,
                    "issues": issues
                })

        return problems

    def create_placeholder_portrait(self, char_name, output_path):
        """Crée un portrait placeholder de 140x170 pixels"""
        # Crée une image placeholder
        img = Image.new('RGB', (140, 170), color=(50, 50, 80))
        draw = ImageDraw.Draw(img)

        # Dessine un cadre
        draw.rectangle([5, 5, 135, 165], outline=(100, 100, 150), width=3)

        # Ajoute le nom du personnage
        # Utilise une police par défaut
        try:
            # Essaye de trouver une police système
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()

        # Nom centré
        text = char_name[:15]  # Limite à 15 caractères
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (140 - text_width) // 2
        y = (170 - text_height) // 2

        draw.text((x, y), text, fill=(200, 200, 220), font=font)

        # Sauvegarde
        img.save(output_path)
        print(f"✅ Portrait créé: {output_path.name}")

    def create_placeholder_icon(self, char_name, output_path):
        """Crée une icône placeholder de 30x30 pixels"""
        img = Image.new('RGB', (30, 30), color=(60, 60, 90))
        draw = ImageDraw.Draw(img)

        # Cadre
        draw.rectangle([2, 2, 28, 28], outline=(120, 120, 180), width=2)

        # Initiales
        initials = ''.join([c[0] for c in char_name.split('-')])[:2]

        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (30 - text_width) // 2
        y = (30 - text_height) // 2

        draw.text((x, y), initials, fill=(220, 220, 240), font=font)

        img.save(output_path)
        print(f"✅ Icône créée: {output_path.name}")

    def fix_character(self, char_info):
        """Répare un personnage avec des problèmes"""
        char_name = char_info["char"]
        char_folder = char_info["folder"]
        issues = char_info["issues"]

        print(f"\n🔧 Réparation: {char_name}")
        print(f"   Problèmes: {', '.join(issues)}")

        fixes_applied = []

        # Crée portrait manquant
        if "NO_PORTRAIT" in issues:
            portrait_path = char_folder / "portrait.png"
            self.create_placeholder_portrait(char_name, portrait_path)
            fixes_applied.append("PORTRAIT_CREATED")

        # Crée icône manquante
        if "NO_PORTRAIT" in issues:  # L'icône est souvent dans le portrait
            icon_path = char_folder / "icon.png"
            self.create_placeholder_icon(char_name, icon_path)
            fixes_applied.append("ICON_CREATED")

        # Crée .def minimal si manquant
        if "NO_DEF" in issues:
            def_path = char_folder / f"{char_name}.def"
            def_content = f"""; Character Definition for {char_name}
[Info]
name = "{char_name}"
displayname = "{char_name}"
versiondate = 01,01,2025
mugenversion = 1.0
author = "Auto-Generated"

[Files]
cmd     = {char_name}.cmd
cns     = {char_name}.cns
st      = {char_name}.st
stcommon = common1.cns
sprite  = {char_name}.sff
anim    = {char_name}.air
sound   = {char_name}.snd
pal1 = {char_name}.act

[Arcade]

[Palette Keymap]
"""
            def_path.write_text(def_content, encoding='utf-8')
            fixes_applied.append("DEF_CREATED")
            print(f"   ✅ Fichier .def créé")

        self.fixes_log.append({
            "char": char_name,
            "issues": issues,
            "fixes": fixes_applied
        })

        return len(fixes_applied) > 0

    def fix_select_def_alignment(self):
        """Corrige l'alignement dans select.def pour que les icônes correspondent"""
        print("\n📋 Correction alignement select.def...")

        select_def = self.game_dir / "data" / "select.def"

        if not select_def.exists():
            print("❌ select.def introuvable")
            return

        # Backup
        backup = select_def.with_suffix('.def.backup')
        shutil.copy(select_def, backup)

        content = select_def.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')

        fixed_lines = []
        in_characters = False

        for line in lines:
            if '[Characters]' in line:
                in_characters = True
                fixed_lines.append(line)
                continue

            if line.startswith('[') and in_characters:
                in_characters = False

            if in_characters and line.strip() and not line.strip().startswith(';'):
                # Ligne de personnage
                parts = line.split(',')
                if len(parts) >= 1:
                    char_name = parts[0].strip()
                    char_folder = self.chars_dir / char_name

                    # Vérifie que le dossier existe
                    if not char_folder.exists():
                        # Commente la ligne
                        fixed_lines.append(f"; {line}  ; DOSSIER MANQUANT")
                        print(f"   ⚠️  Commenté: {char_name} (dossier manquant)")
                        continue

            fixed_lines.append(line)

        # Sauvegarde
        select_def.write_text('\n'.join(fixed_lines), encoding='utf-8')
        print("   ✅ select.def corrigé")

    def generate_report(self):
        """Génère un rapport des corrections"""
        report_path = self.game_dir / "PORTRAIT_FIXES_REPORT.md"

        md = f"""# 🎨 RAPPORT CORRECTIONS PORTRAITS & ICÔNES

**Date**: {Path(__file__).stat().st_mtime}
**Corrections appliquées**: {len(self.fixes_log)}

## 📊 Résumé

"""

        for fix in self.fixes_log:
            md += f"""### {fix['char']}
- **Problèmes**: {', '.join(fix['issues'])}
- **Corrections**: {', '.join(fix['fixes'])}

"""

        md += """
## ✅ Prochaines étapes

1. Remplacer les portraits placeholder par de vrais portraits
2. Vérifier l'affichage dans le jeu
3. Ajuster les tailles si nécessaire (140x170 pour portraits)
"""

        report_path.write_text(md, encoding='utf-8')
        print(f"\n📄 Rapport généré: {report_path}")

    def fix_all(self):
        """Répare tous les portraits et icônes"""
        print("\n🎨 RÉPARATION PORTRAITS & ICÔNES")
        print("=" * 60)

        # Scan
        problems = self.scan_all_characters()

        if not problems:
            print("✅ Aucun problème détecté!")
            return

        print(f"\n⚠️  {len(problems)} personnages avec des problèmes")

        # Répare chaque personnage
        fixed_count = 0
        for char_info in problems:
            if self.fix_character(char_info):
                fixed_count += 1

        # Corrige select.def
        self.fix_select_def_alignment()

        # Rapport
        self.generate_report()

        print("\n" + "=" * 60)
        print(f"✅ {fixed_count} personnages réparés")
        print("=" * 60)

if __name__ == "__main__":
    fixer = PortraitFixer()
    fixer.fix_all()
