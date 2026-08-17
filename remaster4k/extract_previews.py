#!/usr/bin/env python3
"""Genere de vraies previews pour chaque stage (decodage SFF complet)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sff_lib import read_sff

BASE = Path(r"D:\KOF Ultimate Online kofuo")
STAGES = BASE / "stages"
OUT = Path(__file__).parent / "previews"
OUT.mkdir(exist_ok=True)

results = []
defs = [f for f in sorted(STAGES.glob("*.def")) if "backup" not in f.name.lower()]
print(f"{len(defs)} stages")

for d in defs:
    name = d.stem
    sff_path = STAGES / f"{name}.sff"
    info = {"name": name, "ok": False, "sprites": 0, "big": []}
    if not sff_path.exists():
        print(f"[SKIP] {name}: pas de .sff")
        results.append(info)
        continue
    try:
        sff = read_sff(sff_path)
        info["sprites"] = len(sff.sprites)
        # tri par surface decroissante, dedup par (pixels id)
        seen = set()
        ranked = []
        for s in sff.sprites:
            if s.width * s.height == 0:
                continue
            k = (s.width, s.height, bytes(s.pixels[:32]) if s.pixels else bytes(s.rgba[:32]))
            if k in seen:
                continue
            seen.add(k)
            ranked.append(s)
        ranked.sort(key=lambda s: s.width * s.height, reverse=True)
        for rank, s in enumerate(ranked[:4]):
            img = s.to_image(sff.palettes)
            if img is None:
                continue
            fn = OUT / f"{name}__{rank}_{s.group}-{s.number}_{s.width}x{s.height}.png"
            img.convert("RGB").save(fn)
            info["big"].append(fn.name)
        info["ok"] = len(info["big"]) > 0
        print(f"[OK] {name}: {len(sff.sprites)} sprites, top={ranked[0].width}x{ranked[0].height}" if ranked else f"[VIDE] {name}")
    except Exception as e:
        print(f"[ERR] {name}: {e}")
        info["err"] = str(e)
    results.append(info)

(OUT / "_index.json").write_text(json.dumps(results, indent=1, ensure_ascii=False))
ok = sum(1 for r in results if r["ok"])
print(f"\n{ok}/{len(results)} previews extraites -> {OUT}")
