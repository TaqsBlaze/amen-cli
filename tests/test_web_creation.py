"""HTTP validation and result handling for the noninteractive project creator."""

from pathlib import Path

import click
import pytest

from amen import web
from amen.cli import AmenCLI, ProjectExistsError


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setitem(web.app.config, "TESTING", True)
    monkeypatch.setattr(AmenCLI, "welcome_banner", lambda self: None)

    def unexpected_prompt(*args, **kwargs):
        pytest.fail("The web creator must never invoke terminal prompts")

    for prompt in ("confirm", "select", "text"):
        monkeypatch.setattr(f"amen.cli.questionary.{prompt}", unexpected_prompt)
    return web.app.test_client()


@pytest.fixture
def successful_setup(monkeypatch):
    """Keep real creation/scaffolding while avoiding package/environment installation."""
    monkeypatch.setattr(AmenCLI, "create_virtual_environment", lambda self, path: True)
    monkeypatch.setattr(
        AmenCLI,
        "install_framework",
        lambda self, path, framework, database="sqlite3": True,
    )


def payload(**overrides):
    values = {"framework": "flask", "type": "api", "name": "demo", "database": "none"}
    values.update(overrides)
    return values


@pytest.mark.parametrize("body", [None, [], ["demo"], "demo", 7, True])
def test_creator_rejects_non_object_json(client, monkeypatch, body):
    monkeypatch.setattr(
        AmenCLI,
        "create_app",
        lambda *args, **kwargs: pytest.fail("Invalid requests must not start creation"),
    )

    response = client.post("/api/create", json=body)

    assert response.status_code == 400
    assert response.get_json()["status"] == "error"


@pytest.mark.parametrize(
    "data,content_type",
    [
        ("{broken", "application/json"),
        ('{"name": "demo"}', "text/plain"),
        ("", "application/json"),
    ],
)
def test_creator_rejects_malformed_or_non_json_body(client, data, content_type):
    response = client.post("/api/create", data=data, content_type=content_type)

    assert response.status_code == 400
    assert response.get_json()["status"] == "error"


@pytest.mark.parametrize("field", ["framework", "type", "name", "database"])
@pytest.mark.parametrize("value", [None, 1, True, [], {}, "", "  "])
def test_creator_rejects_invalid_field_types(client, monkeypatch, field, value):
    monkeypatch.setattr(
        AmenCLI,
        "create_app",
        lambda *args, **kwargs: pytest.fail("Invalid requests must not start creation"),
    )

    response = client.post("/api/create", json=payload(**{field: value}))

    assert response.status_code == 400
    assert field in response.get_json()["message"]


@pytest.mark.parametrize("field", ["framework", "type", "name"])
def test_creator_rejects_missing_required_fields(client, field):
    values = payload()
    del values[field]

    response = client.post("/api/create", json=values)

    assert response.status_code == 400
    assert field in response.get_json()["message"]


@pytest.mark.parametrize(
    "field,value",
    [("framework", "django"), ("type", "desktop"), ("database", "postgres")],
)
def test_creator_rejects_unknown_choices(client, monkeypatch, field, value):
    monkeypatch.setattr(
        AmenCLI,
        "create_app",
        lambda *args, **kwargs: pytest.fail("Invalid choices must not start creation"),
    )

    response = client.post("/api/create", json=payload(**{field: value}))

    assert response.status_code == 400
    assert field in response.get_json()["message"]


@pytest.mark.parametrize("framework", ["flask", "fastapi"])
@pytest.mark.parametrize("app_type", ["api", "webapp"])
def test_creator_reports_actual_normalized_project(
    client, successful_setup, tmp_path, framework, app_type
):
    response = client.post(
        "/api/create",
        json=payload(
            name="my-demo",
            framework=" " + framework.upper() + " ",
            type=app_type.upper(),
            database=" NONE ",
        ),
    )

    assert response.status_code == 200, response.get_json()
    result = response.get_json()
    assert result["status"] == "success"
    assert result["name"] == "my_demo"
    assert result["path"] == str(tmp_path / "my_demo")
    assert "my_demo" in result["message"]
    assert (tmp_path / "my_demo" / "app.py").is_file()
    assert (tmp_path / "my_demo" / ".amen_config").read_text().strip() == framework


