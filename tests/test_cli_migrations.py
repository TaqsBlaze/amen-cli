"""Framework dispatch and failure reporting for database migrations."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from amen.cli import get_python_path, get_venv_path, main


def migration_project(tmp_path, framework, database=True):
    root = tmp_path / "demo"
    root.mkdir()
    (root / ".amen_config").write_text(framework + "\n")
    if database:
        (root / "demo" / "models").mkdir(parents=True)
    python_path = get_python_path(get_venv_path(root))
    python_path.parent.mkdir(parents=True)
    python_path.write_text("# placeholder interpreter for mocked subprocesses\n")
    return root, python_path


@pytest.mark.parametrize("initialized", [False, True])
def test_flask_migrations_use_project_python_and_explicit_app(
    tmp_path, monkeypatch, initialized
):
    root, python_path = migration_project(tmp_path, "flask")
    if initialized:
        (root / "migrations").mkdir()
    monkeypatch.chdir(tmp_path)
    calls = []
    monkeypatch.setattr(
        "amen.cli.subprocess.run",
        lambda command, **kwargs: calls.append((command, kwargs)),
    )

    result = CliRunner().invoke(main, ["migrate", "demo"])

    assert result.exit_code == 0, result.output
    actions = ["migrate", "upgrade"] if initialized else ["init", "migrate", "upgrade"]
    assert [command for command, _ in calls] == [
        [str(python_path), "-m", "flask", "--app", "demo", "db", action]
        for action in actions
    ]
    assert all(kwargs["cwd"] == str(root) and kwargs["check"] for _, kwargs in calls)


def test_fastapi_migrations_use_alembic(tmp_path, monkeypatch):
    root, python_path = migration_project(tmp_path, "fastapi")
    (root / "alembic.ini").write_text("[alembic]\nscript_location=migrations\n")
    monkeypatch.chdir(tmp_path)
    calls = []
    monkeypatch.setattr(
        "amen.cli.subprocess.run",
        lambda command, **kwargs: calls.append((command, kwargs)),
    )

    result = CliRunner().invoke(main, ["migrate", "demo"])

    assert result.exit_code == 0, result.output
    assert [command for command, _ in calls] == [
        [
            str(python_path),
            "-m",
            "alembic",
            "revision",
            "--autogenerate",
            "-m",
            "Auto migration",
        ],
        [str(python_path), "-m", "alembic", "upgrade", "head"],
    ]
    assert all(kwargs["cwd"] == str(root) and kwargs["check"] for _, kwargs in calls)


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
def test_migrations_reject_database_free_projects(tmp_path, monkeypatch, framework):
    migration_project(tmp_path, framework, database=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "amen.cli.subprocess.run",
        lambda *args, **kwargs: pytest.fail("No migration should run"),
    )

    result = CliRunner().invoke(main, ["migrate", "demo"])

    assert result.exit_code != 0
    assert "no database configured" in result.output


def test_legacy_fastapi_project_gets_actionable_alembic_error(tmp_path, monkeypatch):
    migration_project(tmp_path, "fastapi")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "amen.cli.subprocess.run",
        lambda *args, **kwargs: pytest.fail("Flask must not run for FastAPI"),
    )

    result = CliRunner().invoke(main, ["migrate", "demo"])

    assert result.exit_code != 0
    assert "Alembic configuration is missing" in result.output
    assert "alembic.ini" in result.output


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
def test_migration_failure_reports_stderr_and_stops_upgrade(
    tmp_path, monkeypatch, framework
):
    root, _ = migration_project(tmp_path, framework)
    (root / "migrations").mkdir()
    (root / "alembic.ini").write_text("[alembic]\nscript_location=migrations\n")
    monkeypatch.chdir(tmp_path)
    calls = []

    def fail(command, **kwargs):
        calls.append(command)
        raise subprocess.CalledProcessError(1, command, stderr="database unavailable")

    monkeypatch.setattr("amen.cli.subprocess.run", fail)

    result = CliRunner().invoke(main, ["migrate", "demo"])

    assert result.exit_code != 0
    assert "database unavailable" in result.output
    assert len(calls) == 1


def test_migrations_reject_missing_interpreter(tmp_path, monkeypatch):
    _, python_path = migration_project(tmp_path, "flask")
    python_path.unlink()
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(main, ["migrate", "demo"])

    assert result.exit_code != 0
    assert "Application Python not found" in result.output
