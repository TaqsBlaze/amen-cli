import os
import sys
import subprocess
import tempfile
import venv
from pathlib import Path
import re
import keyword
import math
import time
import psutil
from datetime import datetime
from rich.live import Live
from rich.table import Table
from rich import box

import click
import questionary
import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from . import __version__

from .frameworks import FRAMEWORKS, get_framework_packages
from .templates import TemplateManager
from .editor import edit_file

console = Console()

PACKAGE_CACHE_DIR = Path.home() / ".amen" / "package_cache"
PACKAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)


class PipNetworkError(Exception):
    pass


class ProjectExistsError(click.ClickException):
    """Report a creation conflict without allowing a noninteractive overwrite."""


class CommandExecutionError(click.ClickException):
    """Report a failed subprocess while preserving its shell exit status."""

    def __init__(self, message: str, returncode: int = 1):
        super().__init__(message)
        self.exit_code = returncode if returncode > 0 else 128 - returncode


def _process_failure(message, result):
    """Build a command error using captured diagnostics when available."""
    details = result.stderr or result.stdout or str(result)
    if isinstance(details, bytes):
        details = details.decode("utf-8", errors="replace")
    return CommandExecutionError(f"{message}: {details.strip()}", result.returncode)


def _project_path(app_name):
    """Find an existing project or report a command failure."""
    path = Path.cwd() / app_name
    if not path.is_dir():
        raise click.ClickException(f"Application '{app_name}' not found.")
    return path


def _project_environment(app_path):
    """Require a project's virtual environment before invoking its tools."""
    path = get_venv_path(app_path)
    if not path.is_dir():
        raise click.ClickException(
            f"Virtual environment not found for '{app_path.name}'."
        )
    return path


def _project_framework(app_path):
    """Read and validate the framework from legacy project metadata."""
    config_file = app_path / ".amen_config"
    try:
        with config_file.open(encoding="utf-8") as config:
            framework = config.readline().strip()
    except (OSError, UnicodeError) as error:
        raise click.ClickException(f"Cannot read '{config_file}': {error}") from error
    if framework not in FRAMEWORKS:
        raise click.ClickException(
            f"Unsupported framework '{framework}' in '.amen_config'."
        )
    return framework


VALID_FRAMEWORKS = ["flask", "fastapi", "bottle", "pyramid"]
VALID_PROJECT_TYPES = ["webapp", "api"]


def get_venv_path(app_path: Path) -> Path:
    """Get virtual environment path based on OS"""
    return app_path / "venv"


def get_pip_path(venv_path: Path) -> Path:
    """Get pip executable path based on OS"""
    if sys.platform.startswith('linux'):
        return venv_path / "bin" / "pip"
    return venv_path / "Scripts" / "pip"

def get_python_path(venv_path: Path) -> Path:
    """Get python executable path based on OS"""
    if sys.platform.startswith('linux'):
        return venv_path / "bin" / "python"
    return venv_path / "Scripts" / "python"

def get_flask_path(venv_path: Path) -> Path:
    """Get flask executable path based on OS"""
    if sys.platform.startswith('linux'):
        return venv_path / "bin" / "flask"
    return venv_path / "Scripts" / "flask"


def _write_registration_file(path: Path, content: str):
    """Replace registration text atomically, preserving the original file on failure."""
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(content)
        temporary_path.chmod(path.stat().st_mode & 0o777)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def register_flask_module(project_root: Path, app_name: str, module_name: str):
    """Register a Flask endpoint module in package init."""
    init_file = project_root / app_name / "__init__.py"
    if not init_file.exists():
        return

    content = init_file.read_text(encoding="utf-8")
    if module_name in content:
        return

    import_line = f"from {app_name}.api import "
    lines = content.splitlines()
    changed = False
    for index, line in enumerate(lines):
        if line.startswith(import_line):
            lines[index] = line + f", {module_name}"
            changed = True
            break

    if not changed:
        lines.append(f"{import_line}{module_name}")

    _write_registration_file(init_file, "\n".join(lines) + "\n")


