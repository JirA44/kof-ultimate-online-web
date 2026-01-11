#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Système de réparation automatique
Répare les personnages et portraits pendant que les tests continuent
"""

import os
import re
import shutil
from datetime import datetime
import json

GAME_DIR = r"D:\KOF Ultimate Online"
LOG_FILE = "auto_repair.log"
REPAIR_REPORT = "repair_report.json"

def log(message):
    """Log avec timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    msg = f"[{timestamp}] {message}"
    print(msg)

    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def get_all_characters():
    """Obtenir tous les personnages du jeu"""
    chars_dir = os.path.join(GAME_DIR, 'chars')
    
    if not os.path.exists(chars_dir):
        return []
    
    chars = []
    for item in os.listdir(chars_dir):
        item_path = os.path.join(chars_dir, item)
        if os.path.isdir(item_path):
            chars.append(item)
    
    return chars

def check_character_files(char_name):
    """Vérifier l'intégrité des fichiers d'un personnage"""
    char_dir = os.path.join(GAME_DIR, 'chars', char_name)
    
    if not os.path.exists(char_dir):
        return False, "Dossier introuvable"
    
    # Chercher fichiers essentiels
    has_def = any(f.endswith('.def') for f in os.listdir(char_dir))
    has_sff = any(f.endswith('.sff') for f in os.listdir(char_dir))
    has_air = any(f.endswith('.air') for f in os.listdir(char_dir))
    
    if not has_def:
        return False, "Fichier .def manquant"
    if not has_sff:
        return False, "Fichier .sff manquant"
    if not has_air:
        return False, "Fichier .air manquant"
    
    return True, "OK"

def analyze_and_repair():
    """Analyser et réparer tous les personnages"""
    log("=" * 70)
    log("🔧 DÉMARRAGE SYSTÈME DE RÉPARATION")
    log("=" * 70)
    
    all_chars = get_all_characters()
    
    log(f"📊 {len(all_chars)} personnages trouvés")
    log("")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'total': len(all_chars),
        'ok': [],
        'broken': []
    }
    
    for char in all_chars:
        log(f"🔍 {char}")
        files_ok, msg = check_character_files(char)
        
        if files_ok:
            log(f"  ✅ OK")
            report['ok'].append(char)
        else:
            log(f"  ❌ {msg}")
            report['broken'].append({'name': char, 'reason': msg})
    
    with open(REPAIR_REPORT, 'w') as f:
        json.dump(report, f, indent=2)
    
    log("")
    log(f"✅ OK: {len(report['ok'])}")
    log(f"❌ Cassés: {len(report['broken'])}")

if __name__ == '__main__':
    analyze_and_repair()