def test_creator_defaults_database_to_sqlite(client, successful_setup, tmp_path):
    values = payload()
    del values["database"]

    response = client.post("/api/create", json=values)

    assert response.status_code == 200, response.get_json()
    project = tmp_path / "demo"
    assert (project / "demo" / "database.py").is_file()
    assert "DATABASE_URL=sqlite:///instance/demo.db" in (project / ".env").read_text()


@pytest.mark.parametrize("name", ["../outside", "123demo"])
def test_creator_maps_invalid_names_to_validation_error(
    client, successful_setup, tmp_path, name
):
    response = client.post("/api/create", json=payload(name=name))

    assert response.status_code == 400
    assert response.get_json()["status"] == "error"
    assert list(tmp_path.iterdir()) == []
    assert not (tmp_path.parent / "outside").exists()


def test_creator_preserves_existing_normalized_project_without_prompt(client, tmp_path):
    project = tmp_path / "my_demo"
    project.mkdir()
    marker = project / "user-content.txt"
    marker.write_text("preserve this project")

    response = client.post("/api/create", json=payload(name="my-demo"))

    assert response.status_code == 409
    assert response.get_json()["status"] == "error"
    assert marker.read_text() == "preserve this project"
    assert list(project.iterdir()) == [marker]


@pytest.mark.parametrize("phase", ["environment", "install", "scaffold"])
def test_creator_reports_setup_failures(
    client, successful_setup, monkeypatch, tmp_path, phase
):
    if phase == "environment":
        monkeypatch.setattr(
            AmenCLI, "create_virtual_environment", lambda self, path: False
        )
    elif phase == "install":
        monkeypatch.setattr(AmenCLI, "install_framework", lambda *args: False)
    else:

        def fail(*args, **kwargs):
            raise OSError("injected scaffold write failure")

        monkeypatch.setattr("amen.templates.TemplateManager.generate_structure", fail)

    response = client.post("/api/create", json=payload())

    assert response.status_code == 500
    assert response.get_json()["status"] == "error"
    assert not (tmp_path / "demo" / ".amen_config").exists()


@pytest.mark.parametrize(
    "error,status",
    [
        (click.BadParameter("invalid project choice"), 400),
        (ProjectExistsError("project exists"), 409),
        (click.ClickException("setup failed"), 500),
    ],
)
def test_creator_maps_shared_contract_errors(client, monkeypatch, error, status):
    def fail(self, *, interactive=True):
        assert interactive is False
        raise error

    monkeypatch.setattr(AmenCLI, "create_app", fail)

    response = client.post("/api/create", json=payload())

    assert response.status_code == status
    assert response.get_json()["status"] == "error"


@pytest.mark.parametrize("unexpected", [None, "demo", Path("missing-project")])
def test_creator_defends_against_missing_success_result(
    client, monkeypatch, unexpected
):
    def incomplete(self, *, interactive=True):
        assert interactive is False
        return unexpected

    monkeypatch.setattr(AmenCLI, "create_app", incomplete)

    response = client.post("/api/create", json=payload())

    assert response.status_code == 500
    assert response.get_json()["status"] == "error"
    assert "did not complete" in response.get_json()["message"]


def test_creator_hides_unexpected_exception_details(client, monkeypatch):
    def fail(self, *, interactive=True):
        raise RuntimeError("internal-secret-value")

    monkeypatch.setattr(AmenCLI, "create_app", fail)

    response = client.post("/api/create", json=payload())

    assert response.status_code == 500
    assert response.get_json()["status"] == "error"
    assert "internal-secret-value" not in response.get_data(as_text=True)


def test_creator_page_renders_without_starting_server(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.content_type
    assert "projectForm" in response.get_data(as_text=True)
