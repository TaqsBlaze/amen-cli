![icon](https://raw.githubusercontent.com/TaqsBlaze/amen-cli/refs/heads/main/image/icon.png)

[![PyPI Version](https://img.shields.io/pypi/v/amen-cli)](https://pypi.org/project/amen-cli/)
[![License](https://img.shields.io/github/license/TaqsBlaze/amen-cli)](https://github.com/TaqsBlaze/amen-cli/blob/main/LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/amen-cli)](https://pypi.org/project/amen-cli/)
[![GitHub Stars](https://img.shields.io/github/stars/TaqsBlaze/amen-cli?style=social)](https://github.com/TaqsBlaze/amen-cli)
[![GitHub Issues](https://img.shields.io/github/issues/TaqsBlaze/amen-cli)](https://github.com/TaqsBlaze/amen-cli/issues)
[![GitHub Forks](https://img.shields.io/github/forks/TaqsBlaze/amen-cli?style=social)](https://github.com/TaqsBlaze/amen-cli)
[![GitHub Last Commit](https://img.shields.io/github/last-commit/TaqsBlaze/amen-cli)](https://github.com/TaqsBlaze/amen-cli/commits/main)
[![GitHub Contributors](https://img.shields.io/github/contributors/TaqsBlaze/amen-cli)](https://github.com/TaqsBlaze/amen-cli/graphs/contributors)
[![GitHub Code Size](https://img.shields.io/github/languages/code-size/TaqsBlaze/amen-cli)](https://github.com/TaqsBlaze/amen-cli)
[![GitHub Repo Size](https://img.shields.io/github/repo-size/TaqsBlaze/amen-cli)](https://github.com/TaqsBlaze/amen-cli)
[![PyPI Downloads](https://img.shields.io/pypi/dm/amen-cli)](https://pypi.org/project/amen-cli/)

A laravel installer inspired Python Web Application Scaffolding Tool that helps you create web applications with ease!

## ✨ Features

- 🎯 Interactive project setup wizard
- 🔧 Multiple framework support:
  - Flask - Lightweight WSGI framework
  - FastAPI - Modern, fast API framework
  - Bottle - Simple micro web framework 🚧
  - Pyramid - Flexible web framework 🚧
- 🎨 Project templates for both web apps and APIs
- 🏗️ **Modular project structure** (see below)
- 🔄 Automatic virtual environment setup
- 📦 Dependency management
- 🏗️ Structured project scaffolding
- 🧪 Test scaffolding with pytest
- 🔄 Update checker for the CLI
- 🚀 Command to run your application

## 🛠️ Installation

### Using pip (All platforms)
```bash
pip install amen-cli
```

### Using uv

[uv](https://github.com/astral-sh/uv) is a very fast Python package installer and resolver, written in Rust.

To install `amen-cli` using uv:

1.  Install uv:

    ```bash
    pip install uv
    ```

2.  Install `amen-cli` using uv:

    ```bash
    uv pip install amen-cli
    ```

uv utilizes the `pyproject.toml` file for resolving dependencies, ensuring a consistent and reproducible installation.

### Debian/Ubuntu
```bash
# Install required dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv

# Install AMEN CLI
pip3 install amen-cli

# Optional: Install system-wide (requires root)
sudo pip3 install amen-cli
```

### Linux Post-Installation
Make sure the amen command is in your PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```
Add this line to your ~/.bashrc or ~/.zshrc for permanent effect.

## 📖 Usage

```bash
# Create a new project
amen create
# or use the short-form alias
am create

# You can also use flags to specify the framework, type, and name:
amen create -f flask -t webapp -n myapp
am create -f flask -t webapp -n myapp

# Available options:
# -f, --framework   Framework to use (flask, fastapi, bottle, pyramid)
# -t, --type        Type of application (webapp, api)
# -n, --name        Name of the application

# If flags are not provided, the interactive prompts will be used.

# Follow the interactive prompts to:
# 1. Select a framework
# 2. Choose application type (webapp/api)
# 3. Name your project

# Launch the web interface for project management
amen web [options]
am web [options]

# Available web interface options:
# -p, --port       Port to run the web interface on (default: 3000)
```

### Command Alias

All commands can be run using the short-form alias `am` instead of `amen`:

```bash
am create          # instead of: amen create
am run myapp       # instead of: amen run myapp
am test myapp      # instead of: amen test myapp
am update    # instead of: amen check-update
am config myapp    # instead of: amen config myapp
```

### Additional Commands

```bash
# Run your application
amen run <app_name>
am run <app_name>

# Example:
amen run myapp
am run myapp

# Run tests for your application
amen test <app_name>
am test <app_name>

# Example:
amen test myapp
am test myapp

# Check for updates to the CLI
amen update
am update

# Manage project configuration
amen config <app_name>
am config <app_name>

# Example:
amen config myapp
am config myapp

# Run a security audit on your application
amen audit <app_name> [options]
am audit <app_name> [options]
# Options:
# -f, --format     Output format (txt, json, csv, xml; default: txt)
# -s, --severity   Filter issues by severity (low, medium, high)
# -o, --output     Save audit report to a specified file
# Example:
amen audit myapp -s high
am audit myapp -s high

# Monitor application status and resource usage in real time
amen monitor <app_name> [options]
am monitor <app_name> [options]
# Options:
# -p, --port       Port to monitor
# -r, --refresh    Refresh rate in seconds (accepts decimal values; default: 0.1)
# --web            Run a web based monitor
# Example:
amen monitor myapp --port 5000 --refresh 0.5
am monitor myapp --port 5000 --refresh 0.5
amen monitor myapp --port 5000 --refresh 0.5 --web
am monitor myapp --port 5000 --refresh 0.5 --web

# Run database migrations for your application
amen migrate <app_name>
am migrate <app_name>

# Example:
amen migrate myapp
am migrate myapp
# This will:
# 1. Initialize migrations if not already initialized
# 2. Create a new migration
# 3. Upgrade the database

# Install a package in your application's virtual environment
amen install <app_name> <package>
am install <app_name> <package>

# Example:
amen install myapp requests
am install myapp flask-cors
# This will:
# 1. Cache the package for offline use
# 2. Install the package in the application's virtual environment
```

## 🌟 Project Structure

When you create a project, AMEN now generates a **modular structure**:

```
your-app/
├── venv/                   # Virtual environment
├── your-app/               # Main application package
│   ├── api/                # API endpoint modules
│   ├── auth/               # Authentication (token.py, etc.)
│   ├── models/             # Models module
│   ├── static/             # Static files (CSS, JS, images)
│   │   ├── uploads/
│   │   ├── css/
│   │   └── js/
│   ├── templates/          # HTML templates (if webapp)
│   └── app.py / main.py    # Main application file (Flask: app.py, FastAPI: main.py)
├── tests/                  # Test files
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (local)
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── app.py                  # Application runner
└── README.md               # This file
```

- **Flask**: Uses `app.py` and registers routes from separate files inside `api/` (for example `home.py`, `health.py`, `protected.py`). Token authentication is in `auth/token.py`.
- **FastAPI**: Uses `main.py` and includes routers from separate files in `api/` through `api/endpoints.py`. Token authentication is in `auth/token.py`.
- **Webapp**: Includes HTML templates and static files. FastAPI mounts static and template directories.
- **API**: Generates only API endpoints and disables template/static mounting.

## 🎯 Supported Frameworks

| Framework | Description | Default Port | Status |
|-----------|-------------|--------------|--------|
| Flask     | Lightweight WSGI web framework | 5000 | ✅ |
| FastAPI   | Modern, fast web framework      | 8000 | ✅ |
| Django    | High-level Python web framework | 8000 | ❌ |
| Bottle    | Fast, simple micro framework    | 8080 | 🚧 |
| Pyramid   | Flexible web framework          | 6543 | 🚧 |

## Work in Progress
Currently implementing support for additional web frameworks:

- **Bottle**: Integration in development
- **Pyramid**: Initial implementation phase

These frameworks will enable:
- Route mapping and handling
- Request/response processing
- Middleware integration
- Template rendering support

Check back for updates or follow the project's issues for implementation progress. Contributions are welcome!

> Note: For now, please use our stable implementations for Flask or FastAPI.

## 🚗 Quick Start

```bash
# Install AMEN CLI
pip install amen-cli

# Create a new project
amen create

# Follow the interactive prompts

# Navigate to your project
cd your-project-name

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run your application
python app.py
Or
#Before you cd into your project you can run the following 
amen run <appname>
```

## 🔧 Development

```bash
# Clone the repository
git clone https://github.com/taqsblaze/amen-cli.git

# Install for development and testing
cd amen-cli
pip install -e .
pip install pytest pytest-cov

# Run tests
pytest

# Run tests with coverage
pytest --cov
```

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contact & Support

- 🌐 [GitHub Repository](https://github.com/taqsblaze/amen-cli)
- 🐛 [Issue Tracker](https://github.com/taqsblaze/amen-cli/issues)
- 📧 [Send Email](mailto:tanakah30@gmail.com)

## ⭐ Credits

Created by [Tanaka Chinengundu](https://www.linkedin.com/in/taqsblaze)  
Inspired by Laravel's elegant development experience

---

Made with ❤️ by Tanaka Chinengundu


