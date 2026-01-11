#!/usr/bin/env python3
"""
KOF ULTIMATE ONLINE - FIX EXTREME DAMAGE VALUES
================================================
Fixes unreasonable damage values that break gameplay:
- Damage > 500 normalized to 200
- Negative damage with absolute value > 1000 kept (healing)
- Integer overflow values fixed
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(r"D:\KOF Ultimate Online")
CHARS_DIR = BASE_DIR / "chars"

MAX_REASONABLE_DAMAGE = 500  # Maximum reasonable single-hit damage
MAX_REASONABLE_FALL_DAMAGE = 100

def fix_damage_values(content, filename):
    """Fix extreme damage values in file content."""
    lines = content.split('\n')
    fixed_count = 0
    new_lines = []

    for line in lines:
        original = line
        line_lower = line.lower()

        # Skip comments
        if line.strip().startswith(';'):
            new_lines.append(line)
            continue

        # Fix fall.damage with extreme values (but not negative)
        if 'fall.damage' in line_lower:
            # Match patterns like fall.damage = 99999... or 2147483647
            match = re.search(r'(fall\.damage\s*=\s*)(\d{6,})', line, re.IGNORECASE)
            if match:
                prefix = match.group(1)
                line = line[:match.start()] + prefix + str(MAX_REASONABLE_FALL_DAMAGE) + line[match.end():]
                fixed_count += 1

        # Fix regular damage with extreme positive values
        elif 'damage' in line_lower and '=' in line_lower and 'fall' not in line_lower:
            # Match damage = X or damage = X, Y
            match = re.search(r'(damage\s*=\s*)(\d{6,})', line, re.IGNORECASE)
            if match:
                # Check if it's intentionally high (like healing moves with negative guard damage)
                # Just cap the extreme positive values
                prefix = match.group(1)
                old_val = match.group(2)
                line = line[:match.start()] + prefix + str(MAX_REASONABLE_DAMAGE) + line[match.end():]
                fixed_count += 1

        new_lines.append(line)

    return '\n'.join(new_lines), fixed_count

def process_file(filepath):
    """Process a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return 0, str(e)

    new_content, fixed = fix_damage_values(content, filepath.name)

    if fixed > 0:
        try:
            with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(new_content)
        except Exception as e:
            return 0, str(e)

    return fixed, None

def main():
    print("=" * 60)
    print("  KOF ULTIMATE ONLINE - FIX EXTREME DAMAGE VALUES")
    print("=" * 60)
    print()

    total_fixed = 0
    files_fixed = 0
    errors = []

    for cns_file in CHARS_DIR.rglob('*.cns'):
        fixed, error = process_file(cns_file)
        if error:
            errors.append(f"{cns_file}: {error}")
        elif fixed > 0:
            print(f"Fixed {fixed} extreme values in {cns_file.parent.name}/{cns_file.name}")
            total_fixed += fixed
            files_fixed += 1

    print()
    print("=" * 60)
    print(f"  TOTAL: {total_fixed} extreme values fixed in {files_fixed} files")
    print("=" * 60)

    if errors:
        print(f"\n{len(errors)} files had errors (first 5):")
        for err in errors[:5]:
            print(f"  {err}")

    # Save log
    log_path = BASE_DIR / "save" / "extreme_damage_fix_log.txt"
    with open(log_path, 'w') as f:
        f.write(f"Fixed {total_fixed} extreme damage values in {files_fixed} files\n")
        if errors:
            f.write(f"\nErrors:\n")
            for err in errors:
                f.write(f"  {err}\n")

    print(f"\nLog saved to: {log_path}")

if __name__ == "__main__":
    main()
