#!/usr/bin/env python3
"""QA autonome kofuo — teste le remaster COMME UN USER, sans intervention.

Tier 1 (toujours, sans GPU ni fenetre): integrite SFF de chaque stage/perso
        remasterise (round-trip lecture). Detecte un repack corrompu.
Tier 2 (seulement si user ABSENT + pas de jeu plein ecran au 1er plan):
        lance Ikemen IA-vs-IA sur les stages remasterises, screenshots,
        detection crash / ecran noir / frame gelee / timeout de chargement.

Auto-heal: si un SFF est casse -> restaure le .bak_remaster4k (instantane, sur)
           et flag "needs_reremaster" dans le rapport (PAS de re-remaster auto:
           job GPU long, ne pas lancer sans contexte).
Auto-report: data_qa/REPORT.html + defects.jsonl (style supa self-report).

Usage:
  python kofuo_autoqa.py            # --auto: tier1 + tier2 si idle
  python kofuo_autoqa.py --tier1    # integrite seule (cron frequent)
  python kofuo_autoqa.py --tier2    # in-game force (ignore idle gate)
"""

import ctypes
import json
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from PIL import Image, ImageGrab

from sff_lib import read_sff

BASE = Path(r"D:\KOF Ultimate Online kofuo")
STAGES = BASE / "stages"
CHARS = BASE / "chars"
QA = Path(__file__).parent / "data_qa"
QA.mkdir(exist_ok=True)
SHOTS = QA / "shots"
SHOTS.mkdir(exist_ok=True)
DEFECTS = QA / "defects.jsonl"

REMASTERED_STAGES = [
    "Anubis", "Red_Cliff", "Far from here", "xX-Hell-Dark-Xx",
    "Abyss-Rugal-Palace", "clones lab destroyed", "RED",
]
IDLE_MIN_S = 300          # user inactif > 5 min => on peut jouer
SHOT_EVERY_S = 4
RUN_PER_STAGE_S = 24
BLACK_MEAN = 12           # luminance moyenne sous laquelle = ecran noir
FLAT_STD = 4              # ecart-type sous lequel = frame plate/figee


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def log_defect(d):
    d["ts"] = now()
    with open(DEFECTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")


# ── idle / foreground gate ───────────────────────────────────────────────────

def idle_seconds():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
    info = LASTINPUTINFO()
    info.cbSize = ctypes.sizeof(info)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info))
    millis = ctypes.windll.kernel32.GetTickCount() - info.dwTime
    return millis / 1000.0


def fullscreen_foreground():
    """True si la fenetre 1er plan couvre tout l'ecran (jeu/video plein ecran)."""
    u = ctypes.windll.user32
    hwnd = u.GetForegroundWindow()
    if not hwnd:
        return False
    rect = wintypes.RECT()
    u.GetWindowRect(hwnd, ctypes.byref(rect))
    sw = u.GetSystemMetrics(0)
    sh = u.GetSystemMetrics(1)
    w, h = rect.right - rect.left, rect.bottom - rect.top
    return w >= sw and h >= sh


def char_batch_running():
    """True si le batch remaster persos tourne (evite contention/OOM GPU 4GB
    et faux 'ecran noir' quand Ikemen ne peut pas allouer la VRAM)."""
    try:
        out = subprocess.run(
            ["wmic", "process", "where", "name='python.exe'", "get",
             "commandline"], capture_output=True, text=True, timeout=10,
            creationflags=0x08000000).stdout
        return "remaster_char.py" in out
    except Exception:
        return False


def can_play():
    return (idle_seconds() >= IDLE_MIN_S and not fullscreen_foreground()
            and not char_batch_running())


# ── Tier 1: integrite SFF ────────────────────────────────────────────────────

def check_sff(path):
    """Round-trip lecture. Retourne (ok, info|err)."""
    try:
        sff = read_sff(path)
        n_rgba = sum(1 for s in sff.sprites if s.rgba)
        n_idx = sum(1 for s in sff.sprites if s.pixels)
        if len(sff.sprites) == 0:
            return False, "0 sprite"
        return True, {"sprites": len(sff.sprites), "rgba": n_rgba, "idx": n_idx}
    except Exception as e:
        return False, str(e)


