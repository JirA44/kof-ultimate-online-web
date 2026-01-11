#!/usr/bin/env python3
"""
Script to fix damage parameter syntax errors in MUGEN/IKEMEN character files.
Fixes patterns like: damage = 50, 0+something,10 -> damage = 50+something,10
Also handles spaces: damage = 50, 0 + something, 10 -> damage = 50 + something, 10
"""
import os
import re
import sys

CHARS_DIR = r"D:\KOF Ultimate Online\chars"

# Pattern 1: damage = X, 0[+-]something,Y  (3 values with no spaces)
PATTERN1 = re.compile(
    r'(damage\s*=\s*)(\d+),\s*0([+\-])([^,\n]+),\s*(\d+)',
    re.IGNORECASE
)

# Pattern 2: damage = X, 0 [+-] something, Y  (3 values with spaces)
PATTERN2 = re.compile(
    r'(damage\s*=\s*)(\d+),\s*0\s*([+\-])\s*([^,\n]+),\s*(\d+)',
    re.IGNORECASE
)

def fix_file(filepath):
    """Fix damage errors in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original = content

        # Replace pattern: damage = X, 0+Y,Z -> damage = X+Y,Z
        def replace_match(m):
            prefix = m.group(1)  # "damage = "
            first_num = m.group(2)  # first number
            operator = m.group(3)  # + or -
            expression = m.group(4).strip()  # the expression
            last_num = m.group(5)  # guard damage
            return f"{prefix}{first_num} {operator} {expression},{last_num}"

        content = PATTERN1.sub(replace_match, content)
        content = PATTERN2.sub(replace_match, content)

        if content != original:
            with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    fixed_count = 0
    file_count = 0

    for root, dirs, files in os.walk(CHARS_DIR):
        for filename in files:
            if filename.endswith(('.cns', '.st', '.cmd')):
                filepath = os.path.join(root, filename)
                if fix_file(filepath):
                    print(f"Fixed: {filepath}")
                    fixed_count += 1
                file_count += 1

    print(f"\nProcessed {file_count} files, fixed {fixed_count} files.")

if __name__ == "__main__":
    main()
