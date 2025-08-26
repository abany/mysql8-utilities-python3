#!/usr/bin/env python3
# wrapper for MariaDB my_print_defaults to work with mysql-utilities

import subprocess
import sys
import os
import re

import shutil
import platform
import glob

# Known MySQL package names for RPM-based systems (module-level constant)
KNOWN_MYSQL_RPM_PKGS = [
    'mysql',
    'mysql-community',
    'mysql-community-server',
    'mysql-server',
    'MySQL-server',
    'mysql84-community-release',
    'mysql83-community-release',
    'mysql80-community-release',
    'mysql57-community-release',
    'mysql56-community-release',
    'mysql-community-client',
    'mysql-client',
]

# Regex pattern to extract package name from dpkg -S output (module-level constant)
DPKG_PACKAGE_NAME_REGEX = r'^([^\s:]+):'

# Regex pattern to extract base package name from RPM package string (module-level constant)
RPM_BASE_PKG_REGEX = r'^([^-]+(?:-[^-]+)*)'

def get_my_print_defaults_path():
    """Get the my_print_defaults executable path (lazy evaluation with caching)"""
    if not hasattr(get_my_print_defaults_path, "_cached_path"):
        get_my_print_defaults_path._cached_path = find_my_print_defaults()
    return get_my_print_defaults_path._cached_path

def find_my_print_defaults():
    """Find my_print_defaults executable across different platforms and installations"""
    # Try PATH first (works for most standard installations)
    path_executable = shutil.which('my_print_defaults')
    if path_executable:
        return path_executable
    
    # Platform-specific common locations
    system = platform.system().lower()
    
    candidates = []
    
    if system == 'linux':
        # Linux standard locations
        candidates.extend([
            '/usr/bin/my_print_defaults',
            '/usr/local/bin/my_print_defaults',
            '/opt/mysql/bin/my_print_defaults',
            '/opt/mariadb/bin/my_print_defaults',
            '/usr/local/mysql/bin/my_print_defaults',
            '/usr/local/mariadb/bin/my_print_defaults',
        ])
    elif system == 'darwin':  # macOS
        # macOS standard locations + Homebrew paths
        candidates.extend([
            '/usr/local/bin/my_print_defaults',  # Homebrew default
            '/opt/homebrew/bin/my_print_defaults',  # Apple Silicon Homebrew
            '/usr/local/mysql/bin/my_print_defaults',  # MySQL.com installer
            '/usr/local/mariadb/bin/my_print_defaults',  # MariaDB installer
            '/opt/local/bin/my_print_defaults',  # MacPorts
            '/sw/bin/my_print_defaults',  # Fink
        ])
    elif system == 'windows':
        # Windows common locations

        # Use glob to find my_print_defaults.exe in common installation directories
        win_paths = [
            'C:\\Program Files\\MySQL\\MySQL Server*\\bin\\my_print_defaults.exe',
            'C:\\Program Files\\MariaDB*\\bin\\my_print_defaults.exe',
            'C:\\Program Files (x86)\\MySQL\\MySQL Server*\\bin\\my_print_defaults.exe',
            'C:\\mysql\\bin\\my_print_defaults.exe',
            'C:\\mariadb\\bin\\my_print_defaults.exe',
        ]
        for pattern in win_paths:
            candidates.extend(glob.glob(pattern))
    
    # Check all candidates
    for path in candidates:
        if path and os.path.exists(path):
            return path
    
    return None

def detect_mysql_installation():
    """Detect if MySQL (vs MariaDB) installation provides my_print_defaults"""
    path = get_my_print_defaults_path()
    if not path:
        return False
    
    system = platform.system().lower()
    
    if system == 'linux':
        # Linux: Use RPM/DEB package detection
        return detect_mysql_linux(path)
    elif system == 'darwin':
        # macOS: Check path patterns and version output
        return detect_mysql_macos(path)
    elif system == 'windows':
        # Windows: Check installation path patterns
        return detect_mysql_windows(path)
    
    return False

