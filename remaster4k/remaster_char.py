#!/usr/bin/env python3
"""Enhance IA des sprites persos a resolution identique (zero risque struct):
  sprite indexe -> RGBA -> Real-ESRGAN anime x4 -> downscale taille origine
  -> re-quantization sur les indices UTILISES du sprite (palettes .act safe)
Usage:
  python remaster_char.py pilot <CharDir>     # un perso, avec crops A/B
  python remaster_char.py batch               # tous les persos (journal resume)
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from PIL import Image

from sff_lib import read_sff, write_sff_v2

BASE = Path(r"D:\KOF Ultimate Online kofuo")
CHARS = BASE / "chars"
JOURNAL = Path(__file__).parent / "char_journal.json"
MIN_AREA = 24 * 24          # en-dessous: intouche (icones minuscules)
MAX_AREA = 600_000          # au-dessus: intouche. L'upscale x4 alloue
                            # w*h*16*3*4o (float32) en RAM ; un sprite >0.6MP
                            # depasse 1 GB et casse sur RAM saturee. Ces sprites
                            # sont deja haute-def (intros pleine page) -> on garde l'original.
PORTRAIT_GROUP = 9000        # portraits: intouches (affiches par le screenpack)


def find_sff(char_dir):
    for deff in sorted(char_dir.glob("*.def")):
        txt = deff.read_text(encoding="utf-8", errors="ignore")
        for ln in txt.splitlines():
            ls = ln.split(";")[0].strip()
            if ls.lower().startswith("sprite") and "=" in ls:
                rel = ls.split("=", 1)[1].strip().strip('"')
                p = char_dir / rel
                if p.exists():
                    return p
    # fallback: plus gros .sff du dossier
    sffs = sorted(char_dir.glob("*.sff"), key=lambda p: -p.stat().st_size)
    return sffs[0] if sffs else None


def bleed_edges(rgba_arr, iterations=4):
    rgb = rgba_arr[:, :, :3].astype(np.float32)
    known = rgba_arr[:, :, 3] > 0
    if known.all():
        return rgba_arr
    for _ in range(iterations):
        if known.all():
            break
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sk = np.roll(known, (dy, dx), axis=(0, 1))
            sr = np.roll(rgb, (dy, dx), axis=(0, 1))
            fill = sk & ~known
            rgb[fill] = sr[fill]
            known |= fill
    out = rgba_arr.copy()
    out[:, :, :3] = rgb.astype(np.uint8)
    return out


def requantize(out_rgb, orig_idx, pal):
    """Mappe l'image RGB enhancee vers les indices utilises du sprite.
    La transparence est reprise du sprite ORIGINAL (orig_idx==0) — sortie 1x,
    memes dimensions, pas besoin d'upscaler l'alpha."""
    used = np.unique(orig_idx)
    used = used[used != 0]
    if used.size == 0:
        return orig_idx.copy()
    pal_arr = np.array([pal[i][:3] for i in used], dtype=np.int32)  # (k,3)
    h, w = out_rgb.shape[:2]
    rgb = out_rgb[:, :, :3].astype(np.int32).reshape(-1, 3)
    # distances par blocs. La matrice intermediaire = B*k*3*4 octets : avec une
    # palette pleine (k=255) B=65536 faisait 191 MB et cassait sur RAM saturee.
    # Bloc adaptatif -> ~32 MB quel que soit k.
    idx_flat = np.empty(rgb.shape[0], dtype=np.int64)
    B = max(4096, 32_000_000 // (max(1, pal_arr.shape[0]) * 3 * 4))
    for o in range(0, rgb.shape[0], B):
        chunk = rgb[o:o + B]                                # (b,3)
        d = ((chunk[:, None, :] - pal_arr[None, :, :]) ** 2).sum(2)
        idx_flat[o:o + B] = d.argmin(1)
    mapped = used[idx_flat].reshape(h, w).astype(np.uint8)
    mapped[orig_idx == 0] = 0
    return mapped


ATLAS_W = 512       # planche d'empaquetage. 512 -> sortie x4 = 2048^2 (~50 MB
ATLAS_HMAX = 512    # float32), sur en RAM saturee (1024 = 192 MB, cassait).
GAP = 12            # marge anti-contamination entre sprites


def pack_atlases(items):
    """Shelf-packing: items=[(idx, arr_rgba)] tries par hauteur.
    Rend des atlas [(canvas, [(idx, x, y, w, h)])]."""
    items = sorted(items, key=lambda it: -it[1].shape[0])
    atlases = []
    cur, places = None, []
    x = y = shelf_h = 0
    for idx, arr in items:
        h, w = arr.shape[:2]
        ch = arr.shape[2]
        if cur is None:
            cur = np.zeros((ATLAS_HMAX, ATLAS_W, ch), dtype=np.uint8)
            places = []
            x, y, shelf_h = GAP, GAP, 0
        if x + w + GAP > ATLAS_W:           # nouvelle etagere
            x = GAP
            y += shelf_h + GAP
            shelf_h = 0
        if y + h + GAP > ATLAS_HMAX:        # atlas plein
            atlases.append((cur, places))
            cur = np.zeros((ATLAS_HMAX, ATLAS_W, ch), dtype=np.uint8)
            places = []
            x, y, shelf_h = GAP, GAP, 0
        cur[y:y + h, x:x + w] = arr
        places.append((idx, x, y, w, h))
        x += w + GAP
        shelf_h = max(shelf_h, h)
    if cur is not None and places:
        atlases.append((cur, places))
    return atlases


def enhance_char(char_dir, make_crops=False):
    from torch_upscaler import upscale_rgb
    sff_path = find_sff(char_dir)
    if sff_path is None:
        return "no_sff"
    bak = sff_path.with_suffix(".sff.bak_remaster4k")
    src = bak if bak.exists() else sff_path
    sff = read_sff(src)

    # 1) collecte des sprites uniques a traiter
    uniq = {}           # key -> (premier index sprite, arr bleede, orig_idx, pal)
    order = []
    for i, s in enumerate(sff.sprites):
        if (s.group == PORTRAIT_GROUP or not s.pixels
                or s.width * s.height < MIN_AREA
                or s.width * s.height > MAX_AREA):   # trop gros -> garde l'original
            continue
        key = (bytes(s.pixels), s.palidx)
        if key in uniq:
            continue
        pal = sff.palettes[s.palidx] if 0 <= s.palidx < len(sff.palettes) \
            else [(k, k, k, 255) for k in range(256)]
        orig_idx = np.frombuffer(bytes(s.pixels), dtype=np.uint8) \
            .reshape(s.height, s.width)
        arr = bleed_edges(np.asarray(s.to_image(sff.palettes).convert("RGBA")))
        uniq[key] = (i, arr[:, :, :3], orig_idx, pal)   # RGB seul (alpha origine reutilise)
        order.append(key)

    # 2) gros sprites (> demi-atlas): passage individuel ; le reste: atlas
    big_keys = [k for k in order
                if uniq[k][1].shape[0] > ATLAS_HMAX - 2 * GAP
                or uniq[k][1].shape[1] > ATLAS_W - 2 * GAP
                or uniq[k][1].shape[0] * uniq[k][1].shape[1] > (ATLAS_W * ATLAS_HMAX) // 3]
    small_keys = [k for k in order if k not in set(big_keys)]
    results = {}        # key -> down rgba (taille origine)

    for k in big_keys:
        _, arr, _, _ = uniq[k]
        up = upscale_rgb(arr, outscale=4)
        h, w = arr.shape[:2]
        results[k] = np.asarray(Image.fromarray(up).resize((w, h), Image.LANCZOS))

    atlas_items = [(k, uniq[k][1]) for k in small_keys]
    for canvas, places in pack_atlases(atlas_items):
        up = upscale_rgb(canvas, outscale=4)
        for k, x, y, w, h in places:
            crop = up[y * 4:(y + h) * 4, x * 4:(x + w) * 4]
            results[k] = np.asarray(Image.fromarray(crop).resize((w, h),
                                                                 Image.LANCZOS))

    # 3) requantization + ecriture
    cache = {}
    crops = []
    n_done = 0
    for s in sff.sprites:
        if (s.group == PORTRAIT_GROUP or not s.pixels
                or s.width * s.height < MIN_AREA):
            continue
        key = (bytes(s.pixels), s.palidx)
        if key in cache:
            s.pixels = cache[key]
            continue
        if key not in results:
            continue
        _, _, orig_idx, pal = uniq[key]
        down = results[key]
        newpix = requantize(down, orig_idx, pal).tobytes()
        if make_crops and not crops and s.width >= 60:
            crops.append((s, orig_idx, down, pal))
        cache[key] = newpix
        s.pixels = newpix
        n_done += 1
    if not bak.exists():
        import shutil
        shutil.copy2(sff_path, bak)
    write_sff_v2(sff, sff_path)
    if make_crops and crops:
        s, orig_idx, down, pal = crops[0]
        old = s.__class__(group=s.group, number=s.number, width=s.width,
                          height=s.height, palidx=s.palidx,
                          pixels=orig_idx.tobytes())
        out = Path(__file__).parent
        old.to_image(sff.palettes).convert("RGB").resize(
            (s.width * 4, s.height * 4), Image.NEAREST).save(out / "CHAR_OLD.png")
        s.to_image(sff.palettes).convert("RGB").resize(
            (s.width * 4, s.height * 4), Image.NEAREST).save(out / "CHAR_NEW.png")
    return f"ok:{n_done}"


def wait_for_ram(min_mb=1500, max_wait=600):
    """Attend qu'au moins min_mb de RAM soit libre (RAM partagee avec WC3 /
    modeles ; sans ca l'upscale x4 casse sur pic de saturation). Cap max_wait."""
    try:
        import psutil
    except ImportError:
        return
    waited = 0
    while waited < max_wait:
        avail = psutil.virtual_memory().available / 1e6
        if avail >= min_mb:
            return
        time.sleep(10)
        waited += 10
    # apres max_wait on tente quand meme (le guard MAX_AREA limite la casse)


def main():
    mode = sys.argv[1]
    if mode == "pilot":
        cd = CHARS / sys.argv[2]
        t0 = time.time()
        r = enhance_char(cd, make_crops=True)
        print(f"{cd.name}: {r} en {time.time() - t0:.0f}s", flush=True)
        return
    # batch
    journal = json.loads(JOURNAL.read_text()) if JOURNAL.exists() else {}
    dirs = [d for d in sorted(CHARS.iterdir()) if d.is_dir()]
    todo = [d for d in dirs if d.name not in journal]
    print(f"{len(todo)}/{len(dirs)} persos a traiter", flush=True)
    t0 = time.time()
    for k, d in enumerate(todo):
        t1 = time.time()
        wait_for_ram()
        try:
            r = enhance_char(d)
        except Exception as e:
            r = f"err:{e}"
        journal[d.name] = r
        JOURNAL.write_text(json.dumps(journal, indent=0))
        el = time.time() - t0
        eta = el / (k + 1) * (len(todo) - k - 1)
        print(f"[{k + 1}/{len(todo)}] {d.name}: {r} ({time.time() - t1:.0f}s)"
              f" | total {el / 60:.0f}min, ETA {eta / 60:.0f}min",
              flush=True)


if __name__ == "__main__":
    main()
