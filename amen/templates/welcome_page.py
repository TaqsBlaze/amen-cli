"""Local, framework-independent assets for generated webapp welcome pages."""

from html import escape
from pathlib import Path
import re

from ..frameworks import FRAMEWORKS


def get_welcome_files(
    app_name: str, framework: str, database: str, version: str
) -> dict[str, str | bytes]:
    """Return welcome HTML and static assets relative to a generated project."""
    source = Path(__file__).with_name("welcome")
    database_names = {"none": "No database", "sqlite3": "SQLite", "mysql": "MySQL"}
    values = {
        "APP_NAME": app_name,
        "FRAMEWORK_KEY": framework,
        "FRAMEWORK_NAME": FRAMEWORKS[framework]["name"],
        "DEFAULT_PORT": str(FRAMEWORKS[framework]["default_port"]),
        "DATABASE_KEY": database,
        "DATABASE_NAME": database_names[database],
        "VERSION": version,
        "DOCS_URL": (
            "https://flask.palletsprojects.com/en/stable/quickstart/"
            if framework == "flask"
            else "https://fastapi.tiangolo.com/tutorial/"
        ),
    }
    template = source.joinpath("index.html").read_text(encoding="utf-8")
    template = re.sub(
        r"__AMEN_([A-Z_]+)__",
        lambda match: escape(values[match.group(1)], quote=True)
        .replace("{", "&#123;")
        .replace("}", "&#125;"),
        template,
    )
    return {
        f"{app_name}/templates/index.html": template,
        f"{app_name}/static/css/welcome-tokens.css": source.joinpath(
            "tokens.css"
        ).read_text(encoding="utf-8"),
        f"{app_name}/static/css/style.css": source.joinpath("welcome.css").read_text(
            encoding="utf-8"
        ),
        f"{app_name}/static/js/app.js": source.joinpath("welcome.js").read_text(
            encoding="utf-8"
        ),
        f"{app_name}/static/fonts/instrument-sans-latin-wght-normal.woff2": source.joinpath(
            "fonts/instrument-sans-latin-wght-normal.woff2"
        ).read_bytes(),
        f"{app_name}/static/fonts/OFL.txt": source.joinpath("fonts/OFL.txt").read_text(
            encoding="utf-8"
        ),
    }
