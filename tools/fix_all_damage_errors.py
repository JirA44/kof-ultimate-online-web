#!/usr/bin/env python3
"""
KOF ULTIMATE ONLINE - FIX ALL DAMAGE SYNTAX ERRORS
===================================================
Automatically fixes damage = X, 0 +/- Y patterns
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(r"D:\KOF Ultimate Online")
CHARS_DIR = BASE_DIR / "chars"

def fix_damage_line(line):
    """Fix damage syntax errors in a single line."""
    original = line

    # Pattern 1: damage = X, 0 + something -> damage = X + something
    # Example: damage = 36, 0 + var(8)*9 -> damage = 36 + var(8)*9
    pattern1 = r'(damage\s*=\s*)(\d+)\s*,\s*0\s*\+\s*'
    if re.search(pattern1, line, re.IGNORECASE):
        line = re.sub(pattern1, r'\1\2 + ', line, flags=re.IGNORECASE)

    # Pattern 2: damage = X, 0 - something -> damage = X - something
    pattern2 = r'(damage\s*=\s*)(\d+)\s*,\s*0\s*-\s*'
    if re.search(pattern2, line, re.IGNORECASE):
        line = re.sub(pattern2, r'\1\2 - ', line, flags=re.IGNORECASE)

    # Pattern 3: damage = X, 0 * something -> damage = X * something
    pattern3 = r'(damage\s*=\s*)(\d+)\s*,\s*0\s*\*\s*'
    if re.search(pattern3, line, re.IGNORECASE):
        line = re.sub(pattern3, r'\1\2 * ', line, flags=re.IGNORECASE)

    # Pattern 4: damage = X, 0 / something -> damage = X / something
    pattern4 = r'(damage\s*=\s*)(\d+)\s*,\s*0\s*/\s*'
    if re.search(pattern4, line, re.IGNORECASE):
        line = re.sub(pattern4, r'\1\2 / ', line, flags=re.IGNORECASE)

    # Pattern 5: damage = X, 0/(hitcount+1), Y -> damage = floor(X/(hitcount+1)), Y
    pattern5 = r'(damage\s*=\s*)(\d+)\s*,\s*0\s*/\s*\(hitcount\s*\+\s*1\)\s*,\s*(\d+)'
    if re.search(pattern5, line, re.IGNORECASE):
        line = re.sub(pattern5, r'\1floor(\2/(hitcount+1)), \3', line, flags=re.IGNORECASE)

    # Pattern 6: damage = X, floor(...), Y (3 values) -> damage = floor(...), Y
    # This is trickier - need to remove the first value
    pattern6 = r'(damage\s*=\s*)\d+\s*,\s*(floor\s*\([^)]+\))\s*,\s*(\d+)'
    if re.search(pattern6, line, re.IGNORECASE):
        line = re.sub(pattern6, r'\1\2, \3', line, flags=re.IGNORECASE)

    return line, line != original

def fix_file(filepath):
    """Fix all damage errors in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return 0, str(e)

    fixed_count = 0
    new_lines = []

    for line in lines:
        new_line, was_fixed = fix_damage_line(line)
        new_lines.append(new_line)
        if was_fixed:
            fixed_count += 1

    if fixed_count > 0:
        try:
            with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                f.writelines(new_lines)
        except Exception as e:
            return 0, str(e)

    return fixed_count, None

def main():
    print("=" * 60)
    print("  KOF ULTIMATE ONLINE - AUTO-FIX DAMAGE ERRORS")
    print("=" * 60)
    print()

    total_fixed = 0
    files_fixed = 0
    errors = []

    # Process all .cns files
    for cns_file in CHARS_DIR.rglob('*.cns'):
        fixed, error = fix_file(cns_file)
        if error:
            errors.append(f"{cns_file}: {error}")
        elif fixed > 0:
            print(f"Fixed {fixed} errors in {cns_file.name}")
            total_fixed += fixed
            files_fixed += 1

    print()
    print("=" * 60)
    print(f"  TOTAL: {total_fixed} errors fixed in {files_fixed} files")
    print("=" * 60)

    if errors:
        print(f"\n{len(errors)} files had errors:")
        for err in errors[:10]:
            print(f"  {err}")

    # Save log
    log_path = BASE_DIR / "save" / "damage_fix_log.txt"
    with open(log_path, 'w') as f:
        f.write(f"Fixed {total_fixed} damage errors in {files_fixed} files\n")
        if errors:
            f.write(f"\nErrors:\n")
            for err in errors:
                f.write(f"  {err}\n")

    print(f"\nLog saved to: {log_path}")


if __name__ == "__main__":
    main()
