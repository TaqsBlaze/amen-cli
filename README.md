# 🚀 AMEN CLI   ![icon](https://raw.githubusercontent.com/TaqsBlaze/amen-cli/refs/heads/main/image/icon.png)
A laravel installer inspired Python Web Application Scaffolding Tool that helps you create web applications with ease!

## ✨ Features

- 🎯 Interactive project setup wizard
- 🔧 Multiple framework support:
  - Flask - Lightweight WSGI framework
  - FastAPI - Modern, fast API framework
  - Bottle - Simple micro web framework 🚧
  - Pyramid - Flexible web framework 🚧
- 🎨 Project templates for both web apps and APIs
- 🔄 Automatic virtual environment setup
- 📦 Dependency management
- 🏗️ Structured project scaffolding
- 🧪 Test scaffolding with pytest
- 🔄 Update checker for the CLI
- 🚀 Command to run your application

## 🛠️ Installation

```bash
pip install amen-cli
```

## 📖 Usage

```bash
# Create a new project
amen create

# You can also use flags to specify the framework, type, and name:
amen create -f flask -t webapp -n myapp

# Available options:
# -f, --framework   Framework to use (flask, fastapi, bottle, pyramid)
# -t, --type        Type of application (webapp, api)
# -n, --name        Name of the application

# If flags are not provided, the interactive prompts will be used.

# Follow the interactive prompts to:
# 1. Select a framework
# 2. Choose application type (webapp/api)
# 3. Name your project
```

### Additional Commands

```bash
# Run your application
amen run <app_name>

# Example:
amen run myapp

# Run tests for your application
amen test <app_name>

# Example:
amen test myapp

# Check for updates to the CLI
amen check-update
```

## 🌟 Project Structure

When you create a project, AMEN generates:

```
your-app/
├── venv/                   # Virtual environment
├── app/                    # Main application code
│   ├── templates/         # HTML templates (webapp)
│   └── static/           # Static files
│       ├── css/         # Stylesheets
│       └── js/          # JavaScript files
├── tests/                 # Test directory
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
└── README.md             # Project documentation
```

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
python run.py
```

## 🔧 Development

```bash
# Clone the repository
git clone https://github.com/taqsblaze/amen-cli.git

# Install for development and testing
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
