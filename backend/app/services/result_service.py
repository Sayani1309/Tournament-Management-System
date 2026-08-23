from app.extensions import db
from app.models import Match, MatchParticipant, MatchResult, MatchScore, Tournament
from app.constants.enums import MatchStatus, ResultType, TournamentFormat, TournamentStatus


class ResultError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def get_match_or_404(match_id: int) -> Match:
    match = db.session.get(Match, match_id)
    if not match:
        raise ResultError("Match not found", status_code=404)
    return match


def submit_result(match_id: int, scores: list, result_type: str, winner_participant_id: int = None) -> MatchResult:
    match = get_match_or_404(match_id)

    if match.status == MatchStatus.COMPLETED:
        raise ResultError("This match already has a submitted result", status_code=409)

    if MatchResult.query.filter_by(match_id=match_id).first():
        raise ResultError("This match already has a submitted result", status_code=409)

    match_participants = MatchParticipant.query.filter_by(match_id=match_id).all()
    if len(match_participants) != 2:
        raise ResultError("Match does not have exactly two participants", status_code=500)

    valid_participant_ids = {mp.participant_id for mp in match_participants}
    submitted_ids = {entry["participant_id"] for entry in scores}

    if submitted_ids != valid_participant_ids:
        raise ResultError(
            "Scores must be provided for exactly the two participants in this match",
            status_code=400,
        )

    try:
        result_type_enum = ResultType(result_type)
    except ValueError:
        raise ResultError(f"Invalid result_type: {result_type}", status_code=400)

    if result_type_enum == ResultType.WIN:
        if winner_participant_id is None or winner_participant_id not in valid_participant_ids:
            raise ResultError(
                "WIN requires winner_participant_id to be one of the match's participants",
                status_code=400,
            )
    else:  # DRAW
        if winner_participant_id is not None:
            raise ResultError("DRAW must not include a winner_participant_id", status_code=400)

    try:
        match_result = MatchResult(
            match_id=match_id,
            winner_participant_id=winner_participant_id,
            result_type=result_type_enum,
        )
        db.session.add(match_result)

        mp_by_participant = {mp.participant_id: mp for mp in match_participants}
        for entry in scores:
            mp = mp_by_participant[entry["participant_id"]]
            db.session.add(MatchScore(match_participant_id=mp.id, score=entry["score"]))

        match.status = MatchStatus.COMPLETED
        db.session.flush()

        from app.services.standings_service import update_standings_for_result
        scores_by_participant = {entry["participant_id"]: entry["score"] for entry in scores}
        update_standings_for_result(match, match_result, scores_by_participant)

        tournament = db.session.get(Tournament, match.tournament_id)

        if tournament.format == TournamentFormat.KNOCKOUT:
            if match_result.winner_participant_id is not None:
                from app.services.knockout_service import advance_winner
                advance_winner(match, match_result.winner_participant_id)
        elif tournament.format == TournamentFormat.ROUND_ROBIN:
            db.session.flush()
            remaining = Match.query.filter_by(
                tournament_id=match.tournament_id, status=MatchStatus.SCHEDULED
            ).count()
            if remaining == 0:
                from app.services.tournament_service import advance_lifecycle
                advance_lifecycle(match.tournament_id, TournamentStatus.COMPLETED)

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return match_result


def get_match_result(match_id: int) -> MatchResult:
    get_match_or_404(match_id)
    result = MatchResult.query.filter_by(match_id=match_id).first()
    if not result:
        raise ResultError("No result has been submitted for this match yet", status_code=404)
    return result