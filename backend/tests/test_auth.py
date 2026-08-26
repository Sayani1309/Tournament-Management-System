from app.constants.enums import UserRole


def register(client, email="alice@example.com", role="ORGANIZER", password="password123"):
    payload = {"name": "Alice", "email": email, "password": password, "role": role}
    if role == "PLAYER":
        payload["participation_type"] = "INDIVIDUAL"
    return client.post("/api/v1/auth/register", json=payload)

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

def test_player_individual_registration_creates_player(client, app):
    resp = client.post("/api/v1/auth/register", json={
        "name": "Solo Chess Player", "email": "indiv@example.com", "password": "password123",
        "role": "PLAYER", "participation_type": "INDIVIDUAL",
    })
    assert resp.status_code == 201

    with app.app_context():
        from app.models import Player
        player = Player.query.filter_by(name="Solo Chess Player").first()
        assert player is not None
        assert player.team_id is None
        assert player.user_id is not None


def test_player_new_team_registration_creates_team_and_player(client, app):
    resp = client.post("/api/v1/auth/register", json={
        "name": "Team Captain", "email": "newteam@example.com", "password": "password123",
        "role": "PLAYER", "participation_type": "TEAM", "team_option": "NEW", "team_name": "The Falcons",
    })
    assert resp.status_code == 201

    with app.app_context():
        from app.models import Player, Team
        team = Team.query.filter_by(name="The Falcons").first()
        assert team is not None
        player = Player.query.filter_by(name="Team Captain").first()
        assert player.team_id == team.id


def test_player_existing_team_registration_links_correctly(client, app):
    with app.app_context():
        from app.extensions import db
        from app.models import Team
        team = Team(name="The Ravens")
        db.session.add(team)
        db.session.commit()
        team_id = team.id

    resp = client.post("/api/v1/auth/register", json={
        "name": "Second Member", "email": "existingteam@example.com", "password": "password123",
        "role": "PLAYER", "participation_type": "TEAM", "team_option": "EXISTING", "team_id": team_id,
    })
    assert resp.status_code == 201

    with app.app_context():
        from app.models import Player
        player = Player.query.filter_by(name="Second Member").first()
        assert player.team_id == team_id


def test_player_registration_missing_participation_type_rejected(client):
    resp = client.post("/api/v1/auth/register", json={
        "name": "Incomplete", "email": "incomplete@example.com", "password": "password123",
        "role": "PLAYER",
    })
    assert resp.status_code == 400


def test_player_existing_team_with_invalid_id_rejected(client):
    resp = client.post("/api/v1/auth/register", json={
        "name": "Bad Team Ref", "email": "badteam@example.com", "password": "password123",
        "role": "PLAYER", "participation_type": "TEAM", "team_option": "EXISTING", "team_id": 999999,
    })
    assert resp.status_code == 404


def test_organizer_cannot_send_player_fields(client):
    resp = client.post("/api/v1/auth/register", json={
        "name": "Sneaky Org", "email": "sneaky@example.com", "password": "password123",
        "role": "ORGANIZER", "participation_type": "INDIVIDUAL",
    })
    assert resp.status_code == 400


def test_guest_can_view_teams_without_login(client, app):
    with app.app_context():
        from app.extensions import db
        from app.models import Team
        db.session.add(Team(name="Public Team"))
        db.session.commit()

    resp = client.get("/api/v1/teams")
    assert resp.status_code == 200
    assert any(t["name"] == "Public Team" for t in resp.json["items"])