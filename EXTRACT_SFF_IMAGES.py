#!/usr/bin/env python3
"""
KOF Ultimate Online - SFF Image Extractor
Extrait les images de fond directement des fichiers .sff des stages
"""

import os
import sys
import struct
import zlib
from pathlib import Path

try:
    from PIL import Image
    import io
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image
    import io

BASE_DIR = Path(r"D:\KOF Ultimate Online kofuo")
STAGES_DIR = BASE_DIR / "stages"
OUTPUT_DIR = BASE_DIR / "stage_previews"

def extract_sff_v2(sff_path, output_path, max_sprites=5):
    """
    Extrait les premiers sprites d'un fichier SFF v2
    SFF v2 contient des images PNG/raw compressees
    """
    try:
        with open(sff_path, 'rb') as f:
            # Header SFF v2
            signature = f.read(12)

            if b'ElecbyteSpr' not in signature:
                return False

            # Version
            ver_lo = struct.unpack('<B', f.read(1))[0]
            ver_hi = struct.unpack('<B', f.read(1))[0]
            ver_lo2 = struct.unpack('<B', f.read(1))[0]
            ver_hi2 = struct.unpack('<B', f.read(1))[0]

            # Skip reserved
            f.read(4)

            # Compatibility version
            f.read(4)

            # Skip more header
            f.read(4)  # reserved

            # First sprite offset
            first_sprite_offset = struct.unpack('<I', f.read(4))[0]

            # Sprite count
            sprite_count = struct.unpack('<I', f.read(4))[0]

            # Palette offset
            palette_offset = struct.unpack('<I', f.read(4))[0]

            # Palette count
            palette_count = struct.unpack('<I', f.read(4))[0]

            # Ldata offset (linked data)
            ldata_offset = struct.unpack('<I', f.read(4))[0]

            # Ldata length
            ldata_len = struct.unpack('<I', f.read(4))[0]

            # Tdata offset (sprite data)
            tdata_offset = struct.unpack('<I', f.read(4))[0]

            # Tdata length
            tdata_len = struct.unpack('<I', f.read(4))[0]

            print(f"    SFF v2: {sprite_count} sprites, {palette_count} palettes")

            if sprite_count == 0:
                return False

            # Go to first sprite
            f.seek(first_sprite_offset)

            best_image = None
            best_size = 0

            # Try to find the largest sprite (usually the background)
            for i in range(min(sprite_count, 20)):  # Check first 20 sprites
                try:
                    # Sprite header (28 bytes in SFF v2)
                    group_no = struct.unpack('<H', f.read(2))[0]
                    image_no = struct.unpack('<H', f.read(2))[0]
                    width = struct.unpack('<H', f.read(2))[0]
                    height = struct.unpack('<H', f.read(2))[0]
                    x_axis = struct.unpack('<h', f.read(2))[0]
                    y_axis = struct.unpack('<h', f.read(2))[0]
                    link_index = struct.unpack('<H', f.read(2))[0]
                    fmt = struct.unpack('<B', f.read(1))[0]
                    color_depth = struct.unpack('<B', f.read(1))[0]
                    data_offset = struct.unpack('<I', f.read(4))[0]
                    data_len = struct.unpack('<I', f.read(4))[0]
                    palette_index = struct.unpack('<H', f.read(2))[0]
                    flags = struct.unpack('<H', f.read(2))[0]

                    # Check if this is a large image (background)
                    size = width * height
                    if size > best_size and width >= 200 and height >= 150:
                        # Try to extract this sprite
                        if data_len > 0 and data_offset > 0:
                            current_pos = f.tell()
                            f.seek(tdata_offset + data_offset)

                            raw_data = f.read(data_len)

                            # Try to decompress
                            try:
                                if fmt == 2:  # RLE8
                                    pass
                                elif fmt == 3:  # RLE5
                                    pass
                                elif fmt == 4:  # LZ5
                                    pass
                                elif fmt == 10:  # PNG8
                                    img = Image.open(io.BytesIO(raw_data))
                                    if img.size[0] * img.size[1] > best_size:
                                        best_image = img.copy()
                                        best_size = img.size[0] * img.size[1]
                                elif fmt == 11:  # PNG24
                                    img = Image.open(io.BytesIO(raw_data))
                                    if img.size[0] * img.size[1] > best_size:
                                        best_image = img.copy()
                                        best_size = img.size[0] * img.size[1]
                                elif fmt == 12:  # PNG32
                                    img = Image.open(io.BytesIO(raw_data))
                                    if img.size[0] * img.size[1] > best_size:
                                        best_image = img.copy()
                                        best_size = img.size[0] * img.size[1]
                            except:
                                pass

                            f.seek(current_pos)

                except Exception as e:
                    break

            if best_image:
                best_image.save(str(output_path), "PNG")
                print(f"    ✓ Extracted: {best_image.size[0]}x{best_image.size[1]}")
                return True

    except Exception as e:
        print(f"    Error: {e}")

    return False

