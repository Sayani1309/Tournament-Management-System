# backend/tests/test_venues.py
def register_and_login(client, email, role):
    client.post("/api/v1/auth/register", json={
        "name": "Org", "email": email, "password": "password123", "role": role,
    })
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return resp.json["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_guest_can_view_venues(client):
    resp = client.get("/api/v1/venues")
    assert resp.status_code == 200


def test_creating_venue_requires_organizer(client):
    resp = client.post("/api/v1/venues", json={"name": "Stadium", "location": "City"})
    assert resp.status_code == 401


def test_organizer_can_create_venue(client):
    token = register_and_login(client, "venueorg@example.com", "ORGANIZER")
    resp = client.post(
        "/api/v1/venues",
        json={"name": "Main Stadium", "location": "Kolkata", "capacity": 500},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201


def test_duplicate_venue_name_rejected(client):
    token = register_and_login(client, "venueorg2@example.com", "ORGANIZER")
    client.post(
        "/api/v1/venues",
        json={"name": "Unique Arena", "location": "City"},
        headers=auth_headers(token),
    )
    resp = client.post(
        "/api/v1/venues",
        json={"name": "Unique Arena", "location": "City"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 409