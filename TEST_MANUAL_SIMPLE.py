#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 TEST MANUEL SIMPLE - Vérifie si le jeu plante
Lance le jeu et vérifie immédiatement s'il crash
"""

import subprocess
import time
import sys
from pathlib import Path

def test_game_startup():
    """Teste si le jeu démarre sans crasher"""
    game_dir = Path(__file__).parent

    # Trouve l'exécutable
    possible_exes = [
        game_dir / "KOF_Ultimate_Online.exe",
        game_dir / "Ikemen_GO.exe",
        game_dir / "mugen.exe"
    ]

    game_exe = None
    for exe in possible_exes:
        if exe.exists():
            game_exe = exe
            break

    if not game_exe:
        print("❌ Aucun exécutable trouvé!")
        print("\nCherché dans:")
        for exe in possible_exes:
            print(f"  - {exe}")
        return False

    print("="*70)
    print("🎮 TEST SIMPLE DU JEU")
    print("="*70)
    print(f"\n📁 Exécutable: {game_exe.name}")
    print(f"📂 Dossier: {game_dir}")
    print("\n🚀 Lancement du jeu...")
    print("   (Attendez 10 secondes)")
    print("\n⏸️  Appuyez Ctrl+C pour arrêter\n")

    try:
        # Lance le jeu
        process = subprocess.Popen(
            [str(game_exe)],
            cwd=str(game_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        print("✅ Jeu lancé!")
        print("\n⏳ Test pendant 10 secondes...")

        # Attendre 10 secondes et vérifier
        for i in range(10):
            time.sleep(1)

            # Vérifier si le jeu a crashé
            if process.poll() is not None:
                stdout, stderr = process.communicate()

                print(f"\n❌ CRASH DÉTECTÉ après {i+1} secondes!")
                print(f"   Code de sortie: {process.returncode}")

                if stderr:
                    stderr_text = stderr.decode('utf-8', errors='ignore')
                    if stderr_text.strip():
                        print("\n📄 Erreur:")
                        print(stderr_text[:500])

                print("\n" + "="*70)
                print("🐛 LE JEU CRASH AU DÉMARRAGE")
                print("="*70)
                print("\n💡 Cause probable:")
                print("   - Personnage cassé dans select.def")
                print("   - Stage problématique")
                print("   - Fichier .def corrompu")

                return False

            # Afficher progression
            print(f"   {i+1}/10 secondes... ✓")

        # Jeu toujours actif après 10 secondes
        print("\n✅ JEU FONCTIONNE!")
        print("   Le jeu n'a pas crashé pendant 10 secondes")

        # Tuer le processus
        print("\n🛑 Fermeture du jeu...")
        process.terminate()
        time.sleep(2)

        if process.poll() is None:
            process.kill()

        print("="*70)
        print("✅ TEST RÉUSSI")
        print("="*70)
        return True

    except KeyboardInterrupt:
        print("\n\n⏸️  Test interrompu")
        try:
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                process.kill()
        except:
            pass
        return False

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = test_game_startup()
    sys.exit(0 if success else 1)