def heal_from_backup(sff_path):
    bak = sff_path.with_suffix(".sff.bak_remaster4k")
    if bak.exists():
        import shutil
        shutil.copy2(bak, sff_path)
        return True
    return False


def tier1():
    results = []
    # stages remasterises
    for name in REMASTERED_STAGES:
        p = STAGES / f"{name}.sff"
        ok, info = check_sff(p)
        size_mb = p.stat().st_size / 1e6 if p.exists() else 0
        entry = {"kind": "stage", "name": name, "ok": ok, "info": info,
                 "size_mb": round(size_mb, 1)}
        if not ok:
            healed = heal_from_backup(p)
            entry["healed"] = healed
            entry["needs_reremaster"] = True
            log_defect({"tier": 1, "type": "sff_corrupt", **entry})
        results.append(entry)
        print(f"[T1] stage {name}: {'OK' if ok else 'CASSE'} "
              f"{info if not ok else info} ({size_mb:.1f}MB)", flush=True)
    # persos deja remasterises (ceux qui ont un .bak)
    char_done = sorted(CHARS.glob("*/*.sff.bak_remaster4k"))
    n_char_ok = n_char_bad = 0
    for bak in char_done:
        live = Path(str(bak).replace(".sff.bak_remaster4k", ".sff"))
        ok, info = check_sff(live)
        if ok:
            n_char_ok += 1
        else:
            n_char_bad += 1
            healed = heal_from_backup(live)
            log_defect({"tier": 1, "type": "char_sff_corrupt",
                        "name": live.parent.name, "err": info, "healed": healed})
            print(f"[T1] char {live.parent.name}: CASSE {info} "
                  f"(heal={healed})", flush=True)
    print(f"[T1] persos remasterises: {n_char_ok} OK / {n_char_bad} casses",
          flush=True)
    return {"stages": results, "chars_ok": n_char_ok, "chars_bad": n_char_bad}


# ── Tier 2: in-game ──────────────────────────────────────────────────────────

def grab_ikemen():
    u = ctypes.windll.user32
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, _):
        buf = ctypes.create_unicode_buffer(256)
        u.GetWindowTextW(hwnd, buf, 256)
        if "ikemen" in buf.value.lower() and u.IsWindowVisible(hwnd):
            found.append(hwnd)
        return True

    u.EnumWindows(cb, 0)
    if not found:
        return None
    rect = wintypes.RECT()
    u.GetWindowRect(found[0], ctypes.byref(rect))
    if rect.right - rect.left < 50:
        return None
    return ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))


def analyze(img):
    a = np.asarray(img.convert("L"), dtype=np.float32)
    return float(a.mean()), float(a.std())


def play_stage(name):
    exe = BASE / "Ikemen_GO.exe"
    cmd = [str(exe), "-p1", "kfm", "-p2", "kfm", "-p1.ai", "8", "-p2.ai", "8",
           "-s", f"stages/{name}.def", "-rounds", "1", "-windowed",
           "-nosound", "-time", "20"]
    t0 = time.time()
    proc = subprocess.Popen(cmd, cwd=str(BASE), stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            creationflags=0x08000000)  # NO_WINDOW pour la console
    frames = []
    rendered = False
    last_hash = None
    frozen_count = 0
    defects = []
    while time.time() - t0 < RUN_PER_STAGE_S:
        time.sleep(SHOT_EVERY_S)
        if proc.poll() is not None:
            defects.append({"type": "crash", "stage": name,
                            "after_s": round(time.time() - t0, 1)})
            break
        img = grab_ikemen()
        if img is None:
            continue
        mean, std = analyze(img)
        fn = SHOTS / f"{name}_{int(time.time() - t0):02d}.jpg"
        img.convert("RGB").save(fn, quality=70)
        frames.append((mean, std))
        if mean > BLACK_MEAN and std > FLAT_STD:
            rendered = True
        h = hash(img.convert("L").resize((32, 32)).tobytes())
        frozen_count = frozen_count + 1 if h == last_hash else 0
        last_hash = h
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(8)
        except subprocess.TimeoutExpired:
            proc.kill()
    if not rendered and not any(d["type"] == "crash" for d in defects):
        # jamais rien rendu de non-noir -> ecran noir / timeout chargement
        worst = min((m for m, _ in frames), default=0)
        defects.append({"type": "no_render", "stage": name,
                        "mean_min": round(worst, 1),
                        "hint": "ecran noir ou chargement trop long"})
    if frozen_count >= 3:
        defects.append({"type": "frozen", "stage": name})
    for d in defects:
        log_defect({"tier": 2, **d})
    status = "OK" if not defects else ",".join(d["type"] for d in defects)
    print(f"[T2] {name}: {status} ({len(frames)} frames)", flush=True)
    return {"stage": name, "ok": not defects, "defects": defects,
            "frames": len(frames)}


