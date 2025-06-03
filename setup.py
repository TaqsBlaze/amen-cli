from setuptools import setup, find_packages

# Read the contents of README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="amen-cli",
    version="0.6.0",
    author="Tanaka Chinengundu",
    author_email="tanakah30@gmail.com",
    description="composer-inspired Python web framework scaffolding tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://taqsblaze.github.io/amen-cli",
    packages=find_packages(exclude=["tests*", "examples*"]),
    install_requires=[
        "click>=8.0.0",
        "rich>=12.0.0",
        "questionary>=1.10.0",
        "virtualenv>=20.0.0",
        "requests>=2.25.0",
        "pyyaml>=5.4.0",
    ],
    entry_points={
        'console_scripts': [
            'amen=amen.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.900",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/taqsblaze/amen-cli/issues",
        "Source": "https://github.com/taqsblaze/amen-cli",
        "Documentation": "https://github.com/taqsblaze/amen-cli#readme",
    },
    keywords=["python", "web-framework", "cli", "scaffold", "amen", "composer", "laravel", "flask", "django", "fastapi", "bottle", "pyramid"],
    data_files=[
        ('share/applications', ['debian/amen-cli.desktop']),
        ('share/icons/hicolor/128x128/apps', ['image/icon/icon.ico']),
    ],
)