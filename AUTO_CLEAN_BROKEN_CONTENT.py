#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 NETTOYEUR AUTOMATIQUE DE CONTENU CASSÉ
Retire automatiquement:
- Personnages qui crashent
- Stages problématiques
- Fichiers corrompus
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

class BrokenContentCleaner:
    """Nettoie le contenu cassé détecté par les testeurs IA"""

    def __init__(self, game_dir):
        self.game_dir = Path(game_dir)
        self.bug_db_file = self.game_dir / "BUG_DATABASE.json"
        self.backup_dir = self.game_dir / f"BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.backup_dir.mkdir(exist_ok=True)

        self.load_bug_database()

    def load_bug_database(self):
        """Charge la base de bugs"""
        if self.bug_db_file.exists():
            self.bug_db = json.loads(self.bug_db_file.read_text(encoding='utf-8'))
        else:
            print("❌ Aucune base de bugs trouvée. Lancez d'abord AI_TESTERS_ADVANCED.py")
            self.bug_db = None

    def backup_file(self, file_path):
        """Sauvegarde un fichier avant suppression"""
        file_path = Path(file_path)
        if file_path.exists():
            relative = file_path.relative_to(self.game_dir)
            backup_path = self.backup_dir / relative
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            print(f"   💾 Backup: {relative}")

    def remove_broken_characters(self):
        """Retire les personnages cassés"""
        if not self.bug_db:
            return

        broken_chars = self.bug_db.get('broken_characters', [])

        if not broken_chars:
            print("✅ Aucun personnage cassé détecté")
            return

        print(f"\n🗑️  SUPPRESSION DE {len(broken_chars)} PERSONNAGES CASSÉS:")

        for char_info in broken_chars:
            char_name = char_info['name']
            reason = char_info['reason']

            print(f"\n❌ {char_name} ({reason})")

            # Supprimer du dossier chars/
            char_dir = self.game_dir / "chars" / char_name
            if char_dir.exists():
                self.backup_file(char_dir)
                shutil.rmtree(char_dir)
                print(f"   🗑️  Supprimé: chars/{char_name}/")

        # Mettre à jour select.def
        self.update_select_def_characters(broken_chars)

    def remove_broken_stages(self):
        """Retire les stages cassés"""
        if not self.bug_db:
            return

        broken_stages = self.bug_db.get('broken_stages', [])

        if not broken_stages:
            print("✅ Aucun stage cassé détecté")
            return

        print(f"\n🗑️  SUPPRESSION DE {len(broken_stages)} STAGES CASSÉS:")

        for stage_info in broken_stages:
            stage_name = stage_info['name']
            reason = stage_info['reason']

            print(f"\n❌ {stage_name} ({reason})")

            # Supprimer le fichier .def
            stage_file = self.game_dir / "stages" / f"{stage_name}.def"
            if stage_file.exists():
                self.backup_file(stage_file)
                stage_file.unlink()
                print(f"   🗑️  Supprimé: {stage_file.name}")

            # Supprimer les assets associés (sff, snd, etc.)
            stages_dir = self.game_dir / "stages"
            for ext in ['.sff', '.snd', '.mp3', '.ogg', '.png', '.jpg']:
                asset = stages_dir / f"{stage_name}{ext}"
                if asset.exists():
                    self.backup_file(asset)
                    asset.unlink()
                    print(f"   🗑️  Supprimé: {asset.name}")

        # Mettre à jour select.def
        self.update_select_def_stages(broken_stages)

    def update_select_def_characters(self, broken_chars):
        """Met à jour select.def en retirant les personnages cassés"""
        select_def = self.game_dir / "data" / "select.def"

        if not select_def.exists():
            return

        # Backup
        self.backup_file(select_def)

        content = select_def.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')

        broken_names = [c['name'] for c in broken_chars]

        new_lines = []
        removed_count = 0

        for line in lines:
            # Si la ligne contient un personnage cassé, la commenter
            should_keep = True
            for broken_name in broken_names:
                if line.strip().startswith(broken_name):
                    # Commenter la ligne
                    new_lines.append(f"; [CASSÉ] {line}")
                    removed_count += 1
                    should_keep = False
                    break

            if should_keep:
                new_lines.append(line)

        # Sauvegarder
        select_def.write_text('\n'.join(new_lines), encoding='utf-8')
        print(f"\n✅ select.def mis à jour: {removed_count} lignes commentées")

    def update_select_def_stages(self, broken_stages):
        """Met à jour select.def en retirant les stages cassés"""
        select_def = self.game_dir / "data" / "select.def"

        if not select_def.exists():
            return

        content = select_def.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')

        broken_names = [s['name'] for s in broken_stages]

        new_lines = []
        removed_count = 0

        for line in lines:
            # Si la ligne contient un stage cassé, la commenter
            should_keep = True
            for broken_name in broken_names:
                if broken_name in line and '.def' in line:
                    # Commenter la ligne
                    new_lines.append(f"; [CASSÉ] {line}")
                    removed_count += 1
                    should_keep = False
                    break

            if should_keep:
                new_lines.append(line)

        # Sauvegarder
        select_def.write_text('\n'.join(new_lines), encoding='utf-8')
        print(f"\n✅ select.def stages mis à jour: {removed_count} lignes commentées")

    def generate_report(self):
        """Génère un rapport de nettoyage"""
        if not self.bug_db:
            return

        report = f"""# 🧹 RAPPORT DE NETTOYAGE AUTOMATIQUE

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Backup**: {self.backup_dir.name}

## Éléments Supprimés

### Personnages Cassés: {len(self.bug_db.get('broken_characters', []))}
"""

        for char in self.bug_db.get('broken_characters', []):
            report += f"- **{char['name']}**: {char['reason']}\n"

        report += f"\n### Stages Cassés: {len(self.bug_db.get('broken_stages', []))}\n"

        for stage in self.bug_db.get('broken_stages', []):
            report += f"- **{stage['name']}**: {stage['reason']}\n"

        report += f"""

## Fichiers Sauvegardés

Tous les fichiers supprimés ont été sauvegardés dans:
```
{self.backup_dir}
```

## Restauration

Pour restaurer un fichier supprimé:
```bash
# Copier depuis le backup
copy "{self.backup_dir}\\chars\\[personnage]" "chars\\"
```

## Prochaines Étapes

1. ✅ Relancer le jeu pour vérifier stabilité
2. ✅ Relancer les testeurs IA pour nouveaux tests
3. ✅ Vérifier que le score qualité s'améliore

---

*Rapport généré par Auto Clean Broken Content*
"""

        report_path = self.game_dir / f"CLEANUP_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path.write_text(report, encoding='utf-8')
        print(f"\n📄 Rapport de nettoyage: {report_path}")

    def clean_all(self):
        """Nettoie tout le contenu cassé"""
        print("=" * 70)
        print("🧹 NETTOYAGE AUTOMATIQUE DU CONTENU CASSÉ")
        print("=" * 70)

        if not self.bug_db:
            print("\n❌ Impossible de continuer sans base de bugs")
            return

        print(f"\n📊 Bugs détectés:")
        print(f"   - Personnages cassés: {len(self.bug_db.get('broken_characters', []))}")
        print(f"   - Stages cassés: {len(self.bug_db.get('broken_stages', []))}")

        # Demander confirmation
        print(f"\n⚠️  Un backup sera créé dans: {self.backup_dir}")
        response = input("\n🤔 Confirmer le nettoyage? (oui/non): ")

        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            print("❌ Nettoyage annulé")
            return

        # Nettoyer
        self.remove_broken_characters()
        self.remove_broken_stages()
        self.generate_report()

        print("\n" + "=" * 70)
        print("✅ NETTOYAGE TERMINÉ!")
        print("=" * 70)
        print(f"\n💾 Backup créé: {self.backup_dir}")
        print("\n🎮 Vous pouvez maintenant relancer le jeu")
        print("🤖 Relancez AI_TESTERS_ADVANCED.py pour valider les corrections")


def main():
    game_dir = Path(__file__).parent
    cleaner = BrokenContentCleaner(game_dir)
    cleaner.clean_all()


if __name__ == "__main__":
    main()