def register_fastapi_module(project_root: Path, app_name: str, module_name: str):
    """Register a FastAPI router module in api/endpoints.py."""
    endpoints_file = project_root / app_name / "api" / "endpoints.py"
    if not endpoints_file.exists():
        return

    content = endpoints_file.read_text(encoding="utf-8")
    import_line = f"from .{module_name} import router as {module_name}_router"
    include_line = f"api_router.include_router({module_name}_router)"

    if import_line not in content:
        content = content + "\n" + import_line
    if include_line not in content:
        content = content + "\n" + include_line + "\n"

    _write_registration_file(endpoints_file, content)


def create_project(path, framework, project_type):
    """
    Create a new project with the specified framework and type.
    
    Args:
        path (str): Project directory path
        framework (str): Web framework to use
        project_type (str): Type of project (webapp/api)
    """
    if framework not in VALID_FRAMEWORKS:
        raise ValueError(f"Invalid framework. Choose from: {VALID_FRAMEWORKS}")
    
    if project_type not in VALID_PROJECT_TYPES:
        raise ValueError(f"Invalid project type. Choose from: {VALID_PROJECT_TYPES}")

    # Create project directory
    os.makedirs(path, exist_ok=True)
    
    # Create basic structure
    os.makedirs(os.path.join(path, "app"), exist_ok=True)
    os.makedirs(os.path.join(path, "app", "templates"), exist_ok=True)
    os.makedirs(os.path.join(path, "app", "static"), exist_ok=True)
    
    # Create empty files
    open(os.path.join(path, "requirements.txt"), 'a').close()
    open(os.path.join(path, "README.md"), 'a').close()

