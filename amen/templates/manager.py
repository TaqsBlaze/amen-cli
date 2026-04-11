"""Template management for different frameworks"""

import os
import importlib.util
from pathlib import Path
from ..frameworks import FRAMEWORKS

class TemplateManager:
    def _write_file(self, path: Path, content: str):
        """Helper method to write files with UTF-8 encoding"""
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    def generate_structure(self, app_path: Path, framework: str, app_type: str, app_name: str, database: str):
        """Generate project structure based on framework and app type"""
        
        # Create all necessary directories
        (app_path / app_name).mkdir(exist_ok=True)
        (app_path / app_name / "api").mkdir(exist_ok=True)
        (app_path / app_name / "auth").mkdir(exist_ok=True)
        # Only create models directory if using database
        if database != 'none':
            (app_path / app_name / "models").mkdir(exist_ok=True)
        (app_path / app_name / "static").mkdir(exist_ok=True)
        (app_path / app_name / "static" / "uploads").mkdir(exist_ok=True)
        (app_path / app_name / "static" / "js").mkdir(exist_ok=True)
        (app_path / app_name / "static" / "css").mkdir(exist_ok=True)
        (app_path / app_name / "templates").mkdir(exist_ok=True)
        (app_path / "tests").mkdir(exist_ok=True)
        
        # Generate database configuration if needed
        if database != 'none':
            self._generate_database_files(app_path, app_name, database)
            
        # Generate framework-specific files with database option
        if framework == 'flask':
            self._generate_flask_files(app_path, app_type, app_name, database)
        elif framework == 'fastapi':
            self._generate_fastapi_files(app_path, app_type, app_name, database)
            
        # Generate common files with database option
        self._generate_common_files(app_path, framework, app_name, app_type, database)
    
    def _generate_flask_files(self, app_path: Path, app_type: str, app_name: str, database: str):
        """Generate Flask files"""
        database_uri = f"app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/{app_name}'"
        if database == 'sqlite3':
            database_uri = f"""os.makedirs(app.instance_path, exist_ok=True)
sqlite_path = os.path.join(app.instance_path, "{app_name}.db")
sqlite_path = sqlite_path.replace("\\\\", "/")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{{sqlite_path}}"
""" 

        app_content = f"""from flask import Flask, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate


app = Flask(__name__)
CORS(app, resources={{
    r"/*": {{
        "origins": [
            "http://192.168.1.105",
            "http://localhost",
            "http://127.0.0.1"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }}
}})

app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
{database_uri}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = "{app_name}/static/uploads"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx'}
app.config['TIMEZONE'] = 'Africa/Harare'
app.config['MAIL_SERVER'] = 'mail.your-domain.co.zw'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'noreply@your-domain.co.zw'
app.config['MAIL_PASSWORD'] = 'your-password'
app.config['MAIL_DEFAULT_SENDER'] = ('YourName', 'noreply@your-domain.co.zw')


app.app_context()
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch = True)

from {app_name}.api import home, health, protected
"""
        self._write_file(app_path / app_name / "__init__.py", app_content)
        self._write_file(app_path / "app.py", f"from {app_name} import app\n\nif __name__ == '__main__':\n    app.run()")
        
        if app_type == 'webapp':
            self._generate_html_template(app_path, app_name)
            
        self._generate_token_file(app_path, app_name, framework="flask")
        self._generate_endpoints_file(app_path, app_name, framework='flask', app_type=app_type)
    
    def _generate_fastapi_files(self, app_path: Path, app_type: str, app_name: str, database: str):
        """Generate FastAPI files"""

        static_mount = f"app.mount('/static', StaticFiles(directory='{app_name}/static'), name='static')" if app_type == 'webapp' else ""
        template_mount = f"templates = Jinja2Templates(directory='{app_name}/templates')" if app_type == 'webapp' else ""

        main_content = f"""from fastapi import FastAPI
from {app_name}.api.endpoints import api_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
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

{static_mount}
{template_mount}
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
        self._write_file(app_path / app_name / "main.py", main_content)
        self._write_file(app_path / "app.py", f"import uvicorn\nfrom {app_name}.main import app\n\nif __name__ == '__main__':\n    uvicorn.run(app, host='0.0.0.0', port=8000)")
        
        if app_type == 'webapp':
            self._generate_html_template(app_path, app_name)
        
        self._generate_token_file(app_path, app_name, framework="fastapi")
        self._generate_endpoints_file(app_path, app_name, framework='fastapi', app_type=app_type)
    
    def _generate_html_template(self, app_path: Path, app_name: str):
        """Generate HTML template"""
        # Dynamically import the __init__.py module to get the version

        from .. import __version__
        version = __version__

        template_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{app_name}</title>
    <style>
        :root {{
            --bg: #f8fafc;
            --ink: #0f172a;
            --muted: #475569;
            --line: #e2e8f0;
            --card: #ffffff;
            --brand: #ef4444;
            --brand-ink: #991b1b;
        }}
        body {{
            margin: 0;
            font-family: "Instrument Sans", "Segoe UI", sans-serif;
            color: var(--ink);
            background:
                radial-gradient(circle at 20% 20%, #fee2e2 0%, transparent 45%),
                radial-gradient(circle at 80% 0%, #dbeafe 0%, transparent 35%),
                var(--bg);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 2.5rem 1.25rem 3rem;
        }}
        .topbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
            font-size: 0.95rem;
        }}
        .badge {{
            border: 1px solid var(--line);
            background: #fff;
            border-radius: 999px;
            padding: 0.35rem 0.8rem;
        }}
        .hero {{
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 3rem 2rem;
            box-shadow: 0 25px 50px -30px rgba(15, 23, 42, 0.35);
            animation: rise 600ms ease-out;
        }}
        .hero h1 {{
            font-size: clamp(2rem, 5vw, 3.4rem);
            margin: 0;
            letter-spacing: -0.03em;
            line-height: 1.05;
        }}
        .hero p {{
            color: var(--muted);
            margin: 1.1rem 0 0;
            font-size: 1.08rem;
            max-width: 44rem;
        }}
        .cta {{
            margin-top: 1.75rem;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--brand);
            color: #fff;
            border-radius: 10px;
            padding: 0.8rem 1rem;
            text-decoration: none;
            font-weight: 600;
        }}
        .cards {{
            margin-top: 1.5rem;
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
        }}
        .card {{
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 1rem;
        }}
        .card h3 {{
            margin: 0 0 0.5rem;
            color: var(--brand-ink);
        }}
        .card p {{
            margin: 0;
            color: var(--muted);
            font-size: 0.95rem;
        }}
        .footer {{
            margin-top: 2rem;
            color: var(--muted);
            text-align: center;
        }}
        @keyframes rise {{
            from {{ opacity: 0; transform: translateY(14px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @media (max-width: 800px) {{
            .topbar {{
                flex-direction: column;
                gap: 0.75rem;
                align-items: flex-start;
            }}
            .cards {{
                grid-template-columns: 1fr;
            }}
            .hero {{
                padding: 2.2rem 1.2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="topbar">
            <span class="badge">{app_name}</span>
            <span class="badge">Amen CLI v{version}</span>
        </div>
        <section class="hero">
            <h1>Ship ideas faster with {app_name}.</h1>
            <p>Your new application is running. Start by creating endpoints, utilities, and views with structured commands and keep your project organized from day one.</p>
            <a class="cta" href="https://github.com/taqsblaze/amen-cli">Explore Amen CLI</a>
            <div class="cards">
                <article class="card">
                    <h3>Build</h3>
                    <p>Scaffold routes and utility modules without boilerplate.</p>
                </article>
                <article class="card">
                    <h3>Grow</h3>
                    <p>Add new features with the same command style as your initial setup.</p>
                </article>
                <article class="card">
                    <h3>Deploy</h3>
                    <p>Start clean, iterate quickly, and move from local to production smoothly.</p>
                </article>
            </div>
        </section>
        <footer class="footer">
            <p>&copy; {app_name} powered by Amen CLI.</p>
        </footer>
    </div>
    <script src="/static/js/app.js"></script>
</body>
</html>"""
        self._write_file(app_path / app_name / "templates" / "index.html", template_content)
    
    def _generate_common_files(self, app_path: Path, framework: str, app_name: str, app_type: str, database: str):
        """Generate common files for all projects"""
        
        # requirements.txt
        framework_info = FRAMEWORKS[framework]
        requirements = "\n".join(framework_info['packages'])
        
        # Add database dependencies only if database is selected
        if database != 'none':
            requirements += "\n# Database dependencies"
            requirements += "\nSQLAlchemy>=2.0.0"
            if database == 'mysql':
                requirements += "\nmysqlclient>=2.0.0"
        
        self._write_file(app_path / "requirements.txt", requirements)
        
        # .env
        env_content = f"""SECRET_KEY=your-secret-key-here
DEBUG=True
PORT={framework_info['default_port']}
"""
        # Add database configuration only if database is selected
        if database != 'none':
            env_content += f"\n# Database configuration\n"
            if database == 'sqlite3':
                env_content += f"DATABASE_URL=sqlite:///./{app_name}.db\n"
            elif database == 'mysql':
                env_content += f"DATABASE_URL=mysql://user:password@localhost:3306/{app_name}\n"
        
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
   python app.py
   ```

Your application will be available at `http://localhost:{framework_info['default_port']}`

