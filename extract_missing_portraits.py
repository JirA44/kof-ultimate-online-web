#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraction des portraits manquants pour KOFUO
40 personnages manquants à traiter
"""
import os
import shutil
import struct
from pathlib import Path
from PIL import Image
import io

MISSING_CHARS = [
    "ABYSS'Mega's",
    "AngusPurple-KOFM",
    "Another Scarlet",
    "Arctic Emperor",
    "BLAKE V3-1.1",
    "BW-Meiling",
    "C.Kyo.Blood-KOFM",
    "Carlin.Blood-CKOFM",
    "Caser.Yashiro",
    "D=Rockula",
    "Error Zero",
    "Flamme(S)",
    "HIEL-KOFM",
    "Hiyoi",
    "Kartis",
    "Kasim_LV2-CKOFM[v0.40]",
    "Kevenoce",
    "Keyser-Aunthmer",
    "Kotone",
    "Kyaga-KOFM",
    "Lane.Blood-CKOFM",
    "Littledevil-Phoenix",
    "LUMIEL",
    "New_Kyouki",
    "Noa_MK",
    "Olivia",
    "Orochi.Yamazaki-CKOFM",
    "R.S.P",
    "Raika",
    "Rinne-RH",
    "Rocken",
    "Samael",
    "Sasin",
    "Sonic Vanesa",
    "Tenrou_Kunagi",
    "ThunderMiss.Shermie",
    "VladRose",
    "Voltage Zeroko-Pre",
    "Yamazaki.Blood",
    "Yuri_SV"
]

def find_portrait_in_folder(char_path):
    """Cherche un portrait deja extrait dans le dossier du personnage"""
    patterns = [
        "**/9000,0.png",
        "**/9000,0.pcx",
        "**/portrait*.png",
        "**/Portrait*.png",
        "**/PORTRAIT*.png",
        "**/*portrait*.png",
        "**/立绘/*.png",  # Chinese folder name for portraits
        "**/海报.png",
        "**/*.png"
    ]

    for pattern in patterns:
        matches = list(char_path.glob(pattern))
        for match in matches:
            # Skip tiny files (< 1KB) and very large files (> 500KB for portraits)
            if match.stat().st_size > 1000 and match.stat().st_size < 500000:
                return match
    return None

def read_sff_v1_portrait(sff_path):
    """Extrait le portrait (groupe 9000) depuis un SFF v1"""
    try:
        with open(sff_path, 'rb') as f:
            signature = f.read(12)
            if not signature.startswith(b'ElecbyteSpr'):
                return None

            # Skip version bytes
            f.read(4)

            # Read counts
            group_total = struct.unpack('<I', f.read(4))[0]
            image_total = struct.unpack('<I', f.read(4))[0]
            next_subfile = struct.unpack('<I', f.read(4))[0]
            subfile_header_length = struct.unpack('<I', f.read(4))[0]

            # Skip rest of header
            f.read(480)

            current_pos = 512

            for i in range(min(image_total, 5000)):  # Limit iterations
                try:
                    f.seek(current_pos)

                    next_offset = struct.unpack('<I', f.read(4))[0]
                    length = struct.unpack('<I', f.read(4))[0]
                    f.read(4)  # axis
                    groupno = struct.unpack('<H', f.read(2))[0]
                    imageno = struct.unpack('<H', f.read(2))[0]

                    if groupno == 9000 and imageno == 0:
                        # Skip rest of header and read image data
                        f.read(16)  # Skip to image data
                        image_data = f.read(length - 32) if length > 32 else None

                        if image_data:
                            try:
                                img = Image.open(io.BytesIO(image_data))
                                return img
                            except:
                                pass

                    if next_offset == 0:
                        break
                    current_pos = next_offset
                except:
                    break
    except Exception as e:
        print(f"    Error reading SFF: {e}")
    return None

def read_sff_v2_portrait(sff_path):
    """Essaie de lire un portrait depuis SFF v2"""
    try:
        with open(sff_path, 'rb') as f:
            signature = f.read(12)
            if not signature.startswith(b'ElecbyteSpr'):
                return None

            # Check version
            verhi = struct.unpack('B', f.read(1))[0]
            if verhi < 2:
                return None

            # SFF v2 has different structure
            # Skip to sprite table offset at byte 36
            f.seek(36)
            sprite_offset = struct.unpack('<I', f.read(4))[0]
            sprite_total = struct.unpack('<I', f.read(4))[0]

            # Skip to palette table
            f.seek(48)
            palette_offset = struct.unpack('<I', f.read(4))[0]

            print(f"    SFF v2: {sprite_total} sprites")

            # Read sprite table
            f.seek(sprite_offset)
            for i in range(min(sprite_total, 5000)):
                try:
                    groupno = struct.unpack('<H', f.read(2))[0]
                    imageno = struct.unpack('<H', f.read(2))[0]
                    w = struct.unpack('<H', f.read(2))[0]
                    h = struct.unpack('<H', f.read(2))[0]
                    f.read(8)  # axis, link
                    fmt = struct.unpack('B', f.read(1))[0]
                    coldepth = struct.unpack('B', f.read(1))[0]
                    data_offset = struct.unpack('<I', f.read(4))[0]
                    data_len = struct.unpack('<I', f.read(4))[0]
                    f.read(8)  # palette, flags

                    if groupno == 9000 and imageno == 0:
                        print(f"    Found 9000,0: {w}x{h}, fmt={fmt}")
                        # TODO: Implement proper v2 image extraction
                        break
                except:
                    break
    except Exception as e:
        print(f"    Error reading SFF v2: {e}")
    return None

def find_sff_file(char_path):
    """Trouve le fichier SFF principal du personnage"""
    patterns = ["*/*.sff", "**/*.sff", "*.sff"]
    for pattern in patterns:
        matches = list(char_path.glob(pattern))
        if matches:
            # Prefer main sprite file, avoid sound files
            for m in matches:
                name = m.name.lower()
                if 'snd' not in name and 'sound' not in name:
                    return m
            return matches[0]
    return None

def main():
    print("=" * 60)
    print("  EXTRACTION PORTRAITS MANQUANTS - KOFUO")
    print("=" * 60)

    base_path = Path(r"D:\KOF Ultimate Online kofuo")
    chars_path = base_path / "chars"
    output_path = base_path / "web" / "portraits"
    output_path.mkdir(parents=True, exist_ok=True)

    success = 0
    failed = []

    for char_name in MISSING_CHARS:
        print(f"\n[{MISSING_CHARS.index(char_name)+1}/{len(MISSING_CHARS)}] {char_name}")

        char_path = chars_path / char_name
        if not char_path.exists():
            print(f"  ❌ Folder not found")
            failed.append((char_name, "Folder not found"))
            continue

        output_file = output_path / f"{char_name}.png"

        # 1. Try to find existing portrait
        existing = find_portrait_in_folder(char_path)
        if existing:
            print(f"  ✓ Found existing: {existing.name}")
            try:
                from PIL import ImageFile
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                img = Image.open(existing)
                img.load()  # Force load to catch errors early
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'P', 'LA'):
                    img = img.convert('RGBA')
                    # Create white background
                    bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
                    try:
                        bg.paste(img, mask=img.split()[3])
                    except:
                        bg.paste(img)
                    img = bg.convert('RGB')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(output_file, 'PNG', optimize=True)
                print(f"  ✓ Saved: {output_file.name}")
                success += 1
                continue
            except Exception as e:
                print(f"  ⚠ Failed to process existing: {e}")

        # 2. Try to extract from SFF
        sff_file = find_sff_file(char_path)
        if sff_file:
            print(f"  📄 Found SFF: {sff_file.name}")

            # Try v1 first
            img = read_sff_v1_portrait(sff_file)
            if img:
                img.save(output_file, 'PNG', optimize=True)
                print(f"  ✓ Extracted & saved: {output_file.name}")
                success += 1
                continue

            # Try v2
            img = read_sff_v2_portrait(sff_file)
            if img:
                img.save(output_file, 'PNG', optimize=True)
                print(f"  ✓ Extracted v2 & saved: {output_file.name}")
                success += 1
                continue

        failed.append((char_name, "No portrait found"))
        print(f"  ❌ No portrait found")

    print("\n" + "=" * 60)
    print(f"  RESULTS: {success}/{len(MISSING_CHARS)} extracted")
    print("=" * 60)

    if failed:
        print(f"\n❌ Failed ({len(failed)}):")
        for name, reason in failed:
            print(f"  - {name}: {reason}")

    return success, failed

if __name__ == "__main__":
    main()