class AmenCLI:
    def __init__(self):
        self.template_manager = TemplateManager()

    def welcome_banner(self):
        """Display welcome banner"""
        from . import __version__
        console.print(Panel.fit(
            f"""AMEN: A python Web Application Scaffolding [magenta]tool[/magenta]
        Create your web applications with ease!
        By [bold magenta]Tanaka Chinengundu[/bold magenta]
        [bold blue]Version: {__version__}[/bold blue]
            """,
            border_style="magenta"
        ))
        console.print()

    def select_framework(self) -> str:
        """Interactive framework selection"""
        frameworks = list(FRAMEWORKS.keys())

        choice = questionary.select(
            "🚀 Select a web framework:",
            choices=[
                questionary.Choice(f"{FRAMEWORKS[fw]['name']} - {FRAMEWORKS[fw]['description']}", fw)
                for fw in frameworks
            ]
        ).ask()

        return choice

    def select_app_type(self) -> str:
        """Select application type"""
        return questionary.select(
            "🏗️  What type of application?",
            choices=[
                questionary.Choice("Full Web Application (with frontend)", "webapp"),
                questionary.Choice("API Only", "api"),
            ],
        ).ask()

    def get_app_name(self) -> str:
        """Get application name"""
        answer = questionary.text(
            "📝 Enter your application name:",
            validate=lambda x: len(x.strip()) > 0 or "Application name cannot be empty",
        ).ask()
        return (answer or "").strip()

    def select_database(self) -> str:
        """Select database type"""
        return questionary.select(
            "💾 Select a database:",
            choices=[
                questionary.Choice(
                    "SQLite3 - Lightweight, serverless database", "sqlite3"
                ),
                questionary.Choice("MySQL - Robust client-server database", "mysql"),
                questionary.Choice("None - No database", "none"),
            ],
        ).ask()

    def create_virtual_environment(self, app_path: Path) -> bool:
        """Create virtual environment"""
        venv_path = get_venv_path(app_path)

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Creating virtual environment...", total=None)
                venv.create(venv_path, with_pip=True)
                progress.update(task, description="✅ Virtual environment created")

            return True
        except Exception as e:
            raise click.ClickException(
                f"Error creating virtual environment: {e}"
            ) from e

    def _cache_packages(self, packages: list[str], progress: Progress, task_id: int):
        """Cache packages to the PACKAGE_CACHE_DIR."""
        try:
            progress.update(task_id, description="Caching packages...")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "download",
                    "--no-cache-dir",
                    "-d",
                    str(PACKAGE_CACHE_DIR),
                    *packages,
                ],
                check=True,
                capture_output=True,
            )
            progress.update(task_id, description="Packages cached")
        except subprocess.CalledProcessError:
            # Silently ignore caching errors
            console.print(
                "Error caching packages (network issue). Proceeding with available cache.",
                style="yellow",
            )
            progress.update(task_id, description="Error caching packages")
        except OSError as e:
            console.print(f"Network error during caching: {e}", style="red")
            progress.update(task_id, description="Network error during caching")

    def install_framework(
        self, app_path: Path, framework: str, database: str = "sqlite3"
    ) -> bool:
        """Install selected framework in virtual environment"""
        venv_path = get_venv_path(app_path)
        pip_path = get_pip_path(venv_path)

        framework_info = FRAMEWORKS[framework]
        packages = get_framework_packages(framework, database)

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task_id = progress.add_task(
                    f"Installing {framework_info['name']}...", total=None
                )

                progress.update(
                    task_id,
                    description=f"Installing {framework_info['name']} from cache...",
                )
                try:
                    subprocess.run(
                        [
                            str(pip_path),
                            "install",
                            "--no-index",
                            "--find-links",
                            str(PACKAGE_CACHE_DIR),
                            *packages,
                        ],
                        check=True,
                        capture_output=True,
                    )
                    progress.update(
                        task_id, description=f"{framework_info['name']} installed"
                    )
                    return True
                except subprocess.CalledProcessError:
                    console.print(
                        "Required packages not fully available in cache. Falling back to internet install.",
                        style="yellow",
                    )

                progress.update(
                    task_id,
                    description=f"Installing {framework_info['name']} from internet...",
                )
                subprocess.run(
                    [str(pip_path), "install", *packages],
                    check=True,
                    capture_output=True,
                )

                self._cache_packages(packages, progress, task_id)
                progress.update(
                    task_id, description=f"{framework_info['name']} installed"
                )

            return True
        except subprocess.CalledProcessError as e:
            raise _process_failure(
                f"Error installing {framework_info['name']}", e
            ) from e
        except OSError as e:
            raise click.ClickException(
                f"Could not install {framework_info['name']}: {e}"
            ) from e

    def create_app(self, *, interactive=True) -> Path:
        """Create an app, returning its path only after every setup step succeeds."""
        self.welcome_banner()

        # Get user choices
        framework = self.select_framework()
        if not framework:
            raise click.ClickException("Framework selection cancelled.")
        if framework not in FRAMEWORKS:
            raise click.BadParameter(f"Unsupported framework: {framework}")

        app_type = self.select_app_type()
        if not app_type:
            raise click.ClickException("Application type selection cancelled.")
        if app_type not in VALID_PROJECT_TYPES:
            raise click.BadParameter(f"Unsupported application type: {app_type}")

        app_name = self.get_app_name()
        if not app_name:
            raise click.BadParameter("Application name cannot be empty.")
        app_name = app_name.strip()
        if "-" in app_name:
            # replace - with _ in application name to prevent import errors and application crush
            console.print(
                "⚠️ Renaming application to python compatible naming convernsion",
                style="yellow",
            )
            app_name = app_name.replace("-", "_")
            console.print(f"✅ New application name: {app_name}", style="green")
        if " " in app_name:
            # replace space with _ in application name
            console.print(
                "⚠️ Renaming application to python compatible naming convernsion",
                style="yellow",
            )
            app_name = app_name.replace(" ", "_")
            console.print(f"✅ New application name: {app_name}", style="green")

        if not app_name.isidentifier() or keyword.iskeyword(app_name):
            raise click.BadParameter(
                "Application name must be a valid Python package name."
            )

        database = self.select_database()
        if not database:
            raise click.ClickException("Database selection cancelled.")
        if database not in {"none", "sqlite3", "mysql"}:
            raise click.BadParameter(f"Unsupported database: {database}")

        # Create application directory
        app_path = Path.cwd() / app_name

        if app_path.is_symlink() or (app_path.exists() and not app_path.is_dir()):
            raise ProjectExistsError(f"Project path already exists: {app_path}")
        if app_path.exists():
            if not interactive:
                raise ProjectExistsError(
                    f"Project directory already exists: {app_path}"
                )
            overwrite = questionary.confirm(
                f"Directory '{app_name}' already exists. Overwrite?"
            ).ask()

            if not overwrite:
                raise click.ClickException("Project creation cancelled.")

            import shutil

            shutil.rmtree(app_path)

        try:
            app_path.mkdir()
            console.print(f"📁 Created directory: {app_path}", style="green")

            if not self.create_virtual_environment(app_path):
                raise click.ClickException("Virtual environment creation failed.")
            if not self.install_framework(app_path, framework, database):
                raise click.ClickException("Framework installation failed.")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating project structure...", total=None)
                self.template_manager.generate_structure(
                    app_path, framework, app_type, app_name, database
                )
                progress.update(task, description="✅ Project structure generated")

            (app_path / ".amen_config").write_text(framework + "\n", encoding="utf-8")
        except (OSError, ValueError) as error:
            raise click.ClickException(
                f"Could not create project '{app_name}': {error}"
            ) from error

        console.print(
            Panel(
                f"""🎉 Successfully created '{app_name}'!

📁 Next Steps:
   1.  cd {app_name}
   2. source venv/bin/activate  (Linux/Mac) or venv\\Scripts\\activate (Windows)
   3. python app.py
                                            Or
    Before you cd into application folder:
    amen run {app_name}
   
Your app will be running at http://localhost:{FRAMEWORKS[framework]['default_port']}
            """.strip(),
                title="🎊 Project Created Successfully!",
                border_style="green",
            )
        )
        return app_path


