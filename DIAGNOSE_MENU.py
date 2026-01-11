#!/usr/bin/env python3
"""Diagnostic: Vérifie si le menu principal s'affiche"""
import subprocess
import time
import os
import sys

try:
    import psutil
except ImportError:
    print("Installation de psutil...")
    subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], capture_output=True)
    import psutil

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    print("[INFO] pyautogui non installé - pas de capture d'écran")

BASE_DIR = r"D:\KOF Ultimate Online"
GAME_EXE = os.path.join(BASE_DIR, "Ikemen_GO.exe")

def kill_game():
    """Tue toutes les instances d'Ikemen"""
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            if 'ikemen' in proc.info['name'].lower():
                print(f"  Killing PID {proc.info['pid']}")
                proc.kill()
        except:
            pass

def get_window_info():
    """Récupère les infos de la fenêtre du jeu"""
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            if 'ikemen' in proc.info['name'].lower():
                return {
                    'running': True,
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'memory_mb': proc.memory_info().rss / 1024 / 1024
                }
        except:
            pass
    return {'running': False}

def main():
    print("=" * 60)
    print("  DIAGNOSTIC DU MENU PRINCIPAL")
    print("=" * 60)

    # Kill existing instances
    print("\n[1] Fermeture des instances existantes...")
    kill_game()
    time.sleep(2)

    # Check config
    print("\n[2] Vérification de la configuration...")
    system_def = os.path.join(BASE_DIR, "data", "system.def")
    if os.path.exists(system_def):
        with open(system_def, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if "[Demo Mode]" in content:
                demo_section = content.split("[Demo Mode]")[1].split("[")[0]
                if "enabled = 0" in demo_section:
                    print("  ✓ Demo Mode: DÉSACTIVÉ")
                else:
                    print("  ✗ Demo Mode: ACTIVÉ (problème!)")

            if "menu.item.font" in content:
                print("  ✓ Menu font configuré")

    # Launch game
    print("\n[3] Lancement du jeu...")
    proc = subprocess.Popen([GAME_EXE], cwd=BASE_DIR)
    print(f"  PID: {proc.pid}")

    # Monitor for 15 seconds
    print("\n[4] Surveillance pendant 15 secondes...")
    for i in range(15):
        time.sleep(1)
        info = get_window_info()
        if info['running']:
            print(f"  [{i+1:2}s] Jeu actif - Mémoire: {info['memory_mb']:.1f} MB")
        else:
            print(f"  [{i+1:2}s] CRASH DÉTECTÉ!")
            return

    # Final check
    print("\n[5] Résultat final:")
    info = get_window_info()
    if info['running']:
        print("  ✓ Le jeu tourne sans crash")
        print(f"  ✓ PID: {info['pid']}, Mémoire: {info['memory_mb']:.1f} MB")
        print("\n  VÉRIFICATION MANUELLE REQUISE:")
        print("  → Regarde l'écran du jeu")
        print("  → Est-ce le MENU PRINCIPAL ou la SÉLECTION DE PERSO?")
    else:
        print("  ✗ Le jeu a crashé")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
