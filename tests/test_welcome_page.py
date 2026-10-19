"""Serve generated welcome pages and assets through both supported frameworks."""

import itertools
import os
import subprocess
import sys
import textwrap

import pytest

from amen import __version__
from amen.templates import TemplateManager


def run_project(project, source):
    environment = os.environ.copy()
    environment.pop("DATABASE_URL", None)
    environment.pop("SQLALCHEMY_DATABASE_URI", None)
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(source)],
        cwd=project,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def make_project(tmp_path, framework, database, app_type="webapp", name=None):
    name = name or f"welcome_{framework}_{database}"
    project = tmp_path / name
    project.mkdir()
    TemplateManager().generate_structure(project, framework, app_type, name, database)
    return project


def client_setup(project, framework):
    if framework == "flask":
        return f"from {project.name} import app\nclient = app.test_client()\n"
    return (
        "from fastapi.testclient import TestClient\n"
        f"from {project.name}.main import app\nclient = TestClient(app)\n"
    )


@pytest.mark.parametrize(
    "framework,database",
    list(itertools.product(["flask", "fastapi"], ["none", "sqlite3", "mysql"])),
)
def test_generated_welcome_page_and_local_assets(tmp_path, framework, database):
    project = make_project(tmp_path, framework, database)
    assertions = f"""
        from html.parser import HTMLParser
        from urllib.parse import urlsplit
        import re
        import shlex

        from amen.cli import main
        from amen.frameworks import FRAMEWORKS

        class WelcomeDocument(HTMLParser):
            def __init__(self):
                super().__init__()
                self.body = {{}}
                self.ids = set()
                self.stylesheets = []
                self.scripts = []
                self.resources = []
                self.command_cards = []
                self.copy_targets = []
                self.text = []
                self.stack = []
                self.classes = set()
                self.text_by_id = {{}}
                self.attributes_by_id = {{}}
                self.hidden_ids = {{}}

            def handle_starttag(self, tag, attributes):
                attributes = dict(attributes)
                self.classes.update(attributes.get("class", "").split())
                hidden = "hidden" in attributes or any("hidden" in entry[1] for entry in self.stack)
                if "id" in attributes:
                    self.ids.add(attributes["id"])
                    self.text_by_id[attributes["id"]] = []
                    self.attributes_by_id[attributes["id"]] = attributes
                    self.hidden_ids[attributes["id"]] = hidden
                if tag == "body":
                    self.body = attributes
                if tag == "link" and "stylesheet" in attributes.get("rel", "").split():
                    self.stylesheets.append(attributes.get("href", ""))
                if tag == "script" and "src" in attributes:
                    self.scripts.append(attributes["src"])
                if tag in {{"script", "img", "source", "iframe"}} and "src" in attributes:
                    self.resources.append(attributes["src"])
                if tag == "link" and "href" in attributes:
                    self.resources.append(attributes["href"])
                if "data-copy" in attributes:
                    self.copy_targets.append(attributes["data-copy"])
                card = None
                if tag == "article" and "data-command-name" in attributes:
                    card = {{
                        "name": attributes["data-command-name"], "description": [],
                        "code_ids": [], "hidden": hidden,
                    }}
                    self.command_cards.append(card)
                if tag == "code" and attributes.get("id", "").startswith("command-"):
                    current_card = next((entry[2] for entry in reversed(self.stack) if entry[2] is not None), None)
                    if current_card is not None:
                        current_card["code_ids"].append(attributes["id"])
                if tag not in {{"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}}:
                    self.stack.append((tag, attributes, card))

            def handle_endtag(self, tag):
                for index in range(len(self.stack) - 1, -1, -1):
                    if self.stack[index][0] == tag:
                        del self.stack[index:]
                        break

            def handle_data(self, data):
                self.text.append(data)
                for _, attributes, _ in self.stack:
                    if "id" in attributes:
                        self.text_by_id[attributes["id"]].append(data)
                current_card = next((entry[2] for entry in reversed(self.stack) if entry[2] is not None), None)
                if current_card is not None and any("command-description" in entry[1].get("class", "").split() for entry in self.stack):
                    current_card["description"].append(data)

        response = client.get("/")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        document = WelcomeDocument()
        body = response.get_data(as_text=True) if {framework!r} == "flask" else response.text
        document.feed(body)
        assert document.body["data-app"] == {project.name!r}
        assert document.body["data-framework"] == {framework!r}
        assert document.body["data-database"] == {database!r}
        text = " ".join(document.text)
        assert {project.name!r} in text
        assert {('Flask' if framework == 'flask' else 'FastAPI')!r} in text
        assert {__version__!r} in text
        assert { {"none": "No database", "sqlite3": "SQLite", "mysql": "MySQL"}[database]!r} in text
        assert "theme-toggle" in document.ids
        assert "health-check" in document.ids
        assert "amen-version" in document.ids
        assert not document.hidden_ids["amen-version"]
        version = " ".join(document.text_by_id["amen-version"])
        assert "AMEN" in version and {__version__!r} in version
        assert "command-search" in document.ids
        search = document.attributes_by_id["command-search"]
        assert search.get("type") == "search"
        assert search.get("aria-controls") in document.ids
        assert not ({{"sculpture", "preview-canvas"}} & document.classes)
        assert {{card["name"] for card in document.command_cards}} == set(main.commands) | {{"--help"}}
        add_variants = set()
        for card in document.command_cards:
            assert not card["hidden"], "Commands must be readable without JavaScript"
            description = " ".join(card["description"]).strip()
            assert description, card["name"]
            if card["name"] == "migrate":
                assert "database" in description.lower() and "require" in description.lower()
            assert card["code_ids"], card["name"]
            for code_id in card["code_ids"]:
                assert code_id in document.copy_targets
                example = "".join(document.text_by_id[code_id]).strip()
                arguments = shlex.split(example)
                assert arguments[0] in {{"amen", "am"}}, example
                assert arguments[1] == card["name"], example
                if card["name"] == "--help":
                    assert len(arguments) == 2
                    continue
                # Parse Click arguments without invoking setup, editors, servers, or tools.
                command = main.commands[card["name"]]
                with command.make_context(arguments[1], arguments[2:]) as context:
                    if "app_name" in context.params:
                        assert context.params["app_name"] == {project.name!r}, example
                    if card["name"] == "add":
                        add_variants.add(context.params["item_type"])
                    elif card["name"] == "monitor":
                        assert context.params["port"] == FRAMEWORKS[{framework!r}]["default_port"]
        assert add_variants == {{"endpoint", "view", "util"}}
        assert document.copy_targets
        for target in document.copy_targets:
            assert target and target.removeprefix("#") in document.ids
        assert "/static/css/welcome-tokens.css" in document.stylesheets
        assert "/static/css/style.css" in document.stylesheets
        assert "/static/js/app.js" in document.scripts
        for resource in document.resources:
            parsed = urlsplit(resource)
            assert not parsed.netloc and parsed.scheme not in {{"http", "https"}}, resource
        font_url = "/static/fonts/instrument-sans-latin-wght-normal.woff2"
        for asset in [
            "/static/css/welcome-tokens.css", "/static/css/style.css", "/static/js/app.js",
            font_url, "/static/fonts/OFL.txt",
        ]:
            asset_response = client.get(asset)
            assert asset_response.status_code == 200, asset
            content = asset_response.data if {framework!r} == "flask" else asset_response.content
            assert content
            mime_type = asset_response.headers["content-type"].split(";", 1)[0]
            if asset.endswith(".css"):
                assert mime_type == "text/css", (asset, mime_type)
                assert not re.search(
                    r"(?:url\\(\\s*|@import\\s+)(?:['\\\"])?(?:https?:)?//",
                    asset_response.get_data(as_text=True) if {framework!r} == "flask" else asset_response.text,
                    re.IGNORECASE,
                ), "Styles must not depend on remote runtime resources"
            elif asset.endswith(".js"):
                assert mime_type in {{"text/javascript", "application/javascript"}}, mime_type
            elif asset.endswith(".woff2"):
                assert content.startswith(b"wOF2"), "The served font must be a WOFF2 binary"
                assert mime_type in {{"font/woff2", "application/font-woff2"}}, mime_type
            else:
                assert mime_type == "text/plain", mime_type
                assert b"SIL OPEN FONT LICENSE" in content
        health = client.get("/health")
        assert health.status_code == 200
        health_json = health.get_json() if {framework!r} == "flask" else health.json()
        assert health_json["status"] == "healthy"
    """
    run_project(project, client_setup(project, framework) + textwrap.dedent(assertions))


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
def test_api_only_welcome_remains_json(tmp_path, framework):
    project = make_project(tmp_path, framework, "none", app_type="api")
    run_project(
        project,
        client_setup(project, framework)
        + "response = client.get('/')\n"
        + "assert response.status_code == 200\n"
        + "assert response.headers['content-type'].startswith('application/json')\n"
        + f"assert response.json{'()' if framework == 'fastapi' else ''}['message'] == 'Welcome to {project.name} API!'\n",
    )


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
def test_welcome_renderer_escapes_project_names_without_filesystem_writes(framework):
    from html.parser import HTMLParser

    from jinja2 import Environment

    from amen.templates.welcome_page import get_welcome_files

    name = 'café {{7*7}}"><script id="injected">alert(1)</script> & \'quotes\''
    files = get_welcome_files(name, framework, "none", __version__)
    html = next(
        content
        for path, content in files.items()
        if path.endswith("/templates/index.html")
    )
    assert isinstance(html, str)

    class ProjectDocument(HTMLParser):
        def __init__(self):
            super().__init__()
            self.body = {}
            self.ids = set()

        def handle_starttag(self, tag, attributes):
            attributes = dict(attributes)
            if tag == "body":
                self.body = attributes
            if "id" in attributes:
                self.ids.add(attributes["id"])

    document = ProjectDocument()
    document.feed(Environment(autoescape=True).from_string(html).render())
    assert document.body["data-app"] == name
    assert "injected" not in document.ids
    assert '<script id="injected">' not in html