## 📁 Project Structure

```
{app_name}/
├── venv/                   # Virtual environment
├── {app_name}/             # Main application code
│   ├── api/                # API module
│   ├── auth/               # Authentication module
│   ├── models/             # Models module
│   ├── static/             # Static files (CSS, JS, images)
│       ├── uploads/
│   ├── templates/          # HTML templates (if web app)
│   └── app.py              # Main application file
├── tests/                  # Test files
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (local)
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── app.py                # Application runner
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

CMD ["python", "app.py"]
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
        
        self._write_file(app_path / app_name / "static" / "css" / "style.css", css_content)
        
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
        self._write_file(app_path / app_name / "static" / "js" / "app.js", js_content)
        
        # Generate test files
        test_content = f"""import pytest
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '{app_name}'))

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

    def _generate_token_file(self, app_path: Path, app_name: str, framework: str = "flask"):
        """Generate token.py file for the selected framework"""
        if framework == "flask":
            token_content = f"""import jwt
from functools import wraps
from flask import request, jsonify
import os

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({{'message': 'Token is missing!'}}), 401

        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            # current_user = Users.query.filter_by(public_id=data['public_id']).first()
            current_user = data  # Placeholder
        except Exception:
            return jsonify({{'message': 'Token is invalid!'}}), 401

        return f(current_user, *args, **kwargs)

    return decorated
"""
        elif framework == "fastapi":
            token_content = f"""import jwt
from fastapi import Request, HTTPException, status, Depends
import os

def token_required(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing!")
    token = auth_header.split(" ")[1]
    try:
        data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
        # current_user = get_user_from_db(data['public_id'])
        current_user = data  # Placeholder
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid!")
    return current_user
"""
        else:
            token_content = "# Not implemented for this framework.\n"

        self._write_file(app_path / app_name / "auth" / "token.py", token_content)

    def _generate_endpoints_file(self, app_path: Path, app_name: str, framework: str, app_type: str):
        """Generate separated endpoint modules"""
        if framework == 'flask':
            index_content = f"""from flask import jsonify, render_template
from {app_name} import app

@app.route('/')
def index():
    {"return render_template('index.html', title='" + app_name + "')" if app_type == 'webapp' else "return jsonify({'message': 'Welcome to " + app_name + " API!'})"}
"""
            health_content = f"""from flask import jsonify
from {app_name} import app

@app.route('/health')
def health():
    return jsonify({{'status': 'healthy', 'service': '{app_name}'}})
"""
            protected_content = f"""from flask import jsonify
from {app_name}.auth.token import token_required
from {app_name} import app

@app.route('/protected')
@token_required
def protected(current_user):
    return jsonify({{'message': 'This is a protected route!', 'user': current_user}})
"""
            api_init_content = """from . import home, health, protected
"""
            self._write_file(app_path / app_name / "api" / "__init__.py", api_init_content)
            self._write_file(app_path / app_name / "api" / "home.py", index_content)
            self._write_file(app_path / app_name / "api" / "health.py", health_content)
            self._write_file(app_path / app_name / "api" / "protected.py", protected_content)
        elif framework == 'fastapi':
            if app_type == 'webapp':
                root_content = f"""from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
router = APIRouter()

@router.get("/")
async def root(request: Request):
    templates = Jinja2Templates(directory='{app_name}/templates')
    return templates.TemplateResponse('index.html', {{'request': request, 'title': '{app_name}'}})
"""
            else:
                root_content = f"""from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def root():
    return {{"message": "Welcome to {app_name} API!"}}
"""
            health_content = f"""from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
async def health():
    return {{"status": "healthy", "service": "{app_name}"}}
"""
            protected_content = f"""from fastapi import APIRouter, Depends
from {app_name}.auth.token import token_required
router = APIRouter()

@router.get("/protected")
async def protected(current_user: dict = Depends(token_required)):
    return {{"message": "This is a protected route!", "user": current_user}}
"""
            endpoints_content = """from fastapi import APIRouter
from .root import router as root_router
from .health import router as health_router
from .protected import router as protected_router

api_router = APIRouter()
api_router.include_router(root_router)
api_router.include_router(health_router)
api_router.include_router(protected_router)
"""
            self._write_file(app_path / app_name / "api" / "__init__.py", "")
            self._write_file(app_path / app_name / "api" / "root.py", root_content)
            self._write_file(app_path / app_name / "api" / "health.py", health_content)
            self._write_file(app_path / app_name / "api" / "protected.py", protected_content)
            self._write_file(app_path / app_name / "api" / "endpoints.py", endpoints_content)

    def _generate_database_files(self, app_path: Path, app_name: str, database: str):
        """Generate database configuration files"""

        # Add  model
        model_content = f"""from {app_name} import db
from datetime import datetime
import pytz

time_zone = "Africa/Harare"

class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, index=True)
    firstname = db.Column(db.String(100), nullable=False, index=True)
    lastname = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    role = db.Column(db.String(255), nullable=False, unique=False, default='user', index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(pytz.timezone(time_zone)))
    updated_at = db.Column(db.DateTime(timezone=True))
"""
        self._write_file(app_path / app_name / "models" / "models.py", model_content)

# MANIFEST.in - for including non-Python files in the package
MANIFEST_IN = """
include README.md
include LICENSE
recursive-include amen/templates *.py *.html *.css *.js *.md
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
"""
