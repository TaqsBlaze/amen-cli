from setuptools import setup, find_packages

setup(
    name="amen-cli",
    version="0.1.0",
    description="Laravel-inspired Python web framework scaffolding tool",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "rich>=12.0.0",
        "questionary>=1.10.0",
        "virtualenv>=20.0.0",
    ],
    entry_points={
        'console_scripts': [
            'amen=amen.cli:main',
        ],
    },
    python_requires=">=3.11",
)