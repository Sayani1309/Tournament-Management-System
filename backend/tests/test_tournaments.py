def register_and_login(client, email, role):
    payload = {"name": "Org", "email": email, "password": "password123", "role": role}
    if role == "PLAYER":
        payload["participation_type"] = "INDIVIDUAL"
    client.post("/api/v1/auth/register", json=payload)
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
    assert isinstance(resp.json, dict)
    assert "items" in resp.json
    assert isinstance(resp.json["items"],list)


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

def test_filter_tournaments_by_status(client):
    token = register_and_login(client, "filterorg@example.com", "ORGANIZER")
    t1 = client.post(
        "/api/v1/tournaments",
        json=create_tournament_payload(format="ROUND_ROBIN"),
        headers=auth_headers(token),
    ).json  # stays DRAFT

    resp_draft = client.get("/api/v1/tournaments?status=DRAFT")
    resp_ongoing = client.get("/api/v1/tournaments?status=ONGOING")

    assert resp_draft.status_code == 200
    assert any(t["id"] == t1["id"] for t in resp_draft.json["items"])
    assert not any(t["id"] == t1["id"] for t in resp_ongoing.json["items"])


def test_filter_tournaments_by_invalid_status_rejected(client):
    resp = client.get("/api/v1/tournaments?status=NOT_A_REAL_STATUS")
    assert resp.status_code == 400

def test_cannot_start_with_fewer_than_two_participants(client, app):
    from app.models import Player
    from app.extensions import db

    token = register_and_login(client, "startguard@example.com", "ORGANIZER")
    tournament = client.post(
        "/api/v1/tournaments",
        json={"name": "Guard Test", "sport": "Chess", "format": "ROUND_ROBIN", "participant_type": "INDIVIDUAL"},
        headers=auth_headers(token),
    ).json
    client.post(f"/api/v1/tournaments/{tournament['id']}/open-registration", headers=auth_headers(token))

    with app.app_context():
        player = Player(name="Solo Player")
        db.session.add(player)
        db.session.commit()
        player_id = player.id

    client.post(
        f"/api/v1/tournaments/{tournament['id']}/participants",
        json={"player_id": player_id},
        headers=auth_headers(token),
    )

    resp = client.post(f"/api/v1/tournaments/{tournament['id']}/start", headers=auth_headers(token))
    assert resp.status_code == 409

# --- Input-size limits (CR-010) ---
def test_description_over_limit_rejected(client):
    token = register_and_login(client, "size1@example.com", "ORGANIZER")
    resp = client.post("/api/v1/tournaments", headers=auth_headers(token),
                       json=create_tournament_payload(description="A" * 2001))
    assert resp.status_code == 400


def test_description_at_limit_accepted(client):
    token = register_and_login(client, "size2@example.com", "ORGANIZER")
    resp = client.post("/api/v1/tournaments", headers=auth_headers(token),
                       json=create_tournament_payload(description="A" * 2000))
    assert resp.status_code == 201


def test_oversized_request_body_rejected(client):
    token = register_and_login(client, "size3@example.com", "ORGANIZER")
    resp = client.post("/api/v1/tournaments", headers=auth_headers(token),
                       json=create_tournament_payload(description="A" * 200_000))
    assert resp.status_code in (400, 413)


# --- Tournament creation rate limit (CR-010) ---
import pytest
from app import create_app
from app.config import TestingConfig
from app.extensions import limiter


@pytest.fixture
def rate_limited_client(monkeypatch):
    """The shared test app has rate limiting switched off, so build a second
    app with it on. Used only by the test below."""
    monkeypatch.setattr(TestingConfig, "RATELIMIT_ENABLED", True)
    limited_app = create_app("testing")
    yield limited_app.test_client()
    limiter.enabled = False  # restore the global limiter for the other tests


def test_tournament_creation_is_rate_limited(rate_limited_client):
    client = rate_limited_client
    token = register_and_login(client, "rate1@example.com", "ORGANIZER")
    headers = auth_headers(token)
    codes = [
        client.post("/api/v1/tournaments", headers=headers,
                    json=create_tournament_payload(name=f"T{i}")).status_code
        for i in range(11)
    ]
    assert codes[:10] == [201] * 10
    assert codes[10] == 429


def _date_payload(**extra):
    base = {"name": "Dated Cup", "sport": "Chess", "format": "KNOCKOUT",
            "participant_type": "INDIVIDUAL"}
    base.update(extra)
    return base


def test_end_date_before_start_date_rejected(client):
    token = register_and_login(client, "dateorg1@example.com", "ORGANIZER")
    res = client.post("/api/v1/tournaments",
                      json=_date_payload(start_date="2027-01-05", end_date="2027-01-02"),
                      headers=auth_headers(token))
    assert res.status_code == 400


def test_valid_and_same_day_dates_accepted(client):
    token = register_and_login(client, "dateorg2@example.com", "ORGANIZER")
    for s, e in (("2027-01-02", "2027-01-05"), ("2027-01-02", "2027-01-02")):
        res = client.post("/api/v1/tournaments", json=_date_payload(start_date=s, end_date=e),
                          headers=auth_headers(token))
        assert res.status_code == 201


def test_update_cannot_move_end_before_existing_start(client):
    token = register_and_login(client, "dateorg3@example.com", "ORGANIZER")
    res = client.post("/api/v1/tournaments",
                      json=_date_payload(start_date="2027-01-05", end_date="2027-01-09"),
                      headers=auth_headers(token))
    tid = res.get_json()["id"]
    bad = client.put(f"/api/v1/tournaments/{tid}", json={"end_date": "2027-01-01"},
                     headers=auth_headers(token))
    assert bad.status_code == 400


def test_start_date_in_past_rejected(client):
    from datetime import date, timedelta
    token = register_and_login(client, "pastorg1@example.com", "ORGANIZER")
    two_days_ago = (date.today() - timedelta(days=2)).isoformat()
    res = client.post("/api/v1/tournaments", json=_date_payload(start_date=two_days_ago),
                      headers=auth_headers(token))
    assert res.status_code == 400


def test_start_date_today_or_future_accepted(client):
    from datetime import date, timedelta
    token = register_and_login(client, "pastorg2@example.com", "ORGANIZER")
    for d in (date.today(), date.today() + timedelta(days=3)):
        res = client.post("/api/v1/tournaments", json=_date_payload(start_date=d.isoformat()),
                          headers=auth_headers(token))
        assert res.status_code == 201


def test_update_start_date_to_past_rejected(client):
    from datetime import date, timedelta
    token = register_and_login(client, "pastorg3@example.com", "ORGANIZER")
    tid = client.post("/api/v1/tournaments", json=_date_payload(),
                      headers=auth_headers(token)).get_json()["id"]
    res = client.put(f"/api/v1/tournaments/{tid}",
                     json={"start_date": (date.today() - timedelta(days=2)).isoformat()},
                     headers=auth_headers(token))
    assert res.status_code == 400