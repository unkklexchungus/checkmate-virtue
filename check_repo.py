import os
import argparse
import ast


def find_directories_with_py(root):
    dirs = []
    for dirpath, dirnames, filenames in os.walk(root):
        # skip hidden directories
        if any(part.startswith('.') for part in dirpath.split(os.sep)):
            continue
        if any(fname.endswith('.py') for fname in filenames):
            dirs.append(dirpath)
    return dirs


def check_init_files(root):
    missing = []
    dirs = find_directories_with_py(root)
    for d in dirs:
        init_file = os.path.join(d, '__init__.py')
        if not os.path.isfile(init_file):
            missing.append(d)
    return missing


def scan_imports(root):
    issues = []
    for dirpath, _, filenames in os.walk(root):
        if any(part.startswith('.') or part.startswith('venv') for part in dirpath.split(os.sep)):
            continue
        for fname in filenames:
            if fname.endswith('.py'):
                fullpath = os.path.join(dirpath, fname)
                with open(fullpath, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read(), filename=fullpath)
                    except SyntaxError:
                        continue
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            mod = node.module or ''
                            # catch imports like 'from models.' or 'from utils.' without 'app.' prefix
                            if mod.split('.')[0] in ('models', 'utils', 'api', 'services'):
                                issues.append((fullpath, mod))
    return issues


def check_entrypoint(root):
    candidates = ['main.py', os.path.join('app', 'main.py')]
    found = []
    for c in candidates:
        path = os.path.join(root, c)
        if os.path.isfile(path):
            found.append(path)
    return found


def check_templates_static(root):
    tpl = os.path.join(root, 'app', 'templates')
    static = os.path.join(root, 'app', 'static')
    return os.path.isdir(tpl), os.path.isdir(static)


def check_env(root):
    env_path = os.path.join(root, '.env')
    return os.path.isfile(env_path)


def main():
    parser = argparse.ArgumentParser(description="CLI tool to validate Python project structure");
    parser.add_argument('root', nargs='?', default='.', help='Root of your project');
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    print(f"Checking project at: {root}\n")

    # __init__.py check
    missing_init = check_init_files(root)
    if missing_init:
        print("[WARN] Missing __init__.py in directories:")
        for d in missing_init:
            print(f"  - {d}")
    else:
        print("[OK] All Python packages have __init__.py files.")

    # import issues
    import_issues = scan_imports(root)
    if import_issues:
        print("\n[WARN] Detected imports that may need updating to 'app.' namespace:")
        for path, mod in import_issues:
            print(f"  - {path}: from {mod} import ...")
    else:
        print("[OK] No legacy imports detected.")

    # entrypoint check
    entrys = check_entrypoint(root)
    if entrys:
        print(f"\n[OK] Found entrypoint(s): {', '.join(entrys)}")
    else:
        print("\n[ERROR] No main.py entrypoint found at expected locations.")

    # templates/static
    tpl_exists, static_exists = check_templates_static(root)
    print()
    if tpl_exists:
        print("[OK] 'app/templates' directory exists.")
    else:
        print("[WARN] 'app/templates' directory not found.")
    if static_exists:
        print("[OK] 'app/static' directory exists.")
    else:
        print("[WARN] 'app/static' directory not found.")

    # .env
    has_env = check_env(root)
    print()
    if has_env:
        print("[OK] .env file found.")
    else:
        print("[WARN] .env file not found.")

if __name__ == '__main__':
    main() 