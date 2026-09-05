from app.extensions import db
from app.models import Player, Team, Match, MatchParticipant, MatchResult


def register_and_login(client, email, role="ORGANIZER"):
    client.post("/api/v1/auth/register", json={
        "name": "U", "email": email, "password": "password123", "role": role,
    })
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return resp.json["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def setup_tournament_with_participants(client, app, count, participant_type="INDIVIDUAL", format="ROUND_ROBIN"):
    token = register_and_login(client, f"fx{count}{format}@example.com")
    tournament = client.post(
        "/api/v1/tournaments",
        json={"name": "Fixture Test", "sport": "Chess", "format": format, "participant_type": participant_type},
        headers=auth_headers(token),
    ).json
    client.post(f"/api/v1/tournaments/{tournament['id']}/open-registration", headers=auth_headers(token))

    with app.app_context():
        player_ids = []
        for i in range(count):
            p = Player(name=f"Player {i}")
            db.session.add(p)
            db.session.commit()
            player_ids.append(p.id)

    for pid in player_ids:
        client.post(
            f"/api/v1/tournaments/{tournament['id']}/participants",
            json={"player_id": pid},
            headers=auth_headers(token),
        )

    client.post(f"/api/v1/tournaments/{tournament['id']}/start", headers=auth_headers(token))
    return token, tournament["id"]


def test_guest_can_view_matches_without_login(client, app):
    token, tid = setup_tournament_with_participants(client, app, 4)
    client.post(f"/api/v1/tournaments/{tid}/fixtures", headers=auth_headers(token))

    resp = client.get(f"/api/v1/tournaments/{tid}/matches")
    assert resp.status_code == 200
    assert len(resp.json) > 0


def test_round_robin_even_participant_match_count(client, app):
    token, tid = setup_tournament_with_participants(client, app, 4, format="ROUND_ROBIN")
    resp = client.post(f"/api/v1/tournaments/{tid}/fixtures", headers=auth_headers(token))
    assert resp.status_code == 201
    assert len(resp.json) == 6  # N(N-1)/2 = 4*3/2 = 6


def test_round_robin_odd_participant_match_count(client, app):
    token, tid = setup_tournament_with_participants(client, app, 5, format="ROUND_ROBIN")
    resp = client.post(f"/api/v1/tournaments/{tid}/fixtures", headers=auth_headers(token))
    assert resp.status_code == 201
    assert len(resp.json) == 10  # N(N-1)/2 = 5*4/2 = 10


def test_round_robin_no_self_match_or_duplicate_pairing(client, app):
    token, tid = setup_tournament_with_participants(client, app, 4, format="ROUND_ROBIN")
    client.post(f"/api/v1/tournaments/{tid}/fixtures", headers=auth_headers(token))

    with app.app_context():
        matches = Match.query.filter_by(tournament_id=tid).all()
        seen_pairs = set()
        for m in matches:
            mps = MatchParticipant.query.filter_by(match_id=m.id).all()
            pids = tuple(sorted(mp.participant_id for mp in mps))
            assert len(pids) == 2
            assert pids[0] != pids[1]
            assert pids not in seen_pairs
            seen_pairs.add(pids)


def test_knockout_bracket_slot_counts_and_byes():
    from app.services.fixture_service import _next_power_of_two
    assert _next_power_of_two(8) == 8
    assert _next_power_of_two(7) == 8
    assert _next_power_of_two(6) == 8
    assert _next_power_of_two(5) == 8
    assert _next_power_of_two(4) == 4


def test_knockout_bye_count(client, app):
    token, tid = setup_tournament_with_participants(client, app, 5, format="KNOCKOUT")
    resp = client.post(f"/api/v1/tournaments/{tid}/fixtures", headers=auth_headers(token))
    assert resp.status_code == 201

    with app.app_context():
        results = MatchResult.query.join(Match).filter(Match.tournament_id == tid).all()
        # 5 participants -> 8-slot bracket -> 3 byes -> 3 auto-completed bye matches
        assert len(results) == 3


def test_cannot_generate_fixtures_before_ongoing(client, app):
    token = register_and_login(client, "fxblocked@example.com")
    tournament = client.post(
        "/api/v1/tournaments",
        json={"name": "Blocked", "sport": "Chess", "format": "ROUND_ROBIN", "participant_type": "INDIVIDUAL"},
        headers=auth_headers(token),
    ).json
    # still in DRAFT, never opened/started
    resp = client.post(f"/api/v1/tournaments/{tournament['id']}/fixtures", headers=auth_headers(token))
    assert resp.status_code == 409


def test_cannot_generate_fixtures_twice(client, app):
    token, tid = setup_tournament_with_participants(client, app, 4)
    client.post(f"/api/v1/tournaments/{tid}/fixtures", headers=auth_headers(token))
    resp = client.post(f"/api/v1/tournaments/{tid}/fixtures", headers=auth_headers(token))
    assert resp.status_code == 409

def test_other_organizer_cannot_generate_fixtures(client, app):
    token, tid = setup_tournament_with_participants(client, app, 4)
    other_token = register_and_login(client, "otherorg_fx@example.com")

    resp = client.post(f"/api/v1/tournaments/{tid}/fixtures", headers=auth_headers(other_token))
    assert resp.status_code == 403

def test_matches_include_participant_names(client, app):
    token, tid = setup_tournament_with_participants(client, app, 4)
    client.post(f"/api/v1/tournaments/{tid}/fixtures", headers=auth_headers(token))

    resp = client.get(f"/api/v1/tournaments/{tid}/matches")
    assert resp.status_code == 200
    for match in resp.json:
        assert "participants" in match
        assert len(match["participants"]) == 2
        for p in match["participants"]:
            assert p["name"] is not None

def test_get_single_match(client, app):
    token, tid = setup_tournament_with_participants(client, app, 4)
    client.post(f"/api/v1/tournaments/{tid}/fixtures", headers=auth_headers(token))

    with app.app_context():
        from app.models import Match
        match = Match.query.filter_by(tournament_id=tid).first()
        match_id = match.id

    resp = client.get(f"/api/v1/matches/{match_id}")
    assert resp.status_code == 200
    assert resp.json["id"] == match_id
    assert len(resp.json["participants"]) == 2


def test_get_nonexistent_match_returns_404(client):
    resp = client.get("/api/v1/matches/999999")
    assert resp.status_code == 404

def test_organizer_can_schedule_match_venue_and_time(client, app):
    token, tid = setup_tournament_with_participants(client, app, 4)
    matches = client.post(f"/api/v1/tournaments/{tid}/fixtures", headers=auth_headers(token)).json
    match_id = matches[0]["id"]

    venue_resp = client.post(
        "/api/v1/venues",
        json={"name": "Test Arena", "location": "City"},
        headers=auth_headers(token),
    )
    venue_id = venue_resp.json["id"]

    resp = client.put(
        f"/api/v1/matches/{match_id}/schedule",
        json={"venue_id": venue_id, "scheduled_at": "2026-12-01T15:00:00+00:00"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json["venue_id"] == venue_id


def test_other_organizer_cannot_schedule_match(client, app):
    token, tid = setup_tournament_with_participants(client, app, 4)
    matches = client.post(f"/api/v1/tournaments/{tid}/fixtures", headers=auth_headers(token)).json
    match_id = matches[0]["id"]

    other_token = register_and_login(client, "otherorg_schedule@example.com")
    resp = client.put(
        f"/api/v1/matches/{match_id}/schedule",
        json={"venue_id": None, "scheduled_at": "2026-12-01T15:00:00+00:00"},
        headers=auth_headers(other_token),
    )
    assert resp.status_code == 403