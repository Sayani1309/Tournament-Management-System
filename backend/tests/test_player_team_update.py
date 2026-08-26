def register_and_login(client, email, role, extra=None):
    payload = {"name": "U", "email": email, "password": "password123", "role": role}
    if extra:
        payload.update(extra)
    if role == "PLAYER" and "participation_type" not in payload:
        payload["participation_type"] = "INDIVIDUAL"
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return resp.json["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_player_can_update_their_own_team(client, app):
    from app.extensions import db
    from app.models import Team, Player

    token = register_and_login(client, "selfupdate@example.com", "PLAYER")

    with app.app_context():
        team = Team(name="New Squad")
        db.session.add(team)
        db.session.commit()
        team_id = team.id
        player = Player.query.filter_by(name="U").first()
        player_id = player.id

    resp = client.put(
        f"/api/v1/players/{player_id}/team",
        json={"team_id": team_id},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json["team_id"] == team_id


def test_player_can_remove_themself_from_team(client, app):
    from app.extensions import db
    from app.models import Team, Player

    with app.app_context():
        team = Team(name="Leaving Squad")
        db.session.add(team)
        db.session.commit()
        team_id = team.id

    token = register_and_login(
        client, "leaveteam@example.com", "PLAYER",
        extra={"participation_type": "TEAM", "team_option": "EXISTING", "team_id": team_id},
    )

    with app.app_context():
        player = Player.query.filter_by(name="U").first()
        player_id = player.id
        assert player.team_id == team_id

    resp = client.put(
        f"/api/v1/players/{player_id}/team",
        json={"team_id": None},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json["team_id"] is None


def test_player_cannot_update_another_players_team(client, app):
    from app.extensions import db
    from app.models import Team, Player

    register_and_login(client, "victim@example.com", "PLAYER")
    attacker_token = register_and_login(client, "attacker@example.com", "PLAYER")

    with app.app_context():
        team = Team(name="Hijack Target Squad")
        db.session.add(team)
        db.session.commit()
        team_id = team.id
        victim = Player.query.filter_by(name="U").filter(Player.user_id.isnot(None)).first()
        # Need the victim specifically, not the attacker — query by email-linked user instead
        from app.models import User
        victim_user = User.query.filter_by(email="victim@example.com").first()
        victim_player = Player.query.filter_by(user_id=victim_user.id).first()
        victim_player_id = victim_player.id

    resp = client.put(
        f"/api/v1/players/{victim_player_id}/team",
        json={"team_id": team_id},
        headers=auth_headers(attacker_token),
    )
    assert resp.status_code == 403


def test_organizer_can_update_any_players_team(client, app):
    from app.extensions import db
    from app.models import Team, Player, User

    register_and_login(client, "managedplayer@example.com", "PLAYER")
    org_token = register_and_login(client, "teammgmtorg@example.com", "ORGANIZER")

    with app.app_context():
        team = Team(name="Organizer Assigned Squad")
        db.session.add(team)
        db.session.commit()
        team_id = team.id
        user = User.query.filter_by(email="managedplayer@example.com").first()
        player = Player.query.filter_by(user_id=user.id).first()
        player_id = player.id

    resp = client.put(
        f"/api/v1/players/{player_id}/team",
        json={"team_id": team_id},
        headers=auth_headers(org_token),
    )
    assert resp.status_code == 200
    assert resp.json["team_id"] == team_id


def test_update_team_with_invalid_team_id_rejected(client, app):
    from app.models import Player, User

    token = register_and_login(client, "invalidteamref@example.com", "PLAYER")

    with app.app_context():
        user = User.query.filter_by(email="invalidteamref@example.com").first()
        player = Player.query.filter_by(user_id=user.id).first()
        player_id = player.id

    resp = client.put(
        f"/api/v1/players/{player_id}/team",
        json={"team_id": 999999},
        headers=auth_headers(token),
    )
    assert resp.status_code == 404


def test_update_nonexistent_player_returns_404(client):
    token = register_and_login(client, "orgfor404@example.com", "ORGANIZER")
    resp = client.put(
        "/api/v1/players/999999/team",
        json={"team_id": None},
        headers=auth_headers(token),
    )
    assert resp.status_code == 404