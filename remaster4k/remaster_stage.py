#!/usr/bin/env python3
"""Remaster 4K d'un stage MUGEN/Ikemen (voie PyTorch CUDA):
  sprites -> upscale x2 (Real-ESRGAN anime 6B) -> repack SFFv2 -> patch .def
Usage: python remaster_stage.py "Anubis" [scale]
"""

import re
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from PIL import Image

from sff_lib import SffSprite, read_sff, write_sff_v2
from torch_upscaler import upscale_rgba

BASE = Path(r"D:\KOF Ultimate Online kofuo")
STAGES = BASE / "stages"

MIN_UPSCALE_AREA = 64 * 64   # plus petit: nearest x2 (particules, icones)


def bleed_edges(rgba_arr, iterations=6):
    """Etale les couleurs opaques dans le transparent (anti-halo upscale)."""
    rgb = rgba_arr[:, :, :3].astype(np.float32)
    known = rgba_arr[:, :, 3] > 0
    if known.all():
        return rgba_arr
    for _ in range(iterations):
        if known.all():
            break
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            src_known = np.roll(known, (dy, dx), axis=(0, 1))
            src_rgb = np.roll(rgb, (dy, dx), axis=(0, 1))
            fill = src_known & ~known
            rgb[fill] = src_rgb[fill]
            known |= fill
    out = rgba_arr.copy()
    out[:, :, :3] = rgb.astype(np.uint8)
    return out


def remaster_sff(sff, scale, label=""):
    """Upscale tous les sprites d'un SffFile en place (RGBA fmt PNG32)."""
    cache = {}
    uniq = []
    for i, s in enumerate(sff.sprites):
        if s.width * s.height == 0 or (not s.pixels and not s.rgba):
            continue
        key = (bytes(s.pixels) if s.pixels else bytes(s.rgba), s.palidx)
        if key not in cache:
            cache[key] = None
            uniq.append((i, key))
    total = len(uniq)
    t0 = time.time()
    for n, (i, key) in enumerate(uniq):
        s = sff.sprites[i]
        img = s.to_image(sff.palettes)
        arr = np.asarray(img.convert("RGBA"))
        if s.width * s.height < MIN_UPSCALE_AREA:
            out = np.asarray(img.resize((s.width * scale, s.height * scale),
                                        Image.NEAREST).convert("RGBA"))
        else:
            arr = bleed_edges(arr)
            out = upscale_rgba(arr, outscale=scale)
            th, tw = s.height * scale, s.width * scale
            if out.shape[:2] != (th, tw):
                out = np.asarray(Image.fromarray(out).resize((tw, th),
                                                             Image.LANCZOS))
        cache[key] = out
        if n % 20 == 0 or n == total - 1:
            el = time.time() - t0
            eta = el / (n + 1) * (total - n - 1)
            print(f"  [{label}] {n + 1}/{total} ({el:.0f}s, ETA {eta:.0f}s)",
                  flush=True)
    new_sprites = []
    for s in sff.sprites:
        ns = SffSprite(group=s.group, number=s.number,
                       axisx=s.axisx * scale, axisy=s.axisy * scale,
                       palidx=max(0, s.palidx), coldepth=32)
        key = (bytes(s.pixels) if s.pixels else bytes(s.rgba), s.palidx) \
            if (s.pixels or s.rgba) else None
        out = cache.get(key) if key else None
        if out is not None:
            ns.height, ns.width = out.shape[0], out.shape[1]
            ns.rgba = out.tobytes()
        else:
            ns.width = ns.height = 1
            ns.pixels = b"\x00"
        new_sprites.append(ns)
    sff.sprites = new_sprites


def patch_def(stage, scale):
    """scalestart /= scale sur chaque element [BG xxx].
    IDEMPOTENT: patche toujours depuis le .bak (original), jamais depuis le .def
    courant — sinon un 2e passage re-divise (0.5 -> 0.25)."""
    p = STAGES / f"{stage}.def"
    bak = STAGES / f"{stage}.def.bak_remaster4k"
    if not bak.exists():
        shutil.copy2(p, bak)
    # source de verite = le backup original (jamais le .def deja patche)
    lines = bak.read_text(encoding="utf-8", errors="ignore").splitlines()
    out = []
    in_bg = False
    bg_has_scale = False
    factor = 1.0 / scale

    def flush():
        if in_bg and not bg_has_scale:
            out.append(f"scalestart = {factor:g}, {factor:g}")

    for ln in lines:
        st = ln.strip().lower()
        if st.startswith("["):
            flush()
            in_bg = bool(re.match(r"\[bg[ \]]", st))
            bg_has_scale = False
            out.append(ln)
            continue
        if in_bg:
            m = re.match(r"(\s*scalestart\s*=\s*)([\d.\-]+)\s*,\s*([\d.\-]+)(.*)",
                         ln, re.IGNORECASE)
            if m:
                sx = float(m.group(2)) * factor
                sy = float(m.group(3)) * factor
                out.append(f"{m.group(1)}{sx:g}, {sy:g}{m.group(4)}")
                bg_has_scale = True
                continue
        out.append(ln)
    flush()
    p.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    stage = sys.argv[1]
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    print(f"=== {stage} (x{scale}) ===", flush=True)
    sff_path = STAGES / f"{stage}.sff"
    bak = STAGES / f"{stage}.sff.bak_remaster4k"
    src = bak if bak.exists() else sff_path   # idempotent: repart de l'original
    sff = read_sff(src)
    print(f"{len(sff.sprites)} sprites", flush=True)
    remaster_sff(sff, scale, label=stage)
    if not bak.exists():
        shutil.copy2(sff_path, bak)
    write_sff_v2(sff, sff_path)
    print(f"repack -> {sff_path.name} ({sff_path.stat().st_size / 1e6:.1f} MB)",
          flush=True)
    patch_def(stage, scale)
    print("def patche (scalestart)", flush=True)


if __name__ == "__main__":
    main()