def extract_sff_v1(sff_path, output_path):
    """
    Extrait un sprite d'un fichier SFF v1 (ancien format PCX)
    """
    try:
        with open(sff_path, 'rb') as f:
            # Header
            signature = f.read(12)
            if b'ElecbyteSpr' not in signature:
                return False

            version = f.read(4)

            # Groups, images
            f.read(4)  # groups
            images_count = struct.unpack('<I', f.read(4))[0]

            # First sprite offset
            first_offset = struct.unpack('<I', f.read(4))[0]

            # Subheader size
            subheader_size = struct.unpack('<I', f.read(4))[0]

            # Palette type
            f.read(1)

            print(f"    SFF v1: {images_count} images")

            if images_count == 0:
                return False

            # Go to first sprite
            f.seek(first_offset)

            best_image = None
            best_size = 0

            for i in range(min(images_count, 10)):
                try:
                    next_offset = struct.unpack('<I', f.read(4))[0]
                    data_len = struct.unpack('<I', f.read(4))[0]
                    x_axis = struct.unpack('<h', f.read(2))[0]
                    y_axis = struct.unpack('<h', f.read(2))[0]
                    group_no = struct.unpack('<H', f.read(2))[0]
                    image_no = struct.unpack('<H', f.read(2))[0]
                    link_index = struct.unpack('<H', f.read(2))[0]
                    use_shared_pal = struct.unpack('<B', f.read(1))[0]

                    f.read(13)  # padding

                    if data_len > 0:
                        pcx_data = f.read(data_len)

                        # Try to decode PCX
                        try:
                            img = Image.open(io.BytesIO(pcx_data))
                            size = img.size[0] * img.size[1]
                            if size > best_size:
                                best_image = img.copy()
                                best_size = size
                        except:
                            pass

                    if next_offset > 0:
                        f.seek(next_offset)
                    else:
                        break

                except:
                    break

            if best_image:
                best_image = best_image.convert('RGB')
                best_image.save(str(output_path), "PNG")
                print(f"    ✓ Extracted: {best_image.size[0]}x{best_image.size[1]}")
                return True

    except Exception as e:
        print(f"    Error: {e}")

    return False

def try_find_existing_image(stage_name):
    """Cherche une image existante pour ce stage"""
    # Chercher dans les dossiers communs
    possible_paths = [
        STAGES_DIR / f"{stage_name}.png",
        STAGES_DIR / f"{stage_name}.jpg",
        STAGES_DIR / f"{stage_name}" / "preview.png",
        STAGES_DIR / f"{stage_name}" / "bg.png",
    ]

    for path in possible_paths:
        if path.exists():
            return path
    return None

def create_placeholder(stage_name, output_path):
    """Cree une image placeholder avec le nom du stage"""
    try:
        img = Image.new('RGB', (400, 250), color=(26, 26, 46))

        # Add text (simple, sans font externe)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)

        # Draw stage name
        text = stage_name[:30]
        draw.text((20, 100), text, fill=(233, 69, 96))
        draw.text((20, 130), "(Preview non disponible)", fill=(100, 100, 100))

        img.save(str(output_path), "PNG")
        return True
    except:
        return False