def tier2():
    if grab_ikemen() is not None:
        print("[T2] une fenetre Ikemen est deja ouverte -> skip", flush=True)
        return {"skipped": "ikemen_already_open"}
    out = []
    for name in REMASTERED_STAGES:
        if not can_play():
            print("[T2] user revenu actif -> arret propre", flush=True)
            break
        out.append(play_stage(name))
    return {"stages": out}


# ── report ───────────────────────────────────────────────────────────────────

def write_report(t1res, t2res):
    rows = []
    for s in t1res["stages"]:
        badge = "OK" if s["ok"] else ("REPARE" if s.get("healed") else "CASSE")
        cls = "ok" if s["ok"] else "bad"
        rows.append(f"<tr class='{cls}'><td>{s['name']}</td><td>{badge}</td>"
                    f"<td>{s['size_mb']} MB</td><td>{s['info']}</td></tr>")
    t2rows = ""
    if t2res and t2res.get("stages"):
        for s in t2res["stages"]:
            cls = "ok" if s["ok"] else "bad"
            d = ", ".join(x["type"] for x in s["defects"]) or "—"
            t2rows += (f"<tr class='{cls}'><td>{s['stage']}</td>"
                       f"<td>{'OK' if s['ok'] else 'DEFECT'}</td>"
                       f"<td>{d}</td><td>{s['frames']} frames</td></tr>")
    else:
        skip = (t2res or {}).get("skipped", "user actif / jeu plein ecran")
        t2rows = f"<tr><td colspan=4>Tier 2 non exécuté ({skip})</td></tr>"
    html = f"""<!DOCTYPE html><html lang=fr><head><meta charset=utf-8>
<title>kofuo — QA autonome</title><style>
body{{background:#0b0e14;color:#e8ecf4;font:14px system-ui;padding:28px;max-width:900px;margin:auto}}
h1{{color:#ffd166}}h2{{color:#7aa2ff;border-bottom:1px solid #1f2737;padding-bottom:6px}}
table{{width:100%;border-collapse:collapse;background:#131825;border-radius:8px;overflow:hidden;margin-bottom:24px}}
td{{padding:8px 12px;border-bottom:1px solid #1a2030}}
tr.ok td:nth-child(2){{color:#3ddc84}}tr.bad td:nth-child(2){{color:#ff5c7a;font-weight:700}}
.sub{{color:#8b93a7}}</style></head><body>
<h1>🎮 kofuo — QA autonome</h1>
<div class=sub>généré {now()} · chars: {t1res['chars_ok']} OK / {t1res['chars_bad']} cassés</div>
<h2>Tier 1 — intégrité SFF stages</h2>
<table><tr><th>Stage</th><th>État</th><th>Taille</th><th>Détail</th></tr>{''.join(rows)}</table>
<h2>Tier 2 — test in-game (comme un user)</h2>
<table><tr><th>Stage</th><th>État</th><th>Défauts</th><th>Frames</th></tr>{t2rows}</table>
</body></html>"""
    (QA / "REPORT.html").write_text(html, encoding="utf-8")
    print(f"[QA] rapport -> {QA / 'REPORT.html'}", flush=True)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--auto"
    print(f"=== kofuo autoqa {mode} {now()} ===", flush=True)
    t1res = tier1()
    t2res = None
    if mode == "--tier2":
        t2res = tier2()
    elif mode == "--auto":
        if can_play():
            print(f"[QA] user inactif {int(idle_seconds())}s -> tier 2", flush=True)
            t2res = tier2()
        else:
            print(f"[QA] user actif ou jeu plein écran -> tier 2 reporté",
                  flush=True)
    write_report(t1res, t2res)


if __name__ == "__main__":
    main()
