"""Behavioral regression tests for generated applications and databases."""

import itertools
import os
from contextlib import closing
from pathlib import Path
import sqlite3
import subprocess
import sys
import textwrap

from click.testing import CliRunner
import pytest

from amen import cli
from amen.frameworks import get_framework_packages
from amen.templates import TemplateManager


def generate_project(tmp_path, framework, app_type="api", database="sqlite3"):
    """Generate an isolated, importable application without installing packages."""
    name = f"app_{framework}_{app_type}_{database}"
    project = tmp_path / name
    project.mkdir()
    TemplateManager().generate_structure(project, framework, app_type, name, database)
    (project / ".amen_config").write_text(framework + "\n")
    return project


def run_in_project(project, source, **environment):
    """Run a fresh interpreter so generated packages and dotenv cannot leak."""
    env = os.environ.copy()
    env.pop("DATABASE_URL", None)
    env.pop("SQLALCHEMY_DATABASE_URI", None)
    env.update(environment)
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(source)],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


@pytest.mark.parametrize(
    "framework,app_type,database",
    list(
        itertools.product(
            ["flask", "fastapi"], ["api", "webapp"], ["none", "sqlite3", "mysql"]
        )
    ),
)
def test_generated_application_routes_and_model_registration(
    tmp_path, framework, app_type, database
):
    project = generate_project(tmp_path, framework, app_type, database)
    if framework == "flask":
        setup = f"""
from {project.name} import app
client = app.test_client()
"""
    else:
        setup = f"""
from fastapi.testclient import TestClient
from {project.name}.main import app
client = TestClient(app)
"""
    assertions = """
assert client.get('/health').status_code == 200
response = client.get('/')
assert response.status_code == 200
"""
    if app_type == "webapp":
        assertions += "assert 'text/html' in response.headers['content-type']\n"
    else:
        assertions += "assert 'application/json' in response.headers['content-type']\n"
    if database != "none":
        assertions += (
            "assert 'users' in app.extensions['sqlalchemy'].metadata.tables\n"
            if framework == "flask"
            else f"from {project.name}.database import Base\n"
            "assert 'users' in Base.metadata.tables\n"
        )
    run_in_project(project, setup + assertions)


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
def test_no_database_apps_do_not_import_database_packages(tmp_path, framework):
    project = generate_project(tmp_path, framework, database="none")
    run_in_project(
        project,
        f"""
        import sys
        from importlib.abc import MetaPathFinder

        class NoDatabaseImports(MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname.split('.')[0] in {{
                    'sqlalchemy', 'flask_sqlalchemy', 'flask_migrate',
                    'pymysql', 'alembic',
                }}:
                    raise AssertionError('Unexpected database import: ' + fullname)

        sys.meta_path.insert(0, NoDatabaseImports())
        import {project.name}{'.main' if framework == 'fastapi' else ''}
        """,
    )
    assert not (project / project.name / "models").exists()
    assert not (project / project.name / "database.py").exists()
    assert not (project / "alembic.ini").exists()
    requirements = (project / "requirements.txt").read_text().lower()
    for dependency in [
        "sqlalchemy",
        "pymysql",
        "mysqlclient",
        "alembic",
        "flask-migrate",
    ]:
        assert dependency not in requirements


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
def test_sqlite_persistence_and_per_insert_timestamps(tmp_path, framework):
    project = generate_project(tmp_path, framework)
    setup = (
        f"""
from {project.name} import app, db
app.app_context().push()
db.create_all()
session = db.session
"""
        if framework == "flask"
        else f"""
from {project.name}.database import Base, engine, SessionLocal
from {project.name}.models import Users
Base.metadata.create_all(engine)
session = SessionLocal()
"""
    )
    run_in_project(
        project,
        setup + f"""
from datetime import datetime, timezone
from unittest.mock import patch
from sqlalchemy import select
from {project.name}.models import models

with patch.object(models, 'datetime') as clock:
    clock.now.return_value = datetime(2026, 1, 1, tzinfo=timezone.utc)
    first = models.Users(firstname='First', lastname='User', username='first',
                         email='first@example.test', password='password-hash')
    session.add(first)
    session.commit()
    clock.now.return_value = datetime(2026, 1, 2, tzinfo=timezone.utc)
    second = models.Users(firstname='Second', lastname='User', username='second',
                          email='second@example.test', password='password-hash')
    session.add(second)
    session.commit()

assert first.created_at < second.created_at
assert session.execute(select(models.Users)).scalars().all() == [first, second]
session.close()
""",
    )
    assert (project / "instance" / f"{project.name}.db").is_file()


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
@pytest.mark.parametrize("configuration_source", ["environment", "dotenv"])
def test_database_url_override_is_resolved_from_project_root(
    tmp_path, framework, configuration_source
):
    project = generate_project(tmp_path, framework)
    database_url = "sqlite:///custom/override.db"
    environment = {"DATABASE_URL": database_url}
    if configuration_source == "dotenv":
        (project / ".env").write_text(f"DATABASE_URL={database_url}\n")
        environment = {}
    run_in_project(
        project,
        f"""
        import os
        import sys
        from pathlib import Path
        from sqlalchemy.engine import make_url
        root = Path.cwd()
        sys.path.insert(0, str(root))
        os.chdir(root.parent)
        from {project.name}.database import DATABASE_URL
        expected = root / 'custom' / 'override.db'
        assert Path(make_url(DATABASE_URL).database) == expected
        """,
        **environment,
    )


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
def test_migrate_creates_generated_sqlite_model(tmp_path, monkeypatch, framework):
    project = generate_project(tmp_path, framework)
    (project / "venv").mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(cli, "get_python_path", lambda _: Path(sys.executable))
    result = CliRunner().invoke(cli.main, ["migrate", project.name])
    assert result.exit_code == 0, result.output + str(result.exception or "")
    with closing(
        sqlite3.connect(project / "instance" / f"{project.name}.db")
    ) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert {"users", "alembic_version"} <= tables
    revisions = list((project / "migrations" / "versions").glob("*.py"))
    assert len(revisions) == 1
    assert "users" in revisions[0].read_text()


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
def test_requirements_match_selected_installer_packages(tmp_path, framework):
    for database in ["none", "sqlite3", "mysql"]:
        project = generate_project(tmp_path, framework, database=database)
        requirements = (project / "requirements.txt").read_text().splitlines()
        assert requirements == get_framework_packages(framework, database)
        assert ("pymysql" in requirements) == (database == "mysql")
        assert not any("mysqlclient" in name for name in requirements)


def test_fastapi_database_session_closes_after_dependency_error(tmp_path):
    project = generate_project(tmp_path, "fastapi")
    run_in_project(
        project,
        f"""
        from unittest.mock import patch
        from {project.name} import database

        with patch.object(database, 'SessionLocal') as factory:
            dependency = database.get_db()
            assert next(dependency) is factory.return_value
            try:
                dependency.throw(RuntimeError('request failed'))
            except RuntimeError:
                pass
            else:
                raise AssertionError('Request error was swallowed')
            factory.return_value.close.assert_called_once_with()
        """,
    )