def generate_html_gallery(stages_info):
    """Genere la galerie HTML"""
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>KOF - Stages Gallery</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; padding: 20px; }
        h1 { text-align: center; color: #e94560; margin-bottom: 20px; }
        .info { text-align: center; margin-bottom: 20px; color: #888; }
        .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 15px; }
        .card {
            background: #16213e;
            border: 2px solid #333;
            border-radius: 10px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.2s;
        }
        .card:hover { border-color: #e94560; transform: scale(1.02); }
        .card.remove { border-color: #ef4444; opacity: 0.6; }
        .card.remove::after {
            content: "❌ RETIRER";
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(239,68,68,0.9);
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
        }
        .card { position: relative; }
        .card img { width: 100%; height: 180px; object-fit: cover; }
        .card .name { padding: 10px; font-weight: bold; }
        .card .size { padding: 0 10px 10px; font-size: 12px; color: #888; }
        .summary {
            position: fixed; bottom: 20px; right: 20px;
            background: #0f0f1a; border: 2px solid #e94560;
            padding: 15px; border-radius: 10px;
        }
        .summary button {
            margin-top: 10px; width: 100%; padding: 10px;
            background: #e94560; color: #fff; border: none;
            border-radius: 5px; cursor: pointer; font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>🎮 STAGES - Clique pour marquer à retirer</h1>
    <p class="info">""" + f"{len(stages_info)} stages - Clique sur ceux à supprimer puis 'Exporter'" + """</p>
    <div class="gallery">
"""

    for stage in stages_info:
        img_file = stage.get('img_file', 'placeholder.png')
        size_mb = stage.get('size_mb', 0)

        html += f'''
        <div class="card" data-name="{stage['def_file']}" onclick="toggle(this)">
            <img src="{img_file}" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 200%22><rect fill=%22%231a1a2e%22 width=%22400%22 height=%22200%22/><text x=%22200%22 y=%22100%22 fill=%22%23e94560%22 text-anchor=%22middle%22>{stage["name"][:20]}</text></svg>'">
            <div class="name">{stage['name']}</div>
            <div class="size">{size_mb:.1f} MB</div>
        </div>
'''

    html += """
    </div>
    <div class="summary">
        <div>A retirer: <span id="count" style="color:#ef4444">0</span></div>
        <button onclick="exportList()">📋 Exporter la liste</button>
    </div>
    <script>
        let toRemove = new Set();
        function toggle(el) {
            const name = el.dataset.name;
            if (toRemove.has(name)) {
                toRemove.delete(name);
                el.classList.remove('remove');
            } else {
                toRemove.add(name);
                el.classList.add('remove');
            }
            document.getElementById('count').textContent = toRemove.size;
        }
        function exportList() {
            const list = Array.from(toRemove);
            if (list.length === 0) {
                alert('Aucun stage selectionne!');
                return;
            }
            navigator.clipboard.writeText(list.join('\\n'));
            alert('Copie! ' + list.length + ' stages:\\n\\n' + list.join('\\n'));
        }
    </script>
</body>
</html>
"""
    return html

def main():
    print("=" * 60)
    print("  KOF ULTIMATE ONLINE - SFF IMAGE EXTRACTOR")
    print("=" * 60)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Find all stage .def files
    def_files = [f for f in sorted(STAGES_DIR.glob("*.def")) if 'backup' not in f.name.lower()]
    print(f"\nFound {len(def_files)} stages\n")

    stages_info = []
    extracted = 0
    failed = 0

    for def_path in def_files:
        stage_name = def_path.stem
        sff_path = STAGES_DIR / f"{stage_name}.sff"
        output_path = OUTPUT_DIR / f"{stage_name}.png"

        print(f"Processing: {stage_name}")

        stage_data = {
            'name': stage_name,
            'def_file': def_path.name,
            'size_mb': 0,
            'img_file': f"{stage_name}.png"
        }

        if sff_path.exists():
            stage_data['size_mb'] = sff_path.stat().st_size / (1024 * 1024)

            if output_path.exists():
                print(f"    Already extracted, skipping")
                extracted += 1
            else:
                # Try SFF v2 first
                if extract_sff_v2(sff_path, output_path):
                    extracted += 1
                elif extract_sff_v1(sff_path, output_path):
                    extracted += 1
                else:
                    print(f"    Could not extract, creating placeholder")
                    create_placeholder(stage_name, output_path)
                    failed += 1
        else:
            print(f"    No SFF file found")
            create_placeholder(stage_name, output_path)
            failed += 1

        stages_info.append(stage_data)

    print(f"\n{'=' * 60}")
    print(f"  Extracted: {extracted}")
    print(f"  Failed/Placeholder: {failed}")

    # Generate HTML gallery
    html = generate_html_gallery(stages_info)
    html_path = OUTPUT_DIR / "STAGE_GALLERY.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n  Gallery: {html_path}")
    print("=" * 60)

    # Try to open
    try:
        os.startfile(str(html_path))
    except:
        print(f"\nOuvre: {html_path}")

if __name__ == "__main__":
    main()
