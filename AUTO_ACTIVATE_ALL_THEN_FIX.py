#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ACTIVATION AUTOMATIQUE + AUTO-CORRECTION
1. Active TOUS les 190 personnages
2. Lance tests automatiques
3. Détecte et supprime automatiquement les cassés
4. Recommence jusqu'à 18+/20
"""

import subprocess
import time
import json
import shutil
from pathlib import Path
from datetime import datetime

def activate_all_characters():
    """Active tous les personnages trouvés dans chars/"""
    game_dir = Path(__file__).parent
    chars_dir = game_dir / "chars"
    select_def = game_dir / "data" / "select.def"

    if not chars_dir.exists():
        print("❌ Dossier chars/ manquant")
        return False

    # Backup select.def
    backup = select_def.with_suffix('.def.backup')
    shutil.copy2(select_def, backup)
    print(f"💾 Backup: {backup.name}")

    # Lire tous les personnages
    char_folders = sorted([d.name for d in chars_dir.iterdir() if d.is_dir()])
    print(f"\n📁 Trouvé {len(char_folders)} personnages dans chars/")

    # Lire stages disponibles
    stages_dir = game_dir / "stages"
    stage_files = []
    if stages_dir.exists():
        stage_files = [f.name for f in stages_dir.glob("*.def")]

    if not stage_files:
        print("⚠️  Aucun stage trouvé, utilisation sans stage")
        default_stage = ""
    else:
        default_stage = f", stages/{stage_files[0]}"
        print(f"🗺️  Stage par défaut: {stage_files[0]}")

    # Générer nouveau select.def avec TOUS les personnages
    print("\n📝 Génération nouveau select.def avec TOUS les personnages...")

    new_content = """; IKEMEN GO Select.def
; ROSTER COMPLET - TOUS LES PERSONNAGES ACTIVÉS
; Généré automatiquement pour tests - {datetime.now()}

[Characters]
"""

    for char_name in char_folders:
        new_content += f"{char_name}{default_stage}\n"

    # Ajouter sections stages
    new_content += "\n[ExtraStages]\n"
    for stage in stage_files[:20]:  # 20 premiers stages
        new_content += f"stages/{stage}\n"

    new_content += "\n[Stages]\n"
    for stage in stage_files:
        new_content += f"stages/{stage}\n"

    new_content += """
