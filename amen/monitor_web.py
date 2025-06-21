import os
import sys
import time
import psutil
from pathlib import Path
from datetime import datetime
import threading

from flask import Flask, render_template, jsonify

from rich.console import Console

console = Console()

def get_venv_path(app_path: Path) -> Path:
    """Get virtual environment path based on OS"""
    if sys.platform.startswith('linux'):
        return app_path / "venv" / "bin"
    return app_path / "venv" / "Scripts"

def get_process_info(port):
    """Get process information for the given port"""
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            for conn in proc.net_connections():
                if conn.laddr.port == port:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None

def run_monitor_web(app_name, port, refresh):
    """Run a web interface to monitor application status."""
    app = Flask(__name__)
    app_path = Path.cwd() / app_name

    if not app_path.exists():
        console.print(f"❌ Application '{app_name}' not found.", style="red")
        return

    @app.route('/')
    def index():
        return render_template('monitor.html', app_name=app_name)

    @app.route('/data')
    def data():
        proc = get_process_info(port)
        if proc:
            mem_info = proc.memory_info()
            process_data = {
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'Running',
                'pid': proc.pid,
                'cpu_usage': proc.cpu_percent(),
                'memory_usage': round(proc.memory_percent(), 1),
                'rss_memory': round(mem_info.rss / (1024 * 1024), 1),
                'vms_memory': round(mem_info.vms / (1024 * 1024), 1),
                'threads': proc.num_threads(),
                'open_files': len(proc.open_files()) if hasattr(proc, 'open_files') else 'N/A'
            }
        else:
            process_data = {
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'Not Running',
                'pid': 0,
                'cpu_usage': 0,
                'memory_usage': 0,
                'rss_memory': 0,
                'vms_memory': 0,
                'threads': 0,
                'open_files': 0
            }
        return jsonify(process_data)

    def run_app():
        app.run(debug=True, use_reloader=False, port=5001)

    web_thread = threading.Thread(target=run_app)
    web_thread.daemon = True
    web_thread.start()

    console.print(f"🔍 Monitoring {app_name}...", style="blue")
    console.print(f"📊 Web interface available at http://localhost:5001", style="green")
    console.print(f"Press Ctrl+C to stop monitoring", style="yellow")

    try:
        while True:
            time.sleep(refresh)
    except KeyboardInterrupt:
        console.print("\n✋ Monitoring stopped", style="yellow")