import os
import re
import argparse

def update_file_imports(filepath, patterns):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated = False
    new_lines = []
    for i, line in enumerate(lines):
        original = line
        for pattern, repl in patterns.items():
            if re.search(pattern, line):
                print(f"DEBUG: Found match in {filepath}:{i+1} - '{line.strip()}'")
                line = re.sub(pattern, repl, line)
        if line != original:
            updated = True
        new_lines.append(line)

    if updated:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"[UPDATED] {filepath}")
    return updated


def walk_and_update(root, patterns, include_legacy=True, include_backup=True):
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip virtual environments and hidden directories
        if 'venv' in dirpath or any(part.startswith('.') and part != '.' for part in dirpath.split(os.sep)):
            continue
        # Skip app folder but allow root-level files
        if 'app' in dirpath.split(os.sep) and dirpath != root:
            continue  # skip the already-correct app folder
        if not include_legacy and 'modules' in dirpath.split(os.sep):
            continue
        if not include_backup and 'backup_old_structure' in dirpath.split(os.sep):
            continue
        for fname in filenames:
            if not fname.endswith('.py'):
                continue
            filepath = os.path.join(dirpath, fname)
            print(f"Processing: {filepath}")
            update_file_imports(filepath, patterns)


def main():
    parser = argparse.ArgumentParser(description="Auto-update legacy imports to use 'app.' namespace")
    parser.add_argument('--root', default='.', help='Root directory of the project')
    parser.add_argument('--no-legacy', action='store_true', help="Skip updating 'modules' legacy folders")
    parser.add_argument('--no-backup', action='store_true', help="Skip updating 'backup_old_structure' folder")
    args = parser.parse_args()

    patterns = {
        r'^from\s+\.?models\s+import\s*': r'from app.models import ',
        r'^from\s+\.?utils\s+import\s*': r'from app.utils import ',
        r'^from\s+\.?services\s+import\s*': r'from app.services import ',
        r'^from\s+\.?api\s+import\s*': r'from app.api import ',
    }

    print(f"Starting import updates under: {args.root}\n")
    walk_and_update(
        args.root,
        patterns,
        include_legacy=not args.no_legacy,
        include_backup=not args.no_backup
    )
    print("\nDone.")

if __name__ == '__main__':
    main() 