@click.group()
def main():
    """Amen - inspired by the laravel installer. Python web framework scaffolding tool"""
    pass


@main.command()
@click.option(
    "--framework",
    "-f",
    type=click.Choice(list(FRAMEWORKS.keys()), case_sensitive=False),
    help="Framework to use for the new project (e.g., flask, fastapi)",
)
@click.option(
    "--type",
    "-t",
    type=click.Choice(["webapp", "api"], case_sensitive=False),
    help="Type of application to create (webapp or api)",
)
@click.option("--name", "-n", type=str, help="Name of the application")
def create(framework, type, name):
    """Create a new web application"""
    cli = AmenCLI()
    # If framework is provided, override the interactive prompt
    if framework:
        original_select_framework = cli.select_framework
        cli.select_framework = lambda: framework.lower()

    if type:
        original_select_app_type = cli.select_app_type
        cli.select_app_type = lambda: type.lower()

    if name:
        original_get_app_name = cli.get_app_name
        cli.get_app_name = lambda: name
    cli.create_app()


@main.command()
@click.argument("app_name", type=str)
def run(app_name):
    """Run a project's server and propagate its exit status."""
    app_path = _project_path(app_name)
    venv_path = _project_environment(app_path)
    framework = _project_framework(app_path)
    python_path = get_python_path(venv_path)
    entry_file = app_path / "app.py"
    if not python_path.is_file():
        raise click.ClickException(f"Application Python not found: {python_path}")
    if not entry_file.is_file():
        raise click.ClickException(f"Application runner not found: {entry_file}")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(app_path)
    console.print(f"Starting '{app_name}' using {framework}...", style="green")
    try:
        subprocess.run(
            [str(python_path), str(entry_file)], cwd=str(app_path), env=env, check=True
        )
    except subprocess.CalledProcessError as error:
        raise _process_failure("Application failed", error) from error
    except OSError as error:
        raise click.ClickException(f"Could not run application: {error}") from error


