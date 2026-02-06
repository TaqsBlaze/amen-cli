"""AMEN CLI - Python Web Application Scaffolding Tool"""
import re
from pathlib import Path

def _get_version():
    """Dynamically read version from pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    try:
        with open(pyproject_path, "r") as f:
            content = f.read()
            # Match version = "x.y.z" in pyproject.toml
            match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if match:
                return match.group(1)
    except (FileNotFoundError, IOError):
        pass
    
    return "0.0.0.dev0"  # Fallback version

__version__ = _get_version()
__author__ = "Tanaka Chinengundu"

__description__ = "Inspired by the laravel installer, Python Web Application Scaffolding Tool!"
__license__ = "Modified MIT with Attribution Requirements"
__copyright__ = "Copyright (c) 2025 Tanaka Chinengundu"
__email__ = "tanakah30@gmail.com"
__url__ = "https://taqsblaze.github.io/amen-cli"
__docs__ = "https://github.com/taqsblaze/amen-cli/#readme"
__python_requires__ = ">=3.11"

SUPPORTED_FRAMEWORKS = {
    "flask": {"version": ">=2.0.0", "port": 5000},
    "fastapi": {"version": ">=0.68.0", "port": 8000}
}

# Package status
__status__ = "Development"
__maintainer__ = "Tanaka Chinengundu"
__credits__ = ["Tanaka Chinengundu"]

# Feature flags
ENABLE_LOGGING = True
DEBUG_MODE = True