from flask import Flask, render_template, request, jsonify, url_for
import click
import webbrowser
import threading
import socket
from pathlib import Path
from .frameworks import FRAMEWORKS
from . import __version__
from .cli import AmenCLI, ProjectExistsError
from rich.console import Console
console = Console()
app = Flask(__name__)


def find_free_port(start_port):
        """Find next available port if default is taken"""
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', start_port))
                    return start_port
            except OSError:
                start_port += 1


@app.route("/")
def home():
    frameworks = {k: v["name"] for k, v in FRAMEWORKS.items()}
    return render_template("creator.html", frameworks=frameworks, version=__version__)


@app.route("/api/create", methods=["POST"])
def create_project():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return (
            jsonify(
                {"status": "error", "message": "Request body must be a JSON object."}
            ),
            400,
        )

    values = {}
    for field in ("framework", "type", "name", "database"):
        value = data.get(field, "sqlite3" if field == "database" else None)
        if not isinstance(value, str) or not value.strip():
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"'{field}' must be a nonempty string.",
                    }
                ),
                400,
            )
        values[field] = value.strip() if field == "name" else value.strip().lower()
    choices = {
        "framework": FRAMEWORKS,
        "type": {"webapp", "api"},
        "database": {"none", "sqlite3", "mysql"},
    }
    for field, allowed in choices.items():
        if values[field] not in allowed:
            return (
                jsonify(
                    {"status": "error", "message": f"Invalid {field}: {values[field]}"}
                ),
                400,
            )

    try:
        cli = AmenCLI()
        cli.select_framework = lambda: values["framework"]
        cli.select_app_type = lambda: values["type"]
        cli.get_app_name = lambda: values["name"]
        cli.select_database = lambda: values["database"]
        project_path = cli.create_app(interactive=False)
        if not isinstance(project_path, Path) or not project_path.is_dir():
            raise click.ClickException("Project creation did not complete.")
    except click.BadParameter as error:
        return jsonify({"status": "error", "message": error.format_message()}), 400
    except ProjectExistsError as error:
        return jsonify({"status": "error", "message": error.format_message()}), 409
    except click.ClickException as error:
        return jsonify({"status": "error", "message": error.format_message()}), 500
    except Exception:
        app.logger.exception("Project creation failed")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Project creation failed. Check the server log for details.",
                }
            ),
            500,
        )

    return jsonify(
        {
            "status": "success",
            "message": f"Project {project_path.name} created successfully",
            "name": project_path.name,
            "path": str(project_path.resolve()),
        }
    )


def run_web_interface(port=5000):
    # Find available port
    port = find_free_port(port)
    
    console.print(f"🌐 Starting web interface on port {port}...", style="green")
    url = f"http://localhost:{port}"
    
    # Open browser in a separate thread
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    
    app.run(port=port, debug=False, threaded=True)

def run_web_docs(port=5000):
    '''
    Running web documentation
    '''
    @app.route("/docs", methods=['GET'])
    def docs():

        return render_template("docs/index.html", version=__version__)
    

    port = find_free_port(port)
    console.print(f"🌐 Starting Documentation on port {port}...", style="green")

    url = f"http://localhost:{port}/docs"
    
    # Open browser in a separate thread
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    
    app.run(port=port, debug=False, threaded=True)
