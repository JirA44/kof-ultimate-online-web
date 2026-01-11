#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère un select.def avec TOUS les personnages valides
"""

import os
from pathlib import Path
import shutil

GAME_PATH = Path(__file__).parent
CHARS_PATH = GAME_PATH / "chars"
STAGES_PATH = GAME_PATH / "stages"
SELECT_PATH = GAME_PATH / "data" / "select.def"

def get_valid_chars():
    """Get all characters that have required files"""
    valid = []
    invalid = []

    for char_dir in CHARS_PATH.iterdir():
        if not char_dir.is_dir():
            continue

        char_name = char_dir.name

        # Skip disabled chars
        if "_DISABLED" in char_name or char_name.startswith("."):
            invalid.append((char_name, "disabled"))
            continue

        # Check for .def file
        def_files = list(char_dir.glob("*.def"))
        if not def_files:
            invalid.append((char_name, "no .def"))
            continue

        # Check for _DISABLED_NO_SPRITES marker
        if (char_dir / "_DISABLED_NO_SPRITES").exists():
            invalid.append((char_name, "no sprites marker"))
            continue

        # Check for .sff file (sprites)
        sff_files = list(char_dir.glob("*.sff"))
        if not sff_files:
            # Check in subdirectories
            sff_files = list(char_dir.rglob("*.sff"))

        if not sff_files:
            invalid.append((char_name, "no .sff"))
            continue

        valid.append(char_name)

    return valid, invalid

def get_valid_stages():
    """Get all valid stages"""
    stages = []
    for stage_file in STAGES_PATH.glob("*.def"):
        stages.append(stage_file.stem)
    return stages

def generate_select_def(chars, stages):
    """Generate the select.def content"""
    content = []
    content.append("; ================================================")
    content.append("; KOF ULTIMATE ONLINE - FULL ROSTER")
    content.append(f"; Auto-generated with {len(chars)} characters")
    content.append("; ================================================")
    content.append("")
    content.append("[Characters]")

    # Add all valid characters
    for i, char in enumerate(sorted(chars)):
        stage = stages[i % len(stages)] if stages else "stage0"
        content.append(f"{char}, stages/{stage}.def")

    content.append("")
    content.append("[ExtraStages]")
    for stage in stages[:20]:
        content.append(f"stages/{stage}.def")

    content.append("")
    content.append("[Options]")
    content.append("arcade.maxmatches = 6,0,0,0,0,0,0,0,0,0")
    content.append("team.maxsimul = 4")
    content.append("")

    return "\n".join(content)

if __name__ == "__main__":
    print("Scanning characters...")
    valid_chars, invalid_chars = get_valid_chars()

    print(f"\n✅ Valid characters: {len(valid_chars)}")
    print(f"❌ Invalid characters: {len(invalid_chars)}")

    if invalid_chars:
        print("\nInvalid characters:")
        for name, reason in invalid_chars[:15]:
            print(f"  - {name}: {reason}")
        if len(invalid_chars) > 15:
            print(f"  ... and {len(invalid_chars) - 15} more")

    print("\nScanning stages...")
    stages = get_valid_stages()
    print(f"✅ Valid stages: {len(stages)}")

    # Backup current select.def
    if SELECT_PATH.exists():
        backup_path = SELECT_PATH.with_suffix(".def.backup_before_full")
        shutil.copy2(SELECT_PATH, backup_path)
        print(f"\n📦 Backup saved: {backup_path}")

    # Generate new select.def
    content = generate_select_def(valid_chars, stages)
    SELECT_PATH.write_text(content, encoding='utf-8')

    print(f"\n✅ Generated new select.def with {len(valid_chars)} characters!")
    print(f"   Path: {SELECT_PATH}")
