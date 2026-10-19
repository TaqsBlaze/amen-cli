"""Regression checks for observable command failures and successful recovery."""

import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

from click.testing import CliRunner
import pytest
import requests

from amen import cli


@pytest.fixture
def project(tmp_path, monkeypatch):
    """Create a local project whose external commands can be substituted safely."""
    monkeypatch.chdir(tmp_path)
    root = tmp_path / "demo"
    root.mkdir()
    (root / ".amen_config").write_text("flask\n")
    (root / "app.py").write_text("pass\n")
    (root / "demo" / "models").mkdir(parents=True)
    (root / "demo" / "__init__.py").write_text("# application\n")
    for executable in [cli.get_python_path, cli.get_pip_path]:
        path = executable(cli.get_venv_path(root))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# mocked executable\n")
    return root


@pytest.mark.parametrize(
    "arguments",
    [
        ["run", "missing"],
        ["test", "missing"],
        ["migrate", "missing"],
        ["install", "missing", "requests"],
        ["config", "missing"],
        ["audit", "missing"],
        ["monitor", "missing"],
        ["add", "missing", "endpoint", "reports"],
    ],
)
def test_missing_projects_fail_without_starting_tools(tmp_path, monkeypatch, arguments):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        cli.subprocess, "run", lambda *a, **k: pytest.fail("No tool should run")
    )
    result = CliRunner().invoke(cli.main, arguments)
    assert result.exit_code == 1
    assert "not found" in result.output


@pytest.mark.parametrize("command", ["run", "test", "install", "audit"])
def test_missing_virtual_environment_fails(tmp_path, monkeypatch, command):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "demo").mkdir()
    arguments = [command, "demo"] + (["requests"] if command == "install" else [])
    result = CliRunner().invoke(cli.main, arguments)
    assert result.exit_code == 1
    assert "Virtual environment not found" in result.output


@pytest.mark.parametrize("command", ["run", "test", "install", "migrate"])
@pytest.mark.parametrize("returncode", [3, 7, -15])
def test_child_failure_status_and_diagnostics_are_propagated(
    project, monkeypatch, command, returncode
):
    def fail(arguments, **kwargs):
        raise subprocess.CalledProcessError(
            returncode, arguments, stderr=b"underlying command failed"
        )

    monkeypatch.setattr(cli.subprocess, "run", fail)
    arguments = [command, "demo"] + (["requests"] if command == "install" else [])
    result = CliRunner().invoke(cli.main, arguments)
    assert result.exit_code == (returncode if returncode > 0 else 128 - returncode)
    assert "underlying command failed" in result.output


@pytest.mark.parametrize("command", ["run", "test", "install", "migrate"])
def test_unavailable_tools_are_command_failures(project, monkeypatch, command):
    def fail(*args, **kwargs):
        raise FileNotFoundError("tool unavailable")

    monkeypatch.setattr(cli.subprocess, "run", fail)
    arguments = [command, "demo"] + (["requests"] if command == "install" else [])
    result = CliRunner().invoke(cli.main, arguments)
    assert result.exit_code == 1
    assert "tool unavailable" in result.output


@pytest.mark.parametrize("status", [0, 7])
def test_run_propagates_a_real_application_exit(project, monkeypatch, status):
    (project / "app.py").write_text(f"raise SystemExit({status})\n")
    monkeypatch.setattr(cli, "get_python_path", lambda _: Path(sys.executable))
    result = CliRunner().invoke(cli.main, ["run", "demo"])
    assert result.exit_code == status, result.output


@pytest.mark.parametrize("missing", ["app.py", ".amen_config", "interpreter"])
def test_run_rejects_incomplete_projects(project, missing):
    target = (
        cli.get_python_path(cli.get_venv_path(project))
        if missing == "interpreter"
        else project / missing
    )
    target.unlink()
    result = CliRunner().invoke(cli.main, ["run", "demo"])
    assert result.exit_code == 1
    assert "Error:" in result.output


def test_invalid_framework_metadata_fails(project):
    (project / ".amen_config").write_text("unknown\n")
    for arguments in [["run", "demo"], ["add", "demo", "endpoint", "reports"]]:
        result = CliRunner().invoke(cli.main, arguments)
        assert result.exit_code == 1
        assert "Unsupported framework" in result.output


@pytest.mark.parametrize("command", ["test", "install"])
def test_successful_subprocesses_still_succeed(project, monkeypatch, command):
    monkeypatch.setattr(
        cli.subprocess,
        "run",
        lambda args, **kwargs: subprocess.CompletedProcess(args, 0),
    )
    arguments = [command, "demo"] + (["requests"] if command == "install" else [])
    result = CliRunner().invoke(cli.main, arguments)
    assert result.exit_code == 0, result.output


