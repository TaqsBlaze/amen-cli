import os
import sys
import subprocess
import venv
from pathlib import Path

import click
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .frameworks import FRAMEWORKS
from .templates import TemplateManager

console = Console()

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
            """AMEN: composer-inspired Python Web Framework Scaffolding
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

        # Success message
        console.print(Panel(
            f"""🎉 Successfully created '{app_name}'!

📁 Next Steps:
   1. cd {app_name}
   2. source venv/bin/activate  (Linux/Mac) or venv\\Scripts\\activate (Windows)  
   3. python run.py

Your app will be running at http://localhost:{FRAMEWORKS[framework]['default_port']}
            """.strip(),
            title="🎊 Project Created Successfully!",
            border_style="green"
        ))

@click.group()
def main():
    """Amen - composer-inspired Python web framework scaffolding tool"""
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
    # If type is provided, override the interactive prompt
    if type:
        original_select_app_type = cli.select_app_type
        cli.select_app_type = lambda: type.lower()
    # If name is provided, override the interactive prompt
    if name:
        original_get_app_name = cli.get_app_name
        cli.get_app_name = lambda: name
    cli.create_app()

if __name__ == "__main__":
    main()