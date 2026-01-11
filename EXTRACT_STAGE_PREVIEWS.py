#!/usr/bin/env python3
"""
KOF Ultimate Online - Stage Preview Extractor
Extrait une image de preview pour chaque stage et cree une galerie HTML
"""

import os
import struct
import json
from pathlib import Path

BASE_DIR = Path(r"D:\KOF Ultimate Online kofuo")
STAGES_DIR = BASE_DIR / "stages"
OUTPUT_DIR = BASE_DIR / "stage_previews"

def read_sff_preview(sff_path):
    """
    Tente d'extraire les dimensions et infos du premier sprite d'un fichier SFF
    Les fichiers SFF MUGEN sont complexes, on va juste lire les metadonnees
    """
    try:
        with open(sff_path, 'rb') as f:
            # Lire le header SFF
            signature = f.read(12)
            if b'ElecbyteSpr' in signature:
                version = struct.unpack('<I', f.read(4))[0]
                return {"format": "SFFv1", "size_mb": os.path.getsize(sff_path) / (1024*1024)}
            elif b'ElecbyteSpr' in signature or signature[:4] == b'SFFX':
                return {"format": "SFFv2", "size_mb": os.path.getsize(sff_path) / (1024*1024)}
            else:
                return {"format": "Unknown", "size_mb": os.path.getsize(sff_path) / (1024*1024)}
    except:
        return None

