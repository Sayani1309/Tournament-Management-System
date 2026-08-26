def register_and_login(client, email, role):
    client.post("/api/v1/auth/register", json={
        "name": "User", "email": email, "password": "password123", "role": role,
    })
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return resp.json["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_tournament(client, token, participant_type="INDIVIDUAL", format="ROUND_ROBIN"):
    resp = client.post(
        "/api/v1/tournaments",
        json={"name": "T", "sport": "Chess", "format": format, "participant_type": participant_type},
        headers=auth_headers(token),
    )
    return resp.json


def open_registration(client, token, tournament_id):
    return client.post(
        f"/api/v1/tournaments/{tournament_id}/open-registration", headers=auth_headers(token)
    )


def create_player_direct(client, token):
    # There's no player-creation route yet in this track — for tests we insert
    # directly via the app context in a fixture-style helper instead.
    pass


def test_guest_can_view_participants_without_login(client):
    token = register_and_login(client, "porg1@example.com", "ORGANIZER")
    tournament = create_tournament(client, token)
    resp = client.get(f"/api/v1/tournaments/{tournament['id']}/participants")
    assert resp.status_code == 200
    assert resp.json == []


def test_register_participant_requires_organizer(client):
    token = register_and_login(client, "porg2@example.com", "ORGANIZER")
    tournament = create_tournament(client, token)
    open_registration(client, token, tournament["id"])

    resp = client.post(f"/api/v1/tournaments/{tournament['id']}/participants", json={"player_id": 1})
    assert resp.status_code == 401


def test_individual_registration(client, app):
    from app.extensions import db
    from app.models import Player

    token = register_and_login(client, "porg3@example.com", "ORGANIZER")
    tournament = create_tournament(client, token, participant_type="INDIVIDUAL")
    open_registration(client, token, tournament["id"])

    with app.app_context():
        player = Player(name="Chess Player")
        db.session.add(player)
        db.session.commit()
        player_id = player.id

    resp = client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"player_id": player_id},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201


def test_team_registration(client, app):
    from app.extensions import db
    from app.models import Team

    token = register_and_login(client, "porg4@example.com", "ORGANIZER")
    tournament = create_tournament(client, token, participant_type="TEAM")
    open_registration(client, token, tournament["id"])

    with app.app_context():
        team = Team(name="Team Alpha")
        db.session.add(team)
        db.session.commit()
        team_id = team.id

    resp = client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"team_id": team_id},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201


def test_wrong_participant_type_rejected(client, app):
    from app.extensions import db
    from app.models import Team

    token = register_and_login(client, "porg5@example.com", "ORGANIZER")
    tournament = create_tournament(client, token, participant_type="INDIVIDUAL")
    open_registration(client, token, tournament["id"])

    with app.app_context():
        team = Team(name="Team Beta")
        db.session.add(team)
        db.session.commit()
        team_id = team.id

    resp = client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"team_id": team_id},
        headers=auth_headers(token),
    )
    assert resp.status_code == 400


def test_duplicate_registration_rejected(client, app):
    from app.extensions import db
    from app.models import Player

    token = register_and_login(client, "porg6@example.com", "ORGANIZER")
    tournament = create_tournament(client, token, participant_type="INDIVIDUAL")
    open_registration(client, token, tournament["id"])

    with app.app_context():
        player = Player(name="Dup Player")
        db.session.add(player)
        db.session.commit()
        player_id = player.id

    client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"player_id": player_id},
        headers=auth_headers(token),
    )
    resp = client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"player_id": player_id},
        headers=auth_headers(token),
    )
    assert resp.status_code == 409


def test_registration_rejected_when_not_open(client, app):
    from app.extensions import db
    from app.models import Player

    token = register_and_login(client, "porg7@example.com", "ORGANIZER")
    tournament = create_tournament(client, token, participant_type="INDIVIDUAL")
    # deliberately NOT opening registration — tournament stays DRAFT

    with app.app_context():
        player = Player(name="Blocked Player")
        db.session.add(player)
        db.session.commit()
        player_id = player.id

    resp = client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"player_id": player_id},
        headers=auth_headers(token),
    )
    assert resp.status_code == 409

def test_other_organizer_cannot_register_participants(client, app):
    from app.extensions import db
    from app.models import Player

    token1 = register_and_login(client, "ownorg1@example.com", "ORGANIZER")
    token2 = register_and_login(client, "ownorg2@example.com", "ORGANIZER")

    tournament = create_tournament(client, token1, participant_type="INDIVIDUAL")
    open_registration(client, token1, tournament["id"])

    with app.app_context():
        player = Player(name="Trespasser Target")
        db.session.add(player)
        db.session.commit()
        player_id = player.id

    resp = client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"player_id": player_id},
        headers=auth_headers(token2),
    )
    assert resp.status_code == 403

def test_participant_list_includes_names(client, app):
    from app.extensions import db
    from app.models import Player

    token = register_and_login(client, "pname@example.com", "ORGANIZER")
    tournament = create_tournament(client, token, participant_type="INDIVIDUAL")
    open_registration(client, token, tournament["id"])

    with app.app_context():
        player = Player(name="Named Player")
        db.session.add(player)
        db.session.commit()
        player_id = player.id

    client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"player_id": player_id},
        headers=auth_headers(token),
    )

    resp = client.get(f"/api/v1/tournaments/{tournament['id']}/participants")
    assert resp.status_code == 200
    assert resp.json[0]["participant"]["name"] == "Named Player"