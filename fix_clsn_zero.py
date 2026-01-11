#!/usr/bin/env python3
"""Fix Clsn1: 0 and Clsn2: 0 errors in .air files"""
import re
from pathlib import Path

CHARS_PATH = Path(r"D:\KOF Ultimate Online kofuo\chars")

def fix_air_file(air_path):
    """Remove invalid Clsn1: 0 and Clsn2: 0 lines"""
    try:
        content = air_path.read_text(encoding='utf-8', errors='ignore')
    except:
        try:
            content = air_path.read_text(encoding='latin-1')
        except:
            return 0

    original = content

    # Pattern: Clsn1: 0 or Clsn2: 0 followed by a newline (not followed by Clsn definition)
    # We remove lines that say "Clsn1: 0" or "Clsn2: 0" when they're not followed by actual box definitions

    lines = content.split('\n')
    new_lines = []
    fixes = 0

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check if this is a Clsn: 0 line
        if re.match(r'^Clsn[12]:\s*0\s*$', line, re.IGNORECASE):
            # Check next non-empty line
            next_line = ""
            for j in range(i + 1, min(i + 3, len(lines))):
                if lines[j].strip():
                    next_line = lines[j].strip()
                    break

            # If next line is NOT a Clsn[x] = ... definition, skip this line
            if not re.match(r'^Clsn[12]\[\d+\]', next_line, re.IGNORECASE):
                fixes += 1
                i += 1
                continue

        new_lines.append(lines[i])
        i += 1

    if fixes > 0:
        new_content = '\n'.join(new_lines)
        air_path.write_text(new_content, encoding='utf-8')

    return fixes

def main():
    print("Scanning .air files for Clsn: 0 errors...")

    total_fixes = 0
    files_fixed = 0

    for air_file in CHARS_PATH.rglob("*.air"):
        fixes = fix_air_file(air_file)
        if fixes > 0:
            print(f"  ✓ {air_file.name}: {fixes} fixes")
            total_fixes += fixes
            files_fixed += 1

    print(f"\n✅ Total: {total_fixes} fixes in {files_fixed} files")

if __name__ == "__main__":
    main()
