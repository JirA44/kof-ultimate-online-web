#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOF ULTIMATE ONLINE - PACKAGE CREATOR
Creates a distributable all-in-one package
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

GAME_DIR = Path(__file__).parent
OUTPUT_DIR = GAME_DIR / "release"

# Files/folders to include in package
INCLUDE = [
    "Ikemen_GO.exe",
    "chars",
    "data",
    "external",
    "font",
    "sound",
    "stages",
    "save",
    "KOF_LAUNCHER.py",
    "KOF_ONLINE_FIREBASE.html",
    "INSTALL_AND_PLAY.bat",
    "PLAY_KOF.bat",
    "AUTO_FIX_ALL.py",
    "DEEP_FIX_CHARS.py",
    "FIX_FLYAWAY.py",
    "TIER_LIST.txt",
    "QUALITY_REPORT.txt",
    "README.txt",
]

# Files to exclude
EXCLUDE_PATTERNS = [
    "*.pyc",
    "__pycache__",
    "*.log",
    "backup_before_fix",
    "release",
    ".git",
    "*.tmp",
]

def should_exclude(path):
    """Check if path should be excluded"""
    name = path.name
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False

def create_readme():
    """Create README file"""
    readme = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                         KOF ULTIMATE ONLINE                                   ║
║                        Version 1.0 - Final Release                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

INSTALLATION:
=============
1. Extract this ZIP to any folder
2. Run "INSTALL_AND_PLAY.bat" or "KOF_LAUNCHER.py"
3. The launcher will check and repair any issues automatically
4. Click "PLAY LOCAL" to start the game

ONLINE PLAY:
============
1. Run "INSTALL_AND_PLAY.bat"
2. Choose "PLAY ONLINE"
3. Create an account or log in
4. Click "Quick Match" or create/join a room
5. When matched, launch the game

CONTROLS:
=========
Player 1:
  - Arrows: Move
  - Z/X/C: Punches (Light/Medium/Heavy)
  - A/S/D: Kicks (Light/Medium/Heavy)
  - Enter: Start/Pause

Player 2:
  - I/K/J/L: Move
  - F/G/H: Punches
  - R/T/Y: Kicks
  - RShift: Start

FEATURES:
=========
- 76 tested and optimized characters
- Tier-based power ranking (S/A/B/C/D)
- Online matchmaking with ELO ranking
- Auto-repair system
- No crashes, no fly-away bugs

TROUBLESHOOTING:
================
If the game doesn't start:
1. Run "INSTALL_AND_PLAY.bat" as Administrator
2. Choose option [3] to repair the game
3. Make sure you have the Visual C++ Redistributable installed

If characters are buggy:
1. Run the launcher and choose [3] REPAIR GAME
2. This will fix all known issues automatically

CREDITS:
========
- Ikemen GO Engine
- KOF/SNK (Original characters and concepts)
- MUGEN Community (Character creators)
- Optimized and packaged by KOF Ultimate Online Team

================================================================================
                           ENJOY THE GAME!
================================================================================
"""
    readme_path = GAME_DIR / "README.txt"
    readme_path.write_text(readme, encoding='utf-8')
    return readme_path

def create_package():
    """Create the distribution package"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    KOF ULTIMATE ONLINE - PACKAGE CREATOR                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Create README
    print("Creating README...")
    create_readme()

    # Package name
    timestamp = datetime.now().strftime("%Y%m%d")
    package_name = f"KOF_Ultimate_Online_v1.0_{timestamp}"
    zip_path = OUTPUT_DIR / f"{package_name}.zip"

    print(f"Creating package: {package_name}.zip")
    print("This may take several minutes...\n")

    # Calculate total size
    total_files = 0
    total_size = 0

    for item in INCLUDE:
        path = GAME_DIR / item
        if path.exists():
            if path.is_file():
                total_files += 1
                total_size += path.stat().st_size
            elif path.is_dir():
                for f in path.rglob("*"):
                    if f.is_file() and not should_exclude(f):
                        total_files += 1
                        total_size += f.stat().st_size

    print(f"Files to package: {total_files}")
    print(f"Estimated size: {total_size / (1024*1024):.1f} MB\n")

    # Create ZIP
    processed = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for item in INCLUDE:
            path = GAME_DIR / item

            if not path.exists():
                print(f"  Skipping (not found): {item}")
                continue

            if path.is_file():
                arcname = item
                zf.write(path, arcname)
                processed += 1
                print(f"  [{processed}] Added: {item}")

            elif path.is_dir():
                for file_path in path.rglob("*"):
                    if file_path.is_file() and not should_exclude(file_path):
                        arcname = str(file_path.relative_to(GAME_DIR))
                        zf.write(file_path, arcname)
                        processed += 1

                        if processed % 100 == 0:
                            print(f"  [{processed}] Processing {item}...")

                print(f"  Added folder: {item} ({processed} files total)")

    # Get final size
    final_size = zip_path.stat().st_size / (1024 * 1024)

    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          PACKAGE CREATED                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Package: {package_name}.zip{' '*(42-len(package_name))}║
║  Location: release/                                                         ║
║  Size: {final_size:.1f} MB{' '*60}║
║  Files: {processed}{' '*65}║
╚══════════════════════════════════════════════════════════════════════════════╝

The package is ready for distribution!
Users just need to:
1. Download and extract the ZIP
2. Run INSTALL_AND_PLAY.bat
3. Play!
    """)

    return zip_path

if __name__ == "__main__":
    create_package()