def _preflight_scaffold_paths(project_root, new_files, updated_files=()):
    """Check every scaffold destination before creating or changing files."""
    for path in new_files:
        if path.exists() or path.is_symlink():
            raise click.ClickException(f"Refusing to overwrite existing path: {path}")
    for path in updated_files:
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise click.ClickException(
                f"Cannot update scaffold registration path: {path}"
            )
    for path in [*new_files, *updated_files]:
        parent = path.parent
        while parent != project_root.parent:
            if parent.is_symlink():
                raise click.ClickException(
                    f"Refusing to write through symlink: {parent}"
                )
            if parent.exists() and not parent.is_dir():
                raise click.ClickException(
                    f"Scaffold parent is not a directory: {parent}"
                )
            parent = parent.parent


def _write_new_scaffold_files(files, register=None):
    """Create scaffold files exclusively and remove partial output on failure."""
    created = []
    created_directories = []
    try:
        for path, content in files.items():
            missing_directories = []
            parent = path.parent
            while not parent.exists():
                missing_directories.append(parent)
                parent = parent.parent
            path.parent.mkdir(parents=True, exist_ok=True)
            created_directories.extend(reversed(missing_directories))
            with path.open("x", encoding="utf-8") as handle:
                created.append(path)
                handle.write(content)
        if register is not None:
            register()
    except (OSError, UnicodeError) as error:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        for directory in reversed(created_directories):
            try:
                directory.rmdir()
            except OSError:
                pass  # Preserve directories that another process has populated.
        raise click.ClickException(f"Could not create scaffold: {error}") from error


@main.command()
@click.argument("app_name", type=str)
@click.argument(
    "item_type", type=click.Choice(["endpoint", "util", "view"], case_sensitive=False)
)
@click.argument("name", type=str)
def add(app_name, item_type, name):
    """Add endpoint, util, or view scaffolding without replacing existing files."""
    app_path = _project_path(app_name)

    module_name = name.strip().replace("-", "_").replace(" ", "_")
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", module_name):
        raise click.BadParameter("Invalid name. Use letters, numbers, and underscores only.")

    framework = _project_framework(app_path)
    item_type = item_type.lower()
    package_dir = app_path / app_name
    files = {}
    updated_files = []

    if item_type == "util":
        util_file = package_dir / "utils" / f"{module_name}.py"
        initializer = util_file.parent / "__init__.py"
        files[util_file] = f'''def run():
    """Utility entry point for {module_name}."""
    print("Running {module_name} utility")
'''
        if initializer != util_file:
            if initializer.exists() or initializer.is_symlink():
                updated_files.append(initializer)
            else:
                files[initializer] = ""
    elif framework in ("flask", "fastapi"):
        endpoint_file = package_dir / "api" / f"{module_name}.py"
        if framework == "flask":
            updated_files.append(package_dir / "__init__.py")
            if item_type == "view":
                files[endpoint_file] = f"""from flask import render_template
from {app_name} import app

@app.route('/{module_name}')
def {module_name}():
    return render_template('{module_name}.html')
"""
            else:
                files[endpoint_file] = f"""from flask import jsonify
from {app_name} import app

@app.route('/{module_name}')
def {module_name}():
    return jsonify({{'message': '{module_name} endpoint'}})
"""
        else:
            updated_files.append(package_dir / "api" / "endpoints.py")
            if item_type == "view":
                files[endpoint_file] = f"""from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

@router.get('/{module_name}')
async def {module_name}(request: Request):
    templates = Jinja2Templates(directory='{app_name}/templates')
    return templates.TemplateResponse(request=request, name='{module_name}.html', context={{'title': '{module_name}'}})
"""
            else:
                files[endpoint_file] = f"""from fastapi import APIRouter

router = APIRouter()

@router.get('/{module_name}')
async def {module_name}():
    return {{'message': '{module_name} endpoint'}}
"""
        if item_type == "view":
            template_file = package_dir / "templates" / f"{module_name}.html"
            files[template_file] = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{module_name}</title>
</head>
<body>
    <h1>{module_name.title()} page</h1>
