#
# Copyright (c) 2010, 2014, Oracle and/or its affiliates. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#
"""This module containts the Metadata for Python Software Packages"""
from __future__ import print_function

import glob
import os
from fnmatch import fnmatch

import mysql.utilities


def find_packages(*args, **kwrds):
    """Find all packages and sub-packages and return a list of them.

    The function accept any number of directory names that will be
    searched to find packages. Packages are identified as
    sub-directories containing an __init__.py file.  All duplicates
    will be removed from the list and it will be sorted
    alphabetically.

    Packages can be excluded by pattern using the 'exclude' keyword,
    which accepts a list of patterns.  All packages with names that
    match the beginning of an exclude pattern will be excluded.

    Root base path can be attached to each package by using 'inc_base'
    keyword.
    """
    excludes = kwrds.get('exclude', [])
    inc_base = kwrds.get('inc_base', False)
    pkgs = {}
    for base_path in args:
        for root, _, files in os.walk(base_path):
            if '__init__.py' in files:
                assert root.startswith(base_path)
                pkg = root[len(base_path)+1:].replace(os.sep, '.')
                if inc_base and pkg:
                    pkg = os.path.join(base_path, pkg).replace(os.sep, '.')
                elif inc_base:
                    pkg = base_path.replace(os.sep, '.')
                pkgs[pkg] = root

    # Filter out packages discovered inside virtualenv or site-packages
    bad_indicators = ('site-packages', os.path.join('.venv', ''),
                      os.path.join('venv', ''), os.path.join('lib', 'python'))
    filtered_pkgs = {}
    for pkg_name, pkg_root in pkgs.items():
        try:
            norm_root = os.path.normpath(pkg_root).lower()
            if any(ind in norm_root for ind in bad_indicators):
                # skip packages coming from virtualenv/site-packages
                continue
        except Exception:
            # keep package if anything odd happens
            filtered_pkgs[pkg_name] = pkg_root
        else:
            filtered_pkgs[pkg_name] = pkg_root

    pkgs = filtered_pkgs
    result = list(pkgs.keys())
    for excl in excludes:
        # We exclude packages that *begin* with an exclude pattern.
        result = [pkg for pkg in result if not fnmatch(pkg, excl + "*")]
    result.sort()
    return result


def add_optional_resources(*args, **kwrds):
    """Adds additional resources, as source packages, scripts and data files.

    The function will try to find all resources in the directory names given,
    that will be searched to find packages, data files and scripts.

    Packages are identified as sub-directories containing an __init__.py file.
    All duplicates will be removed from the list and it will be sorted
    alphabetically. This function uses the find_packages function; see his
    help to know more how packages are found.

    Scripts must be set on 'scripts', and a list of the desired scripts to add
    must be given by 'scripts' keyword.

    Data files can be set in a dictionary with the keyword
    'data_files', where destination is used as key and a list of source files,
    are the item for that key.
    """

    excludes = kwrds.get('exclude', [])
    inc_base = kwrds.get('inc_base', True)
    data_files = kwrds.get('data_files', {})

    packages_found = []

    pkg_base = args[0]
    print('checking {0} for packages to distribute'.format(pkg_base))
    pkgs = find_packages(pkg_base, exclude=excludes, inc_base=inc_base)
    print("packages found: {0}".format(pkgs))
    packages_found.extend(pkgs)

    scripts_found = []
    for _, _, scripts in os.walk('scripts'):
        for script in scripts:
            script_path = os.path.join('scripts', script)
            if not script_path.endswith('.py') and \
               not os.path.exists('{0}.py'.format(script_path)):
                os.rename(script_path, '{0}.py'.format(script_path))
                script_path = '{0}.py'.format(script_path)
            if script_path.endswith('.py'):
                scripts_found.append(script_path)
    print("scripts found: {0}".format(scripts_found))

    data_files_found = []
    for _, _, data_files in os.walk('data'):
        datafiles = []
        zipfiles = []
        otherfiles = []
        for src in data_files:
            _, ext = os.path.splitext(src)
            if ext == '.zip' and os.name != 'nt':
                zipfiles.append(os.path.join('data', src))
            else:
                datafiles.append(os.path.join('data', src))
        if datafiles:
            data_files_found.append(('data', datafiles))
        if zipfiles:
            data_files_found.append(('/etc/mysql', zipfiles))
        if otherfiles:
            data_files_found.append(('other', otherfiles))

    if packages_found:
        INSTALL['packages'].extend(packages_found)
        print("package set {0}".format(set(INSTALL['packages'])))
        INSTALL['packages'] = list(set(INSTALL['packages']))
    if scripts_found:
        INSTALL['scripts'].extend(scripts_found)
        INSTALL['scripts'] = list(set(INSTALL['scripts']))
    if data_files_found:
        INSTALL['data_files'] = data_files_found


def find_packages(root='.'):
    """
    Find packages only inside the project root and skip virtualenvs / site-packages.
    Returns a sorted list of dotted package names.
    """
    root = os.path.abspath(root)
    exclude_top_dirs = {'.git', '.venv', 'venv', 'env', 'build', 'dist', '__pycache__'}
    packages = []

    for dirpath, dirnames, filenames in os.walk(root):
        # compute relative path from project root
        rel = os.path.relpath(dirpath, root)
        # normalize '.' to empty
        if rel == '.':
            rel = ''
        # skip any top-level excluded directory (and prune it)
        parts = rel.split(os.sep) if rel else []
        if parts and parts[0] in exclude_top_dirs:
            dirnames[:] = []  # don't descend
            continue

        # skip directories that look like site-packages / venv paths
        norm = os.path.normpath(dirpath).lower()
        if 'site-packages' in norm or os.path.join('.venv', '') in norm or os.path.join('venv', '') in norm:
            dirnames[:] = []
            continue

        if '__init__.py' in filenames:
            if rel == '':
                # ignore top-level project root as a package unless it actually is intended
                # (this repository uses package directories under mysql/)
                pass
            else:
                pkg = rel.replace(os.sep, '.')
                packages.append(pkg)

    packages.sort()
    return packages


def find_scripts(scripts_dir='scripts'):
    if not os.path.isdir(scripts_dir):
        return []
    return [os.path.join(scripts_dir, f) for f in os.listdir(scripts_dir)
            if os.path.isfile(os.path.join(scripts_dir, f)) and f.endswith('.py')]


META_INFO = {
    'name': 'mysql-utilities-python3',
    'version': '2',
    'description': 'MySQL Utilities Python 3 (dev install)',
    'author': 'Abraham Perez',
    'url': 'https://github.com/abany/mysql8-utilities-python3.git',
}

INSTALL = {
    'packages': find_packages(),
    'scripts': find_scripts(),
    'include_package_data': True,
}
# This adds any optional resource
add_optional_resources('mysql', exclude=["tests"])

if __name__ == "__main__":
    for key, item in INSTALL.items():
        print("--> {0}".format(key))
        print("      {0}".format(item))
        print()
