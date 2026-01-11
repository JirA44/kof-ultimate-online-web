#!/usr/bin/env python3
"""
KOF Ultimate Online - Stage Capture avec OBS Studio
Capture automatique de chaque stage via OBS WebSocket
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

# Installation des dependances
def install_deps():
    deps = ["obsws-python", "pillow", "pyautogui"]
    for dep in deps:
        try:
            __import__(dep.replace("-", "_").split("[")[0])
        except ImportError:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep, "-q"])

install_deps()

import obsws_python as obs
from PIL import Image
import pyautogui

BASE_DIR = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo kofuo")
STAGES_DIR = BASE_DIR / "stages"
OUTPUT_DIR = BASE_DIR / "stage_previews"
IKEMEN_EXE = BASE_DIR / "Ikemen_GO.exe"

# OBS WebSocket settings (default)
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = ""  # Laisser vide si pas de mot de passe

class OBSController:
    def __init__(self):
        self.client = None
        self.connected = False

    def connect(self):
        try:
            if OBS_PASSWORD:
                self.client = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=OBS_PASSWORD)
            else:
                self.client = obs.ReqClient(host=OBS_HOST, port=OBS_PORT)
            self.connected = True
            print("✓ Connected to OBS!")
            return True
        except Exception as e:
            print(f"✗ Could not connect to OBS: {e}")
            print("\nAssurez-vous que:")
            print("  1. OBS Studio est ouvert")
            print("  2. WebSocket Server est active (Tools > WebSocket Server Settings)")
            print("  3. Le port est 4455")
            return False

    def take_screenshot(self, filename):
        """Prend un screenshot via OBS"""
        try:
            # Methode 1: Screenshot via OBS
            output_path = str(OUTPUT_DIR / filename)

            # Utiliser SaveSourceScreenshot
            response = self.client.save_source_screenshot(
                source_name="",  # Current scene
                image_format="png",
                image_file_path=output_path,
                image_width=640,
                image_height=480
            )
            print(f"  ✓ Screenshot saved: {filename}")
            return True
        except Exception as e:
            print(f"  Using fallback screenshot method...")
            return self.take_screenshot_fallback(filename)

    def take_screenshot_fallback(self, filename):
        """Fallback: screenshot avec pyautogui"""
        try:
            time.sleep(0.5)
            screenshot = pyautogui.screenshot()
            output_path = OUTPUT_DIR / filename
            screenshot.save(str(output_path))
            print(f"  ✓ Screenshot (fallback): {filename}")
            return True
        except Exception as e:
            print(f"  ✗ Screenshot failed: {e}")
            return False

    def start_recording(self):
        try:
            self.client.start_record()
            print("  ▶ Recording started")
            return True
        except:
            return False

    def stop_recording(self):
        try:
            response = self.client.stop_record()
            print("  ⏹ Recording stopped")
            return response.output_path if hasattr(response, 'output_path') else None
        except:
            return None

def get_stages():
    """Liste tous les stages"""
    stages = []
    for def_file in sorted(STAGES_DIR.glob("*.def")):
        if 'backup' not in def_file.name.lower():
            stages.append({
                "name": def_file.stem,
                "def_file": def_file.name,
                "path": f"stages/{def_file.name}"
            })
    return stages

def create_stage_launcher_script(stage_path):
    """Cree un script Lua pour lancer directement sur un stage"""
    lua_script = f'''
-- Auto-load stage for screenshot
main.stageMenu = true
main.stageFile = "{stage_path}"
'''
    script_path = BASE_DIR / "external" / "script" / "auto_stage.lua"
    # This is complex in Ikemen, we'll use a different approach
    return None

def simple_screenshot_mode(stages):
    """Mode simple: screenshots avec pyautogui pendant que le jeu tourne"""
    print("\n" + "=" * 60)
    print("  MODE CAPTURE SIMPLE")
    print("=" * 60)
    print("""
Instructions:
1. Lance le jeu (Ikemen_GO.exe)
2. Va dans Options > Stage Select ou VS Mode
3. Pour chaque stage:
   - Selectionne le stage
   - Appuie sur ESPACE ici quand le stage est visible
   - Le script prendra un screenshot

