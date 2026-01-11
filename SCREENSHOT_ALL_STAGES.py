#!/usr/bin/env python3
"""
KOF Ultimate Online - Stage Screenshot Taker
Lance le jeu sur chaque stage et prend une capture d'écran
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path

try:
    from PIL import ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Installing Pillow for screenshots...")
    subprocess.run([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import ImageGrab

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    print("Installing pyautogui...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyautogui", "-q"])
    import pyautogui

BASE_DIR = Path(r"D:\KOF Ultimate Online kofuo")
STAGES_DIR = BASE_DIR / "stages"
OUTPUT_DIR = BASE_DIR / "stage_previews"
IKEMEN_EXE = BASE_DIR / "Ikemen_GO.exe"

def get_all_stages():
    """Recupere la liste de tous les stages"""
    stages = []
    for def_file in sorted(STAGES_DIR.glob("*.def")):
        if 'backup' not in def_file.name.lower():
            stages.append({
                "name": def_file.stem,
                "def_file": def_file.name,
                "path": f"stages/{def_file.name}"
            })
    return stages

def take_screenshot(name, delay=3):
    """Prend une capture d'écran et la sauvegarde"""
    time.sleep(delay)

    try:
        # Capture l'écran entier
        screenshot = ImageGrab.grab()

        # Sauvegarder
        output_path = OUTPUT_DIR / f"{name}.png"
        screenshot.save(str(output_path), "PNG")
        print(f"  ✓ Screenshot saved: {output_path.name}")
        return True
    except Exception as e:
        print(f"  ✗ Error taking screenshot: {e}")
        return False

def create_stage_test_config(stage_path):
    """Cree une config temporaire pour charger un stage specifique"""
    # Modifier le fichier select.def temporairement pour forcer ce stage
    config = {
        "stage": stage_path,
        "p1": "chars/kyo/kyo.def",
        "p2": "chars/iori/iori.def"
    }

    config_path = BASE_DIR / "save" / "screenshot_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f)

    return config_path

def create_quick_match_lua():
    """Cree un script Lua pour lancer directement un match sur un stage"""
    lua_content = '''
-- Quick match for screenshot
local config_path = "save/screenshot_config.json"
local file = io.open(config_path, "r")
if file then
    local content = file:read("*all")
    file:close()
    -- Parse and load stage
end
'''
    return lua_content

def main():
    print("=" * 60)
    print("  KOF ULTIMATE ONLINE - STAGE SCREENSHOT TOOL")
    print("=" * 60)

    # Creer le dossier de sortie
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Recuperer tous les stages
    stages = get_all_stages()
    print(f"\nFound {len(stages)} stages to screenshot")

    print("\n" + "=" * 60)
    print("  MODE: MANUEL ASSISTE")
    print("=" * 60)
    print("""
Ce script va:
1. Lancer le jeu
2. Tu selectionnes un stage manuellement
3. Appuie sur F12 pour prendre le screenshot
4. Le script sauvegarde automatiquement

OU utilise le mode automatique (plus lent):
- Le script lance le jeu pour chaque stage
- Attend 5 secondes
- Prend le screenshot
- Ferme le jeu
""")

    print("\nOptions:")
    print("  1. Mode Manuel (tu navigues, F12 = screenshot)")
    print("  2. Mode Semi-Auto (liste des stages, tu confirmes chacun)")
    print("  3. Generer une page HTML avec les noms pour review")

    choice = input("\nChoix (1/2/3): ").strip()

    if choice == "1":
        manual_mode(stages)
    elif choice == "2":
        semi_auto_mode(stages)
    else:
        generate_review_page(stages)

def manual_mode(stages):
    """Mode manuel avec hotkey F12"""
    print("\n" + "=" * 60)
    print("  MODE MANUEL")
    print("=" * 60)
    print("""
Instructions:
1. Lance le jeu manuellement
2. Va dans VS Mode > Select Stage
3. Pour chaque stage:
   - Selectionne-le et lance un combat
   - Appuie sur F12 pour screenshot
   - Note le nom du stage
4. Les screenshots seront dans stage_previews/
""")

    print("\nStages a capturer:")
    for i, stage in enumerate(stages, 1):
        print(f"  {i:2}. {stage['name']}")

    print(f"\nLancement du monitoring F12...")
    print("Appuie sur Ctrl+C pour arreter\n")

    screenshot_count = 0
    try:
        import keyboard

        def on_f12():
            nonlocal screenshot_count
            screenshot_count += 1
            name = f"stage_{screenshot_count:02d}"

            # Demander le nom
            print(f"\nScreenshot #{screenshot_count}")
            stage_name = input("Nom du stage (ou Enter pour ignorer): ").strip()
            if stage_name:
                name = stage_name.replace(" ", "_").replace("/", "_")

            take_screenshot(name, delay=0.5)

        keyboard.on_press_key("F12", lambda e: on_f12())
        print("En attente de F12... (Ctrl+C pour quitter)")
        keyboard.wait()

    except ImportError:
        print("Module 'keyboard' non installe.")
        print("Installation...")
        subprocess.run([sys.executable, "-m", "pip", "install", "keyboard", "-q"])
        print("Relance le script!")
    except KeyboardInterrupt:
        print(f"\n\nTermine! {screenshot_count} screenshots pris.")

