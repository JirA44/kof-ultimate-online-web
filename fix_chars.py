import os
import glob
import re

chars_dir = 'Ikemen_GO/chars'
fixed = 0

for char_dir in os.listdir(chars_dir):
    char_path = os.path.join(chars_dir, char_dir)
    if os.path.isdir(char_path):
        def_files = glob.glob(os.path.join(char_path, '*.def'))
        for def_file in def_files:
            try:
                with open(def_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                original = content
                # Comment out stcommon=common1.cns lines
                content = re.sub(
                    r'^(\s*stcommon\s*=.*common1\.cns.*)$',
                    r'; \1 ; AUTO-FIXED',
                    content,
                    flags=re.MULTILINE | re.IGNORECASE
                )

                if content != original:
                    with open(def_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed += 1
                    print(f'Fixed: {char_dir}')
            except Exception as e:
                print(f'Error {char_dir}: {e}')

print(f'\nTotal fixed: {fixed} characters')