def test_cache_failure_does_not_fail_successful_install(project, monkeypatch):
    calls = []

    def run(arguments, **kwargs):
        calls.append(arguments)
        if "download" in arguments:
            raise subprocess.CalledProcessError(
                1, arguments, stderr="cache unavailable"
            )
        return subprocess.CompletedProcess(arguments, 0)

    monkeypatch.setattr(cli.subprocess, "run", run)
    result = CliRunner().invoke(cli.main, ["install", "demo", "requests"])
    assert result.exit_code == 0, result.output
    assert len(calls) == 2
    assert "Successfully installed" in result.output


def prepare_creation(monkeypatch):
    """Provide complete choices while leaving the real creation service in use."""
    monkeypatch.setattr(cli.AmenCLI, "welcome_banner", lambda _: None)
    monkeypatch.setattr(cli.AmenCLI, "select_framework", lambda _: "flask")
    monkeypatch.setattr(cli.AmenCLI, "select_app_type", lambda _: "api")
    monkeypatch.setattr(cli.AmenCLI, "get_app_name", lambda _: "demo")
    monkeypatch.setattr(cli.AmenCLI, "select_database", lambda _: "none")
    monkeypatch.setattr(cli.AmenCLI, "create_virtual_environment", lambda *_: True)
    monkeypatch.setattr(cli.AmenCLI, "install_framework", lambda *_: True)


@pytest.mark.parametrize("stage", ["create_virtual_environment", "install_framework"])
def test_creation_false_setup_results_fail(tmp_path, monkeypatch, stage):
    monkeypatch.chdir(tmp_path)
    prepare_creation(monkeypatch)
    monkeypatch.setattr(cli.AmenCLI, stage, lambda *args: False)
    result = CliRunner().invoke(cli.main, ["create"])
    assert result.exit_code == 1
    assert "failed" in result.output.lower()
    assert not (tmp_path / "demo" / ".amen_config").exists()
    assert "Successfully created" not in result.output


@pytest.mark.parametrize(
    "selection",
    ["select_framework", "select_app_type", "get_app_name", "select_database"],
)
def test_cancelled_creation_does_not_report_success(tmp_path, monkeypatch, selection):
    monkeypatch.chdir(tmp_path)
    prepare_creation(monkeypatch)
    monkeypatch.setattr(cli.AmenCLI, selection, lambda _: None)
    result = CliRunner().invoke(cli.main, ["create"])
    assert result.exit_code != 0
    assert not (tmp_path / "demo").exists()


def test_creation_write_failure_reports_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    prepare_creation(monkeypatch)

    def fail(*args, **kwargs):
        raise OSError("cannot write scaffold")

    monkeypatch.setattr(cli.TemplateManager, "generate_structure", fail)
    result = CliRunner().invoke(cli.main, ["create"])
    assert result.exit_code == 1
    assert "cannot write scaffold" in result.output


def test_failed_framework_install_preserves_pip_status(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.AmenCLI, "welcome_banner", lambda _: None)
    monkeypatch.setattr(cli.AmenCLI, "select_database", lambda _: "none")
    monkeypatch.setattr(cli.AmenCLI, "create_virtual_environment", lambda *_: True)

    def fail(args, **kwargs):
        raise subprocess.CalledProcessError(
            9, args, stderr="dependency resolution failed"
        )

    monkeypatch.setattr(cli.subprocess, "run", fail)
    result = CliRunner().invoke(
        cli.main, ["create", "-f", "flask", "-t", "api", "-n", "demo"]
    )
    assert result.exit_code == 9
    assert "dependency resolution failed" in result.output


def test_virtual_environment_error_is_reported(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.AmenCLI, "select_database", lambda _: "none")

    def fail(*args, **kwargs):
        raise OSError("venv unavailable")

    monkeypatch.setattr(cli.venv, "create", fail)
    result = CliRunner().invoke(
        cli.main, ["create", "-f", "flask", "-t", "api", "-n", "demo"]
    )
    assert result.exit_code == 1
    assert "venv unavailable" in result.output


def test_declined_project_overwrite_fails_without_deleting_files(project, monkeypatch):
    prepare_creation(monkeypatch)
    monkeypatch.setattr(
        cli.questionary, "confirm", lambda *a, **k: SimpleNamespace(ask=lambda: False)
    )
    before = (project / "app.py").read_bytes()
    result = CliRunner().invoke(cli.main, ["create"])
    assert result.exit_code == 1
    assert (project / "app.py").read_bytes() == before


