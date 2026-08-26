from datetime import datetime, timezone

from app.extensions import db
from app.models import Tournament
from app.constants.enums import TournamentStatus, TournamentFormat, ParticipationType


class TournamentError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidTransitionError(TournamentError):
    def __init__(self, current, target):
        super().__init__(
            f"Cannot transition tournament from {current.value} to {target.value}",
            status_code=409,
        )


# The only allowed forward transitions. No skipping, no reverse.
ALLOWED_TRANSITIONS = {
    TournamentStatus.DRAFT: {TournamentStatus.REGISTRATION_OPEN},
    TournamentStatus.REGISTRATION_OPEN: {TournamentStatus.ONGOING},
    TournamentStatus.ONGOING: {TournamentStatus.COMPLETED},
    TournamentStatus.COMPLETED: set(),
}

# Fields the organizer may still edit once the tournament leaves DRAFT.
# participant_type and format become locked immediately upon leaving DRAFT.
LOCKED_AFTER_DRAFT = {"participant_type", "format"}


def create_tournament(organizer_id: int, name: str, sport: str, format: str,
                       participant_type: str, description: str = None,
                       start_date=None, end_date=None) -> Tournament:
    try:
        format_enum = TournamentFormat(format)
    except ValueError:
        raise TournamentError(f"Invalid format: {format}")

    try:
        participant_type_enum = ParticipationType(participant_type)
    except ValueError:
        raise TournamentError(f"Invalid participant_type: {participant_type}")

    tournament = Tournament(
        organizer_id=organizer_id,
        name=name,
        sport=sport,
        format=format_enum,
        participant_type=participant_type_enum,
        description=description,
        start_date=start_date,
        end_date=end_date,
        status=TournamentStatus.DRAFT,
    )
    db.session.add(tournament)
    db.session.commit()
    return tournament


def get_tournament_or_404(tournament_id: int) -> Tournament:
    tournament = db.session.get(Tournament, tournament_id)
    if not tournament:
        raise TournamentError("Tournament not found", status_code=404)
    return tournament


def update_tournament(tournament_id: int, organizer_id: int, **fields) -> Tournament:
    tournament = get_tournament_or_404(tournament_id)

    if tournament.organizer_id != organizer_id:
        raise TournamentError("Only the owning organizer can edit this tournament", status_code=403)

    if tournament.status == TournamentStatus.COMPLETED:
        raise TournamentError("Completed tournaments are read-only", status_code=409)

    if tournament.status != TournamentStatus.DRAFT:
        # participant_type / format are locked once registration is open or later
        for locked_field in LOCKED_AFTER_DRAFT:
            if locked_field in fields and fields[locked_field] is not None:
                raise TournamentError(
                    f"'{locked_field}' cannot be changed after tournament leaves DRAFT",
                    status_code=409,
                )

    for key, value in fields.items():
        if value is None:
            continue
        if key == "format":
            value = TournamentFormat(value)
        if key == "participant_type":
            value = ParticipationType(value)
        setattr(tournament, key, value)

    db.session.commit()
    return tournament


def advance_lifecycle(tournament_id: int, target_status: TournamentStatus, organizer_id: int = None) -> Tournament:
    """The single choke point B's services should call/check against.
    Raises InvalidTransitionError on any disallowed transition."""
    tournament = get_tournament_or_404(tournament_id)

    if organizer_id is not None and tournament.organizer_id != organizer_id:
        raise TournamentError("Only the owning organizer can change lifecycle state", status_code=403)

    allowed_next = ALLOWED_TRANSITIONS.get(tournament.status, set())
    if target_status not in allowed_next:
        raise InvalidTransitionError(tournament.status, target_status)

    tournament.status = target_status
    db.session.commit()
    return tournament


def list_tournaments():
    return Tournament.query.order_by(Tournament.created_at.desc())