</body>
</html>
"""
    else:
        raise click.ClickException(
            f"Unsupported framework '{framework}' for add command."
        )

    _preflight_scaffold_paths(app_path, files, updated_files)
    register = None
    if item_type != "util":
        if framework == "flask":
            register = lambda: register_flask_module(app_path, app_name, module_name)
        else:
            register = lambda: register_fastapi_module(app_path, app_name, module_name)
    _write_new_scaffold_files(files, register)
    console.print(f"Added {item_type}: {next(iter(files))}", style="green")


@main.command()
@click.argument("app_name", type=str)
def test(app_name):
    """Run project tests and propagate pytest's exit status."""
    app_path = _project_path(app_name)
    python_path = get_python_path(_project_environment(app_path))
    try:
        console.print(f"Running tests for '{app_name}'...", style="blue")
        subprocess.run(
            [str(python_path), "-m", "pytest", "--cov=.", "--cov-report=term-missing"],
            cwd=str(app_path),
            check=True,
        )
    except subprocess.CalledProcessError as error:
        raise _process_failure("Tests failed", error) from error
    except OSError as error:
        raise click.ClickException(f"Could not run tests: {error}") from error
    console.print(f"Tests completed successfully for '{app_name}'.", style="green")


@main.command()
def update():
    """Check for an update and report failed lookups or installations."""
    package_name = "amen-cli"
    console.print(f"Checking for updates for '{package_name}'...", style="blue")
    try:
        response = requests.get(
            f"https://pypi.org/pypi/{package_name}/json", timeout=10
        )
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]
        if not isinstance(latest_version, str) or not latest_version:
            raise ValueError("The package index returned no version")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True,
            check=True,
        )
        current_version = result.stdout.split("Version: ")[1].splitlines()[0]
        if current_version == latest_version:
            console.print(
                f"You are already using the latest version ({current_version}).",
                style="green",
            )
            return
        console.print(
            f"New version available: {latest_version} (current: {current_version}).",
            style="yellow",
        )
        if not questionary.confirm(
            "Do you want to update to the latest version?"
        ).ask():
            raise click.ClickException("Update cancelled.")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Installing update...", total=None)
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--use-feature=fast-deps",
                    "--upgrade",
                    "--user",
                    f"{package_name}=={latest_version}",
                ],
                check=True,
                capture_output=True,
            )
            progress.update(task, description="Update completed")
    except requests.RequestException as error:
        raise click.ClickException(
            f"Failed to fetch version information: {error}"
        ) from error
    except subprocess.CalledProcessError as error:
        raise _process_failure("Update command failed", error) from error
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        raise click.ClickException(
            f"Could not check or install update: {error}"
        ) from error
    console.print(f"Successfully updated to version {latest_version}.", style="green")


@main.command
def about():
    """Show information about amen-cli"""
    from . import (
        __version__,
        __description__,
        __author__,
        __url__,
        SUPPORTED_FRAMEWORKS,
    )

    console.print(
        Panel.fit(
            f"""
                    Current version: [blue]{__version__}[/blue]
                    Description: [white]{__description__}[/white]
                    Developed by: [bold magenta]{__author__}[/bold magenta]
                    Project URL: [bright_cyan][link={__url__}]{__url__}[/link][/bright_cyan]
                            """,
            style="green",
        )
    )


@main.command()
@click.argument("app_name", type=str)
@click.option(
    "--framework",
    "-f",
    type=click.Choice(list(FRAMEWORKS.keys()), case_sensitive=False),
    help="Specify the framework (flask, fastapi, etc.). If not provided, it will be detected from .amen_config.",
)
def config(app_name, framework):
    """Open project configuration and report editor or filesystem failures."""
    app_path = _project_path(app_name)
    config_file = app_path / ".env"
    try:
        if not config_file.exists():
            config_file.touch()
        console.print(f"Opening .env for '{app_name}' in Ring editor.", style="green")
        edit_file(str(config_file))
    except Exception as error:
        raise click.ClickException(f"Failed to open .env file: {error}") from error


