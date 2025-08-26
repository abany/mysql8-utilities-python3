# Minimal metadata used only for isolated builds (pip editable/build)
import os

def find_packages(root='.'):
    """Minimal, robust package discovery for isolated builds."""
    root = os.path.abspath(root)
    exclude_top_dirs = {'.git', '.venv', 'venv', 'env', 'build', 'dist', '__pycache__'}
    packages = []

    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel == '.':
            rel = ''
        parts = rel.split(os.sep) if rel else []
        if parts and parts[0] in exclude_top_dirs:
            dirnames[:] = []
            continue

        norm = os.path.normpath(dirpath).lower()
        if 'site-packages' in norm or os.path.join('.venv', '') in norm or os.path.join('venv', '') in norm:
            dirnames[:] = []
            continue

        if '__init__.py' in filenames:
            if rel != '':
                packages.append(rel.replace(os.sep, '.'))

    packages.sort()
    return packages

def find_scripts(scripts_dir='scripts'):
    if not os.path.isdir(scripts_dir):
        return []
    return [os.path.join(scripts_dir, f) for f in os.listdir(scripts_dir)
            if os.path.isfile(os.path.join(scripts_dir, f)) and f.endswith('.py')]

META_INFO = {
    'name': 'mysql-utilities-python3',
    'version': '3.3.0',
    'description': 'MySQL Utilities Python 3 (dev install)',
    'author': 'Abraham Perez',
    'url': 'https://github.com/abany/mysql8-utilities-python3.git',
}

INSTALL = {
    'packages': find_packages(),
    'scripts': find_scripts(),
    'include_package_data': True,
}