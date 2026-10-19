"""Framework configurations and metadata"""

FRAMEWORKS = {
    "flask": {
        "name": "Flask",
        "description": "Lightweight WSGI web application framework",
        "packages": [
            "flask",
            "flask-cors",
            "python-dotenv",
            "pytest",
            "pytest-cov",
            "pyjwt",
        ],
        "default_port": 5000,
        "entry_file": "app.py",
    },
    # 'django': {
    #     'name': 'Django',
    #     'description': 'High-level Python web framework',
    #     'packages': ['django', 'django-cors-headers', 'python-dotenv'],
    #     'default_port': 8000,
    #     'entry_file': 'manage.py',
    # },
    "fastapi": {
        "name": "FastAPI",
        "description": "Modern, fast web framework for building APIs",
        "packages": [
            "fastapi>=0.108.0",
            "uvicorn[standard]",
            "python-dotenv",
            "jinja2",
            "pytest",
            "pytest-cov",
            "pyjwt",
        ],
        "default_port": 8000,
        "entry_file": "main.py",
    },
    # 'bottle': {
    #     'name': 'Bottle',
    #     'description': 'Fast, simple micro web framework',
    #     'packages': ['bottle', 'python-dotenv'],
    #     'default_port': 8080,
    #     'entry_file': 'app.py',
    # },
    # 'pyramid': {
    #     'name': 'Pyramid',
    #     'description': 'Flexible, open source web framework',
    #     'packages': ['pyramid', 'waitress', 'python-dotenv'],
    #     'default_port': 6543,
    #     'entry_file': 'app.py',
    # }
}


def get_framework_packages(framework: str, database: str = "sqlite3") -> list[str]:
    """Return the dependencies needed by the selected framework and database."""
    if database not in {"none", "sqlite3", "mysql"}:
        raise ValueError(f"Unsupported database: {database}")

    packages = list(FRAMEWORKS[framework]["packages"])
    if database != "none":
        packages.append("sqlalchemy>=2.0.0")
        if framework == "flask":
            packages.extend(["flask-sqlalchemy>=3.1.0", "flask-migrate>=4.0.0"])
        elif framework == "fastapi":
            packages.append("alembic>=1.16.0")
        if database == "mysql":
            packages.append("pymysql")
    return packages
