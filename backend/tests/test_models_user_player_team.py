import pytest
from app.extensions import db
from app.models import User, Team, Player, Venue
from app.constants.enums import UserRole


def test_user_created_with_role(app):
    with app.app_context():
        user = User(
            name="Alice",
            email="alice@example.com",
            password_hash="hashed-not-plaintext",
            role=UserRole.ORGANIZER,
        )
        db.session.add(user)
        db.session.commit()

        fetched = User.query.filter_by(email="alice@example.com").first()
        assert fetched.password_hash != "plaintext"
        assert fetched.role == UserRole.ORGANIZER


def test_player_team_id_is_nullable(app):
    with app.app_context():
        player = Player(name="Bob")  # no team_id, no user_id
        db.session.add(player)
        db.session.commit()

        assert player.team_id is None
        assert player.user_id is None


def test_player_can_belong_to_team(app):
    with app.app_context():
        team = Team(name="Team A")
        db.session.add(team)
        db.session.commit()

        player = Player(name="Carol", team_id=team.id)
        db.session.add(player)
        db.session.commit()

        assert player.team.name == "Team A"
        assert team.players[0].name == "Carol"


def test_duplicate_email_rejected(app):
    with app.app_context():
        db.session.add(User(name="A", email="dup@example.com", password_hash="x", role=UserRole.PLAYER))
        db.session.commit()

        db.session.add(User(name="B", email="dup@example.com", password_hash="y", role=UserRole.PLAYER))
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()


def test_venue_capacity_check_constraint(app):
    with app.app_context():
        db.session.add(Venue(name="Stadium", location="City", capacity=-5))
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()