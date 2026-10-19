"""Template management for different frameworks"""

import os
import importlib.util
from pathlib import Path
from ..frameworks import FRAMEWORKS, get_framework_packages
from .database import get_database_templates
from .welcome_page import get_welcome_files


class TemplateManager:
    def _write_file(self, path: Path, content: str | bytes):
        """Write template text as UTF-8 or preserve a bundled binary asset."""
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")

    def generate_structure(
        self,
        app_path: Path,
        framework: str,
        app_type: str,
        app_name: str,
        database: str,
    ):
        """Generate project structure based on framework and app type"""
        if framework not in FRAMEWORKS:
            raise ValueError(f"Unsupported framework: {framework}")
        if database not in {"none", "sqlite3", "mysql"}:
            raise ValueError(f"Unsupported database: {database}")

        # Create all necessary directories
        (app_path / app_name).mkdir(exist_ok=True)
        (app_path / app_name / "api").mkdir(exist_ok=True)
        (app_path / app_name / "auth").mkdir(exist_ok=True)
        # Only create models directory if using database
        if database != "none":
            (app_path / app_name / "models").mkdir(exist_ok=True)
        (app_path / app_name / "static").mkdir(exist_ok=True)
        (app_path / app_name / "static" / "uploads").mkdir(exist_ok=True)
        (app_path / app_name / "static" / "js").mkdir(exist_ok=True)
        (app_path / app_name / "static" / "css").mkdir(exist_ok=True)
        (app_path / app_name / "templates").mkdir(exist_ok=True)
        (app_path / "tests").mkdir(exist_ok=True)

        # Generate database configuration if needed
        if database != "none":
            self._generate_database_files(app_path, app_name, database, framework)

        # Generate framework-specific files with database option
        if framework == "flask":
            self._generate_flask_files(app_path, app_type, app_name, database)
        elif framework == "fastapi":
            self._generate_fastapi_files(app_path, app_type, app_name, database)

        # Generate common files with database option
        self._generate_common_files(app_path, framework, app_name, app_type, database)

    def _generate_flask_files(
        self, app_path: Path, app_type: str, app_name: str, database: str
    ):
        """Generate Flask files"""
        database_imports = ""
        database_setup = ""
        if database != "none":
            database_imports = f"""from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from {app_name}.database import DATABASE_URL
"""
            database_setup = f"""app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from {app_name}.models import Users
migrate = Migrate(app, db, render_as_batch=True)
"""

        app_content = f"""from flask import Flask, request
import os
from flask_cors import CORS
{database_imports}


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


{database_setup}

from {app_name}.api import home, health, protected
"""
        self._write_file(app_path / app_name / "__init__.py", app_content)
        self._write_file(
            app_path / "app.py",
            f"from {app_name} import app\n\nif __name__ == '__main__':\n    app.run()",
        )

        if app_type == "webapp":
            self._generate_html_template(
                app_path, app_name, framework="flask", database=database
            )

        self._generate_token_file(app_path, app_name, framework="flask")
        self._generate_endpoints_file(
            app_path, app_name, framework="flask", app_type=app_type
        )

    def _generate_fastapi_files(
        self, app_path: Path, app_type: str, app_name: str, database: str
    ):
        """Generate FastAPI files"""

        static_mount = (
            f"app.mount('/static', StaticFiles(directory='{app_name}/static'), name='static')"
            if app_type == "webapp"
            else ""
        )
        template_mount = (
            f"templates = Jinja2Templates(directory='{app_name}/templates')"
            if app_type == "webapp"
            else ""
        )

        main_content = f"""from fastapi import FastAPI
from {app_name}.api.endpoints import api_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

load_dotenv()
{"from " + app_name + ".models import Users" if database != 'none' else ""}

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
        self._write_file(app_path / app_name / "__init__.py", "")
        self._write_file(
            app_path / "app.py",
            f"import uvicorn\nfrom {app_name}.main import app\n\nif __name__ == '__main__':\n    uvicorn.run(app, host='0.0.0.0', port=8000)",
        )

        if app_type == "webapp":
            self._generate_html_template(
                app_path, app_name, framework="fastapi", database=database
            )

        self._generate_token_file(app_path, app_name, framework="fastapi")
        self._generate_endpoints_file(
            app_path, app_name, framework="fastapi", app_type=app_type
        )

    def _generate_html_template(
        self, app_path: Path, app_name: str, framework: str = "flask", database: str = "none"
    ):
        """Generate the welcome page and its local, framework-specific assets."""
        from .. import __version__

        for name, content in get_welcome_files(
            app_name, framework, database, __version__
        ).items():
            self._write_file(app_path / name, content)

    def _generate_common_files(
        self,
        app_path: Path,
        framework: str,
        app_name: str,
        app_type: str,
        database: str,
    ):
        """Generate common files for all projects"""

        # requirements.txt
        framework_info = FRAMEWORKS[framework]
        requirements = "\n".join(get_framework_packages(framework, database)) + "\n"

        self._write_file(app_path / "requirements.txt", requirements)

        # .env
        env_content = f"""SECRET_KEY=your-secret-key-here
DEBUG=True
PORT={framework_info['default_port']}
"""
        # Add database configuration only if database is selected
        if database != "none":
            env_content += f"\n# Database configuration\n"
            if database == "sqlite3":
                env_content += f"DATABASE_URL=sqlite:///instance/{app_name}.db\n"
            elif database == "mysql":
                env_content += (
                    f"DATABASE_URL=mysql+pymysql://root@localhost:3306/{app_name}\n"
                )

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
        parts = request.headers.get('Authorization', '').split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({{'message': 'Token is missing or malformed!'}}), 401
        token = parts[1]

        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            # current_user = Users.query.filter_by(public_id=data['public_id']).first()
            current_user = data  # Placeholder
        except jwt.InvalidTokenError:
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
    return templates.TemplateResponse(request=request, name='index.html', context={{'title': '{app_name}'}})
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
            self._write_file(
                app_path / app_name / "api" / "protected.py", protected_content
            )
            self._write_file(
                app_path / app_name / "api" / "endpoints.py", endpoints_content
            )

    def _generate_database_files(
        self, app_path: Path, app_name: str, database: str, framework: str
    ):
        """Generate the selected framework's database, models, and migrations."""
        for name, content in get_database_templates(
            app_name, framework, database
        ).items():
            self._write_file(app_path / name, content)


# MANIFEST.in - for including non-Python files in the package
MANIFEST_IN = """
include README.md
include LICENSE
recursive-include amen/templates *.py *.html *.css *.js *.md
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
"""
