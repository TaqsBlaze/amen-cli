"""Exercise generated Flask authentication without starting application servers."""

import itertools
import os
import subprocess
import sys
import textwrap

import pytest

from amen.templates import TemplateManager


@pytest.mark.parametrize(
    "app_type,database",
    list(itertools.product(["api", "webapp"], ["none", "sqlite3", "mysql"])),
)
def test_generated_flask_bearer_authentication(tmp_path, app_type, database):
    name = f"auth_{app_type}_{database}"
    project = tmp_path / name
    project.mkdir()
    TemplateManager().generate_structure(project, "flask", app_type, name, database)
    environment = os.environ.copy()
    environment.pop("DATABASE_URL", None)
    environment["SECRET_KEY"] = "test-secret-for-flask-authentication-0123456789"
    source = f"""
        import os
        import time
        from unittest.mock import patch

        import jwt

        from {name} import app
        from {name}.auth.token import token_required

        app.config["TESTING"] = True
        client = app.test_client()
        secret = os.environ["SECRET_KEY"]
        claims = {{"sub": "test-user", "exp": int(time.time()) + 3600}}
        token = jwt.encode(claims, secret, algorithm="HS256")

        malformed = [
            None, "", " ", "\\t", "Bearer", "Bearer ", "Bearer\\t",
            "Bearer token extra", "Bearer\\ttoken\\textra",
            "Basic " + token, "Token " + token, "Bearer " + token + " extra",
            "Bearer invalid-token",
        ]
        for header in malformed:
            headers = {{}} if header is None else {{"Authorization": header}}
            response = client.get("/protected", headers=headers)
            assert response.status_code == 401, (header, response.status_code)
            assert response.is_json
            assert secret not in response.get_data(as_text=True)

        accepted = [
            "Bearer " + token,
            "bearer " + token,
            "BEARER " + token,
            "Bearer    " + token,
            "  Bearer\\t" + token + " ",
        ]
        for header in accepted:
            response = client.get("/protected", headers={{"Authorization": header}})
            assert response.status_code == 200, (header, response.get_data(as_text=True))
            assert response.get_json()["user"]["sub"] == "test-user"

        invalid_tokens = [
            jwt.encode({{"sub": "expired", "exp": int(time.time()) - 1}}, secret, algorithm="HS256"),
            jwt.encode(claims, "a-different-signing-secret-0123456789012345", algorithm="HS256"),
            jwt.encode(claims, secret, algorithm="HS512"),
        ]
        for invalid in invalid_tokens:
            response = client.get("/protected", headers={{"Authorization": "Bearer " + invalid}})
            assert response.status_code == 401
            assert secret not in response.get_data(as_text=True)

        # An unrelated decoder bug must not be disguised as invalid credentials.
        with patch("{name}.auth.token.jwt.decode", side_effect=RuntimeError("decoder bug")):
            try:
                client.get("/protected", headers={{"Authorization": "Bearer " + token}})
            except RuntimeError as error:
                assert str(error) == "decoder bug"
            else:
                raise AssertionError("Unrelated decoder errors must propagate")

        @token_required
        def failing_handler(current_user):
            raise RuntimeError("handler bug")

        with app.test_request_context(headers={{"Authorization": "Bearer " + token}}):
            try:
                failing_handler()
            except RuntimeError as error:
                assert str(error) == "handler bug"
            else:
                raise AssertionError("Handler errors must propagate")
    """
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(source)],
        cwd=project,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
