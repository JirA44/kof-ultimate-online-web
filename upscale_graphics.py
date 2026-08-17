"""
upscale_graphics.py - KOF Ultimate Online
Upscale 2x bicubic (PIL) en attendant un outil IA (realesrgan-ncnn-vulkan / waifu2x)
Usage :
    python upscale_graphics.py [--src DOSSIER] [--out DOSSIER]
Défaut : cherche les PNG dans ../stages/ et les sous-dossiers de ../data/chars/
"""

import argparse
import os
import sys
import time
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("[ERREUR] Pillow n'est pas installé. Lance : pip install Pillow")
    sys.exit(1)

# Dossier racine du jeu (parent de ce script)
GAME_ROOT = Path(__file__).parent

DEFAULT_SOURCES = [
    GAME_ROOT / "stages",
    GAME_ROOT / "data" / "chars",
]
DEFAULT_OUT = GAME_ROOT / "upscaled"

LOG_FILE = GAME_ROOT / "upscale_log.txt"
EXTENSIONS = {".png", ".PNG"}
SCALE = 2
RESAMPLE = Image.BICUBIC


def log(msg: str, logfile):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    logfile.write(line + "\n")


def upscale_file(src_path: Path, dst_path: Path, logfile) -> bool:
    """Upscale un fichier PNG x2 bicubic. Retourne True si succès."""
    try:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src_path) as img:
            orig_mode = img.mode
            new_w = img.width * SCALE
            new_h = img.height * SCALE
            upscaled = img.resize((new_w, new_h), RESAMPLE)
            upscaled.save(dst_path, format="PNG")
        log(f"OK  {src_path.name} ({img.width}x{img.height} → {new_w}x{new_h}) [{orig_mode}]", logfile)
        return True
    except Exception as e:
        log(f"ERR {src_path.name} — {e}", logfile)
        return False


def collect_pngs(src_dirs: list[Path]) -> list[Path]:
    """Collecte récursivement tous les PNG dans les dossiers sources."""
    found = []
    for d in src_dirs:
        if not d.exists():
            print(f"[WARN] Dossier source introuvable : {d}")
            continue
        for ext in EXTENSIONS:
            found.extend(d.rglob(f"*{ext}"))
    return found


def main():
    parser = argparse.ArgumentParser(description="Upscale PNG KOF x2 bicubic")
    parser.add_argument("--src", nargs="*", help="Dossiers sources (défaut : stages/ + data/chars/)")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Dossier de sortie (défaut : upscaled/)")
    args = parser.parse_args()

    src_dirs = [Path(s) for s in args.src] if args.src else DEFAULT_SOURCES
    out_root = Path(args.out)

    out_root.mkdir(parents=True, exist_ok=True)

    pngs = collect_pngs(src_dirs)
    if not pngs:
        print("[INFO] Aucun fichier PNG trouvé dans les sources.")
        return

    print(f"[INFO] {len(pngs)} PNG trouvés — upscale {SCALE}x bicubic → {out_root}")
    print(f"[INFO] Log : {LOG_FILE}")

    ok = err = 0
    with open(LOG_FILE, "a", encoding="utf-8") as logfile:
        log(f"=== Début upscale — {len(pngs)} fichiers ===", logfile)
        for src in pngs:
            # Préserve la structure relative depuis la racine du jeu
            try:
                rel = src.relative_to(GAME_ROOT)
            except ValueError:
                rel = Path(src.name)
            dst = out_root / rel

            if upscale_file(src, dst, logfile):
                ok += 1
            else:
                err += 1

        log(f"=== Terminé — {ok} OK / {err} erreurs ===", logfile)

    print(f"\n[RÉSULTAT] {ok} fichiers upscalés, {err} erreurs. Voir {LOG_FILE}")
    print(f"[CONSEIL] Pour l'IA réelle, installe realesrgan-ncnn-vulkan :")
    print(f"  https://github.com/xinntao/Real-ESRGAN/releases")
    print(f"  Puis : realesrgan-ncnn-vulkan.exe -i stages/ -o upscaled_ai/ -n realesr-animevideov3")


if __name__ == "__main__":
    main()
