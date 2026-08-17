#!/usr/bin/env python3
"""Test in-game: lance Ikemen GO en fenetre sur un stage remasterise,
capture des screenshots, puis quitte (rounds=1, AI vs AI).
Usage: python test_ingame.py "Anubis" [duree_s]
"""

import subprocess
import sys
import time
from pathlib import Path

import ctypes
from ctypes import wintypes

BASE = Path(r"D:\KOF Ultimate Online kofuo")
OUT = Path(__file__).parent / "ingame_shots"
OUT.mkdir(exist_ok=True)


def screenshot_window(title_part, path):
    """Capture la fenetre dont le titre contient title_part (via PIL)."""
    from PIL import ImageGrab
    user32 = ctypes.windll.user32
    hwnd_found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def enum_cb(hwnd, _):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buf, 256)
        if title_part.lower() in buf.value.lower() and user32.IsWindowVisible(hwnd):
            hwnd_found.append(hwnd)
        return True

    user32.EnumWindows(enum_cb, 0)
    if not hwnd_found:
        return False
    hwnd = hwnd_found[0]
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
    img.save(path)
    return True


def main():
    stage = sys.argv[1]
    dur = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    exe = BASE / "Ikemen_GO.exe"
    cmd = [str(exe), "-p1", "kfm", "-p2", "kfm", "-p1.ai", "8", "-p2.ai", "8",
           "-s", f"stages/{stage}.def", "-rounds", "1", "-windowed",
           "-nosound", "-time", "30"]
    print(f"lancement: {stage}", flush=True)
    proc = subprocess.Popen(cmd, cwd=str(BASE),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shots = 0
    t0 = time.time()
    while time.time() - t0 < dur and proc.poll() is None:
        time.sleep(5)
        fn = OUT / f"{stage}_{shots:02d}.png"
        if screenshot_window("Ikemen", fn):
            shots += 1
            print(f"  shot {fn.name}", flush=True)
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(10)
        except subprocess.TimeoutExpired:
            proc.kill()
    print(f"fini: {shots} screenshots, exit={proc.returncode}", flush=True)


if __name__ == "__main__":
    main()