Pret? Appuie ENTER pour commencer...
""")
    input()

    OUTPUT_DIR.mkdir(exist_ok=True)
    captured = 0

    print("\nStages a capturer:")
    for i, stage in enumerate(stages):
        existing = OUTPUT_DIR / f"{stage['name']}.png"
        status = "✓" if existing.exists() and existing.stat().st_size > 5000 else " "
        print(f"  [{status}] {i+1:2}. {stage['name']}")

    print("\n" + "-" * 40)
    print("Appuie ESPACE pour capturer, Q pour quitter")
    print("-" * 40 + "\n")

    stage_index = 0
    try:
        import keyboard

        def on_space():
            nonlocal stage_index, captured
            if stage_index >= len(stages):
                print("\nTous les stages ont ete captures!")
                return

            stage = stages[stage_index]
            filename = f"{stage['name']}.png"

            print(f"\n[{stage_index+1}/{len(stages)}] Capturing: {stage['name']}")

            # Petit delai pour s'assurer que l'ecran est stable
            time.sleep(0.3)

            try:
                screenshot = pyautogui.screenshot()
                output_path = OUTPUT_DIR / filename
                screenshot.save(str(output_path))
                print(f"  ✓ Saved: {filename}")
                captured += 1
            except Exception as e:
                print(f"  ✗ Error: {e}")

            stage_index += 1

            if stage_index < len(stages):
                print(f"\nProchain: {stages[stage_index]['name']}")
                print("Appuie ESPACE quand pret...")

        keyboard.on_press_key("space", lambda e: on_space())

        print("En attente... (Q pour quitter)\n")
        print(f"Premier stage: {stages[0]['name']}")
        print("Appuie ESPACE quand le stage est visible...")

        while stage_index < len(stages):
            if keyboard.is_pressed('q'):
                break
            time.sleep(0.1)

    except ImportError:
        print("Module 'keyboard' requis. Installation...")
        subprocess.run([sys.executable, "-m", "pip", "install", "keyboard", "-q"])
        print("Relance le script!")
        return

    print(f"\n{'=' * 60}")
    print(f"  Termine! {captured} screenshots captures")
    print(f"  Dossier: {OUTPUT_DIR}")
    print("=" * 60)

def obs_auto_mode(stages):
    """Mode automatique avec OBS"""
    print("\n" + "=" * 60)
    print("  MODE OBS AUTOMATIQUE")
    print("=" * 60)

    obs_ctrl = OBSController()
    if not obs_ctrl.connect():
        print("\nImpossible de se connecter a OBS.")
        print("Voulez-vous utiliser le mode simple? (o/N): ", end="")
        if input().strip().lower() == 'o':
            simple_screenshot_mode(stages)
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    print("""
Ce mode va:
1. Attendre que tu selectionnes un stage dans le jeu
2. Tu appuies ENTER ici
3. OBS prend un screenshot
4. Passe au stage suivant

