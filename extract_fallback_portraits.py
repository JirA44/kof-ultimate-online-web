#!/usr/bin/env python3
"""
Extraction portraits de fallback (premier sprite lisible)
Pour les personnages sans groupe 9000
"""
import struct
from pathlib import Path
from PIL import Image, ImageFile
import io

ImageFile.LOAD_TRUNCATED_IMAGES = True

FAILED_CHARS = [
    "Caser.Yashiro", "D=Rockula", "Error Zero", "Hiyoi",
    "Kasim_LV2-CKOFM[v0.40]", "Kevenoce", "Keyser-Aunthmer", "Kyaga-KOFM",
    "Lane.Blood-CKOFM", "LUMIEL", "Olivia", "Orochi.Yamazaki-CKOFM",
    "R.S.P", "Rinne-RH", "Rocken", "Samael", "Sasin", "Yamazaki.Blood"
]

def extract_any_usable_sprite(sff_path, min_size=50):
    """Extrait n'importe quel sprite utilisable comme portrait"""
    try:
        with open(sff_path, 'rb') as f:
            signature = f.read(12)
            if not signature.startswith(b'ElecbyteSpr'):
                return None

            f.read(4)  # version
            group_total = struct.unpack('<I', f.read(4))[0]
            image_total = struct.unpack('<I', f.read(4))[0]
            f.read(8)  # offsets
            f.read(480)  # padding

            current_pos = 512
            best_img = None
            best_size = 0

            # Priority groups for portraits
            priority_groups = [9000, 9001, 9002, 0, 1, 2, 5, 10, 200]
            found_sprites = {}

            for i in range(min(image_total, 3000)):
                try:
                    f.seek(current_pos)
                    next_offset = struct.unpack('<I', f.read(4))[0]
                    length = struct.unpack('<I', f.read(4))[0]
                    f.read(4)  # axis
                    groupno = struct.unpack('<H', f.read(2))[0]
                    imageno = struct.unpack('<H', f.read(2))[0]
                    index = struct.unpack('<H', f.read(2))[0]
                    f.read(14)  # rest of header

                    if length > 32 and index == 0:  # Not linked sprite
                        image_data = f.read(length - 32)

                        if len(image_data) > 100:
                            try:
                                img = Image.open(io.BytesIO(image_data))
                                w, h = img.size

                                # Score based on: group priority, size, aspect ratio
                                if w >= min_size and h >= min_size:
                                    score = w * h
                                    if groupno in priority_groups:
                                        score *= 10
                                    if 0.5 <= w/h <= 2:  # Good aspect ratio
                                        score *= 2

                                    if groupno not in found_sprites or score > found_sprites[groupno][0]:
                                        found_sprites[groupno] = (score, img.copy(), groupno, imageno)
                            except:
                                pass

                    if next_offset == 0:
                        break
                    current_pos = next_offset
                except:
                    break

            # Find best sprite by priority
            for group in priority_groups:
                if group in found_sprites:
                    return found_sprites[group][1]

            # Fallback: return largest sprite
            if found_sprites:
                best = max(found_sprites.values(), key=lambda x: x[0])
                return best[1]

    except Exception as e:
        print(f"    Error: {e}")
    return None

def main():
    print("=" * 60)
    print("  FALLBACK PORTRAIT EXTRACTION")
    print("=" * 60)

    base_path = Path(r"D:\KOF Ultimate Online kofuo")
    chars_path = base_path / "chars"
    output_path = base_path / "web" / "portraits"

    success = 0
    for char_name in FAILED_CHARS:
        print(f"\n{char_name}...")

        char_path = chars_path / char_name
        if not char_path.exists():
            print(f"  ❌ Folder not found")
            continue

        output_file = output_path / f"{char_name}.png"
        if output_file.exists():
            print(f"  ✓ Already exists")
            success += 1
            continue

        # Find SFF
        sffs = list(char_path.glob("**/*.sff"))
        if not sffs:
            print(f"  ❌ No SFF found")
            continue

        sff_file = sffs[0]
        print(f"  📄 {sff_file.name}")

        img = extract_any_usable_sprite(sff_file)
        if img:
            try:
                if img.mode != 'RGB':
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        bg = Image.new('RGB', img.size, (40, 40, 60))  # Dark blue bg
                        if img.mode == 'RGBA':
                            bg.paste(img, mask=img.split()[3])
                        else:
                            bg.paste(img)
                        img = bg
                    else:
                        img = img.convert('RGB')

                img.save(output_file, 'PNG', optimize=True)
                print(f"  ✓ Saved: {output_file.name}")
                success += 1
            except Exception as e:
                print(f"  ❌ Save error: {e}")
        else:
            print(f"  ❌ No usable sprite found")

    print(f"\n{'='*60}")
    print(f"  RESULT: {success}/{len(FAILED_CHARS)} recovered")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
