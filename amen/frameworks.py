"""Framework configurations and metadata"""

FRAMEWORKS = {
    'flask': {
        'name': 'Flask',
        'description': 'Lightweight WSGI web application framework',
        'packages': ['flask', 'flask-cors', 'python-dotenv','pytest','pytest-cov','pyjwt','flask-sqlalchemy','sqlalchemy','pymysql'],
        'default_port': 5000,
        'entry_file': 'app.py',
    },
    # 'django': {
    #     'name': 'Django',
    #     'description': 'High-level Python web framework',
    #     'packages': ['django', 'django-cors-headers', 'python-dotenv'],
    #     'default_port': 8000,
    #     'entry_file': 'manage.py',
    # },
    'fastapi': {
        'name': 'FastAPI',
        'description': 'Modern, fast web framework for building APIs',
        'packages': ['fastapi', 'uvicorn[standard]', 'python-dotenv','jinja2','pytest','pytest-cov','pyjwt', 'sqlalchemy', 'pymysql'],
        'default_port': 8000,
        'entry_file': 'main.py',
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
    # },
    # 'django-hotsauce': {
    #     'name': 'Django Hotsauce',
    #     'description': 'Django-based rapid development framework',
    #     'packages': ['django', 'django-hotsauce', 'python-dotenv'],
    #     'default_port': 8000,
    #     'entry_file': 'manage.py',
    # }
}