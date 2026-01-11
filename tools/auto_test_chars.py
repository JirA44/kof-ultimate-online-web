#!/usr/bin/env python3
"""
KOF ULTIMATE ONLINE - AUTO CHARACTER TESTER
============================================
Scans character files for common bugs:
- Damage syntax errors
- Invalid state definitions
- Missing animations
- Hitbox issues
- Command errors
"""

import os
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(r"D:\KOF Ultimate Online")
CHARS_DIR = BASE_DIR / "chars"

class CharacterTester:
    def __init__(self):
        self.errors = defaultdict(list)
        self.warnings = defaultdict(list)
        self.chars_tested = 0

    def scan_cns_file(self, filepath: Path):
        """Scan a .cns file for common errors."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            self.errors[str(filepath)].append(f"Cannot read file: {e}")
            return

        char_name = filepath.parent.name
        filename = filepath.name

        for i, line in enumerate(lines, 1):
            line_stripped = line.strip().lower()

            # Skip comments and empty lines
            if line_stripped.startswith(';') or not line_stripped:
                continue

            # Check for damage syntax errors (3 values instead of 2)
            if 'damage' in line_stripped and '=' in line_stripped:
                # Pattern: damage = X, 0 +/- something, Y (wrong)
                if re.search(r'damage\s*=\s*\d+\s*,\s*0\s*[+\-*/]', line_stripped):
                    self.errors[char_name].append(f"{filename}:{i} - Damage syntax error: {line.strip()[:60]}")
                # Pattern: damage = X, floor(...), Y (wrong - 3 values)
                elif re.search(r'damage\s*=\s*\d+\s*,\s*floor\s*\(', line_stripped):
                    self.errors[char_name].append(f"{filename}:{i} - Damage with floor() may have 3 values: {line.strip()[:60]}")

            # Check for invalid velset values
            if 'velset' in line_stripped and '=' in line_stripped:
                match = re.search(r'velset\s*=\s*([^;]+)', line_stripped)
                if match:
                    values = match.group(1).split(',')
                    if len(values) > 2:
                        self.warnings[char_name].append(f"{filename}:{i} - VelSet has {len(values)} values (expected 2)")

            # Check for invalid posset values
            if 'posset' in line_stripped and '=' in line_stripped:
                match = re.search(r'posset\s*=\s*([^;]+)', line_stripped)
                if match:
                    values = match.group(1).split(',')
                    if len(values) > 2:
                        self.warnings[char_name].append(f"{filename}:{i} - PosSet has {len(values)} values (expected 2)")

            # Check for changestate without value
            if 'changestate' in line_stripped and 'value' not in line_stripped:
                if '[state' not in line_stripped:
                    self.warnings[char_name].append(f"{filename}:{i} - ChangeState may be missing value")

            # Check for hitdef without damage
            if '[state' in line_stripped and 'hitdef' in line_stripped:
                # Look ahead for damage in this state
                found_damage = False
                for j in range(i, min(i+30, len(lines))):
                    if '[state' in lines[j].lower() and j > i:
                        break
                    if 'damage' in lines[j].lower():
                        found_damage = True
                        break
                if not found_damage:
                    self.warnings[char_name].append(f"{filename}:{i} - HitDef state may be missing damage")

            # Check for invalid anim numbers (negative or very high)
            if 'anim' in line_stripped and '=' in line_stripped:
                match = re.search(r'anim\s*=\s*(-?\d+)', line_stripped)
                if match:
                    anim_num = int(match.group(1))
                    if anim_num < 0:
                        self.errors[char_name].append(f"{filename}:{i} - Negative anim number: {anim_num}")
                    elif anim_num > 50000:
                        self.warnings[char_name].append(f"{filename}:{i} - Very high anim number: {anim_num}")

            # Check for statetype errors
            if 'statetype' in line_stripped and '=' in line_stripped:
                match = re.search(r'statetype\s*=\s*(\w+)', line_stripped)
                if match:
                    stype = match.group(1).upper()
                    if stype not in ['S', 'C', 'A', 'L', 'U']:
                        self.errors[char_name].append(f"{filename}:{i} - Invalid statetype: {stype}")

            # Check for physics errors
            if 'physics' in line_stripped and '=' in line_stripped:
                match = re.search(r'physics\s*=\s*(\w+)', line_stripped)
                if match:
                    physics = match.group(1).upper()
                    if physics not in ['S', 'C', 'A', 'N', 'U']:
                        self.errors[char_name].append(f"{filename}:{i} - Invalid physics: {physics}")

            # Check for corrupted characters (encoding issues)
            if re.search(r'[\x80-\xff]{3,}', line):
                self.warnings[char_name].append(f"{filename}:{i} - Possible encoding corruption")

    def scan_cmd_file(self, filepath: Path):
        """Scan a .cmd file for command errors."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            self.errors[str(filepath)].append(f"Cannot read file: {e}")
            return

        char_name = filepath.parent.name
        filename = filepath.name

        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Check for corrupted command names
            if 'name' in line_stripped.lower() and '=' in line_stripped:
                if re.search(r'[\x80-\xff]', line_stripped):
                    self.errors[char_name].append(f"{filename}:{i} - Corrupted command name: {line.strip()[:40]}")

            # Check for invalid command time
            if 'command.time' in line_stripped.lower():
                match = re.search(r'command\.time\s*=\s*(\d+)', line_stripped.lower())
                if match:
                    time_val = int(match.group(1))
                    if time_val > 300:
                        self.warnings[char_name].append(f"{filename}:{i} - Very high command.time: {time_val}")

    def scan_character(self, char_dir: Path):
        """Scan all files for a character."""
        if not char_dir.is_dir():
            return

        self.chars_tested += 1

        # Scan all .cns files
        for cns_file in char_dir.glob('*.cns'):
            self.scan_cns_file(cns_file)

        # Scan all .cmd files
        for cmd_file in char_dir.glob('*.cmd'):
            self.scan_cmd_file(cmd_file)

        # Also check subdirectories
        for subdir in char_dir.iterdir():
            if subdir.is_dir():
                for cns_file in subdir.glob('*.cns'):
                    self.scan_cns_file(cns_file)

    def run_full_scan(self):
        """Scan all characters."""
        print("=" * 60)
        print("  KOF ULTIMATE ONLINE - CHARACTER BUG SCANNER")
        print("=" * 60)
        print()

        for char_dir in CHARS_DIR.iterdir():
            if char_dir.is_dir() and not char_dir.name.startswith('.'):
                self.scan_character(char_dir)

        print(f"Scanned {self.chars_tested} characters")
        print()

        # Report errors
        if self.errors:
            print("=" * 60)
            print("  ERRORS FOUND (must fix)")
            print("=" * 60)
            for char, errs in sorted(self.errors.items()):
                print(f"\n[{char}]")
                for err in errs[:10]:  # Limit to 10 per char
                    print(f"  ERROR: {err}")
                if len(errs) > 10:
                    print(f"  ... and {len(errs) - 10} more errors")
        else:
            print("No critical errors found!")

        print()

        # Report warnings
        if self.warnings:
            print("=" * 60)
            print("  WARNINGS (should review)")
            print("=" * 60)
            warn_count = 0
            for char, warns in sorted(self.warnings.items()):
                if warn_count > 50:
                    print(f"\n... and more warnings in other characters")
                    break
                print(f"\n[{char}]")
                for warn in warns[:5]:
                    print(f"  WARN: {warn}")
                    warn_count += 1
                if len(warns) > 5:
                    print(f"  ... and {len(warns) - 5} more warnings")

        print()
        print("=" * 60)
        total_errors = sum(len(e) for e in self.errors.values())
        total_warnings = sum(len(w) for w in self.warnings.values())
        print(f"  TOTAL: {total_errors} errors, {total_warnings} warnings")
        print("=" * 60)

        return self.errors, self.warnings


def main():
    tester = CharacterTester()
    errors, warnings = tester.run_full_scan()

    # Save report
    report_path = BASE_DIR / "save" / "char_bug_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("KOF ULTIMATE ONLINE - CHARACTER BUG REPORT\n")
        f.write("=" * 50 + "\n\n")

        f.write("ERRORS:\n")
        for char, errs in sorted(errors.items()):
            f.write(f"\n[{char}]\n")
            for err in errs:
                f.write(f"  {err}\n")

        f.write("\n\nWARNINGS:\n")
        for char, warns in sorted(warnings.items()):
            f.write(f"\n[{char}]\n")
            for warn in warns:
                f.write(f"  {warn}\n")

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
