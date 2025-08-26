# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python 3 port of MySQL Utilities 1.6 - a collection of database administration tools for MySQL/MariaDB servers. The utilities provide functionality for database comparison, copying, replication management, auditing, and more.

## Core Architecture

The codebase is structured as follows:

- **mysql/utilities/** - Main package containing all utility libraries
  - **command/** - High-level command implementations for each utility
  - **common/** - Shared libraries (server connections, database operations, parsing, etc.)
- **scripts/** - Command-line entry points for all utilities (e.g., mysqldbcompare.py, mysqlrpladmin.py)
- **unit_tests/** - Unit tests using Python's unittest framework
- **mysql-test/** - System-level integration tests with custom test framework

## Key Components

- **Server abstraction**: `mysql.utilities.common.server` provides MySQL server connection and management
- **Database operations**: `mysql.utilities.common.database` handles database-level operations  
- **Replication management**: `mysql.utilities.common.replication` and related modules
- **Comparison engine**: `mysql.utilities.common.dbcompare` for database/table comparisons
- **Format output**: `mysql.utilities.common.format` for consistent output formatting
- **Parser utilities**: Various parsers for connection strings, SQL, configuration files

## Development Commands

### Building and Installation
```bash
# Install the package in development mode
python setup.py develop

# Build source distribution
python setup.py sdist

# Install from source
python setup.py install
```

### Testing
```bash
# Run all unit tests
python check.py

# Run specific unit test
python check.py test_server_version

# Run integration tests (requires running MySQL server)
cd mysql-test
python mut.py --help  # See available options
```

### Test Requirements
- Running MySQL/MariaDB server
- MySQL Connector/Python
- `preprocess` package for test data preprocessing
- Proper MySQL configuration (.my.cnf or .mylogin.cnf)

For testing, some MySQL plugins may need to be disabled:
```sql
UNINSTALL COMPONENT 'file://component_validate_password';
-- or for older versions:
-- uninstall plugin validate_password;
```

## Server Compatibility

The utilities support:
- MySQL 5.6+, including MySQL 8.0+ 
- MariaDB
- Percona Server

Version-specific handling is done via `server.has_mysqlproc()` and `server.get_server_type()` methods to handle differences in system table locations and features between versions.

## Common Patterns

- All utilities follow consistent command-line option patterns
- Server connections use `--server=user:pass@host:port` format
- Most utilities support multiple output formats via `--format` option
- Error handling uses custom exception classes in `mysql.utilities.exception`
- Logging and verbosity controlled via common options framework