[Options]
arcade.rematches = 0
team.loseondraw = 1
"""

    # Écrire
    select_def.write_text(new_content, encoding='utf-8')

    print(f"✅ {len(char_folders)} personnages activés!")
    print(f"✅ {len(stage_files)} stages ajoutés")

    return True

def run_auto_tests_and_fix():
    """Lance tests et corrections automatiques"""
    game_dir = Path(__file__).parent

    print("\n" + "="*70)
    print("🔍 LANCEMENT TESTS AUTOMATIQUES")
    print("="*70)

    # Lance les testeurs IA
    tester_script = game_dir / "AI_TESTERS_ADVANCED.py"

    if not tester_script.exists():
        print("❌ AI_TESTERS_ADVANCED.py manquant")
        return False

    print("\n🤖 Testeurs IA: 50 tests rapides pour détecter tous les bugs...")
    print("   (Cela va prendre 5-10 minutes)")

    try:
        process = subprocess.Popen(
            ['python', str(tester_script)],
            cwd=str(game_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Attendre maximum 10 minutes
        timeout = 600
        start_time = time.time()

        while process.poll() is None and (time.time() - start_time) < timeout:
            time.sleep(5)

            # Vérifier progression
            bug_db_file = game_dir / "BUG_DATABASE.json"
            if bug_db_file.exists():
                try:
                    bug_db = json.loads(bug_db_file.read_text(encoding='utf-8'))
                    total_tests = bug_db.get('total_tests', 0)
                    if total_tests > 0:
                        print(f"   📊 Tests effectués: {total_tests}")

                    # Si assez de tests, arrêter
                    if total_tests >= 50:
                        print(f"   ✅ 50 tests atteints!")
                        process.terminate()
                        break
                except:
                    pass

        # Forcer arrêt si nécessaire
        if process.poll() is None:
            process.terminate()
            time.sleep(2)
            if process.poll() is None:
                process.kill()

        # Vérifier résultats
        bug_db_file = game_dir / "BUG_DATABASE.json"
        if not bug_db_file.exists():
            print("⚠️  Aucune base de bugs générée")
            return False

        bug_db = json.loads(bug_db_file.read_text(encoding='utf-8'))

        broken_chars = bug_db.get('broken_characters', [])
        broken_stages = bug_db.get('broken_stages', [])

        print(f"\n🐛 BUGS DÉTECTÉS:")
        print(f"   ❌ Personnages cassés: {len(broken_chars)}")
        print(f"   🗺️  Stages cassés: {len(broken_stages)}")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def auto_clean():
    """Nettoie automatiquement sans confirmation"""
    game_dir = Path(__file__).parent
    cleaner_script = game_dir / "AUTO_CLEAN_BROKEN_CONTENT.py"

    print("\n" + "="*70)
    print("🧹 NETTOYAGE AUTOMATIQUE")
    print("="*70)

    bug_db_file = game_dir / "BUG_DATABASE.json"
    if not bug_db_file.exists():
        print("⚠️  Pas de bugs à nettoyer")
        return True

    bug_db = json.loads(bug_db_file.read_text(encoding='utf-8'))

    broken_chars = bug_db.get('broken_characters', [])
    broken_stages = bug_db.get('broken_stages', [])

    if not broken_chars and not broken_stages:
        print("✅ Aucun contenu cassé à nettoyer")
        return True

    print(f"\n🗑️  Suppression automatique:")
    print(f"   - {len(broken_chars)} personnages cassés")
    print(f"   - {len(broken_stages)} stages cassés")

    # Backup automatique
    backup_dir = game_dir / f"AUTO_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(exist_ok=True)

    # Supprimer personnages cassés
    for char_info in broken_chars:
        char_name = char_info['name']
        char_dir = game_dir / "chars" / char_name

        if char_dir.exists():
            try:
                # Backup
                backup_char = backup_dir / "chars" / char_name
                backup_char.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(char_dir, backup_char)

                # Supprimer
                shutil.rmtree(char_dir)
                print(f"   ✅ Retiré: {char_name}")
            except Exception as e:
                print(f"   ❌ Erreur {char_name}: {e}")

    # Supprimer stages cassés
    for stage_info in broken_stages:
        stage_name = stage_info['name']
        stage_file = game_dir / "stages" / f"{stage_name}.def"

        if stage_file.exists():
            try:
                # Backup
                backup_stage = backup_dir / "stages" / stage_file.name
                backup_stage.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(stage_file, backup_stage)

                # Supprimer
                stage_file.unlink()
                print(f"   ✅ Retiré: {stage_name}")
            except Exception as e:
                print(f"   ❌ Erreur {stage_name}: {e}")

    # Régénérer select.def sans les cassés
    print("\n📝 Mise à jour select.def...")
    activate_all_characters()  # Régénère sans les cassés

    print(f"\n💾 Backup créé: {backup_dir.name}")
    print("✅ Nettoyage terminé!")

    return True

def main():
    """Processus complet automatique"""
    print("="*70)
    print("🚀 ACTIVATION + TESTS + AUTO-CORRECTION")
    print("="*70)

    cycle = 1
    max_cycles = 5

    while cycle <= max_cycles:
        print(f"\n{'='*70}")
        print(f"🔄 CYCLE #{cycle}")
        print(f"{'='*70}")

        # Étape 1: Activer tous les personnages
        print(f"\n1️⃣ Activation de tous les personnages...")
        if not activate_all_characters():
            print("❌ Échec activation")
            break

        # Étape 2: Tests automatiques
        print(f"\n2️⃣ Tests automatiques...")
        if not run_auto_tests_and_fix():
            print("⚠️  Tests incomplets, retry au prochain cycle")

        # Étape 3: Nettoyage automatique
        print(f"\n3️⃣ Nettoyage automatique...")
        auto_clean()

        # Calculer score
        bug_db_file = Path(__file__).parent / "BUG_DATABASE.json"
        if bug_db_file.exists():
            bug_db = json.loads(bug_db_file.read_text(encoding='utf-8'))
            total_bugs = (
                len(bug_db.get('broken_characters', [])) +
                len(bug_db.get('broken_stages', [])) +
                len(bug_db.get('startup_crashes', []))
            )

            score = max(0, 20 - (total_bugs * 0.5))
            print(f"\n📊 Score estimé: {score:.1f}/20")

            if score >= 18:
                print("\n🏆 OBJECTIF ATTEINT!")
                break

        cycle += 1

        if cycle <= max_cycles:
            print(f"\n⏸️  Pause 30 secondes avant cycle #{cycle}...")
            time.sleep(30)

    print("\n" + "="*70)
    print("✅ PROCESSUS AUTOMATIQUE TERMINÉ")
    print("="*70)

if __name__ == "__main__":
    main()
