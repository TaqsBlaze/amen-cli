"""Regression checks for safe incremental scaffolding and database selection."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from amen.cli import AmenCLI, main
from amen.frameworks import get_framework_packages
from amen.templates.manager import TemplateManager


def make_project(tmp_path, framework):
    root = tmp_path / "demo"
    package = root / "demo"
    (package / "api").mkdir(parents=True)
    (root / ".amen_config").write_text(framework + "\n")
    registration = (
        package / "__init__.py"
        if framework == "flask"
        else package / "api" / "endpoints.py"
    )
    registration.write_text(
        "from demo.api import existing\n"
        if framework == "flask"
        else "from fastapi import APIRouter\napi_router = APIRouter()\n"
    )
    return root, package, registration


def snapshot(root):
    result = {}
    for path in root.rglob("*"):
        relative = str(path.relative_to(root))
        if path.is_symlink():
            result[relative] = ("symlink", os.readlink(path))
        elif path.is_dir():
            result[relative] = ("directory",)
        else:
            result[relative] = ("file", path.read_bytes())
    return result


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
@pytest.mark.parametrize("case", ["endpoint", "util", "view_route", "view_template"])
@pytest.mark.parametrize("collision", ["file", "directory", "symlink", "dangling"])
def test_add_refuses_all_output_collisions(
    tmp_path, monkeypatch, framework, case, collision
):
    root, package, registration = make_project(tmp_path, framework)
    monkeypatch.chdir(tmp_path)
    item_type = "view" if case.startswith("view_") else case
    if case == "util":
        target = package / "utils" / "reports.py"
    elif case == "view_template":
        target = package / "templates" / "reports.html"
    else:
        target = package / "api" / "reports.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    outside = tmp_path / "user-content.txt"
    if collision == "file":
        target.write_text("user content")
    elif collision == "directory":
        target.mkdir()
        (target / "user-content.txt").write_text("user content")
    else:
        if collision == "symlink":
            outside.write_text("user content")
        target.symlink_to(outside)
    before = snapshot(root)

    result = CliRunner().invoke(main, ["add", "demo", item_type, "reports"])

    assert result.exit_code != 0
    assert "Refusing to overwrite existing path" in result.output
    assert snapshot(root) == before
    assert registration.read_text()
    if collision == "symlink":
        assert outside.read_text() == "user content"
    elif collision == "dangling":
        assert not outside.exists()


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
@pytest.mark.parametrize("item_type", ["endpoint", "util", "view"])
def test_add_creates_new_files_and_refuses_repeat(
    tmp_path, monkeypatch, framework, item_type
):
    root, package, registration = make_project(tmp_path, framework)
    monkeypatch.chdir(tmp_path)
    initializer = package / "utils" / "__init__.py"
    initializer.parent.mkdir()
    initializer.write_text("# custom utility initialization\n")
    original_mtime = initializer.stat().st_mtime_ns

    result = CliRunner().invoke(main, ["add", "demo", item_type, "reports"])

    assert result.exit_code == 0, result.output
    output = package / ("utils" if item_type == "util" else "api") / "reports.py"
    assert output.is_file()
    if item_type == "view":
        assert (package / "templates" / "reports.html").is_file()
    if item_type != "util":
        assert "reports" in registration.read_text()
    assert initializer.read_text() == "# custom utility initialization\n"
    assert initializer.stat().st_mtime_ns == original_mtime
    before = snapshot(root)

    repeated = CliRunner().invoke(main, ["add", "demo", item_type, "reports"])

    assert repeated.exit_code != 0
    assert snapshot(root) == before


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
def test_add_rejects_registration_symlinks(tmp_path, monkeypatch, framework):
    root, package, registration = make_project(tmp_path, framework)
    monkeypatch.chdir(tmp_path)
    outside = tmp_path / "registration.py"
    outside.write_text("# user registration\n")
    registration.unlink()
    registration.symlink_to(outside)
    before = snapshot(root)

    result = CliRunner().invoke(main, ["add", "demo", "view", "reports"])

    assert result.exit_code != 0
    assert "registration path" in result.output
    assert snapshot(root) == before
    assert outside.read_text() == "# user registration\n"


def test_add_rejects_symlink_parent_before_writing_counterpart(tmp_path, monkeypatch):
    root, package, _ = make_project(tmp_path, "fastapi")
    monkeypatch.chdir(tmp_path)
    outside = tmp_path / "external-templates"
    outside.mkdir()
    (package / "templates").symlink_to(outside, target_is_directory=True)
    before = snapshot(root)

    result = CliRunner().invoke(main, ["add", "demo", "view", "reports"])

    assert result.exit_code != 0
    assert "symlink" in result.output
    assert snapshot(root) == before
    assert list(outside.iterdir()) == []


def test_add_rejects_file_as_parent(tmp_path, monkeypatch):
    root, package, _ = make_project(tmp_path, "flask")
    monkeypatch.chdir(tmp_path)
    (package / "utils").write_text("user content")
    before = snapshot(root)

    result = CliRunner().invoke(main, ["add", "demo", "util", "reports"])

    assert result.exit_code != 0
    assert "not a directory" in result.output
    assert snapshot(root) == before


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
def test_add_removes_partial_view_after_write_failure(tmp_path, monkeypatch, framework):
    root, package, _ = make_project(tmp_path, framework)
    monkeypatch.chdir(tmp_path)
    before = snapshot(root)
    original_open = Path.open
    template_file = package / "templates" / "reports.html"

    def failing_open(path, mode="r", *args, **kwargs):
        if path == template_file and mode == "x":
            raise OSError("injected template write failure")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", failing_open)

    result = CliRunner().invoke(main, ["add", "demo", "view", "reports"])

    assert result.exit_code != 0
    assert "injected template write failure" in result.output
    assert snapshot(root) == before


def test_added_fastapi_view_renders_html(tmp_path, monkeypatch):
    root = tmp_path / "demo"
    root.mkdir()
    TemplateManager().generate_structure(root, "fastapi", "webapp", "demo", "none")
    (root / ".amen_config").write_text("fastapi\n")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(main, ["add", "demo", "view", "reports"])
    assert result.exit_code == 0, result.output

    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "from fastapi.testclient import TestClient; "
            "from demo.main import app; "
            "response = TestClient(app).get('/reports'); "
            "assert response.status_code == 200; "
            "assert '<h1>Reports page</h1>' in response.text",
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert probe.returncode == 0, probe.stderr


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
@pytest.mark.parametrize("database", ["none", "sqlite3", "mysql"])
def test_installer_uses_selected_database_packages(
    tmp_path, monkeypatch, framework, database
):
    commands = []
    monkeypatch.setattr(
        "amen.cli.subprocess.run", lambda command, **kwargs: commands.append(command)
    )

    assert AmenCLI().install_framework(tmp_path, framework, database)

    expected = get_framework_packages(framework, database)
    assert len(commands) == 1
    assert commands[0][-len(expected) :] == expected


def test_create_passes_database_choice_to_installer(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cli = AmenCLI()
    cli.welcome_banner = lambda: None
    cli.select_framework = lambda: "fastapi"
    cli.select_app_type = lambda: "api"
    cli.get_app_name = lambda: "demo"
    cli.select_database = lambda: "none"
    cli.create_virtual_environment = lambda path: True
    calls = []
    cli.install_framework = lambda *args: calls.append(args) or True
    cli.template_manager.generate_structure = lambda *args: None

    cli.create_app()

    assert calls == [(tmp_path / "demo", "fastapi", "none")]


def test_cancelled_database_selection_creates_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    existing = tmp_path / "demo"
    existing.mkdir()
    (existing / "user-content.txt").write_text("preserve me")
    before = snapshot(existing)
    monkeypatch.setattr(AmenCLI, "select_database", lambda self: None)
    monkeypatch.setattr(
        AmenCLI,
        "create_virtual_environment",
        lambda *args: pytest.fail(
            "Environment creation must not start after cancellation"
        ),
    )
    monkeypatch.setattr(
        "amen.cli.questionary.confirm",
        lambda *args, **kwargs: pytest.fail(
            "Overwrite prompt must not appear after cancellation"
        ),
    )

    result = CliRunner().invoke(
        main, ["create", "-f", "flask", "-t", "api", "-n", "demo"]
    )

    assert result.exit_code != 0
    assert "Database selection cancelled" in result.output
    assert snapshot(existing) == before


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
def test_add_preserves_registry_and_removes_outputs_on_registration_failure(
    tmp_path, monkeypatch, framework
):
    root, package, registration = make_project(tmp_path, framework)
    monkeypatch.chdir(tmp_path)
    original_mode = registration.stat().st_mode
    before = snapshot(root)
    original_replace = Path.replace

    def failing_replace(path, target):
        if target == registration:
            raise OSError("injected registration replacement failure")
        return original_replace(path, target)

    monkeypatch.setattr(Path, "replace", failing_replace)

    result = CliRunner().invoke(main, ["add", "demo", "view", "reports"])

    assert result.exit_code != 0
    assert "injected registration replacement failure" in result.output
    assert snapshot(root) == before
    assert registration.stat().st_mode == original_mode