def get_stage_info(def_path):
    """Lit le fichier .def pour extraire les infos du stage"""
    info = {
        "name": def_path.stem,
        "def_file": def_path.name,
        "sff_file": None,
        "bgm": None,
        "author": None
    }

    try:
        with open(def_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

            for line in content.split('\n'):
                line = line.strip().lower()
                if line.startswith('spr ') or line.startswith('spr='):
                    info["sff_file"] = line.split('=')[-1].strip().strip('"')
                elif line.startswith('bgmusic ') or line.startswith('bgmusic='):
                    info["bgm"] = line.split('=')[-1].strip().strip('"')
                elif line.startswith('author ') or line.startswith('author='):
                    info["author"] = line.split('=')[-1].strip().strip('"')
                elif 'name' in line and '=' in line and 'displayname' not in line:
                    val = line.split('=')[-1].strip().strip('"')
                    if val and len(val) < 50:
                        info["name"] = val
    except:
        pass

    return info

def create_gallery_html(stages_info):
    """Cree une page HTML galerie des stages"""

    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>KOF Ultimate Online - Stage Gallery</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #e94560;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(233,69,96,0.5);
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }
        .controls {
            text-align: center;
            margin-bottom: 20px;
        }
        .controls input {
            padding: 10px 20px;
            width: 300px;
            border: 2px solid #e94560;
            border-radius: 8px;
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 16px;
        }
        .controls input:focus {
            outline: none;
            box-shadow: 0 0 15px rgba(233,69,96,0.5);
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .stage-card {
            background: rgba(0,0,0,0.4);
            border: 2px solid #333;
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s;
            position: relative;
        }
        .stage-card:hover {
            border-color: #e94560;
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(233,69,96,0.3);
        }
        .stage-card.selected {
            border-color: #ef4444;
            background: rgba(239,68,68,0.2);
        }
        .stage-card.selected::after {
            content: "A RETIRER";
            position: absolute;
            top: 10px;
            right: 10px;
            background: #ef4444;
            color: #fff;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 12px;
        }
        .stage-preview {
            height: 120px;
            background: linear-gradient(45deg, #1a1a2e, #0f3460);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
        }
        .stage-info {
            padding: 15px;
        }
        .stage-name {
            font-size: 16px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 8px;
        }
        .stage-meta {
            font-size: 12px;
            color: #888;
        }
        .stage-meta span {
            display: block;
            margin: 3px 0;
        }
        .stage-actions {
            padding: 10px 15px;
            border-top: 1px solid #333;
            display: flex;
            gap: 10px;
        }
        .btn {
            flex: 1;
            padding: 8px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.2s;
        }
        .btn-remove {
            background: #ef4444;
            color: #fff;
        }
        .btn-remove:hover {
            background: #dc2626;
        }
        .btn-keep {
            background: #22c55e;
            color: #fff;
        }
        .btn-keep:hover {
            background: #16a34a;
        }
        .summary {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0,0,0,0.9);
            border: 2px solid #e94560;
            border-radius: 10px;
            padding: 20px;
            min-width: 250px;
        }
        .summary h3 {
            color: #e94560;
            margin-bottom: 10px;
        }
        .summary-stats {
            margin-bottom: 15px;
        }
        .summary-stats div {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
        }
        .btn-export {
            width: 100%;
            padding: 10px;
            background: #e94560;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        .btn-export:hover {
            background: #c73659;
        }
    </style>
</head>
<body>
    <h1>🎮 KOF ULTIMATE ONLINE - STAGES</h1>
    <p class="subtitle">Cliquez sur une carte pour la marquer a retirer</p>

    <div class="controls">
        <input type="text" id="search" placeholder="🔍 Rechercher un stage..." oninput="filterStages()">
    </div>

    <div class="gallery" id="gallery">
"""

    icons = ["🏯", "🏰", "🌆", "🌃", "⛩️", "🏟️", "🎪", "🌋", "🏔️", "🌊", "🌙", "☀️", "⚡", "🔥", "❄️", "🌸"]

    for i, stage in enumerate(stages_info):
        icon = icons[i % len(icons)]
        size_str = f"{stage.get('size_mb', 0):.1f} MB" if stage.get('size_mb') else "?"

        html += f"""
        <div class="stage-card" data-name="{stage['name'].lower()}" onclick="toggleStage(this, '{stage['def_file']}')">
            <div class="stage-preview">{icon}</div>
            <div class="stage-info">
                <div class="stage-name">{stage['name']}</div>
                <div class="stage-meta">
                    <span>📁 {stage['def_file']}</span>
                    <span>💾 {size_str}</span>
                </div>
            </div>
            <div class="stage-actions">
                <button class="btn btn-remove" onclick="event.stopPropagation(); markRemove(this.closest('.stage-card'), '{stage['def_file']}')">❌ Retirer</button>
                <button class="btn btn-keep" onclick="event.stopPropagation(); markKeep(this.closest('.stage-card'), '{stage['def_file']}')">✅ Garder</button>
            </div>
        </div>
"""

    html += """
    </div>

    <div class="summary">
        <h3>📋 Resume</h3>
        <div class="summary-stats">
            <div><span>Total stages:</span><span id="totalStages">0</span></div>
            <div><span>A retirer:</span><span id="toRemove" style="color:#ef4444">0</span></div>
            <div><span>A garder:</span><span id="toKeep" style="color:#22c55e">0</span></div>
        </div>
        <button class="btn-export" onclick="exportList()">📥 Exporter la liste</button>
    </div>

    <script>
        let stagesToRemove = new Set();
        let allStages = [];

        document.querySelectorAll('.stage-card').forEach(card => {
            allStages.push(card.dataset.name);
        });

        updateSummary();

        function toggleStage(card, defFile) {
            if (stagesToRemove.has(defFile)) {
                stagesToRemove.delete(defFile);
                card.classList.remove('selected');
            } else {
                stagesToRemove.add(defFile);
                card.classList.add('selected');
            }
            updateSummary();
        }

        function markRemove(card, defFile) {
            stagesToRemove.add(defFile);
            card.classList.add('selected');
            updateSummary();
        }

        function markKeep(card, defFile) {
            stagesToRemove.delete(defFile);
            card.classList.remove('selected');
            updateSummary();
        }

        function updateSummary() {
            document.getElementById('totalStages').textContent = allStages.length;
            document.getElementById('toRemove').textContent = stagesToRemove.size;
            document.getElementById('toKeep').textContent = allStages.length - stagesToRemove.size;
        }

        function filterStages() {
            const search = document.getElementById('search').value.toLowerCase();
            document.querySelectorAll('.stage-card').forEach(card => {
                const name = card.dataset.name;
                card.style.display = name.includes(search) ? 'block' : 'none';
            });
        }

        function exportList() {
            const list = Array.from(stagesToRemove);
            const text = "STAGES A RETIRER:\\n\\n" + list.join("\\n");

            // Copier dans le presse-papier
            navigator.clipboard.writeText(list.join("\\n")).then(() => {
                alert("Liste copiee! " + list.length + " stages a retirer:\\n\\n" + list.slice(0,5).join("\\n") + (list.length > 5 ? "\\n..." : ""));
            });

            // Aussi sauvegarder en JSON
            const blob = new Blob([JSON.stringify(list, null, 2)], {type: 'application/json'});
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'stages_to_remove.json';
            a.click();
        }
    </script>
</body>
</html>
"""
    return html

def main():
    print("=" * 60)
    print("  KOF ULTIMATE ONLINE - STAGE PREVIEW EXTRACTOR")
    print("=" * 60)

    # Creer le dossier de sortie
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Trouver tous les stages
    stages_info = []
    def_files = list(STAGES_DIR.glob("*.def"))

    # Filtrer les backups
    def_files = [f for f in def_files if 'backup' not in f.name.lower()]

    print(f"\nFound {len(def_files)} stages")

    for def_path in sorted(def_files):
        print(f"  Processing: {def_path.name}")

        info = get_stage_info(def_path)

        # Chercher le fichier SFF correspondant
        sff_name = def_path.stem + ".sff"
        sff_path = STAGES_DIR / sff_name

        if sff_path.exists():
            sff_info = read_sff_preview(sff_path)
            if sff_info:
                info["size_mb"] = sff_info.get("size_mb", 0)
                info["format"] = sff_info.get("format", "Unknown")

        stages_info.append(info)

    # Sauvegarder les infos en JSON
    json_path = OUTPUT_DIR / "stages_info.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(stages_info, f, indent=2, ensure_ascii=False)
    print(f"\nStages info saved to: {json_path}")

    # Creer la galerie HTML
    html_content = create_gallery_html(stages_info)
    html_path = OUTPUT_DIR / "STAGE_GALLERY.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Gallery HTML saved to: {html_path}")

    # Ouvrir la galerie
    print(f"\nOpening gallery...")
    os.startfile(str(html_path))

    print("\n" + "=" * 60)
    print("  DONE! Use the gallery to select stages to remove.")
    print("  Click 'Exporter la liste' to save your selection.")
    print("=" * 60)

if __name__ == "__main__":
    main()
