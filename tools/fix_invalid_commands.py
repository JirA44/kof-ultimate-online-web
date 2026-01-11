#!/usr/bin/env python3
"""Fix invalid command references in character files"""

import os
import re
from pathlib import Path

BASE_DIR = Path(r"D:\KOF Ultimate Online")
CHARS_DIR = BASE_DIR / "chars"

# Invalid commands to fix
INVALID_COMMANDS = {
    '"SEE"': '"a"',  # Replace SEE with button a
    '"see"': '"a"',
}

def fix_file(filepath):
    """Fix invalid commands in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return 0, str(e)

    original = content
    fixed_count = 0

    for invalid, valid in INVALID_COMMANDS.items():
        if invalid in content:
            count = content.count(invalid)
            content = content.replace(invalid, valid)
            fixed_count += count

    if fixed_count > 0:
        try:
            with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(content)
        except Exception as e:
            return 0, str(e)

    return fixed_count, None

def main():
    print("=" * 50)
    print("  FIXING INVALID COMMAND REFERENCES")
    print("=" * 50)

    total_fixed = 0
    files_fixed = 0

    for cns_file in CHARS_DIR.rglob('*.cns'):
        fixed, error = fix_file(cns_file)
        if error:
            print(f"Error: {cns_file}: {error}")
        elif fixed > 0:
            print(f"Fixed {fixed} in {cns_file.parent.name}/{cns_file.name}")
            total_fixed += fixed
            files_fixed += 1

    print()
    print(f"TOTAL: {total_fixed} invalid commands fixed in {files_fixed} files")

if __name__ == "__main__":
    main()