@pytest.mark.parametrize("status", [0, 1, 2, 7])
def test_audit_distinguishes_findings_and_tool_failure(project, monkeypatch, status):
    monkeypatch.setattr(
        cli.subprocess,
        "run",
        lambda args, **kwargs: subprocess.CompletedProcess(
            args, status, '{"results": []}\n', "tool failed" if status > 1 else ""
        ),
    )
    result = CliRunner().invoke(cli.main, ["audit", "demo", "--format", "json"])
    assert result.exit_code == status
    if status <= 1:
        assert json.loads(result.stdout) == {"results": []}
    else:
        assert "tool failed" in result.output


@pytest.mark.parametrize(
    "severity,expected",
    [
        ("low", "low"),
        ("l", "low"),
        ("medium", "medium"),
        ("m", "medium"),
        ("high", "high"),
        ("h", "high"),
    ],
)
def test_audit_passes_supported_severity_values(
    project, monkeypatch, severity, expected
):
    commands = []

    def run(args, **kwargs):
        commands.append(args)
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(cli.subprocess, "run", run)
    result = CliRunner().invoke(cli.main, ["audit", "demo", "--severity", severity])
    assert result.exit_code == 0, result.output
    assert commands[0][commands[0].index("--severity-level") + 1] == expected


@pytest.mark.parametrize("findings", [False, True])
def test_audit_real_bandit_status_and_environment_exclusion(project, findings):
    (project / "venv" / "unsafe.py").write_text("import pickle\npickle.loads(data)\n")
    (project / "app.py").write_text(
        "import pickle\npickle.loads(data)\n" if findings else "print('hello')\n"
    )
    result = CliRunner().invoke(
        cli.main, ["audit", "demo", "--format", "json", "--severity", "medium"]
    )
    assert result.exit_code == int(findings), result.output
    report = json.loads(result.stdout)
    assert bool(report["results"]) == findings
    assert all("venv" not in item["filename"] for item in report["results"])


@pytest.mark.parametrize("command", ["web", "docs"])
def test_server_startup_failures_return_nonzero(monkeypatch, command):
    import amen.web as web_module

    def fail(*args, **kwargs):
        raise OSError("server unavailable")

    monkeypatch.setattr(
        web_module, "run_web_interface" if command == "web" else "run_web_docs", fail
    )
    result = CliRunner().invoke(cli.main, [command])
    assert result.exit_code == 1
    assert "server unavailable" in result.output


def test_editor_failure_returns_nonzero(project, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("display unavailable")

    monkeypatch.setattr(cli, "edit_file", fail)
    result = CliRunner().invoke(cli.main, ["config", "demo"])
    assert result.exit_code == 1
    assert "display unavailable" in result.output


@pytest.mark.parametrize("refresh", ["0", "-1", "nan", "inf"])
@pytest.mark.parametrize("web", [False, True])
def test_invalid_monitor_refresh_fails_before_startup(project, refresh, web):
    result = CliRunner().invoke(
        cli.main, ["monitor", "demo", "--refresh", refresh] + (["--web"] if web else [])
    )
    assert result.exit_code == 2
    assert "--refresh" in result.output


def test_web_monitor_startup_failure_reaches_cli(project, monkeypatch):
    import amen.monitor_web as monitor_module

    def fail(*args, **kwargs):
        raise OSError("monitor port unavailable")

    monkeypatch.setattr(monitor_module.Flask, "run", fail)
    result = CliRunner().invoke(cli.main, ["monitor", "demo", "--web"])
    assert result.exit_code == 1
    assert "monitor port unavailable" in result.output


@pytest.mark.parametrize("reason", ["network", "metadata", "lookup", "installation"])
def test_update_failures_return_nonzero(monkeypatch, reason):
    def get(*args, **kwargs):
        if reason == "network":
            raise requests.ConnectionError("index unavailable")
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {} if reason == "metadata" else {"info": {"version": "9.0.0"}},
        )

    def run(args, **kwargs):
        if (reason == "lookup" and "show" in args) or (
            reason == "installation" and "install" in args
        ):
            raise subprocess.CalledProcessError(6, args, stderr="pip failed")
        return subprocess.CompletedProcess(args, 0, "Version: 0.13.1\n", "")

    monkeypatch.setattr(cli.requests, "get", get)
    monkeypatch.setattr(cli.subprocess, "run", run)
    monkeypatch.setattr(
        cli.questionary, "confirm", lambda *a, **k: SimpleNamespace(ask=lambda: True)
    )
    result = CliRunner().invoke(cli.main, ["update"])
    assert result.exit_code == (6 if reason in {"lookup", "installation"} else 1)
    assert "Successfully updated" not in result.output
