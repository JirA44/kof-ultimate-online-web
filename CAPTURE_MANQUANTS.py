#!/usr/bin/env python3
"""
Capture les 26 stages manquants - Guide etape par etape
"""
import os
from pathlib import Path

BASE_DIR = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo kofuo")
STAGES_DIR = BASE_DIR / "stages"
OUTPUT_DIR = BASE_DIR / "stage_previews"

def get_missing_stages():
    """Retourne les stages sans vraie capture (< 50 KB = placeholder)"""
    missing = []
    for f in sorted(STAGES_DIR.glob("*.def")):
        if 'backup' not in f.name.lower():
            name = f.stem
            img = OUTPUT_DIR / f"{name}.png"
            if not img.exists() or img.stat().st_size < 50000:  # < 50KB = placeholder
                missing.append(name)
    return missing

def main():
    print("=" * 60)
    print("  STAGES A CAPTURER (26 manquants)")
    print("=" * 60)

    missing = get_missing_stages()

    print(f"\n{len(missing)} stages ont besoin d'une capture:\n")

    for i, name in enumerate(missing, 1):
        print(f"  {i:2}. {name}")

    print("\n" + "=" * 60)
    print("  METHODE SIMPLE")
    print("=" * 60)
    print("""
1. Lance Ikemen_GO.exe
2. Va dans VS Mode > Selectionne 2 persos
3. A l'ecran de selection de stage:

   Pour CHAQUE stage ci-dessus:
   - Navigue jusqu'au stage
   - Appuie sur Win+Shift+S (Outil Capture Windows)
   - Selectionne la zone du stage
   - Sauvegarde dans: stage_previews\\NOM_DU_STAGE.png

   OU utilise Win+Alt+PrtSc (Xbox Game Bar)
   Les captures vont dans: C:\\Users\\%USERNAME%\\Videos\\Captures

4. Quand termine, relance ce script pour generer la galerie
""")

    print("=" * 60)
    input("\nAppuie ENTER pour ouvrir le dossier stage_previews...")

    os.startfile(str(OUTPUT_DIR))

    input("\nAppuie ENTER quand tu as fini pour regenerer la galerie...")

    # Regenerer la galerie
    generate_gallery()

def generate_gallery():
    """Genere la galerie HTML mise a jour"""
    stages = []
    for f in sorted(STAGES_DIR.glob("*.def")):
        if 'backup' not in f.name.lower():
            stages.append(f.stem)

    html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>KOF Stages</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial;background:#1a1a2e;color:#fff;padding:20px}
h1{text-align:center;color:#e94560;margin-bottom:10px}
.info{text-align:center;color:#888;margin-bottom:20px}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:15px}
.c{background:#16213e;border:3px solid #333;border-radius:10px;overflow:hidden;cursor:pointer;position:relative}
.c:hover{border-color:#e94560}
.c.r{border-color:#ef4444}
.c.r img{opacity:0.3}
.c.r::after{content:"RETIRER";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:#ef4444;padding:10px 20px;border-radius:8px;font-weight:bold;font-size:18px}
.c img{width:100%;height:180px;object-fit:cover}
.c .n{padding:10px;font-weight:bold;text-align:center}
.c.placeholder img{filter:grayscale(1);opacity:0.5}
.c.placeholder .n::after{content:" (manquant)";color:#ef4444;font-size:12px}
.s{position:fixed;bottom:20px;right:20px;background:#0a0a15;border:2px solid #e94560;padding:20px;border-radius:10px;max-width:220px}
.s button{width:100%;padding:10px;margin:5px 0;background:#e94560;color:#fff;border:none;border-radius:5px;cursor:pointer;font-weight:bold}
.s button:hover{background:#c73659}
.stats{margin-bottom:10px;font-size:14px}
</style></head><body>
<h1>KOF STAGES - Clique pour retirer</h1>
<p class="info">""" + f"{len(stages)} stages" + """</p>
<div class="g">
"""

    real_count = 0
    placeholder_count = 0

    for s in stages:
        img = OUTPUT_DIR / f"{s}.png"
        is_real = img.exists() and img.stat().st_size > 50000

        if is_real:
            src = f"{s}.png"
            real_count += 1
            extra_class = ""
        else:
            placeholder_count += 1
            extra_class = " placeholder"
            if img.exists():
                src = f"{s}.png"
            else:
                src = f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 320 180'><rect fill='%23162032' width='320' height='180'/><text x='160' y='90' fill='%23e94560' text-anchor='middle'>{s[:20]}</text></svg>"

        html += f'<div class="c{extra_class}" data-n="{s}.def" onclick="t(this)"><img src="{src}"><div class="n">{s}</div></div>\n'

    html += """</div>
<div class="s">
<div class="stats">
<div>Vraies images: <b style="color:#22c55e">""" + str(real_count) + """</b></div>
<div>Placeholders: <b style="color:#ef4444">""" + str(placeholder_count) + """</b></div>
<div style="margin-top:10px">A retirer: <b id="c" style="color:#ef4444">0</b></div>
</div>
<button onclick="e()">Copier la liste</button>
<button onclick="sa()" style="background:#666">Tout selectionner</button>
<button onclick="da()" style="background:#333">Deselectionner</button>
</div>
<script>
let r=new Set();
function t(el){let n=el.dataset.n;r.has(n)?(r.delete(n),el.classList.remove('r')):(r.add(n),el.classList.add('r'));document.getElementById('c').textContent=r.size}
function e(){if(!r.size){alert('Aucun!');return}navigator.clipboard.writeText([...r].join('\\n'));alert('Copie!\\n\\n'+[...r].join('\\n'))}
function sa(){document.querySelectorAll('.c').forEach(el=>{r.add(el.dataset.n);el.classList.add('r')});document.getElementById('c').textContent=r.size}
function da(){document.querySelectorAll('.c').forEach(el=>{r.delete(el.dataset.n);el.classList.remove('r')});document.getElementById('c').textContent=r.size}
</script></body></html>"""

    html_path = OUTPUT_DIR / "STAGE_GALLERY.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\nGalerie mise a jour!")
    print(f"  Vraies images: {real_count}")
    print(f"  Placeholders: {placeholder_count}")
    print(f"\nOuverture de la galerie...")

    os.startfile(str(html_path))

if __name__ == "__main__":
    main()