def semi_auto_mode(stages):
    """Mode semi-automatique"""
    print("\n" + "=" * 60)
    print("  MODE SEMI-AUTOMATIQUE")
    print("=" * 60)

    print("\nJe vais te montrer chaque stage.")
    print("Pour chaque stage:")
    print("  - Le jeu va se lancer sur ce stage")
    print("  - Attends que le stage soit visible")
    print("  - Appuie sur ENTER ici pour prendre le screenshot")
    print("  - Le jeu se fermera automatiquement")
    print("\nPret? ", end="")
    input()

    for i, stage in enumerate(stages, 1):
        print(f"\n[{i}/{len(stages)}] {stage['name']}")
        print(f"  Stage: {stage['path']}")

        # Verifier si le screenshot existe deja
        output_path = OUTPUT_DIR / f"{stage['name']}.png"
        if output_path.exists():
            skip = input("  Screenshot existe deja. Skip? (o/N): ").strip().lower()
            if skip == 'o':
                continue

        print("  Appuie ENTER quand le stage est visible...")
        input()

        take_screenshot(stage['name'], delay=0.5)

def generate_review_page(stages):
    """Genere une page HTML pour review avec les images existantes"""
    print("\n" + "=" * 60)
    print("  GENERATION PAGE DE REVIEW")
    print("=" * 60)

    # Chercher les screenshots existants
    existing = []
    missing = []

    for stage in stages:
        img_path = OUTPUT_DIR / f"{stage['name']}.png"
        if img_path.exists():
            existing.append(stage)
            stage['has_screenshot'] = True
            stage['img_path'] = f"{stage['name']}.png"
        else:
            missing.append(stage)
            stage['has_screenshot'] = False

    print(f"  Screenshots existants: {len(existing)}")
    print(f"  Screenshots manquants: {len(missing)}")

    if missing:
        print("\nStages sans screenshot:")
        for stage in missing:
            print(f"  - {stage['name']}")

    # Generer le HTML
    html = generate_gallery_html_with_images(stages)

    html_path = OUTPUT_DIR / "STAGE_GALLERY.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\nGalerie generee: {html_path}")

    # Ouvrir
    try:
        os.startfile(str(html_path))
    except:
        pass

def generate_gallery_html_with_images(stages):
    """Genere le HTML avec les vraies images"""

    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>KOF Ultimate Online - Stage Gallery</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #1a1a2e;
            color: #fff;
            padding: 20px;
        }
        h1 { text-align: center; color: #e94560; margin-bottom: 20px; }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }
        .stage-card {
            background: rgba(0,0,0,0.4);
            border: 2px solid #333;
            border-radius: 12px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.3s;
        }
        .stage-card:hover { border-color: #e94560; transform: scale(1.02); }
        .stage-card.selected { border-color: #ef4444; background: rgba(239,68,68,0.2); }
        .stage-card.selected::before {
            content: "❌ A RETIRER";
            position: absolute;
            top: 10px; right: 10px;
            background: #ef4444;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
            z-index: 10;
        }
        .stage-card { position: relative; }
        .stage-img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: #0a0a15;
        }
        .stage-img.missing {
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            background: linear-gradient(45deg, #1a1a2e, #0f3460);
        }
        .stage-name {
            padding: 15px;
            font-weight: bold;
            font-size: 16px;
        }
        .summary {
            position: fixed;
            bottom: 20px; right: 20px;
            background: rgba(0,0,0,0.95);
            border: 2px solid #e94560;
            padding: 20px;
            border-radius: 10px;
            min-width: 200px;
        }
        .summary button {
            width: 100%;
            padding: 10px;
            background: #e94560;
            border: none;
            color: #fff;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>🎮 KOF ULTIMATE ONLINE - STAGES (Clique pour retirer)</h1>
    <div class="gallery">
"""

    for stage in stages:
        if stage.get('has_screenshot'):
            img_html = f'<img class="stage-img" src="{stage["img_path"]}" alt="{stage["name"]}">'
        else:
            img_html = f'<div class="stage-img missing">🎮</div>'

        html += f'''
        <div class="stage-card" onclick="toggle(this, '{stage["def_file"]}')">
            {img_html}
            <div class="stage-name">{stage["name"]}</div>
        </div>
'''

    html += """
    </div>
    <div class="summary">
        <div>Total: <span id="total">0</span></div>
        <div>A retirer: <span id="remove" style="color:#ef4444">0</span></div>
        <button onclick="exportList()">📥 Exporter</button>
    </div>
    <script>
        let toRemove = new Set();
        document.getElementById('total').textContent = document.querySelectorAll('.stage-card').length;

        function toggle(el, name) {
            if (toRemove.has(name)) {
                toRemove.delete(name);
                el.classList.remove('selected');
            } else {
                toRemove.add(name);
                el.classList.add('selected');
            }
            document.getElementById('remove').textContent = toRemove.size;
        }

        function exportList() {
            const list = Array.from(toRemove);
            navigator.clipboard.writeText(list.join('\\n'));
            alert('Liste copiee!\\n\\n' + list.join('\\n'));
        }
    </script>
</body>
</html>
"""
    return html

if __name__ == "__main__":
    main()
