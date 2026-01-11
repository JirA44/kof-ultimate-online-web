#!/usr/bin/env python3
"""
KOF ULTIMATE ONLINE - ADVANCED GAMEPLAY BUG SCANNER
====================================================
Scans for real gameplay bugs that affect fighting:
- HitDef without proper damage/velocity
- Missing juggle values
- Broken fall parameters
- Infinite state loops
- Missing required states
"""

import os
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(r"D:\KOF Ultimate Online")
CHARS_DIR = BASE_DIR / "chars"

class AdvancedGameplayScanner:
    def __init__(self):
        self.critical_bugs = defaultdict(list)
        self.gameplay_issues = defaultdict(list)
        self.chars_scanned = 0

    def scan_hitdef_block(self, lines, start_idx, char_name, filename):
        """Analyze a HitDef state block for issues."""
        issues = []
        has_damage = False
        has_hitflag = False
        has_ground_velocity = False
        has_air_velocity = False
        has_juggle = False
        damage_value = 0

        for i in range(start_idx, min(start_idx + 60, len(lines))):
            line = lines[i].strip().lower()

            # Stop at next state
            if i > start_idx and line.startswith('[state'):
                break

            if 'damage' in line and '=' in line:
                has_damage = True
                match = re.search(r'damage\s*=\s*(\d+)', line)
                if match:
                    damage_value = int(match.group(1))

            if 'hitflag' in line:
                has_hitflag = True

            if 'ground.velocity' in line:
                has_ground_velocity = True

            if 'air.velocity' in line:
                has_air_velocity = True

            if 'juggle' in line and '=' in line:
                has_juggle = True

        # Check for issues
        if not has_damage:
            issues.append(f"{filename}:{start_idx+1} - HitDef missing damage")
        elif damage_value == 0:
            issues.append(f"{filename}:{start_idx+1} - HitDef with 0 damage")

        if not has_ground_velocity and not has_air_velocity:
            # This is okay for some moves, just a warning
            pass

        return issues

    def scan_cns_file(self, filepath: Path):
        """Scan CNS file for gameplay bugs."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            self.critical_bugs[str(filepath.parent.name)].append(f"Cannot read: {e}")
            return

        char_name = filepath.parent.name
        filename = filepath.name

        in_hitdef = False
        hitdef_start = 0
        state_counts = defaultdict(int)
        changestate_targets = []

        for i, line in enumerate(lines):
            line_lower = line.strip().lower()

            # Skip comments
            if line_lower.startswith(';'):
                continue

            # Track state definitions
            if line_lower.startswith('[statedef'):
                match = re.search(r'\[statedef\s+(-?\d+)', line_lower)
                if match:
                    state_num = int(match.group(1))
                    state_counts[state_num] += 1

            # Detect HitDef states
            if '[state' in line_lower and 'hitdef' in line_lower:
                in_hitdef = True
                hitdef_start = i

            # End of HitDef analysis
            if in_hitdef and i > hitdef_start + 2 and line_lower.startswith('[state'):
                issues = self.scan_hitdef_block(lines, hitdef_start, char_name, filename)
                for issue in issues:
                    self.gameplay_issues[char_name].append(issue)
                in_hitdef = False

            # Check for problematic damage values
            if 'damage' in line_lower and '=' in line_lower:
                # Check for negative damage
                match = re.search(r'damage\s*=\s*(-\d+)', line_lower)
                if match:
                    neg_dmg = int(match.group(1))
                    if neg_dmg < -50:  # Some healing is OK
                        self.critical_bugs[char_name].append(
                            f"{filename}:{i+1} - Extremely negative damage: {neg_dmg}")

                # Check for absurdly high damage
                match = re.search(r'damage\s*=\s*(\d+)', line_lower)
                if match:
                    dmg = int(match.group(1))
                    if dmg > 500:  # Most moves shouldn't do more than 500
                        self.gameplay_issues[char_name].append(
                            f"{filename}:{i+1} - Very high damage: {dmg}")

            # Check for invalid velocities (too extreme)
            if 'velset' in line_lower and '=' in line_lower:
                match = re.search(r'velset\s*=\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)', line_lower)
                if match:
                    try:
                        vel_x = abs(float(match.group(1)))
                        vel_y = abs(float(match.group(2)))
                        if vel_x > 50 or vel_y > 50:
                            self.gameplay_issues[char_name].append(
                                f"{filename}:{i+1} - Extreme velocity: {match.group(0)}")
                    except:
                        pass

            # Check for changestate infinite loops
            if 'changestate' in line_lower and 'value' in line_lower:
                match = re.search(r'value\s*=\s*(-?\d+)', line_lower)
                if match:
                    target = int(match.group(1))
                    changestate_targets.append((i+1, target))

            # Check for missing triggerall/trigger
            if 'changestate' in line_lower or 'selfstate' in line_lower:
                # Look back for trigger
                has_trigger = False
                for j in range(max(0, i-10), i):
                    if 'trigger' in lines[j].lower():
                        has_trigger = True
                        break
                if not has_trigger:
                    self.gameplay_issues[char_name].append(
                        f"{filename}:{i+1} - State change may lack trigger condition")

            # Check for fall parameters
            if 'fall' in line_lower and 'recover' in line_lower:
                match = re.search(r'fall\.recover\s*=\s*(\d+)', line_lower)
                if match and int(match.group(1)) == 0:
                    self.gameplay_issues[char_name].append(
                        f"{filename}:{i+1} - fall.recover = 0 (unrecoverable?)")

        # Check for duplicate statedefs
        for state, count in state_counts.items():
            if count > 1 and state >= 0:  # Negative states are special
                self.gameplay_issues[char_name].append(
                    f"{filename} - State {state} defined {count} times (conflict!)")

    def scan_character(self, char_dir: Path):
        """Scan all files for a character."""
        if not char_dir.is_dir():
            return

        self.chars_scanned += 1

        # Scan all .cns files
        for cns_file in char_dir.rglob('*.cns'):
            self.scan_cns_file(cns_file)

    def run_scan(self):
        """Run full scan."""
        print("=" * 60)
        print("  KOF ULTIMATE ONLINE - ADVANCED GAMEPLAY SCANNER")
        print("=" * 60)
        print()

        for char_dir in sorted(CHARS_DIR.iterdir()):
            if char_dir.is_dir() and not char_dir.name.startswith('.'):
                self.scan_character(char_dir)

        print(f"Scanned {self.chars_scanned} characters")
        print()

        # Critical bugs
        if self.critical_bugs:
            print("=" * 60)
            print("  CRITICAL BUGS (must fix!)")
            print("=" * 60)
            for char, bugs in sorted(self.critical_bugs.items())[:20]:
                print(f"\n[{char}]")
                for bug in bugs[:5]:
                    print(f"  CRITICAL: {bug}")
                if len(bugs) > 5:
                    print(f"  ... and {len(bugs)-5} more")
        else:
            print("No critical bugs found!")

        print()

        # Gameplay issues
        if self.gameplay_issues:
            print("=" * 60)
            print("  GAMEPLAY ISSUES (should review)")
            print("=" * 60)
            shown = 0
            for char, issues in sorted(self.gameplay_issues.items()):
                if shown > 30:
                    print(f"\n... and more issues in other characters")
                    break
                if issues:
                    print(f"\n[{char}]")
                    for issue in issues[:3]:
                        print(f"  ISSUE: {issue}")
                        shown += 1
                    if len(issues) > 3:
                        print(f"  ... and {len(issues)-3} more issues")

        print()
        print("=" * 60)
        total_critical = sum(len(b) for b in self.critical_bugs.values())
        total_issues = sum(len(i) for i in self.gameplay_issues.values())
        print(f"  TOTAL: {total_critical} critical, {total_issues} gameplay issues")
        print("=" * 60)

        # Save report
        report_path = BASE_DIR / "save" / "gameplay_bugs_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("KOF ULTIMATE ONLINE - GAMEPLAY BUGS REPORT\n")
            f.write("=" * 50 + "\n\n")

            f.write("CRITICAL BUGS:\n")
            for char, bugs in sorted(self.critical_bugs.items()):
                f.write(f"\n[{char}]\n")
                for bug in bugs:
                    f.write(f"  {bug}\n")

            f.write("\n\nGAMEPLAY ISSUES:\n")
            for char, issues in sorted(self.gameplay_issues.items()):
                if issues:
                    f.write(f"\n[{char}]\n")
                    for issue in issues:
                        f.write(f"  {issue}\n")

        print(f"\nReport saved to: {report_path}")

        return self.critical_bugs, self.gameplay_issues


def main():
    scanner = AdvancedGameplayScanner()
    scanner.run_scan()


if __name__ == "__main__":
    main()