Lance le jeu et appuie ENTER quand pret...
""")
    input()

    for i, stage in enumerate(stages):
        existing = OUTPUT_DIR / f"{stage['name']}.png"
        if existing.exists() and existing.stat().st_size > 10000:
            print(f"[{i+1}/{len(stages)}] {stage['name']} - deja capture, skip")
            continue

        print(f"\n[{i+1}/{len(stages)}] {stage['name']}")
        print("  Affiche ce stage dans le jeu puis appuie ENTER...")
        input()

        filename = f"{stage['name']}.png"
        obs_ctrl.take_screenshot(filename)

    print("\n✓ Capture terminee!")

def generate_final_gallery(stages):
    """Genere la galerie finale avec toutes les images"""
    print("\nGeneration de la galerie...")

    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>KOF - Stages Gallery</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; padding: 20px; }
        h1 { text-align: center; color: #e94560; margin-bottom: 20px; }
        .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 15px; }
        .card {
            background: #16213e; border: 3px solid #333; border-radius: 10px;
            overflow: hidden; cursor: pointer; transition: all 0.2s; position: relative;
        }
        .card:hover { border-color: #e94560; }
        .card.remove { border-color: #ef4444; }
        .card.remove img { opacity: 0.3; }
        .card.remove::after {
            content: "❌ A RETIRER"; position: absolute; top: 50%; left: 50%;
            transform: translate(-50%, -50%); background: #ef4444;
            padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 18px;
        }
        .card img { width: 100%; height: 200px; object-fit: cover; display: block; }
        .card .info { padding: 12px; }
        .card .name { font-weight: bold; font-size: 14px; }
        .summary {
            position: fixed; bottom: 20px; right: 20px;
            background: #0f0f1a; border: 2px solid #e94560;
            padding: 20px; border-radius: 10px; min-width: 200px;
        }
        .summary h3 { color: #e94560; margin-bottom: 10px; }
        .summary .count { font-size: 24px; color: #ef4444; }
        button {
            width: 100%; padding: 12px; margin-top: 10px;
            background: #e94560; color: #fff; border: none;
            border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 14px;
        }
        button:hover { background: #c73659; }
    </style>
</head>
<body>
    <h1>🎮 KOF STAGES - Clique pour marquer a retirer</h1>
    <div class="gallery">
"""

    for stage in stages:
        img_file = f"{stage['name']}.png"
        img_path = OUTPUT_DIR / img_file
        has_img = img_path.exists() and img_path.stat().st_size > 5000

        if has_img:
            img_src = img_file
        else:
            # Placeholder SVG
            img_src = f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 200'><rect fill='%23162032' width='400' height='200'/><text x='200' y='90' fill='%23e94560' text-anchor='middle' font-size='16'>{stage['name'][:25]}</text><text x='200' y='120' fill='%23666' text-anchor='middle' font-size='12'>(pas de preview)</text></svg>"

        html += f'''
        <div class="card" data-name="{stage['def_file']}" onclick="toggle(this)">
            <img src="{img_src}" alt="{stage['name']}">
            <div class="info">
                <div class="name">{stage['name']}</div>
            </div>
        </div>
'''

    html += """
    </div>
    <div class="summary">
        <h3>Selection</h3>
        <div>A retirer: <span class="count" id="count">0</span></div>
        <button onclick="exportList()">📋 Copier la liste</button>
        <button onclick="selectAll()" style="background:#666">Tout selectionner</button>
        <button onclick="deselectAll()" style="background:#333">Tout deselectionner</button>
    </div>
    <script>
        let toRemove = new Set();

        function toggle(el) {
            const name = el.dataset.name;
            if (toRemove.has(name)) {
                toRemove.delete(name);
                el.classList.remove('remove');
            } else {
                toRemove.add(name);
                el.classList.add('remove');
            }
            updateCount();
        }

        function updateCount() {
            document.getElementById('count').textContent = toRemove.size;
        }

        function selectAll() {
            document.querySelectorAll('.card').forEach(el => {
                toRemove.add(el.dataset.name);
                el.classList.add('remove');
            });
            updateCount();
        }

        function deselectAll() {
            document.querySelectorAll('.card').forEach(el => {
                toRemove.delete(el.dataset.name);
                el.classList.remove('remove');
            });
            updateCount();
        }

        function exportList() {
            const list = Array.from(toRemove);
            if (list.length === 0) {
                alert('Aucun stage selectionne!');
                return;
            }
            navigator.clipboard.writeText(list.join('\\n')).then(() => {
                alert('Liste copiee! (' + list.length + ' stages)\\n\\n' + list.join('\\n'));
            });
        }
    </script>
</body>
</html>
"""

    html_path = OUTPUT_DIR / "STAGE_GALLERY.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ Galerie: {html_path}")
    return html_path

def main():
    print("=" * 60)
    print("  KOF ULTIMATE ONLINE - STAGE CAPTURE TOOL")
    print("=" * 60)

    stages = get_stages()
    print(f"\n{len(stages)} stages trouves\n")

    # Check existing
    OUTPUT_DIR.mkdir(exist_ok=True)
    existing = sum(1 for s in stages if (OUTPUT_DIR / f"{s['name']}.png").exists()
                   and (OUTPUT_DIR / f"{s['name']}.png").stat().st_size > 5000)

    print(f"Screenshots existants: {existing}/{len(stages)}")

    print("\nOptions:")
    print("  1. Mode Simple (ESPACE pour screenshot)")
    print("  2. Mode OBS WebSocket")
    print("  3. Generer la galerie avec les images existantes")
    print("  4. Quitter")

    choice = input("\nChoix: ").strip()

    if choice == "1":
        simple_screenshot_mode(stages)
        generate_final_gallery(stages)
    elif choice == "2":
        obs_auto_mode(stages)
        generate_final_gallery(stages)
    elif choice == "3":
        html_path = generate_final_gallery(stages)
        try:
            os.startfile(str(html_path))
        except:
            print(f"\nOuvre: {html_path}")
    else:
        print("Bye!")

if __name__ == "__main__":
    main()
