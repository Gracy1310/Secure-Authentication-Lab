
import re
import sqlite3
import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    database = tmp_path / "test_auth.db"

    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-only",
        "DATABASE": str(database)
    })

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def get_csrf_token(client, path):
    response = client.get(path)
    assert response.status_code == 200

    html = response.get_data(as_text=True)
    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        html
    )

    assert match is not None
    return match.group(1)


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_register_user(client):
    token = get_csrf_token(client, "/register")

    response = client.post("/register", data={
        "username": "teststudent",
        "password": "BlueTeam@2026Secure",
        "csrf_token": token
    })

    assert response.status_code in (200, 302)


def test_password_is_hashed(app, client):
    token = get_csrf_token(client, "/register")

    client.post("/register", data={
        "username": "hashstudent",
        "password": "BlueTeam@2026Secure",
        "csrf_token": token
    })

    connection = sqlite3.connect(app.config["DATABASE"])
    result = connection.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        ("hashstudent",)
    ).fetchone()
    connection.close()

    assert result is not None
    assert result[0].startswith("scrypt:")
    assert result[0] != "BlueTeam@2026Secure"


def test_invalid_login_rejected(client):
    token = get_csrf_token(client, "/login")

    response = client.post("/login", data={
        "username": "unknownuser",
        "password": "WrongPassword@123",
        "csrf_token": token
    })

    assert b"Invalid username or password" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")

    assert response.status_code in (302, 401)
