import re

from app.extensions import db
from app.models import Match, MatchParticipant
from app.constants.enums import MatchStatus, TournamentStatus
from app.services.tournament_service import advance_lifecycle

_ROUND_SLOT_RE = re.compile(r"^Round (\d+)-Match (\d+)$")


def _parse_round_slot(round_label: str):
    m = _ROUND_SLOT_RE.match(round_label)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def _round_match_count(tournament_id: int, round_num: int) -> int:
    prefix = f"Round {round_num}-Match "
    return Match.query.filter(
        Match.tournament_id == tournament_id,
        Match.round.like(f"{prefix}%"),
    ).count()


def _get_or_create_next_match(tournament_id: int, next_round_num: int, next_slot_index: int) -> Match:
    label = f"Round {next_round_num}-Match {next_slot_index}"
    match = Match.query.filter_by(tournament_id=tournament_id, round=label).first()
    if match is None:
        match = Match(tournament_id=tournament_id, round=label, status=MatchStatus.SCHEDULED)
        db.session.add(match)
        db.session.flush()
    return match


def advance_winner(match: Match, winner_participant_id: int):
    """Called (inside the same transaction as result submission, or right after
    bye creation) whenever a KNOCKOUT match produces a winner. Slots the winner
    into the next round's match, creating it if needed. If this match's round
    only had one match total, this was the final — the tournament transitions
    to COMPLETED instead of advancing anyone further."""
    parsed = _parse_round_slot(match.round)
    if parsed is None:
        return  # not a knockout-style round label (e.g. round-robin) — nothing to do

    round_num, slot_index = parsed

    if _round_match_count(match.tournament_id, round_num) == 1:
        advance_lifecycle(match.tournament_id, TournamentStatus.COMPLETED)
        return

    next_round_num = round_num + 1
    next_slot_index = slot_index // 2
    next_match = _get_or_create_next_match(match.tournament_id, next_round_num, next_slot_index)

    already_present = MatchParticipant.query.filter_by(
        match_id=next_match.id, participant_id=winner_participant_id
    ).first()
    if not already_present:
        db.session.add(MatchParticipant(match_id=next_match.id, participant_id=winner_participant_id))