__version__ = "0.1.0"
__author__ = "Tanaka Chinengundu"

__description__ = "A composer-inspired Python Web Framework Scaffolding Tool"
__license__ = "Modified MIT with Attribution Requirements"
__copyright__ = "Copyright (c) 2025 Tanaka Chinengundu"
__email__ = "tanakah30@gmail.com"
__url__ = "https://github.com/taqsblaze/amen-cli"
__docs__ = "https://github.com/taqsblaze/amen-cli/#readme"
__python_requires__ = ">=3.7"

SUPPORTED_FRAMEWORKS = {
    "flask": {"version": ">=2.0.0", "port": 5000},
    "django": {"version": ">=4.0.0", "port": 8000},
    "fastapi": {"version": ">=0.68.0", "port": 8000},
    "bottle": {"version": ">=0.12.0", "port": 8080},
    "pyramid": {"version": ">=2.0.0", "port": 6543}
}

# Package status
__status__ = "Development"
__maintainer__ = "Tanaka Chinengundu"
__credits__ = ["Tanaka Chinengundu"]

# Feature flags
ENABLE_LOGGING = True
DEBUG_MODE = False