from app.extensions import db
from app.models import Participant, TournamentParticipant
from app.constants.enums import ParticipationType, TournamentStatus
from app.services.tournament_service import get_tournament_or_404, TournamentError


class ParticipantError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_participant(tournament_id: int, organizer_id: int, player_id: int = None, team_id: int = None) -> TournamentParticipant:
    if (player_id is None) == (team_id is None):
        # both None, or both provided — invalid either way
        raise ParticipantError("Exactly one of player_id or team_id must be provided")

    tournament = get_tournament_or_404(tournament_id)

    if tournament.organizer_id != organizer_id:
        raise ParticipantError(
            "Only the owning organizer can register participants for this tournament",
            status_code=403,
        )
    
    if tournament.status != TournamentStatus.REGISTRATION_OPEN:
        raise ParticipantError(
            "Registration is not open for this tournament", status_code=409
        )

    if tournament.participant_type == ParticipationType.TEAM and team_id is None:
        raise ParticipantError(
            "This tournament requires team participants, not individual players", status_code=400
        )
    if tournament.participant_type == ParticipationType.INDIVIDUAL and player_id is None:
        raise ParticipantError(
            "This tournament requires individual player participants, not teams", status_code=400
        )

    participant_type = ParticipationType.TEAM if team_id is not None else ParticipationType.INDIVIDUAL

    # Reuse an existing Participant row for this player/team if one already exists,
    # rather than creating duplicates — Participant is meant to be a stable identity.
    query = Participant.query.filter_by(type=participant_type)
    if player_id is not None:
        query = query.filter_by(player_id=player_id)
    else:
        query = query.filter_by(team_id=team_id)
    participant = query.first()

    if participant is None:
        participant = Participant(type=participant_type, player_id=player_id, team_id=team_id)
        db.session.add(participant)
        db.session.flush()  # get participant.id without a full commit yet

    existing_registration = TournamentParticipant.query.filter_by(
        tournament_id=tournament_id, participant_id=participant.id
    ).first()
    if existing_registration:
        raise ParticipantError(
            "This participant is already registered in this tournament", status_code=409
        )

    registration = TournamentParticipant(tournament_id=tournament_id, participant_id=participant.id)
    db.session.add(registration)
    db.session.commit()
    return registration


def list_participants(tournament_id: int):
    get_tournament_or_404(tournament_id)  # 404 if tournament doesn't exist
    return (
        TournamentParticipant.query
        .filter_by(tournament_id=tournament_id)
        .order_by(TournamentParticipant.registered_at)
        .all()
    )