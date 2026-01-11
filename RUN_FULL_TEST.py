#!/usr/bin/env python3
"""Lance le test complet directement"""
import subprocess
import time
import os
import json
import psutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"D:\KOF Ultimate Online")
GAME_EXE = BASE_DIR / "Ikemen_GO.exe"
DATA_DIR = BASE_DIR / "data"
CHARS_DIR = BASE_DIR / "chars"

TOTAL_TIMEOUT = 15  # secondes par test

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def kill_game():
    for proc in psutil.process_iter(['name']):
        try:
            if 'ikemen' in proc.info['name'].lower():
                proc.kill()
        except:
            pass

def test_char(char_name):
    # Creer select.def
    content = f"""[Characters]
{char_name}, stages/Abyss-Rugal-Palace.def
kfm, stages/Abyss-Rugal-Palace.def
[ExtraStages]
stages/Abyss-Rugal-Palace.def
[Options]
arcade.maxmatches = 1,0,0,0,0,0,0,0,0,0
"""
    with open(DATA_DIR / "select.def", 'w') as f:
        f.write(content)

    kill_game()
    time.sleep(1)

    try:
        proc = subprocess.Popen([str(GAME_EXE)], cwd=str(BASE_DIR),
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        start = time.time()

        while time.time() - start < TOTAL_TIMEOUT:
            if proc.poll() is not None:
                return False  # Crash
            time.sleep(0.5)

        kill_game()
        return True  # OK
    except Exception as e:
        log(f"  Error: {e}")
        return False

def main():
    chars = sorted([d.name for d in CHARS_DIR.iterdir() if d.is_dir()])
    total = len(chars)

    log(f"Testing {total} characters...")
    log(f"Estimated time: {total * (TOTAL_TIMEOUT + 3) // 60} minutes")

    passed = []
    crashed = []

    for i, char in enumerate(chars, 1):
        log(f"[{i:3}/{total}] {char[:40]:<40} ", )

        ok = test_char(char)
        if ok:
            passed.append(char)
            print("OK")
        else:
            crashed.append(char)
            print("CRASH")

        time.sleep(2)

    # Save results
    results = {'passed': passed, 'crashed': crashed, 'date': datetime.now().isoformat()}
    with open(BASE_DIR / "full_test_results.json", 'w') as f:
        json.dump(results, f, indent=2)

    # Generate stable select.def
    output = f"""; AUTO-TESTED ROSTER - {len(passed)} stable chars
; Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}

[Characters]
"""
    for c in sorted(passed):
        output += f"{c}, stages/Abyss-Rugal-Palace.def\n"

    output += "\n; === CRASHES ===\n"
    for c in sorted(crashed):
        output += f"; {c}\n"

    output += "\n[ExtraStages]\nstages/Abyss-Rugal-Palace.def\n"

    with open(DATA_DIR / "select.def", 'w') as f:
        f.write(output)

    log("=" * 50)
    log(f"DONE! {len(passed)} stable, {len(crashed)} crashed")
    log("=" * 50)

if __name__ == "__main__":
    main()
