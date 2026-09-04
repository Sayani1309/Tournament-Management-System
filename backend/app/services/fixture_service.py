import math

from app.extensions import db
from app.models import Tournament, TournamentParticipant, Match, MatchParticipant, MatchResult
from app.constants.enums import TournamentFormat, TournamentStatus, MatchStatus, ResultType
from app.services.tournament_service import get_tournament_or_404, TournamentError


class FixtureError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _get_registered_participant_ids(tournament_id: int):
    rows = TournamentParticipant.query.filter_by(tournament_id=tournament_id).order_by(
        TournamentParticipant.registered_at
    ).all()
    return [row.participant_id for row in rows]


def _create_match(tournament_id, round_label, participant_ids, venue_id=None, scheduled_at=None):
    match = Match(
        tournament_id=tournament_id,
        round=round_label,
        venue_id=venue_id,
        scheduled_at=scheduled_at,
        status=MatchStatus.SCHEDULED,
    )
    db.session.add(match)
    db.session.flush()  # get match.id

    for pid in participant_ids:
        db.session.add(MatchParticipant(match_id=match.id, participant_id=pid))

    return match


def _create_bye_match(tournament_id, round_label, participant_id):
    """A bye is represented as a single-participant match that is immediately
    completed with that participant as the winner, so downstream knockout
    progression logic (Phase 6) can treat byes and real wins uniformly —
    both are 'a completed match with a winner' from Round 2's perspective."""
    match = Match(
        tournament_id=tournament_id,
        round=round_label,
        status=MatchStatus.COMPLETED,
    )
    db.session.add(match)
    db.session.flush()

    db.session.add(MatchParticipant(match_id=match.id, participant_id=participant_id))

    db.session.add(MatchResult(
        match_id=match.id,
        winner_participant_id=participant_id,
        result_type=ResultType.WIN,
    ))
    return match


# ---------- Round Robin ----------

def _generate_round_robin_pairs(participant_ids):
    """Standard circle method. Returns a list of rounds, each round a list of
    (a, b) pairs. Odd participant counts get a BYE sentinel (None) rotated in;
    matches against None are skipped, giving each participant exactly one bye
    across the schedule. No self-pairing, no duplicate pairing."""
    ids = list(participant_ids)
    if len(ids) % 2 == 1:
        ids.append(None)  # BYE sentinel

    n = len(ids)
    rounds = []
    fixed = ids[0]
    rotating = ids[1:]

    for _ in range(n - 1):
        round_pairs = []
        current = [fixed] + rotating
        for i in range(n // 2):
            a, b = current[i], current[n - 1 - i]
            if a is not None and b is not None:
                round_pairs.append((a, b))
        rounds.append(round_pairs)
        rotating = [rotating[-1]] + rotating[:-1]  # rotate

    return rounds


def generate_round_robin_fixtures(tournament_id: int):
    participant_ids = _get_registered_participant_ids(tournament_id)
    if len(participant_ids) < 2:
        raise FixtureError("At least 2 participants are required to generate fixtures")

    rounds = _generate_round_robin_pairs(participant_ids)
    matches = []
    for round_index, pairs in enumerate(rounds, start=1):
        round_label = f"Round {round_index}"
        for a, b in pairs:
            matches.append(_create_match(tournament_id, round_label, [a, b]))

    db.session.commit()
    return matches


# ---------- Knockout ----------

def _next_power_of_two(n: int) -> int:
    if n <= 1:
        return 1
    return 2 ** math.ceil(math.log2(n))


def generate_knockout_fixtures(tournament_id: int):
    participant_ids = _get_registered_participant_ids(tournament_id)
    if len(participant_ids) < 2:
        raise FixtureError("At least 2 participants are required to generate fixtures")

    bracket_size = _next_power_of_two(len(participant_ids))
    bye_count = bracket_size - len(participant_ids)

    ids = list(participant_ids)
    matches = []
    slot_index = 0
    idx = 0

    bye_matches = []  # (match, winner_participant_id) — advanced only after the full round exists

    for _ in range(bye_count):
        pid = ids[idx]
        idx += 1
        label = f"Round 1-Match {slot_index}"
        bye_match = _create_bye_match(tournament_id, label, pid)
        matches.append(bye_match)
        bye_matches.append((bye_match, pid))
        slot_index += 1

    while idx < len(ids):
        a = ids[idx]
        b = ids[idx + 1]
        idx += 2
        label = f"Round 1-Match {slot_index}"
        matches.append(_create_match(tournament_id, label, [a, b]))
        slot_index += 1

    db.session.flush()  # ensure every Round 1 match exists before advancing any bye winner

    from app.services.knockout_service import advance_winner
    for bye_match, pid in bye_matches:
        advance_winner(bye_match, pid)

    db.session.commit()
    return matches

# ---------- Entry point ----------

def generate_fixtures(tournament_id: int, organizer_id: int):
    tournament = get_tournament_or_404(tournament_id)
    
    if tournament.organizer_id != organizer_id:
        raise FixtureError(
            "Only the owning organizer can generate fixtures for this tournament",
            status_code=403,
        )
    
    if tournament.status != TournamentStatus.ONGOING:
        raise FixtureError(
            "Fixtures can only be generated once the tournament is ONGOING", status_code=409
        )

    existing = Match.query.filter_by(tournament_id=tournament_id).first()
    if existing:
        raise FixtureError("Fixtures have already been generated for this tournament", status_code=409)

    if tournament.format == TournamentFormat.ROUND_ROBIN:
        return generate_round_robin_fixtures(tournament_id)
    elif tournament.format == TournamentFormat.KNOCKOUT:
        return generate_knockout_fixtures(tournament_id)
    else:
        raise FixtureError(f"Unsupported format: {tournament.format}")


def list_matches(tournament_id: int):
    get_tournament_or_404(tournament_id)
    return Match.query.filter_by(tournament_id=tournament_id).order_by(Match.id).all()

def get_match_or_404(match_id: int) -> Match:
    match = db.session.get(Match, match_id)
    if not match:
        raise FixtureError("Match not found", status_code=404)
    return match