"""Template management for different frameworks"""

import os
from pathlib import Path
from ..frameworks import FRAMEWORKS

class TemplateManager:
    def _write_file(self, path: Path, content: str):
        """Helper method to write files with UTF-8 encoding"""
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    def generate_structure(self, app_path: Path, framework: str, app_type: str, app_name: str):
        """Generate project structure based on framework and app type"""
        
        # Create all necessary directories
        (app_path / "app").mkdir(exist_ok=True)
        (app_path / "app" / "templates").mkdir(exist_ok=True)
        (app_path / "app" / "static").mkdir(exist_ok=True)
        (app_path / "app" / "static" / "css").mkdir(exist_ok=True)
        (app_path / "app" / "static" / "js").mkdir(exist_ok=True)
        (app_path / "tests").mkdir(exist_ok=True)  # Create tests directory
        
        # Generate framework-specific files
        if framework == 'flask':
            self._generate_flask_files(app_path, app_type, app_name)
        elif framework == 'fastapi':
            self._generate_fastapi_files(app_path, app_type, app_name)
        # Add other frameworks as needed
        
        # Generate common files
        self._generate_common_files(app_path, framework, app_name, app_type)
    
    def _generate_flask_files(self, app_path: Path, app_type: str, app_name: str):
        """Generate Flask files"""
        app_content = f"""from flask import Flask, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def index():
    {"return render_template('index.html', title='" + app_name + "')" if app_type == 'webapp' else "return jsonify({'message': 'Welcome to " + app_name + " API!'})"}

@app.route('/health')
def health():
    return jsonify({{'status': 'healthy', 'service': '{app_name}'}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
"""
        self._write_file(app_path / "app" / "app.py", app_content)
        self._write_file(app_path / "run.py", "from app.app import app\n\nif __name__ == '__main__':\n    app.run()")
        
        if app_type == 'webapp':
            self._generate_html_template(app_path, app_name)
    
    def _generate_fastapi_files(self, app_path: Path, app_type: str, app_name: str):
        """Generate FastAPI files"""
        main_content = f"""from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
{"from fastapi.templating import Jinja2Templates" if app_type == 'webapp' else ""}
{"from fastapi.staticfiles import StaticFiles" if app_type == 'webapp' else ""}
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="{app_name}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

{"app.mount('/static', StaticFiles(directory='app/static'), name='static')" if app_type == 'webapp' else ""}
{"templates = Jinja2Templates(directory='app/templates')" if app_type == 'webapp' else ""}

@app.get("/")
async def root({"request: Request" if app_type == 'webapp' else ""}):
    {"return templates.TemplateResponse('index.html', {'request': request, 'title': '" + app_name + "'})" if app_type == 'webapp' else 'return {"message": "Welcome to ' + app_name + ' API!"}'}

@app.get("/health")
async def health():
    return {{"status": "healthy", "service": "{app_name}"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
        self._write_file(app_path / "app" / "main.py", main_content)
        self._write_file(app_path / "run.py", "import uvicorn\nfrom app.main import app\n\nif __name__ == '__main__':\n    uvicorn.run(app, host='0.0.0.0', port=8000)")
        
        if app_type == 'webapp':
            self._generate_html_template(app_path, app_name)
    
    def _generate_html_template(self, app_path: Path, app_name: str):
        """Generate HTML template"""
        template_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{app_name}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <h1>Welcome to {app_name}!</h1>
        <p>Your application is running successfully.</p>
    </div>
    <script src="/static/js/app.js"></script>
</body>
</html>"""
        self._write_file(app_path / "app" / "templates" / "index.html", template_content)
    
    def _generate_common_files(self, app_path: Path, framework: str, app_name: str, app_type: str):
        """Generate common files for all projects"""
        
        # requirements.txt
        framework_info = FRAMEWORKS[framework]
        requirements = "\n".join(framework_info['packages'])
        self._write_file(app_path / "requirements.txt", requirements)
        
        # .env
        env_content = f"""SECRET_KEY=your-secret-key-here
DEBUG=True
PORT={framework_info['default_port']}
"""
        self._write_file(app_path / ".env", env_content)
        
        # README.md
        readme_content = f"""# {app_name}

A web application built with {framework_info['name']}.

## Quick Start

1. Activate virtual environment:
   ```bash
   source venv/bin/activate  # Linux/Mac
   venv\\Scripts\\activate    # Windows
3. **Install dependencies** (if not already installed)
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

Your application will be available at `http://localhost:{framework_info['default_port']}`

## 📁 Project Structure

```
{app_name}/
├── venv/                   # Virtual environment
├── app/                    # Main application code
│   ├── __init__.py
│   ├── {framework_info['entry_file']}     # Main application file
│   ├── templates/          # HTML templates (if web app)
│   └── static/            # Static files (CSS, JS, images)
│       ├── css/
│       └── js/
├── tests/                  # Test files
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (local)
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── run.py                # Application runner
└── README.md             # This file
```

## 🛠️ Development

### Framework: {FRAMEWORKS[framework]['name']}
{FRAMEWORKS[framework]['description']}

### Application Type: {"Full Web Application" if app_type == 'webapp' else "API Only"}

### Available Endpoints
- `GET /` - {"Main page" if app_type == 'webapp' else "API welcome message"}
- `GET /health` - Health check endpoint

### Adding New Routes

#### {FRAMEWORKS[framework]['name']} specific instructions:
'''

        # Add framework-specific route examples
        if framework == 'flask':
            readme_content += '''
```python
from flask import Flask

@app.route('/new-route')
def new_route():
    return 'Hello from new route!'
```
'''
        elif framework == 'fastapi':
            readme_content += '''
```python
from fastapi import FastAPI

@app.get("/new-route")
async def new_route():
    return {{"message": "Hello from new route!"}}
```
'''
        elif framework == 'django':
            readme_content += '''
1. Add to `app/urls.py`:
```python
path('new-route/', views.new_route, name='new_route'),
```

2. Add to `app/views.py`:
```python
def new_route(request):
    return JsonResponse({{'message': 'Hello from new route!'}})
```
'''
        elif framework == 'bottle':
            readme_content += '''
```python
@app.route('/new-route')
def new_route():
    return {{'message': 'Hello from new route!'}}
```
'''
        elif framework == 'pyramid':
            readme_content += '''
1. Add route in `main()`:
```python
config.add_route('new_route', '/new-route')
```

2. Add view function:
```python
@view_config(route_name='new_route', renderer='json')
def new_route_view(request):
    return {{'message': 'Hello from new route!'}}
```
"""

        readme_content += f"""

## 🧪 Testing

Run tests with:
```bash
pytest tests/
```

## 📦 Deployment

### Environment Variables
Make sure to set these in production:
- `SECRET_KEY`: A secure secret key
- `DEBUG`: Set to `False` in production
- `PORT`: Port number for the application

### Docker (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .`
RUN pip install -r requirements.txt

COPY . .

EXPOSE {framework_info['default_port']}

CMD ["python", "run.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [Amen CLI](https://github.com/your-username/amen-cli)
- Powered by {FRAMEWORKS[framework]['name']}

---

Happy coding! 🎉
"""
        
        self._write_file(app_path / "README.md", readme_content)
        
        # Generate CSS
        css_content = """/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

/* Header */
header {
    text-align: center;
    margin-bottom: 3rem;
    color: white;
}

header h1 {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
    font-weight: 300;
}

/* Hero Section */
.hero {
    background: white;
    padding: 3rem;
    border-radius: 15px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    text-align: center;
    margin-bottom: 3rem;
}

.hero h2 {
    color: #667eea;
    font-size: 2rem;
    margin-bottom: 1rem;
}

.hero p {
    font-size: 1.1rem;
    color: #666;
}

/* Features Grid */
.features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
}

.feature {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
}

.feature h3 {
    color: #667eea;
    font-size: 1.3rem;
    margin-bottom: 1rem;
}

.feature p {
    color: #666;
    font-size: 1rem;
}

/* Footer */
footer {
    text-align: center;
    color: white;
    opacity: 0.8;
    padding: 2rem 0;
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }
    
    header h1 {
        font-size: 2rem;
    }
    
    .hero {
        padding: 2rem;
    }
    
    .hero h2 {
        font-size: 1.5rem;
    }
    
    .features {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .feature {
        padding: 1.5rem;
    }
}

/* Animation */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.hero, .feature {
    animation: fadeInUp 0.6s ease-out;
}

.feature:nth-child(2) {
    animation-delay: 0.1s;
}

.feature:nth-child(3) {
    animation-delay: 0.2s;
}
"""
        
        self._write_file(app_path / "app" / "static" / "css" / "style.css", css_content)
        
        # Generate JavaScript
        js_content = """// Main application JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Application loaded successfully!');
    
    // Add smooth scrolling for anchor links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add click animation to features
    const features = document.querySelectorAll('.feature');
    features.forEach(feature => {
        feature.addEventListener('click', function() {
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
    
    // Health check function (example API call)
    async function checkHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            console.log('Health check:', data);
        } catch (error) {
            console.error('Health check failed:', error);
        }
    }
    
    // Uncomment to perform health check on load
    // checkHealth();
});

// Utility functions
const utils = {
    // Format date
    formatDate: (date) => {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(date);
    },
    
    // Debounce function
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Show notification (you can integrate with a toast library)
    showNotification: (message, type = 'info') => {
        console.log(`[${type.toUpperCase()}] ${message}`);
        // Implement your notification system here
    }
};

// Export for use in other scripts
window.AppUtils = utils;
"""
        self._write_file(app_path / "app" / "static" / "js" / "app.js", js_content)
        
        # Generate test files
        test_content = f"""import pytest
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

def test_basic_functionality():
    '''Test basic functionality'''
    assert True  # Replace with actual tests

class Test{app_name.replace('-', '').replace('_', '').title()}:
    '''Test class for {app_name}'''
    
    def test_app_creation(self):
        '''Test application creation'''
        # Add your app-specific tests here
        pass
    
    def test_health_endpoint(self):
        '''Test health endpoint'''
        # Add health endpoint test
        pass
"""
# Add more tests as needed

        
        self._write_file(app_path / "tests" / "__init__.py", "")
        self._write_file(app_path / "tests" / f"test_{app_name.replace('-', '_')}.py", test_content)
        
        # Generate pytest configuration
        pytest_ini = """
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts = -v --tb=short
"""
        
        self._write_file(app_path / "pytest.ini", pytest_ini)

        self._write_file(app_path / "pytest.ini", pytest_ini)

# MANIFEST.in - for including non-Python files in the package
MANIFEST_IN = """
include README.md
include LICENSE
recursive-include amen/templates *.py *.html *.css *.js *.md
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
"""