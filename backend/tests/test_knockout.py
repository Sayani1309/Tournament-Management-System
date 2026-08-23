from app.extensions import db
from app.models import Player, Match, MatchParticipant, MatchResult, Tournament


def register_and_login(client, email, role="ORGANIZER"):
    client.post("/api/v1/auth/register", json={
        "name": "U", "email": email, "password": "password123", "role": role,
    })
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return resp.json["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def setup_knockout_tournament(client, app, count, email):
    token = register_and_login(client, email)
    tournament = client.post(
        "/api/v1/tournaments",
        json={"name": "KO Test", "sport": "Chess", "format": "KNOCKOUT", "participant_type": "INDIVIDUAL"},
        headers=auth_headers(token),
    ).json
    client.post(f"/api/v1/tournaments/{tournament['id']}/open-registration", headers=auth_headers(token))

    with app.app_context():
        player_ids = []
        for i in range(count):
            p = Player(name=f"KO Player {i}")
            db.session.add(p)
            db.session.commit()
            player_ids.append(p.id)

    for pid in player_ids:
        client.post(f"/api/v1/tournaments/{tournament['id']}/participants", json={"player_id": pid}, headers=auth_headers(token))

    client.post(f"/api/v1/tournaments/{tournament['id']}/start", headers=auth_headers(token))
    client.post(f"/api/v1/tournaments/{tournament['id']}/fixtures", headers=auth_headers(token))

    return token, tournament["id"]


def submit_win(client, token, match_id, winner_id, loser_id):
    return client.post(
        f"/api/v1/matches/{match_id}/result",
        json={
            "result_type": "WIN",
            "winner_participant_id": winner_id,
            "scores": [
                {"participant_id": winner_id, "score": 1},
                {"participant_id": loser_id, "score": 0},
            ],
        },
        headers=auth_headers(token),
    )


def test_winner_advances_to_next_round_slot(client, app):
    token, tid = setup_knockout_tournament(client, app, 4, "ko1@example.com")

    with app.app_context():
        m0 = Match.query.filter_by(tournament_id=tid, round="Round 1-Match 0").first()
        mps = MatchParticipant.query.filter_by(match_id=m0.id).all()
        p_ids = [mp.participant_id for mp in mps]

    submit_win(client, token, m0.id, p_ids[0], p_ids[1])

    with app.app_context():
        next_match = Match.query.filter_by(tournament_id=tid, round="Round 2-Match 0").first()
        assert next_match is not None
        mps = MatchParticipant.query.filter_by(match_id=next_match.id).all()
        assert p_ids[0] in [mp.participant_id for mp in mps]


def test_next_round_match_populated_by_both_winners(client, app):
    token, tid = setup_knockout_tournament(client, app, 4, "ko2@example.com")

    with app.app_context():
        m0 = Match.query.filter_by(tournament_id=tid, round="Round 1-Match 0").first()
        m1 = Match.query.filter_by(tournament_id=tid, round="Round 1-Match 1").first()
        m0_pids = [mp.participant_id for mp in MatchParticipant.query.filter_by(match_id=m0.id).all()]
        m1_pids = [mp.participant_id for mp in MatchParticipant.query.filter_by(match_id=m1.id).all()]

    submit_win(client, token, m0.id, m0_pids[0], m0_pids[1])
    submit_win(client, token, m1.id, m1_pids[0], m1_pids[1])

    with app.app_context():
        final = Match.query.filter_by(tournament_id=tid, round="Round 2-Match 0").first()
        mps = MatchParticipant.query.filter_by(match_id=final.id).all()
        assert len(mps) == 2
        assert set(mp.participant_id for mp in mps) == {m0_pids[0], m1_pids[0]}


def test_final_determines_champion_and_completes_tournament(client, app):
    token, tid = setup_knockout_tournament(client, app, 4, "ko3@example.com")

    with app.app_context():
        m0 = Match.query.filter_by(tournament_id=tid, round="Round 1-Match 0").first()
        m1 = Match.query.filter_by(tournament_id=tid, round="Round 1-Match 1").first()
        m0_pids = [mp.participant_id for mp in MatchParticipant.query.filter_by(match_id=m0.id).all()]
        m1_pids = [mp.participant_id for mp in MatchParticipant.query.filter_by(match_id=m1.id).all()]

    submit_win(client, token, m0.id, m0_pids[0], m0_pids[1])
    submit_win(client, token, m1.id, m1_pids[0], m1_pids[1])

    with app.app_context():
        final = Match.query.filter_by(tournament_id=tid, round="Round 2-Match 0").first()
        final_id = final.id

    submit_win(client, token, final_id, m0_pids[0], m1_pids[0])

    resp = client.get(f"/api/v1/tournaments/{tid}")
    assert resp.json["status"] == "COMPLETED"

    with app.app_context():
        result = MatchResult.query.filter_by(match_id=final_id).first()
        assert result.winner_participant_id == m0_pids[0]


def test_bye_auto_advances_without_organizer_action(client, app):
    token, tid = setup_knockout_tournament(client, app, 3, "ko4@example.com")
    # 3 participants -> 4-slot bracket -> 1 bye

    with app.app_context():
        bye_results = MatchResult.query.join(Match).filter(Match.tournament_id == tid).all()
        assert len(bye_results) == 1
        bye_result = bye_results[0]
        bye_winner_id = bye_result.winner_participant_id

        next_round_matches = Match.query.filter(
            Match.tournament_id == tid, Match.round.like("Round 2-Match%")
        ).all()
        assert len(next_round_matches) == 1
        mps = MatchParticipant.query.filter_by(match_id=next_round_matches[0].id).all()
        assert bye_winner_id in [mp.participant_id for mp in mps]