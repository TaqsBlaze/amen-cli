# <img src="https://raw.githubusercontent.com/TaqsBlaze/amen-cli/refs/heads/main/image/icon.png" width="32" /> **AMEN CLI Wiki**

---

> **A Laravel-inspired Python Web Application Scaffolding Tool**

---

## 🎨 Overview

**AMEN CLI** is a modern, interactive, and modular Python project scaffolding tool for web applications and APIs.  
It supports multiple frameworks, generates a clean modular structure, and helps you get started with best practices in seconds.

---

## 🌈 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Framework Support](#framework-support)
- [Usage](#usage)
- [Development](#development)
- [Contributing](#contributing)
- [Contact & Support](#contact--support)

---

## <span style="color:#6C63FF;">✨ Features</span>

- Interactive project setup wizard
- Multiple framework support: Flask, FastAPI, Bottle (WIP), Pyramid (WIP)
- Modular project structure (see below)
- Webapp and API templates
- Automatic virtual environment setup
- Dependency management
- Test scaffolding with pytest
- Update checker for the CLI
- Easy project runner

---

## <span style="color:#43B581;">🛠️ Installation</span>

```bash
pip install amen-cli
```

---

## <span style="color:#F59E42;">🚀 Quick Start</span>

```bash
# Create a new project
amen create

# Or use flags for automation:
amen create -f flask -t webapp -n myapp
```

**Flags:**
- `-f, --framework`   Framework (flask, fastapi, bottle, pyramid)
- `-t, --type`        Application type (webapp, api)
- `-n, --name`        Project name

**Run your app:**
```bash
cd myapp
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
python run.py
```
Or, from the parent directory:
```bash
amen run myapp
```

---

## <span style="color:#FF5E5B;">🏗️ Project Structure</span>

```text
your-app/
├── venv/                   # Virtual environment
├── your-app/               # Main application package
│   ├── api/                # API endpoints (endpoints.py)
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
├── run.py                  # Application runner
└── README.md               # Project documentation
```

---

## <span style="color:#00B8A9;">🎯 Framework Support</span>

| Framework | Description | Default Port | Status |
|-----------|-------------|--------------|--------|
| **Flask**     | Lightweight WSGI web framework | 5000 | ✅ |
| **FastAPI**   | Modern, fast web framework      | 8000 | ✅ |
| Django    | High-level Python web framework | 8000 | ❌ |
| Bottle    | Fast, simple micro framework    | 8080 | 🚧 |
| Pyramid   | Flexible web framework          | 6543 | 🚧 |

---

## <span style="color:#F59E42;">📖 Usage</span>

```bash
# Create a new project
amen create

# Run your application
amen run <app_name>

# Run tests
amen test <app_name>

# Check for updates
amen check-update

# Manage project configuration
amen config <app_name>
```

---

## <span style="color:#43B581;">🔧 Development</span>

```bash
git clone https://github.com/taqsblaze/amen-cli.git
pip install -e .
pip install pytest pytest-cov
pytest
pytest --cov
```

---

## <span style="color:#6C63FF;">🤝 Contributing</span>

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## <span style="color:#FF5E5B;">👥 Contact & Support</span>

- 🌐 [GitHub Repository](https://github.com/taqsblaze/amen-cli)
- 🐛 [Issue Tracker](https://github.com/taqsblaze/amen-cli/issues)
- 📧 [Send Email](mailto:tanakah30@gmail.com)

---

## <span style="color:#00B8A9;">⭐ Credits</span>

Created by [Tanaka Chinengundu](https://www.linkedin.com/in/taqsblaze)  
Inspired by Laravel's elegant development experience

---

<div align="center" style="color:#6C63FF;">
Made with ❤️ by Tanaka Chinengundu
</div>
