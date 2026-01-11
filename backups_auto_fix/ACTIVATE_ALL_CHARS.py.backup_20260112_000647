#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Réactiver tous les personnages dans select.def
"""

import os
import shutil
from datetime import datetime

SELECT_PATH = r"D:\KOF Ultimate Online\data\select.def"
BACKUP_PATH = f"D:\KOF Ultimate Online\data\select.def.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Backup
shutil.copy2(SELECT_PATH, BACKUP_PATH)
print(f"✅ Backup: {BACKUP_PATH}")

# Lire le fichier
with open(SELECT_PATH, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Réactiver tous les personnages (enlever les commentaires)
new_lines = []
in_characters_section = False
reactivated = 0

for line in lines:
    stripped = line.strip()
    
    # Détecter section [Characters]
    if stripped == '[Characters]':
        in_characters_section = True
        new_lines.append(line)
        continue
    
    # Fin de section
    if stripped.startswith('[') and in_characters_section:
        in_characters_section = False
    
    # Réactiver les lignes commentées dans [Characters]
    if in_characters_section and stripped.startswith(';'):
        # Vérifier si c'est un personnage commenté
        uncommented = stripped[1:].strip()
        if ',' in uncommented and not uncommented.startswith('='):
            # C'est un personnage, le réactiver
            new_lines.append(uncommented + '\n')
            reactivated += 1
            print(f"✅ Réactivé: {uncommented.split(',')[0]}")
        else:
            # Commentaire normal, garder
            new_lines.append(line)
    else:
        new_lines.append(line)

# Sauvegarder
with open(SELECT_PATH, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"\n📊 {reactivated} personnages réactivés")
print(f"💾 Backup: {BACKUP_PATH}")