def detect_mysql_linux(path):
    """Detect MySQL on Linux using package managers"""
    # Try RPM first
    try:
        rpm_cmd = ['rpm', '-qf', path]
        rpm_result = subprocess.check_output(rpm_cmd, stderr=subprocess.DEVNULL, text=True).strip()
        if rpm_result:
            # Use the first non-empty line as the package name
            pkg_name = next((line.strip() for line in rpm_result.splitlines() if line.strip()), None)
            if pkg_name:
                # Extract base package name (before version info) using regex
                # Pattern matches package name until version number or end of string
                # Handles various versioning schemes: -8.0.34, .1.el8, -el8, etc.
                match = re.match(RPM_BASE_PKG_REGEX, pkg_name)
                base_pkg_name = match.group(1) if match else pkg_name
                # Match only exact package names from the known list
                if any(base_pkg_name.lower() == name.lower() for name in KNOWN_MYSQL_RPM_PKGS):
                    return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Try dpkg if rpm did not succeed
    try:
        dpkg_cmd = ['dpkg', '-S', path]
        dpkg_result = subprocess.check_output(dpkg_cmd, stderr=subprocess.DEVNULL, text=True).strip()
        if dpkg_result:
            # Extract package name before the first colon using regex
            # dpkg -S output format: "package:architecture: /path/to/file"
            match = re.match(DPKG_PACKAGE_NAME_REGEX, dpkg_result)
            if match:
                pkg_info = match.group(1)
                # Check against known MySQL packages and exclude MariaDB
                if (any(pkg_info.lower() == name.lower() for name in KNOWN_MYSQL_RPM_PKGS) and 
                    'mariadb' not in pkg_info.lower()):
                    return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return False

def detect_mysql_macos(path):
    """Detect MySQL on macOS using path patterns and version detection"""
    # Check common MySQL installation paths
    mysql_paths = [
        '/usr/local/mysql/',
        '/opt/homebrew/var/mysql/',
        '/usr/local/var/mysql/',
    ]
    
    # If installed in a MySQL-specific directory, it's likely MySQL
    for mysql_path in mysql_paths:
        if mysql_path in path:
            return True
    
    # Try version detection as fallback
    try:
        version_cmd = [path, '--version']
        version_result = subprocess.check_output(version_cmd, stderr=subprocess.DEVNULL, text=True).strip()
        if 'mysql' in version_result.lower() and 'mariadb' not in version_result.lower():
            return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return False

def detect_mysql_windows(path):
    """Detect MySQL on Windows using installation path patterns"""
    # Check if path contains MySQL-specific directories
    path_lower = path.lower()
    
    mysql_indicators = [
        'mysql server',
        '\\mysql\\',
        'program files\\mysql\\',
        'program files (x86)\\mysql\\',
    ]
    
    for indicator in mysql_indicators:
        if indicator in path_lower:
            return True
    
    return False

def main():
    """Wrapper for my_print_defaults to handle login-path option for MariaDB compatibility"""
    
    path = get_my_print_defaults_path()
    # Early exit if executable not found
    if not path:
        sys.exit('Error: my_print_defaults executable not found. Please install MySQL or MariaDB client tools.')
    
    # Detect if MySQL (vs MariaDB) provides my_print_defaults
    # If so, execute it directly without processing login-path arguments
    is_mysql = detect_mysql_installation()
    if is_mysql:
        exit_code = subprocess.call([path] + sys.argv[1:])
        sys.exit(exit_code)

    # Process arguments for MariaDB compatibility
    loginpath = None
    keep = []
    grabarg = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        
        if grabarg:
            grabarg = False
            # Validate that the argument is not another option
            if arg.startswith('-'):
                sys.exit('Error: Missing value for login-path option.')
            loginpath = arg
            i += 1
            continue

        if arg in ('-?', '--help'):
            # Show original help plus our login-path option
            subprocess.call([path] + args)
            print("\t-l, --login-path=name")
            print("\t\t\tpath to be read from the login file")
            sys.exit(0)

        if arg in ("-l", "--login-path"):
            # Check if this is the last argument
            if i + 1 >= len(args):
                sys.exit('Error: Missing value for login-path option.')
            grabarg = True
        elif arg.startswith("--login-path="):
            loginpath = arg.split("=", 1)[1]
            # Validate that there's actually a value after the equals
            if not loginpath:
                sys.exit('Error: Missing value for login-path option.')
        else:
            keep.append(arg)
        
        i += 1
    
    # Final check: if grabarg is still True, we're missing the value
    if grabarg:
        sys.exit('Error: Missing value for login-path option.')

    # Build final command
    cmd = [path] + keep
    if loginpath:
        cmd.append(loginpath)
    
    # Execute my_print_defaults with processed arguments
    exit_code = subprocess.call(cmd)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()