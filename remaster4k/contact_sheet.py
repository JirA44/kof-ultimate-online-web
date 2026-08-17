#!/usr/bin/env python3
"""Planche-contact: une ligne par stage, top-6 sprites redimensionnes h=110."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from PIL import Image, ImageDraw

from sff_lib import read_sff

BASE = Path(r"D:\KOF Ultimate Online kofuo")
STAGES = BASE / "stages"
OUT = Path(__file__).parent

TH = 110          # hauteur vignette
LABEL_W = 230
ROW_W = LABEL_W + 6 * (200 + 4)

defs = [f for f in sorted(STAGES.glob("*.def"))
        if "backup" not in f.name.lower() and (STAGES / f"{f.stem}.sff").exists()]

rows = []
for d in defs:
    name = d.stem
    try:
        sff = read_sff(STAGES / f"{name}.sff")
    except Exception as e:
        print(f"[ERR] {name}: {e}")
        continue
    seen, ranked = set(), []
    for s in sff.sprites:
        if s.width * s.height == 0 or s.is_linked:
            continue
        k = (s.width, s.height, bytes(s.pixels[:32]) if s.pixels else bytes(s.rgba[:32]))
        if k in seen:
            continue
        seen.add(k)
        ranked.append(s)
    ranked.sort(key=lambda s: s.width * s.height, reverse=True)
    row = Image.new("RGB", (ROW_W, TH + 8), (24, 24, 34))
    dr = ImageDraw.Draw(row)
    dr.text((6, TH // 2 - 12), name[:28], fill=(255, 210, 80))
    dr.text((6, TH // 2 + 2), f"{len(sff.sprites)} spr", fill=(140, 140, 150))
    x = LABEL_W
    for s in ranked[:6]:
        img = s.to_image(sff.palettes)
        if img is None:
            continue
        # fond damier discret pour voir l'alpha
        bg = Image.new("RGB", img.size, (60, 60, 70))
        bg.paste(img, (0, 0), img)
        w = max(1, int(s.width * TH / s.height))
        w = min(w, 200)
        bg = bg.resize((w, TH))
        row.paste(bg, (x, 4))
        x += w + 4
        if x > ROW_W - 60:
            break
    rows.append(row)
    print(f"[OK] {name}")

sheet = Image.new("RGB", (ROW_W, len(rows) * (TH + 10)), (10, 10, 14))
for i, r in enumerate(rows):
    sheet.paste(r, (0, i * (TH + 10)))
fn = OUT / "CONTACT_SHEET.png"
sheet.save(fn)
print(f"-> {fn} ({sheet.size})")
