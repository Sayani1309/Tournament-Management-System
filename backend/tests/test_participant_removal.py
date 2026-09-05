def register_and_login(client, email, role="ORGANIZER"):
    payload = {"name": "U", "email": email, "password": "password123", "role": role}
    if role == "PLAYER":
        payload["participation_type"] = "INDIVIDUAL"
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return resp.json["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_tournament(client, token, participant_type="INDIVIDUAL"):
    resp = client.post(
        "/api/v1/tournaments",
        json={"name": "Removal Test", "sport": "Chess", "format": "ROUND_ROBIN", "participant_type": participant_type},
        headers=auth_headers(token),
    )
    return resp.json


def test_organizer_can_remove_participant_before_start(client, app):
    from app.extensions import db
    from app.models import Player

    token = register_and_login(client, "removeorg1@example.com")
    tournament = create_tournament(client, token)
    client.post(f"/api/v1/tournaments/{tournament['id']}/open-registration", headers=auth_headers(token))

    with app.app_context():
        player = Player(name="Removable Player")
        db.session.add(player)
        db.session.commit()
        player_id = player.id

    reg_resp = client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"player_id": player_id},
        headers=auth_headers(token),
    )
    participant_id = reg_resp.json["participant_id"]

    resp = client.delete(
        f"/api/v1/tournaments/{tournament['id']}/participants/{participant_id}",
        headers=auth_headers(token),
    )
    assert resp.status_code == 204

    list_resp = client.get(f"/api/v1/tournaments/{tournament['id']}/participants")
    assert list_resp.json == []


def test_cannot_remove_participant_after_tournament_started(client, app):
    from app.extensions import db
    from app.models import Player

    token = register_and_login(client, "removeorg2@example.com")
    tournament = create_tournament(client, token)
    client.post(f"/api/v1/tournaments/{tournament['id']}/open-registration", headers=auth_headers(token))

    with app.app_context():
        p1 = Player(name="Stay Player 1")
        p2 = Player(name="Stay Player 2")
        db.session.add_all([p1, p2])
        db.session.commit()
        p1_id, p2_id = p1.id, p2.id

    reg_resp = client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"player_id": p1_id},
        headers=auth_headers(token),
    )
    participant_id = reg_resp.json["participant_id"]
    client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"player_id": p2_id},
        headers=auth_headers(token),
    )

    client.post(f"/api/v1/tournaments/{tournament['id']}/start", headers=auth_headers(token))

    resp = client.delete(
        f"/api/v1/tournaments/{tournament['id']}/participants/{participant_id}",
        headers=auth_headers(token),
    )
    assert resp.status_code == 409


def test_other_organizer_cannot_remove_participant(client, app):
    from app.extensions import db
    from app.models import Player

    token1 = register_and_login(client, "removeorg3@example.com")
    token2 = register_and_login(client, "removeorg4@example.com")

    tournament = create_tournament(client, token1)
    client.post(f"/api/v1/tournaments/{tournament['id']}/open-registration", headers=auth_headers(token1))

    with app.app_context():
        player = Player(name="Protected Player")
        db.session.add(player)
        db.session.commit()
        player_id = player.id

    reg_resp = client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"player_id": player_id},
        headers=auth_headers(token1),
    )
    participant_id = reg_resp.json["participant_id"]

    resp = client.delete(
        f"/api/v1/tournaments/{tournament['id']}/participants/{participant_id}",
        headers=auth_headers(token2),
    )
    assert resp.status_code == 403


def test_remove_nonexistent_participant_returns_404(client, app):
    token = register_and_login(client, "removeorg5@example.com")
    tournament = create_tournament(client, token)
    client.post(f"/api/v1/tournaments/{tournament['id']}/open-registration", headers=auth_headers(token))

    resp = client.delete(
        f"/api/v1/tournaments/{tournament['id']}/participants/999999",
        headers=auth_headers(token),
    )
    assert resp.status_code == 404


def test_player_cannot_remove_participant(client, app):
    from app.extensions import db
    from app.models import Player

    token = register_and_login(client, "removeorg6@example.com")
    player_token = register_and_login(client, "removeplayer@example.com", role="PLAYER")

    tournament = create_tournament(client, token)
    client.post(f"/api/v1/tournaments/{tournament['id']}/open-registration", headers=auth_headers(token))

    with app.app_context():
        player = Player(name="Bystander Player")
        db.session.add(player)
        db.session.commit()
        player_id = player.id

    reg_resp = client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"player_id": player_id},
        headers=auth_headers(token),
    )
    participant_id = reg_resp.json["participant_id"]

    resp = client.delete(
        f"/api/v1/tournaments/{tournament['id']}/participants/{participant_id}",
        headers=auth_headers(player_token),
    )
    assert resp.status_code == 403

def test_removed_participant_standing_row_cleaned_up(client, app):
    from app.extensions import db
    from app.models import Player, Standing

    token = register_and_login(client, "cleanupstanding@example.com")
    tournament = create_tournament(client, token)
    client.post(f"/api/v1/tournaments/{tournament['id']}/open-registration", headers=auth_headers(token))

    with app.app_context():
        player = Player(name="Ghost Standing Player")
        db.session.add(player)
        db.session.commit()
        player_id = player.id

    reg_resp = client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"player_id": player_id},
        headers=auth_headers(token),
    )
    participant_id = reg_resp.json["participant_id"]

    # Force a standings view, which triggers the zero-row backfill for this participant
    client.get(f"/api/v1/tournaments/{tournament['id']}/standings")

    with app.app_context():
        existing = Standing.query.filter_by(
            tournament_id=tournament["id"], participant_id=participant_id
        ).first()
        assert existing is not None  # confirm the backfill actually created it

    client.delete(
        f"/api/v1/tournaments/{tournament['id']}/participants/{participant_id}",
        headers=auth_headers(token),
    )

    with app.app_context():
        remaining = Standing.query.filter_by(
            tournament_id=tournament["id"], participant_id=participant_id
        ).first()
        assert remaining is None