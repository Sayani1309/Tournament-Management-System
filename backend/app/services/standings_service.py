from app.extensions import db
from app.models import Standing, MatchScore, MatchParticipant, Match, Player, Team
from app.constants.enums import ResultType
from app.services.tournament_service import get_tournament_or_404


def _get_or_create_standing(tournament_id: int, participant_id: int) -> Standing:
    standing = Standing.query.filter_by(
        tournament_id=tournament_id, participant_id=participant_id
    ).first()
    if standing is None:
        standing = Standing(
            tournament_id=tournament_id,
            participant_id=participant_id,
            played=0, won=0, drawn=0, lost=0, points=0, score_difference=0,
        )
        db.session.add(standing)
        db.session.flush()  # get standing.id without a full commit
    return standing


def update_standings_for_result(match, match_result, scores_by_participant: dict):
    """
    scores_by_participant: {participant_id: score, participant_id: score} — exactly 2 entries.
    Must be called from *inside* submit_result's transaction, before commit, so a
    rollback there also undoes any standings changes made here.
    """
    tournament_id = match.tournament_id
    participant_ids = list(scores_by_participant.keys())
    a_id, b_id = participant_ids[0], participant_ids[1]
    a_score, b_score = scores_by_participant[a_id], scores_by_participant[b_id]

    pairs = [(a_id, a_score, b_score), (b_id, b_score, a_score)]

    for participant_id, own_score, opp_score in pairs:
        standing = _get_or_create_standing(tournament_id, participant_id)

        standing.played += 1
        current_diff = standing.score_difference or 0
        standing.score_difference = current_diff + (float(own_score) - float(opp_score))

        if match_result.result_type == ResultType.DRAW:
            standing.drawn += 1
            standing.points += 1
        elif match_result.winner_participant_id == participant_id:
            standing.won += 1
            standing.points += 3
        else:
            standing.lost += 1


def _participant_total_score(tournament_id: int, participant_id: int) -> float:
    """Sum of this participant's scores across all matches in this tournament —
    used only as the third-level tiebreak, not persisted (Standing has no such
    column in the frozen schema, and doesn't need one for anything but ordering)."""
    total = (
        db.session.query(db.func.coalesce(db.func.sum(MatchScore.score), 0))
        .join(MatchParticipant, MatchScore.match_participant_id == MatchParticipant.id)
        .join(Match, MatchParticipant.match_id == Match.id)
        .filter(Match.tournament_id == tournament_id, MatchParticipant.participant_id == participant_id)
        .scalar()
    )
    return float(total or 0)


def _participant_display_name(participant) -> str:
    if participant.player_id is not None:
        player = db.session.get(Player, participant.player_id)
        return player.name if player else ""
    if participant.team_id is not None:
        team = db.session.get(Team, participant.team_id)
        return team.name if team else ""
    return ""


def list_standings(tournament_id: int):
    """Returns a list of (Standing, total_score, display_name) tuples, sorted per
    SRS §27: points desc, score_difference desc, total score desc, name asc."""
    get_tournament_or_404(tournament_id)
    standings = Standing.query.filter_by(tournament_id=tournament_id).all()

    enriched = []
    for standing in standings:
        total_score = _participant_total_score(tournament_id, standing.participant_id)
        name = _participant_display_name(standing.participant)
        enriched.append((standing, total_score, name))

    enriched.sort(key=lambda row: (
        -row[0].points,
        -(row[0].score_difference or 0),
        -row[1],
        row[2],
    ))
    return enriched