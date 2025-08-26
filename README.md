# MySQL Utilities Python 3

A Python 3 port of MySQL Utilities 1.6 - a collection of database administration tools for MySQL/Aurora/RDS/MariaDB instances.

## Overview

MySQL Utilities provides a set of command-line tools for database administration tasks including:
- Database comparison (`mysqldbcompare`)
- Database copying (`mysqldbcopy`) 
- Database export/import (`mysqldbexport`, `mysqldbimport`)
- Replication management (`mysqlrpladmin`, `mysqlrplcheck`)
- Server management (`mysqlserverinfo`, `mysqlserverclone`)
- And many more utilities for MySQL/Aurora/RDS/MariaDB administration

## Installation

### Prerequisites
- Python 3.6 or higher
- Access to MySQL/MariaDB servers for testing utilities

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd mysql8-utilities-python3
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
# Install MySQL Connector (8.x version for compatibility)
pip install mysql-connector-python==8.4.0

# Install future package (required for Python 2/3 compatibility)
pip install future
```

### Step 4: Install MySQL Utilities
```bash
python3 setup.py install
```

### Step 5: Verify Installation
```bash
# Check if utilities are available
which mysqldbcompare
mysqldbcompare --help
```

## Usage

### Basic Command Structure
All utilities follow the MySQL Utilities connection format:
```bash
utility_name --server1=user:password@host:port --server2=user:password@host:port [options] database1:database2
```

### Example: Database Comparison
```bash
# Activate virtual environment first
source venv/bin/activate

# Compare database structures between two servers
mysqldbcompare \
  --server1='user:pass@server1.example.com:3306' \
  --server2='user:pass@server2.example.com:3306' \
  --run-all-tests \
  --skip-row-count \
  --skip-data-check \
  mydatabase:mydatabase
```

### Available Utilities

| Command | Description |
|---------|-------------|
| `mysqldbcompare` | Compare databases for consistency |
| `mysqldbcopy` | Copy databases between servers |
| `mysqldbexport` | Export database objects and data |
| `mysqldbimport` | Import database objects and data |
| `mysqldiff` | Compare object definitions |
| `mysqldiskusage` | Show disk usage for databases |
| `mysqlfailover` | Perform failover operations |
| `mysqlindexcheck` | Check for duplicate or redundant indexes |
| `mysqlrpladmin` | Manage MySQL replication |
| `mysqlrplcheck` | Check replication consistency |
| `mysqlrplshow` | Show replication topology |
| `mysqlserverclone` | Clone a MySQL server |
| `mysqlserverinfo` | Show server information |
| `mysqluserclone` | Clone MySQL users |

### Common Options
- `--help`: Show help for any command
- `--version`: Show version information
- `--verbose`: Enable verbose output
- `--quiet`: Suppress non-essential output
- `--format=FORMAT`: Output format (grid, tab, csv, vertical)

## Development

### Running Tests

#### Unit Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run all unit tests
python3 check.py

# Run specific test
python3 check.py test_server_version
```

#### Integration Tests
```bash
# Requires running MySQL server
cd mysql-test

# Run integration tests
python3 mut.py --help  # See available options
```

### Test Requirements
- Running MySQL/MariaDB server
- Proper MySQL configuration (`.my.cnf` or `.mylogin.cnf`)
- For some tests, disable password validation:
  ```sql
  UNINSTALL COMPONENT 'file://component_validate_password';
  -- or for older versions:
  -- UNINSTALL PLUGIN validate_password;
  ```

## Compatibility

### Database Servers
- MySQL 5.6+
- MySQL 5.7+
- MySQL 8.0+ (with compatibility handling for system table changes)
- Aurora MySQL
- MariaDB
- Percona Server

### Python Versions
- Python 3.6+
- Originally designed for Python 2.6/2.7, ported to Python 3

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: No module named 'mysql'
**Solution**: Make sure to activate the virtual environment and install the package properly:
```bash
source venv/bin/activate
python3 setup.py install
```

#### 2. MySQL Connector Issues
**Solution**: Use the compatible version:
```bash
pip install mysql-connector-python==8.4.0
```

#### 3. Connection Issues
- Verify server credentials and network connectivity
- Check VPN/firewall settings
- Ensure MySQL server allows remote connections if needed

#### 4. Permission Errors
- Ensure the MySQL user has appropriate privileges
- Some utilities require specific permissions (e.g., SUPER, REPLICATION CLIENT)

### Getting Help
- Use `--help` with any command for detailed options
- Check the `mysql-test/README.txt` for testing information
- Review server compatibility notes in `NOTES.md`

## Environment Setup

### Quick Start Script
For convenience, we provide a sample setup script with your credentials:

```bash
# Copy the sample and customize it with your credentials
cp local_setup.sh.sample local_setup.sh

# Edit local_setup.sh with your actual database credentials
# (local_setup.sh is gitignored for security)

# Make it executable and run
chmod +x local_setup.sh
./local_setup.sh
```

The sample includes:
- Environment activation
- Database credential variables (DB_USER1, DB_PASS1, DB_USER2, DB_PASS2)
- Host and database name configuration
- Example commands for common operations
- Security reminders

### Security Note
**Never commit credentials to version control!** Use environment variables or local configuration files:

```bash
# Option 1: Environment variables
export DB_USER="your_username"
export DB_PASS="your_password"
mysqldbcompare --server1=$DB_USER:$DB_PASS@host1:3306 --server2=$DB_USER:$DB_PASS@host2:3306 db1:db2

# Option 2: MySQL configuration files
# Create ~/.my.cnf or ~/.mylogin.cnf with your credentials
mysqldbcompare --server1=host1:3306 --server2=host2:3306 db1:db2
```

## License

This project is licensed under the GNU General Public License v2.0 - see the LICENSE.txt file for details.

## Contributing

When contributing to this project:
1. Follow existing code style and patterns
2. Run unit tests before submitting changes
3. Update documentation as needed
4. Test with multiple MySQL/Aurora/RDS/MariaDB versions when possible
