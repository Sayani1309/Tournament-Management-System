from app.constants.enums import UserRole


def register(client, email="alice@example.com", role="ORGANIZER", password="password123"):
    return client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": email, "password": password, "role": role},
    )


def login(client, email="alice@example.com", password="password123"):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def test_valid_registration(client):
    resp = register(client)
    assert resp.status_code == 201
    assert resp.json["email"] == "alice@example.com"
    assert "password" not in resp.json
    assert "password_hash" not in resp.json


def test_duplicate_email_registration(client):
    register(client)
    resp = register(client)
    assert resp.status_code == 409


def test_valid_login(client):
    register(client)
    resp = login(client)
    assert resp.status_code == 200
    assert "access_token" in resp.json


def test_invalid_password(client):
    register(client)
    resp = login(client, password="wrongpassword")
    assert resp.status_code == 401


def test_protected_endpoint_without_jwt(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_protected_endpoint_with_jwt(client):
    register(client)
    token = login(client).json["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json["email"] == "alice@example.com"


def test_player_forbidden_from_organizer_route(client):
    register(client, email="bob@example.com", role="PLAYER")
    token = login(client, email="bob@example.com").json["access_token"]

    resp = client.get(
        "/api/v1/_test/organizer-only", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403