@main.command()
@click.argument("app_name", type=str)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["txt", "json", "csv", "xml"], case_sensitive=False),
    default="txt",
    help="Output format for the security audit report",
)
@click.option(
    "--severity",
    "-s",
    type=click.Choice(["low", "l", "m", "h", "medium", "high"], case_sensitive=False),
    help="Filter issues by severity level",
)
@click.option("--output", "-o", type=str, help="Save audit report to specified file")
def audit(app_name, format, severity, output):
    """Run Bandit, returning 1 for findings and the tool's status for failures."""
    app_path = _project_path(app_name)
    venv_path = _project_environment(app_path)
    command = [
        sys.executable,
        "-m",
        "bandit",
        "-r",
        str(app_path),
        "-x",
        str(venv_path),
    ]
    if format != "txt":
        command.extend(["-f", format])
    if severity:
        severity_names = {"l": "low", "m": "medium", "h": "high"}
        command.extend(["--severity-level", severity_names.get(severity, severity)])
    if output:
        command.extend(["-o", output])
    try:
        result = subprocess.run(
            command, cwd=str(app_path), capture_output=True, text=True
        )
    except OSError as error:
        raise click.ClickException(f"Could not run security audit: {error}") from error
    if result.returncode not in (0, 1):
        raise _process_failure("Security audit failed", result)
    if not output:
        if result.stdout:
            click.echo(result.stdout, nl=False)
        if result.stderr:
            click.echo(result.stderr, err=True, nl=False)
    else:
        console.print(f"Audit report saved to: {output}", style="green")
    if result.returncode == 1:
        raise click.exceptions.Exit(1)


@main.command()
@click.option(
    "--port",
    "-p",
    default=5050,
    type=click.IntRange(1, 65535),
    help="Port to run the web interface on",
)
def web(port):
    """Launch project creation and report startup failures."""
    try:
        from .web import run_web_interface

        run_web_interface(port)
    except click.ClickException:
        raise
    except Exception as error:
        raise click.ClickException(f"Error starting web interface: {error}") from error


@main.command()
@click.option(
    "--port",
    "-p",
    default=5000,
    type=click.IntRange(1, 65535),
    help="Port to run web documentation on",
)
def docs(port):
    """Launch offline documentation and report startup failures."""
    try:
        from .web import run_web_docs

        run_web_docs(port)
    except click.ClickException:
        raise
    except Exception as error:
        raise click.ClickException(
            f"Error starting documentation interface: {error}"
        ) from error


@main.command()
@click.argument("app_name", type=str)
@click.option("--port", "-p", type=click.IntRange(1, 65535), help="Port to monitor")
@click.option(
    "--refresh", "-r", type=float, default=0.1, help="Refresh rate in seconds"
)
@click.option("--web", is_flag=True, help="Run web-based monitor")
def monitor(app_name, port, refresh, web):
    """Monitor application status and resource usage"""
    app_path = _project_path(app_name)
    if not math.isfinite(refresh) or refresh <= 0:
        raise click.BadParameter(
            "Refresh interval must be a finite number greater than zero.",
            param_hint="--refresh",
        )

    try:
        if web:
            from .monitor_web import run_monitor_web

            run_monitor_web(app_name=app_name, port=port, refresh=refresh)
            return

        def get_process_info(port):
            """Get process information for the given port"""
            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent"]
            ):
                try:
                    for conn in proc.net_connections():
                        if conn.laddr.port == port:
                            return proc
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return None

        def generate_table(proc):
            """Generate rich table with monitoring data"""
            table = Table(
                title=f"Application Monitor - {app_name}",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold magenta",
            )

            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            if proc:
                table.add_row("Status", "[green]Running[/green]")
                table.add_row("PID", str(proc.pid))
                table.add_row("CPU Usage", f"{proc.cpu_percent()}%")
                table.add_row("Memory Usage", f"{proc.memory_percent():.1f}%")

                # Add memory details
                mem_info = proc.memory_info()
                table.add_row("RSS Memory", f"{mem_info.rss / (1024*1024):.1f} MB")
                table.add_row("VMS Memory", f"{mem_info.vms / (1024*1024):.1f} MB")

                # Add thread count
                table.add_row("Threads", str(proc.num_threads()))

                # Add open files count
                try:
                    table.add_row("Open Files", str(len(proc.open_files())))
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    table.add_row("Open Files", "N/A")
            else:
                table.add_row("Status", "[red]Not Running[/red]")

            return table

        console.print(f"🔍 Monitoring {app_name}...", style="blue")
        console.print(f"Press Ctrl+C to stop monitoring", style="yellow")

        with Live(refresh_per_second=1 / refresh) as live:
            while True:
                proc = get_process_info(port) if port else None
                live.update(generate_table(proc))
                time.sleep(refresh)

    except KeyboardInterrupt:
        console.print("\n✋ Monitoring stopped", style="yellow")
    except Exception as e:
        raise click.ClickException(f"Monitoring failed: {e}") from e


