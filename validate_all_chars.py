import os
import re

chars_dir = "D:/KOF Ultimate Online/chars"
select_def = "D:/KOF Ultimate Online/Ikemen_GO/data/select.def"

print("=" * 60)
print("VALIDATION COMPLETE DES PERSONNAGES")
print("=" * 60)

# Lire le select.def
with open(select_def, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

broken_chars = []
valid_chars = []

for i, line in enumerate(lines):
    line = line.strip()
    # Skip comments and empty lines
    if not line or line.startswith(';') or line.startswith('['):
        continue

    # Extract character name
    char_name = line.split(',')[0].strip()
    if not char_name:
        continue

    char_path = os.path.join(chars_dir, char_name)

    # Check if directory exists
    if not os.path.isdir(char_path):
        broken_chars.append((i+1, char_name, "Dossier manquant"))
        continue

    # Check for .def file
    def_file = os.path.join(char_path, f"{char_name}.def")
    if not os.path.exists(def_file):
        # Try to find any .def file
        def_files = [f for f in os.listdir(char_path) if f.endswith('.def')]
        if not def_files:
            broken_chars.append((i+1, char_name, "Pas de fichier .def"))
            continue

    # Check for .sff file
    sff_files = [f for f in os.listdir(char_path) if f.endswith('.sff')]
    if not sff_files:
        broken_chars.append((i+1, char_name, "Pas de fichier .sff"))
        continue

    # Check for .air file
    air_files = [f for f in os.listdir(char_path) if f.endswith('.air')]
    if not air_files:
        broken_chars.append((i+1, char_name, "Pas de fichier .air"))
        continue

    valid_chars.append(char_name)

print(f"\nPersonnages valides: {len(valid_chars)}")
print(f"Personnages casses: {len(broken_chars)}")

if broken_chars:
    print("\n" + "=" * 60)
    print("PERSONNAGES A DESACTIVER:")
    print("=" * 60)
    for line_num, name, reason in broken_chars:
        print(f"  Ligne {line_num}: {name} - {reason}")

    # Fix the select.def
    print("\nCorrection du select.def...")

    with open(select_def, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    fixed = 0
    for _, name, _ in broken_chars:
        # Comment out broken characters
        pattern = rf'^({re.escape(name)},)'
        replacement = f';{name},'
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        if new_content != content:
            content = new_content
            fixed += 1

    with open(select_def, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Desactive {fixed} personnages casses")

print("\n" + "=" * 60)
print("VALIDATION TERMINEE")
print("=" * 60)
