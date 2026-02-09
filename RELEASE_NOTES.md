# Release Notes

## Version 0.12.0 - Database Migrations & Package Management

### 🎉 New Features

#### 1. Database Migrations Command (`amen migrate`)
A new command for managing database migrations using Flask-Migrate. This command simplifies the process of initializing, creating, and upgrading database schemas.

**Features:**
- Automatic initialization of migrations if not already initialized
- Automatic migration file creation
- Automatic database upgrade
- Support for both SQLite and client-server databases (MySQL, PostgreSQL, etc.)
- Clear error messages and progress feedback

**Usage:**
```bash
amen migrate <app_name>
am migrate <app_name>

# Example:
amen migrate myapp
am migrate myapp
```

**What it does:**
1. Checks if migrations directory exists
2. If not, initializes Flask-Migrate with `flask db init`
3. Creates a new migration with `flask db migrate`
4. Applies the migration with `flask db upgrade`

**Requirements:**
- Flask-Migrate must be installed in the application's virtual environment
- For client-server databases, ensure the database server is running and properly configured

**Note:** Currently optimized for Flask applications. FastAPI support will be added in future versions.

---

#### 2. Package Installation Command (`amen install`)
A new command for installing packages directly into an application's virtual environment with automatic offline caching support.

**Features:**
- Install packages into application-specific virtual environments
- Automatic package caching for offline use
- Fallback to PyPI if caching fails due to network issues
- Clear progress indicators and status messages
- Support for any pip-compatible package

**Usage:**
```bash
amen install <app_name> <package>
am install <app_name> <package>

# Examples:
amen install myapp requests
amen install myapp flask-cors
amen install myapp sqlalchemy
am install myapp flask-migrate
```

**What it does:**
1. Validates that the application and virtual environment exist
2. Attempts to download and cache the package to `~/.amen/package_cache` for offline use
3. Installs the package in the application's virtual environment using pip
4. If caching fails due to network issues, it still installs from PyPI
5. Displays success message upon completion

**Benefits:**
- Faster package installation on subsequent setups (using cached packages)
- Offline installation capability for previously cached packages
- Keeps all application dependencies isolated in virtual environments
- Automatic version tracking through `requirements.txt`

**Note:** Package caching is attempted but won't block installation if it fails. The package will still be installed from PyPI.

---

### 🔧 Under the Hood

#### New Helper Functions
- `get_flask_path()`: Get the Flask CLI executable path based on the operating system

#### Enhanced Error Handling
- Both commands include comprehensive error messages for common issues
- Network errors during caching are handled gracefully
- Clear guidance provided when dependencies are missing

---

### 📋 Command Reference

| Command | Syntax | Purpose |
|---------|--------|---------|
| migrate | `amen migrate <app_name>` | Run database migrations |
| install | `amen install <app_name> <package>` | Install a package in app's venv |

---

### 🐛 Known Issues

- Flask-Migrate support is currently limited to Flask applications
- FastAPI database migration support requires manual setup (will be automated in future versions)
- Package caching uses PyPI's wheel format; some packages may not cache if wheels are unavailable

---

### 🚀 Future Enhancements

- FastAPI database migration support
- Advanced dependency management with `pip-tools`
- Automatic dependency resolution with conflict detection
- Package version pinning and lockfile generation

---

### 💡 Tips & Tricks

**For Database Migrations:**
- Always backup your database before running migrations
- Test migrations on a development database first
- Use meaningful migration names by editing the generated migration files

**For Package Installation:**
- Use `amen install <app_name> -r requirements.txt` to install from a requirements file (standard pip syntax)
- Check `~/.amen/package_cache` to see cached packages
- Manually delete cache files if you want to re-download packages

---

### 📝 Changelog

#### Added
- `migrate` command for Flask database migrations
- `install` command for managing application dependencies
- Automatic package caching system in `~/.amen/package_cache`
- `get_flask_path()` helper function

#### Improved
- Error messages now include specific guidance for resolution
- Progress indicators for long-running operations

---

### 🙏 Contributors

Thanks to the community for feedback and feature requests!

---

**For more information and documentation, visit:**
- 📖 [Documentation](https://github.com/TaqsBlaze/amen-cli/docs)
- 🐛 [Issue Tracker](https://github.com/TaqsBlaze/amen-cli/issues)
- 💬 [Discussions](https://github.com/TaqsBlaze/amen-cli/discussions)
