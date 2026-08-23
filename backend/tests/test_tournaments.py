def register_and_login(client, email, role):
    client.post("/api/v1/auth/register", json={
        "name": "Org", "email": email, "password": "password123", "role": role,
    })
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return resp.json["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_tournament_payload(**overrides):
    payload = {
        "name": "Chess Open",
        "sport": "Chess",
        "format": "ROUND_ROBIN",
        "participant_type": "INDIVIDUAL",
    }
    payload.update(overrides)
    return payload


def test_guest_can_view_tournaments_without_login(client):
    resp = client.get("/api/v1/tournaments")
    assert resp.status_code == 200
    assert isinstance(resp.json, list)


def test_create_tournament_requires_organizer(client):
    resp = client.post("/api/v1/tournaments", json=create_tournament_payload())
    assert resp.status_code == 401  # no token at all


def test_player_cannot_create_tournament(client):
    token = register_and_login(client, "player1@example.com", "PLAYER")
    resp = client.post(
        "/api/v1/tournaments", json=create_tournament_payload(), headers=auth_headers(token)
    )
    assert resp.status_code == 403


def test_organizer_can_create_tournament(client):
    token = register_and_login(client, "org1@example.com", "ORGANIZER")
    resp = client.post(
        "/api/v1/tournaments", json=create_tournament_payload(), headers=auth_headers(token)
    )
    assert resp.status_code == 201
    assert resp.json["status"] == "DRAFT"


def test_guest_can_view_single_tournament(client):
    token = register_and_login(client, "org2@example.com", "ORGANIZER")
    created = client.post(
        "/api/v1/tournaments", json=create_tournament_payload(), headers=auth_headers(token)
    ).json

    resp = client.get(f"/api/v1/tournaments/{created['id']}")
    assert resp.status_code == 200
    assert resp.json["name"] == "Chess Open"


def test_invalid_tournament_data(client):
    token = register_and_login(client, "org3@example.com", "ORGANIZER")
    resp = client.post(
        "/api/v1/tournaments",
        json={"name": "", "sport": "Chess", "format": "ROUND_ROBIN", "participant_type": "INDIVIDUAL"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 400


def test_lifecycle_draft_to_registration_open(client):
    token = register_and_login(client, "org4@example.com", "ORGANIZER")
    created = client.post(
        "/api/v1/tournaments", json=create_tournament_payload(), headers=auth_headers(token)
    ).json

    resp = client.post(
        f"/api/v1/tournaments/{created['id']}/open-registration", headers=auth_headers(token)
    )
    assert resp.status_code == 200
    assert resp.json["status"] == "REGISTRATION_OPEN"


def test_invalid_lifecycle_transition_draft_to_ongoing(client):
    token = register_and_login(client, "org5@example.com", "ORGANIZER")
    created = client.post(
        "/api/v1/tournaments", json=create_tournament_payload(), headers=auth_headers(token)
    ).json

    # Skipping REGISTRATION_OPEN — should be rejected
    resp = client.post(f"/api/v1/tournaments/{created['id']}/start", headers=auth_headers(token))
    assert resp.status_code == 409


def test_cannot_change_format_after_leaving_draft(client):
    token = register_and_login(client, "org6@example.com", "ORGANIZER")
    created = client.post(
        "/api/v1/tournaments", json=create_tournament_payload(), headers=auth_headers(token)
    ).json

    client.post(f"/api/v1/tournaments/{created['id']}/open-registration", headers=auth_headers(token))

    resp = client.put(
        f"/api/v1/tournaments/{created['id']}",
        json={"format": "KNOCKOUT"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 409


def test_other_organizer_cannot_edit_tournament(client):
    token1 = register_and_login(client, "org7@example.com", "ORGANIZER")
    token2 = register_and_login(client, "org8@example.com", "ORGANIZER")

    created = client.post(
        "/api/v1/tournaments", json=create_tournament_payload(), headers=auth_headers(token1)
    ).json

    resp = client.put(
        f"/api/v1/tournaments/{created['id']}",
        json={"name": "Hijacked"},
        headers=auth_headers(token2),
    )
    assert resp.status_code == 403