@main.command()
@click.argument("app_name", type=str)
def migrate(app_name):
    """Generate and apply migrations using the application's framework."""
    app_path = Path.cwd() / app_name
    if not app_path.is_dir():
        raise click.ClickException(f"Application '{app_name}' not found.")

    config_file = app_path / ".amen_config"
    if not config_file.is_file():
        raise click.ClickException(
            f"Configuration file '.amen_config' not found in '{app_name}'."
        )
    framework = config_file.read_text(encoding="utf-8").strip()
    if framework not in ("flask", "fastapi"):
        raise click.ClickException(
            f"Migrations are not supported for framework '{framework}'."
        )
    package_name = app_path.name
    if not (app_path / package_name / "models").is_dir():
        raise click.ClickException(
            f"Application '{app_name}' has no database configured."
        )

    python_path = get_python_path(get_venv_path(app_path))
    if not python_path.is_file():
        raise click.ClickException(
            f"Application Python not found: {python_path}. Create the project's virtual environment first."
        )

    if framework == "flask":
        command = [str(python_path), "-m", "flask", "--app", package_name, "db"]
        commands = []
        if not (app_path / "migrations").exists():
            commands.append([*command, "init"])
        commands.extend([[*command, "migrate"], [*command, "upgrade"]])
    else:
        if not (app_path / "alembic.ini").is_file():
            raise click.ClickException(
                "Alembic configuration is missing. Add alembic.ini and a migration environment "
                "for this FastAPI project, or generate a new project with database support."
            )
        command = [str(python_path), "-m", "alembic"]
        commands = [
            [*command, "revision", "--autogenerate", "-m", "Auto migration"],
            [*command, "upgrade", "head"],
        ]

    try:
        for command in commands:
            subprocess.run(
                command,
                cwd=str(app_path),
                check=True,
                capture_output=True,
                text=True,
            )
    except subprocess.CalledProcessError as error:
        raise _process_failure("Migration failed", error) from error
    except OSError as error:
        raise click.ClickException(f"Could not run migrations: {error}") from error

    console.print("Database upgraded successfully", style="green")


@main.command()
@click.argument("app_name", type=str)
@click.argument("package", type=str)
def install(app_name, package):
    """Install a project package; optional cache failures do not hide install errors."""
    app_path = _project_path(app_name)
    pip_path = get_pip_path(_project_environment(app_path))
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Caching {package}...", total=None)
            try:
                subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "download",
                        "--no-cache-dir",
                        "-d",
                        str(PACKAGE_CACHE_DIR),
                        package,
                    ],
                    check=True,
                    capture_output=True,
                )
            except (subprocess.CalledProcessError, OSError):
                console.print(
                    f"Could not cache {package}; continuing with installation.",
                    style="yellow",
                )
            progress.update(task, description=f"Installing {package}...")
            subprocess.run(
                [str(pip_path), "install", package], check=True, capture_output=True
            )
            progress.update(task, description=f"{package} installed")
    except subprocess.CalledProcessError as error:
        raise _process_failure(f"Failed to install {package}", error) from error
    except OSError as error:
        raise click.ClickException(f"Could not install package: {error}") from error
    console.print(f"Successfully installed {package} in '{app_name}'.", style="green")


if __name__ == "__main__":
    main()
