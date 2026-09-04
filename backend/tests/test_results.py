from app.extensions import db
from app.models import Player, Match, MatchParticipant


def register_and_login(client, email, role="ORGANIZER"):
    payload = {"name": "U", "email": email, "password": "password123", "role": role}
    if role == "PLAYER":
        payload["participation_type"] = "INDIVIDUAL"
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return resp.json["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def setup_match(client, app, email):
    token = register_and_login(client, email)
    tournament = client.post(
        "/api/v1/tournaments",
        json={"name": "Result Test", "sport": "Chess", "format": "ROUND_ROBIN", "participant_type": "INDIVIDUAL"},
        headers=auth_headers(token),
    ).json
    client.post(f"/api/v1/tournaments/{tournament['id']}/open-registration", headers=auth_headers(token))

    with app.app_context():
        p1 = Player(name="Player One")
        p2 = Player(name="Player Two")
        db.session.add_all([p1, p2])
        db.session.commit()
        p1_id, p2_id = p1.id, p2.id

    client.post(f"/api/v1/tournaments/{tournament['id']}/participants", json={"player_id": p1_id}, headers=auth_headers(token))
    client.post(f"/api/v1/tournaments/{tournament['id']}/participants", json={"player_id": p2_id}, headers=auth_headers(token))
    client.post(f"/api/v1/tournaments/{tournament['id']}/start", headers=auth_headers(token))
    client.post(f"/api/v1/tournaments/{tournament['id']}/fixtures", headers=auth_headers(token))

    with app.app_context():
        match = Match.query.filter_by(tournament_id=tournament["id"]).first()
        match_id = match.id
        mps = MatchParticipant.query.filter_by(match_id=match_id).all()
        participant_ids = [mp.participant_id for mp in mps]

    return token, match_id, participant_ids


def test_valid_result_win(client, app):
    token, match_id, pids = setup_match(client, app, "res1@example.com")
    resp = client.post(
        f"/api/v1/matches/{match_id}/result",
        json={
            "result_type": "WIN",
            "winner_participant_id": pids[0],
            "scores": [
                {"participant_id": pids[0], "score": 1},
                {"participant_id": pids[1], "score": 0},
            ],
        },
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    assert resp.json["result_type"] == "WIN"
    assert resp.json["winner_participant_id"] == pids[0]


def test_valid_result_draw(client, app):
    token, match_id, pids = setup_match(client, app, "res2@example.com")
    resp = client.post(
        f"/api/v1/matches/{match_id}/result",
        json={
            "result_type": "DRAW",
            "scores": [
                {"participant_id": pids[0], "score": 1},
                {"participant_id": pids[1], "score": 1},
            ],
        },
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    assert resp.json["result_type"] == "DRAW"
    assert resp.json["winner_participant_id"] is None


def test_win_without_winner_rejected(client, app):
    token, match_id, pids = setup_match(client, app, "res3@example.com")
    resp = client.post(
        f"/api/v1/matches/{match_id}/result",
        json={
            "result_type": "WIN",
            "scores": [
                {"participant_id": pids[0], "score": 1},
                {"participant_id": pids[1], "score": 0},
            ],
        },
        headers=auth_headers(token),
    )
    assert resp.status_code == 400


def test_nonexistent_match_returns_404(client, app):
    token = register_and_login(client, "res4@example.com")
    resp = client.post(
        "/api/v1/matches/999999/result",
        json={"result_type": "DRAW", "scores": [{"participant_id": 1, "score": 0}, {"participant_id": 2, "score": 0}]},
        headers=auth_headers(token),
    )
    assert resp.status_code == 404


def test_duplicate_result_rejected(client, app):
    token, match_id, pids = setup_match(client, app, "res5@example.com")
    payload = {
        "result_type": "DRAW",
        "scores": [
            {"participant_id": pids[0], "score": 1},
            {"participant_id": pids[1], "score": 1},
        ],
    }
    client.post(f"/api/v1/matches/{match_id}/result", json=payload, headers=auth_headers(token))
    resp = client.post(f"/api/v1/matches/{match_id}/result", json=payload, headers=auth_headers(token))
    assert resp.status_code == 409


def test_player_cannot_submit_result(client, app):
    token, match_id, pids = setup_match(client, app, "res6@example.com")
    player_token = register_and_login(client, "res6player@example.com", role="PLAYER")

    resp = client.post(
        f"/api/v1/matches/{match_id}/result",
        json={
            "result_type": "DRAW",
            "scores": [
                {"participant_id": pids[0], "score": 1},
                {"participant_id": pids[1], "score": 1},
            ],
        },
        headers=auth_headers(player_token),
    )
    assert resp.status_code == 403


def test_guest_can_view_result_without_login(client, app):
    token, match_id, pids = setup_match(client, app, "res7@example.com")
    client.post(
        f"/api/v1/matches/{match_id}/result",
        json={
            "result_type": "DRAW",
            "scores": [
                {"participant_id": pids[0], "score": 1},
                {"participant_id": pids[1], "score": 1},
            ],
        },
        headers=auth_headers(token),
    )
    resp = client.get(f"/api/v1/matches/{match_id}/result")
    assert resp.status_code == 200
    assert resp.json["result_type"] == "DRAW"


def test_both_participants_scores_stored(client, app):
    token, match_id, pids = setup_match(client, app, "res8@example.com")
    client.post(
        f"/api/v1/matches/{match_id}/result",
        json={
            "result_type": "WIN",
            "winner_participant_id": pids[0],
            "scores": [
                {"participant_id": pids[0], "score": 3},
                {"participant_id": pids[1], "score": 1},
            ],
        },
        headers=auth_headers(token),
    )

    with app.app_context():
        from app.models import MatchScore, MatchParticipant
        mps = MatchParticipant.query.filter_by(match_id=match_id).all()
        scores = [MatchScore.query.filter_by(match_participant_id=mp.id).first() for mp in mps]
        assert all(s is not None for s in scores)
        stored_scores = sorted(float(s.score) for s in scores)
        assert stored_scores == [1.0, 3.0]

def test_other_organizer_cannot_submit_result(client, app):
    token, match_id, pids = setup_match(client, app, "ownres@example.com")
    other_token = register_and_login(client, "otherorg_res@example.com")

    resp = client.post(
        f"/api/v1/matches/{match_id}/result",
        json={
            "result_type": "DRAW",
            "scores": [
                {"participant_id": pids[0], "score": 1},
                {"participant_id": pids[1], "score": 1},
            ],
        },
        headers=auth_headers(other_token),
    )
    assert resp.status_code == 403

def test_knockout_match_cannot_be_draw(client, app):
    from app.models import Player
    from app.extensions import db

    token = register_and_login(client, "koresult@example.com")
    tournament = client.post(
        "/api/v1/tournaments",
        json={"name": "KO Draw Test", "sport": "Chess", "format": "KNOCKOUT", "participant_type": "INDIVIDUAL"},
        headers=auth_headers(token),
    ).json
    client.post(f"/api/v1/tournaments/{tournament['id']}/open-registration", headers=auth_headers(token))

    with app.app_context():
        p1 = Player(name="KO A")
        p2 = Player(name="KO B")
        db.session.add_all([p1, p2])
        db.session.commit()
        p1_id, p2_id = p1.id, p2.id

    client.post(f"/api/v1/tournaments/{tournament['id']}/participants", json={"player_id": p1_id}, headers=auth_headers(token))
    client.post(f"/api/v1/tournaments/{tournament['id']}/participants", json={"player_id": p2_id}, headers=auth_headers(token))
    client.post(f"/api/v1/tournaments/{tournament['id']}/start", headers=auth_headers(token))
    matches = client.post(f"/api/v1/tournaments/{tournament['id']}/fixtures", headers=auth_headers(token)).json
    match_id = matches[0]["id"]
    participant_ids = [p["id"] for p in matches[0]["participants"]]

    resp = client.post(
        f"/api/v1/matches/{match_id}/result",
        json={
            "result_type": "DRAW",
            "scores": [
                {"participant_id": participant_ids[0], "score": 1},
                {"participant_id": participant_ids[1], "score": 1},
            ],
        },
        headers=auth_headers(token),
    )
    assert resp.status_code == 400