import pytest
from app.extensions import db
from app.models import (
    User, Team, Player, Tournament, Participant, TournamentParticipant,
    Match, MatchParticipant, MatchResult, MatchScore, Standing,
)
from app.constants.enums import UserRole, ParticipationType, TournamentFormat, TournamentStatus, MatchStatus, ResultType


def _make_organizer(session):
    user = User(name="Org", email="modeltest@example.com", password_hash="x", role=UserRole.ORGANIZER)
    session.add(user)
    session.commit()
    return user


def _make_tournament(session, organizer, participant_type=ParticipationType.INDIVIDUAL):
    t = Tournament(
        name="Test Cup", sport="Chess", format=TournamentFormat.ROUND_ROBIN,
        participant_type=participant_type, status=TournamentStatus.DRAFT,
        organizer_id=organizer.id,
    )
    session.add(t)
    session.commit()
    return t


def test_participant_requires_exactly_one_of_player_or_team(app):
    with app.app_context():
        player = Player(name="Solo Player")
        db.session.add(player)
        db.session.commit()

        valid = Participant(type=ParticipationType.INDIVIDUAL, player_id=player.id)
        db.session.add(valid)
        db.session.commit()
        assert valid.id is not None


def test_participant_rejects_both_player_and_team(app):
    with app.app_context():
        player = Player(name="P")
        team = Team(name="T")
        db.session.add_all([player, team])
        db.session.commit()

        bad = Participant(type=ParticipationType.TEAM, player_id=player.id, team_id=team.id)
        db.session.add(bad)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()


def test_participant_rejects_neither_player_nor_team(app):
    with app.app_context():
        bad = Participant(type=ParticipationType.INDIVIDUAL)
        db.session.add(bad)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()


def test_match_participant_uniqueness(app):
    with app.app_context():
        organizer = _make_organizer(db.session)
        tournament = _make_tournament(db.session, organizer)
        player = Player(name="P1")
        db.session.add(player)
        db.session.commit()
        participant = Participant(type=ParticipationType.INDIVIDUAL, player_id=player.id)
        db.session.add(participant)
        db.session.commit()

        match = Match(tournament_id=tournament.id, round="1", status=MatchStatus.SCHEDULED)
        db.session.add(match)
        db.session.commit()

        mp1 = MatchParticipant(match_id=match.id, participant_id=participant.id)
        db.session.add(mp1)
        db.session.commit()

        mp2 = MatchParticipant(match_id=match.id, participant_id=participant.id)
        db.session.add(mp2)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()


def test_match_score_uniqueness(app):
    with app.app_context():
        organizer = _make_organizer(db.session)
        tournament = _make_tournament(db.session, organizer)
        player = Player(name="P2")
        db.session.add(player)
        db.session.commit()
        participant = Participant(type=ParticipationType.INDIVIDUAL, player_id=player.id)
        db.session.add(participant)
        db.session.commit()
        match = Match(tournament_id=tournament.id, round="1", status=MatchStatus.SCHEDULED)
        db.session.add(match)
        db.session.commit()
        mp = MatchParticipant(match_id=match.id, participant_id=participant.id)
        db.session.add(mp)
        db.session.commit()

        score1 = MatchScore(match_participant_id=mp.id, score=2)
        db.session.add(score1)
        db.session.commit()

        score2 = MatchScore(match_participant_id=mp.id, score=3)
        db.session.add(score2)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()


def test_match_result_winner_must_match_result_type(app):
    with app.app_context():
        organizer = _make_organizer(db.session)
        tournament = _make_tournament(db.session, organizer)
        match = Match(tournament_id=tournament.id, round="1", status=MatchStatus.SCHEDULED)
        db.session.add(match)
        db.session.commit()

        bad = MatchResult(match_id=match.id, result_type=ResultType.WIN, winner_participant_id=None)
        db.session.add(bad)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()


def test_standing_unique_per_tournament_participant(app):
    with app.app_context():
        organizer = _make_organizer(db.session)
        tournament = _make_tournament(db.session, organizer)
        player = Player(name="P3")
        db.session.add(player)
        db.session.commit()
        participant = Participant(type=ParticipationType.INDIVIDUAL, player_id=player.id)
        db.session.add(participant)
        db.session.commit()

        s1 = Standing(tournament_id=tournament.id, participant_id=participant.id)
        db.session.add(s1)
        db.session.commit()

        s2 = Standing(tournament_id=tournament.id, participant_id=participant.id)
        db.session.add(s2)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()