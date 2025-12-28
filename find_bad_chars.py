import os
import subprocess
import time
import shutil

select_def = "D:/KOF Ultimate Online/Ikemen_GO/data/select.def"
backup_def = "D:/KOF Ultimate Online/Ikemen_GO/data/select_full_backup.def"
chars_dir = "D:/KOF Ultimate Online/chars"
ikemen = "D:/KOF Ultimate Online/Ikemen_GO/Ikemen_GO.exe"

# Backup original
shutil.copy(select_def, backup_def)

# Read all active characters
with open(select_def, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

lines = content.split('\n')
chars = []
for line in lines:
    line = line.strip()
    if not line or line.startswith(';') or line.startswith('['):
        continue
    if 'stages/' not in line.lower():
        continue
    char_name = line.split(',')[0].strip()
    if char_name and os.path.isdir(os.path.join(chars_dir, char_name)):
        chars.append(char_name)

print(f"Found {len(chars)} characters to test")

# Test first 10 characters
test_chars = chars[:10]
print(f"Testing first 10: {test_chars}")

select_content = """; TEST SELECT.DEF

[Characters]
"""
for c in test_chars:
    select_content += f"{c}, stages/Abyss-Rugal-Palace.def\n"

select_content += """
[ExtraStages]
stages/Abyss-Rugal-Palace.def

[Stages]
stages/Abyss-Rugal-Palace.def

[Options]
arcade.rematches = 0
team.loseondraw = 1
"""

with open(select_def, 'w', encoding='utf-8') as f:
    f.write(select_content)

print("Testing with 10 characters...")
print("Launch the game manually and check if it works!")
print(f"\nCharacters being tested:")
for i, c in enumerate(test_chars, 1):
    print(f"  {i}. {c}")
