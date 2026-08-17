#!/usr/bin/env python3
"""Retire les stages moches de la rotation: reassigne les persos vers les
stages gardes (round-robin) et reecrit [ExtraStages]. Backup avant."""

import re
import shutil
from pathlib import Path

SELECT = Path(r"D:\KOF Ultimate Online kofuo\data\select.def")
BACKUP = SELECT.with_suffix(".def.bak_remaster4k")

KEEP = [
    "Anubis",
    "Red_Cliff",
    "Far from here",
    "xX-Hell-Dark-Xx",
    "Abyss-Rugal-Palace",
    "clones lab destroyed",
    "RED",
]
keep_set = {k.lower() for k in KEEP}

if not BACKUP.exists():
    shutil.copy2(SELECT, BACKUP)
    print(f"backup -> {BACKUP.name}")

lines = SELECT.read_text(encoding="utf-8", errors="ignore").splitlines()
out, section = [], ""
rr = 0
reassigned = 0
stage_re = re.compile(r"^(.*?,\s*)stages/(.+?)\.def(.*)$", re.IGNORECASE)

for ln in lines:
    stripped = ln.strip()
    if stripped.startswith("["):
        section = stripped.lower()
        if section == "[extrastages]":
            out.append(ln)
            for k in KEEP:
                out.append(f"stages/{k}.def")
            continue
        out.append(ln)
        continue
    if section == "[extrastages]":
        continue  # remplace entierement
    if section == "[characters]":
        m = stage_re.match(stripped)
        if m:
            stage = m.group(2)
            if stage.lower().rstrip() not in keep_set:
                new_stage = KEEP[rr % len(KEEP)]
                rr += 1
                reassigned += 1
                out.append(f"{m.group(1)}stages/{new_stage}.def{m.group(3)}")
                continue
    out.append(ln)

SELECT.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"{reassigned} persos reassignes vers {len(KEEP)} stages gardes")
