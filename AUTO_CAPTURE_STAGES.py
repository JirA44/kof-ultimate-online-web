#!/usr/bin/env python3
"""
KOF - Auto Capture Stages
Appuie sur F12 dans le jeu, le script capture et nomme automatiquement
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

try:
    import pyautogui
    import keyboard
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pyautogui", "keyboard", "-q"])
    import pyautogui
    import keyboard

BASE_DIR = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo kofuo")
STAGES_DIR = BASE_DIR / "stages"
OUTPUT_DIR = BASE_DIR / "stage_previews"

def get_stages():
    stages = []
    for f in sorted(STAGES_DIR.glob("*.def")):
        if 'backup' not in f.name.lower():
            stages.append(f.stem)
    return stages

def main():
    print("=" * 60)
    print("  KOF - AUTO CAPTURE STAGES")
    print("=" * 60)

    OUTPUT_DIR.mkdir(exist_ok=True)
    stages = get_stages()

    # Verifier quels stages ont deja un screenshot
    captured = []
    missing = []
    for s in stages:
        img = OUTPUT_DIR / f"{s}.png"
        if img.exists() and img.stat().st_size > 10000:
            captured.append(s)
        else:
            missing.append(s)

    print(f"\nStages: {len(stages)} total")
    print(f"  Deja captures: {len(captured)}")
    print(f"  Manquants: {len(missing)}")

    if not missing:
        print("\nTous les stages ont deja un screenshot!")
        print("Appuie ENTER pour regenerer la galerie...")
        input()
        generate_gallery(stages)
        return

    print("\n" + "-" * 60)
    print("STAGES A CAPTURER:")
    print("-" * 60)
    for i, s in enumerate(missing, 1):
        print(f"  {i:2}. {s}")

    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("=" * 60)
    print("""
1. Lance Ikemen_GO.exe
2. Va dans VS Mode > selectionne tes persos
3. A l'ecran de selection de stage:
   - Navigue jusqu'au stage voulu
   - Appuie F12 ici (pas dans le jeu!)
   - Le script prend le screenshot et passe au suivant

4. Quand tu as fini, appuie Q pour quitter et generer la galerie
""")

    print("Appuie ENTER quand tu es pret...")
    input()

    current_idx = 0
    screenshots_taken = 0

    print("\n" + "=" * 60)
    print(f"CAPTURE EN COURS - Stage: {missing[current_idx]}")
    print("F12 = Capture | N = Passer | Q = Quitter")
    print("=" * 60 + "\n")

    running = True

    def take_screenshot():
        nonlocal current_idx, screenshots_taken
        if current_idx >= len(missing):
            return

        stage_name = missing[current_idx]
        filename = f"{stage_name}.png"
        filepath = OUTPUT_DIR / filename

        time.sleep(0.2)  # Petit delai

        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(str(filepath))
            screenshots_taken += 1
            print(f"  ✓ [{screenshots_taken}] {stage_name}")

            current_idx += 1
            if current_idx < len(missing):
                print(f"\n  Prochain: {missing[current_idx]}")
                print("  (F12 = Capture, N = Passer)")
            else:
                print("\n  ✓ Tous les stages ont ete captures!")
                print("  Appuie Q pour generer la galerie")
        except Exception as e:
            print(f"  ✗ Erreur: {e}")

    def skip_stage():
        nonlocal current_idx
        if current_idx < len(missing):
            print(f"  → Passe: {missing[current_idx]}")
            current_idx += 1
            if current_idx < len(missing):
                print(f"  Prochain: {missing[current_idx]}")

    def quit_capture():
        nonlocal running
        running = False

    keyboard.on_press_key("F12", lambda e: take_screenshot())
    keyboard.on_press_key("n", lambda e: skip_stage())
    keyboard.on_press_key("q", lambda e: quit_capture())

    while running and current_idx < len(missing):
        time.sleep(0.1)

    keyboard.unhook_all()

    print(f"\n{'=' * 60}")
    print(f"  Termine! {screenshots_taken} screenshots pris")
    print(f"{'=' * 60}")

    generate_gallery(stages)

def generate_gallery(stages):
    print("\nGeneration de la galerie...")

    html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>KOF Stages</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial;background:#1a1a2e;color:#fff;padding:20px}
h1{text-align:center;color:#e94560;margin-bottom:20px}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:15px}
.c{background:#16213e;border:3px solid #333;border-radius:10px;overflow:hidden;cursor:pointer;position:relative}
.c:hover{border-color:#e94560}
.c.r{border-color:#ef4444}
.c.r img{opacity:0.3}
.c.r::after{content:"❌ RETIRER";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:#ef4444;padding:10px 20px;border-radius:8px;font-weight:bold}
.c img{width:100%;height:180px;object-fit:cover}
.c .n{padding:10px;font-weight:bold}
.s{position:fixed;bottom:20px;right:20px;background:#0a0a15;border:2px solid #e94560;padding:20px;border-radius:10px}
.s button{width:100%;padding:10px;margin:5px 0;background:#e94560;color:#fff;border:none;border-radius:5px;cursor:pointer;font-weight:bold}
</style></head><body>
<h1>🎮 KOF STAGES - Clique pour retirer</h1>
<div class="g">
"""

    for s in stages:
        img = OUTPUT_DIR / f"{s}.png"
        if img.exists() and img.stat().st_size > 5000:
            src = f"{s}.png"
        else:
            src = f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 320 180'><rect fill='%23162032' width='320' height='180'/><text x='160' y='90' fill='%23e94560' text-anchor='middle'>{s[:20]}</text></svg>"

        html += f'<div class="c" data-n="{s}.def" onclick="t(this)"><img src="{src}"><div class="n">{s}</div></div>\n'

    html += """</div>
<div class="s">
<div>A retirer: <b id="c" style="color:#ef4444">0</b></div>
<button onclick="e()">📋 Exporter</button>
</div>
<script>
let r=new Set();
function t(el){let n=el.dataset.n;r.has(n)?(r.delete(n),el.classList.remove('r')):(r.add(n),el.classList.add('r'));document.getElementById('c').textContent=r.size}
function e(){if(!r.size){alert('Aucun!');return}navigator.clipboard.writeText([...r].join('\\n'));alert('Copie!\\n\\n'+[...r].join('\\n'))}
</script></body></html>"""

    html_path = OUTPUT_DIR / "STAGE_GALLERY.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ Galerie: {html_path}")

    try:
        os.startfile(str(html_path))
    except:
        pass

if __name__ == "__main__":
    main()
