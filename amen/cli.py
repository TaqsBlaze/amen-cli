import os
import sys
import subprocess
import venv
from pathlib import Path

import click
import questionary
import requests  # Add this import for HTTP requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .frameworks import FRAMEWORKS
from .templates import TemplateManager

console = Console()

class PipNetworkError(Exception):
    pass

VALID_FRAMEWORKS = ['flask', 'fastapi', 'bottle', 'pyramid']
VALID_PROJECT_TYPES = ['webapp', 'api']

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
        console.print(Panel.fit(
            """AMEN: inspired by the laravel installer, a python Web Framework Scaffolding
        Create your web applications with ease!
        By [bold magenta]Tanaka Chinengundu[/bold magenta]
        [bold blue]
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
            ]
        ).ask()
    
    def get_app_name(self) -> str:
        """Get application name"""
        return questionary.text(
            "📝 Enter your application name:",
            validate=lambda x: len(x.strip()) > 0 or "Application name cannot be empty"
        ).ask().strip()
    
    def create_virtual_environment(self, app_path: Path) -> bool:
        """Create virtual environment"""
        venv_path = app_path / "venv"
        
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
            console.print(f"❌ Error creating virtual environment: {e}", style="red")
            return False
    
    def install_framework(self, app_path: Path, framework: str) -> bool:
        """Install selected framework in virtual environment"""
        venv_path = app_path / "venv"
        
        # Determine pip path based on OS
        if sys.platform == "win32":
            pip_path = venv_path / "Scripts" / "pip"
        else:
            pip_path = venv_path / "bin" / "pip"

        framework_info = FRAMEWORKS[framework]
        packages = framework_info['packages']
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Installing {framework_info['name']}...", total=None)
                
                for package in packages:
                    subprocess.run([
                        str(pip_path), "install", package
                    ], check=True, capture_output=True)
                
                progress.update(task, description=f"✅ {framework_info['name']} installed")
            
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Error installing {framework_info['name']}: {e}", style="red")
            return False
    
    def create_app(self):
        """Main app creation flow"""
        self.welcome_banner()
        
        # Get user choices
        framework = self.select_framework()
        if not framework:
            console.print("❌ No framework selected. Exiting.", style="red")
            return
            
        app_type = self.select_app_type()
        if not app_type:
            console.print("❌ No application type selected. Exiting.", style="red")
            return
            
        app_name = self.get_app_name()
        if not app_name:
            console.print("❌ No application name provided. Exiting.", style="red")
            return

        # Create application directory
        app_path = Path.cwd() / app_name
        
        if app_path.exists():
            overwrite = questionary.confirm(
                f"Directory '{app_name}' already exists. Overwrite?"
            ).ask()
            
            if not overwrite:
                console.print("❌ Operation cancelled.", style="yellow")
                return
            
            import shutil
            shutil.rmtree(app_path)

        app_path.mkdir()
        console.print(f"📁 Created directory: {app_path}", style="green")

        # Create virtual environment
        if not self.create_virtual_environment(app_path):
            return

        # Install framework
        if not self.install_framework(app_path, framework):
            return

        # Generate project structure
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating project structure...", total=None)
            self.template_manager.generate_structure(app_path, framework, app_type, app_name)
            progress.update(task, description="✅ Project structure generated")

        # Create .amen_config file
        with open(app_path / ".amen_config", "w") as f:
            f.write(framework + "\n")  

        # Success message
        console.print(Panel(
            f"""🎉 Successfully created '{app_name}'!

📁 Next Steps:
   1. cd {app_name}
   2. source venv/bin/activate  (Linux/Mac) or venv\\Scripts\\activate (Windows)
   3. amen run {app_name}

Your app will be running at http://localhost:{FRAMEWORKS[framework]['default_port']}
            """.strip(),
            title="🎊 Project Created Successfully!",
            border_style="green"
        ))

@click.group()
def main():
    """Amen - inspired by the laravel installer. Python web framework scaffolding tool"""
    pass

@main.command()
@click.option(
    "--framework", "-f",
    type=click.Choice(list(FRAMEWORKS.keys()), case_sensitive=False),
    help="Framework to use for the new project (e.g., flask, fastapi)"
)
@click.option(
    "--type", "-t",
    type=click.Choice(['webapp', 'api'], case_sensitive=False),
    help="Type of application to create (webapp or api)"
)
@click.option(
    "--name", "-n",
    type=str,
    help="Name of the application"
)
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
    """Runs the development server for a created application."""
    app_path = str(f"{Path.cwd()}\\" + app_name)

    print("App path", app_path)
    if not Path(app_path).exists() or not Path(app_path).is_dir():
        console.print(f"❌ Application '{app_name}' not found.", style="red")
        return

    venv_path = Path(app_path) / "venv"
    if not venv_path.exists() or not venv_path.is_dir():
        console.print(f"❌ Virtual environment not found for '{app_name}'.", style="red")
        console.print("   Please create the application using `amen create` first.", style="yellow")
        return

    # Determine activate script path based on OS
    if sys.platform == "win32":
        activate_script = venv_path / "Scripts" / "activate"
    else:
        activate_script = venv_path / "bin" / "activate"

    # Find the framework used by the application (read from a config file or similar)
    config_file = Path(app_path) / ".amen_config"
    if not config_file.exists():
        console.print(f"❌ Configuration file '.amen_config' not found in '{app_name}'.", style="red")
        console.print("   Please ensure the application was created with `amen create`.", style="yellow")
        return

    with open(config_file, "r") as f:
        framework = f.readline().strip() 

    if framework not in FRAMEWORKS:
        console.print(f"❌ Unsupported framework '{framework}' in '.amen_config'.", style="red")
        return

    entry_file = "run.py"
    default_port = FRAMEWORKS[framework]['default_port']

    # Construct the run command
    if sys.platform == "win32":
        run_command = f"\"{venv_path / 'Scripts' / 'python'}\" \"{str(Path(app_path) / entry_file)}\""
    else:
        run_command = f"\"{venv_path / 'bin' / 'python'}\" \"{Path(app_path) / entry_file}\""

    try:
        console.print(f"🚀 Starting '{app_name}' using {framework}...", style="green")
        # Run the application
        env = os.environ.copy()  # Copy existing environment variables
        env["PYTHONPATH"] = str(Path(app_path))  # Add app path to PYTHONPATH
        process = subprocess.Popen(run_command, shell=True, cwd=str(Path(app_path)), env=env)
        process.wait() 
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Error running the application: {e}", style="red")
    except FileNotFoundError as e:
        console.print(f"❌ Error: {e}.  Make sure {entry_file} exists.", style="red")

@main.command()
@click.argument("app_name", type=str)
def test(app_name):
    """Run tests for the specified application using pytest and generate a coverage report."""
    app_path = str(Path.cwd() / app_name)

    if not Path(app_path).exists() or not Path(app_path).is_dir():
        console.print(f"❌ Application '{app_name}' not found.", style="red")
        return

    venv_path = Path(app_path) / "venv"
    if not venv_path.exists() or not venv_path.is_dir():
        console.print(f"❌ Virtual environment not found for '{app_name}'.", style="red")
        console.print("   Please create the application using `amen create` first.", style="yellow")
        return

    # Determine pytest path based on OS
    if sys.platform == "win32":
        pytest_path = venv_path / "Scripts" / "pytest"
    else:
        pytest_path = venv_path / "bin" / "pytest"

    try:
        console.print(f"🧪 Running tests for '{app_name}'...", style="blue")
        # Run pytest with coverage
        subprocess.run(
            [str(pytest_path), "--cov=.", "--cov-report=term-missing"],
            cwd=str(Path(app_path)),
            check=True,
        )
        console.print(f"✅ Tests completed successfully for '{app_name}'.", style="green")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Tests failed: {e}", style="red")
    except FileNotFoundError as e:
        console.print(f"❌ Error: {e}. Make sure pytest is installed in the virtual environment.", style="red")

@main.command()
def check_update():
    """Check for a new version on PyPI and upgrade the package."""
    package_name = "amen-cli"  # Replace with the actual package name on PyPI
    console.print(f"🔍 Checking for updates for '{package_name}'...", style="blue")

    try:
        # Fetch the latest version from PyPI
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]

        # Get the current installed version
        current_version = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True,
        ).stdout.split("Version: ")[1].splitlines()[0]

        if current_version == latest_version:
            console.print(f"✅ You are already using the latest version ({current_version}).", style="green")
        else:
            console.print(f"⬆️ New version available: {latest_version} (current: {current_version}).", style="yellow")
            update = questionary.confirm("Do you want to update to the latest version?").ask()
            if update:
                # Run pip install to upgrade the package
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", f"{package_name}=={latest_version}"],
                    check=True,
                )
                console.print(f"✅ Successfully updated to version {latest_version}.", style="green")
            else:
                console.print("❌ Update cancelled.", style="red")
    except requests.RequestException as e:
        console.print(f"❌ Failed to fetch version information: {e}", style="red")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Failed to update the package: {e}", style="red")
    except Exception as e:
        console.print(f"❌ An unexpected error occurred: {e}", style="red")

if __name__ == "__main__":
    main()