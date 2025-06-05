from flask import Flask, render_template, request, jsonify, url_for
import webbrowser
import threading
import socket
from .frameworks import FRAMEWORKS
from . import __version__
from .cli import AmenCLI
from rich.console import Console
console = Console()

def run_web_interface(port=5000):
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

    @app.route('/')
    def home():
        frameworks = {k: v['name'] for k, v in FRAMEWORKS.items()}
        return render_template('creator.html', frameworks=frameworks, version = __version__)

    @app.route('/api/create', methods=['POST'])
    def create_project():
        data = request.json
        cli = AmenCLI()
        
        try:
            # Override interactive prompts with web form data
            cli.select_framework = lambda: data['framework']
            cli.select_app_type = lambda: data['type']
            cli.get_app_name = lambda: data['name']
            cli.select_database = lambda: data.get('database', 'sqlite3')
            
            cli.create_app()
            return jsonify({'status': 'success', 'message': f"Project {data['name']} created successfully"})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

    # Find available port
    port = find_free_port(port)
    
    console.print(f"🌐 Starting web interface on port {port}...", style="green")
    url = f"http://localhost:{port}"
    
    # Open browser in a separate thread
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    
    app.run(port=port, debug=False, threaded=True)