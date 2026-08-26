from app.extensions import db
from app.models import Standing, MatchScore, MatchParticipant, Match, TournamentParticipant
from app.constants.enums import ResultType
from app.services.tournament_service import get_tournament_or_404
from app.services.participant_service import get_participant_display


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
        db.session.flush()
    return standing


def update_standings_for_result(match, match_result, scores_by_participant: dict):
    tournament_id = match.tournament_id
    participant_ids = list(scores_by_participant.keys())
    a_id, b_id = participant_ids[0], participant_ids[1]
    a_score, b_score = scores_by_participant[a_id], scores_by_participant[b_id]

    pairs = [(a_id, a_score, b_score), (b_id, b_score, a_score)]

    for participant_id, own_score, opp_score in pairs:
        standing = _get_or_create_standing(tournament_id, participant_id)

        standing.played += 1
        current_diff = float(standing.score_difference or 0)
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
    total = (
        db.session.query(db.func.coalesce(db.func.sum(MatchScore.score), 0))
        .join(MatchParticipant, MatchScore.match_participant_id == MatchParticipant.id)
        .join(Match, MatchParticipant.match_id == Match.id)
        .filter(Match.tournament_id == tournament_id, MatchParticipant.participant_id == participant_id)
        .scalar()
    )
    return float(total or 0)


def list_standings(tournament_id: int):
    """Returns a list of (Standing, total_score, display_name) tuples, sorted per
    SRS §27. Ensures every registered participant has a Standing row, even if they
    haven't played yet — a fresh registration shows up at 0 points, not missing
    entirely."""
    get_tournament_or_404(tournament_id)

    registered_participant_ids = [
        tp.participant_id
        for tp in TournamentParticipant.query.filter_by(tournament_id=tournament_id).all()
    ]
    for participant_id in registered_participant_ids:
        _get_or_create_standing(tournament_id, participant_id)
    db.session.commit()

    standings = Standing.query.filter_by(tournament_id=tournament_id).all()

    enriched = []
    for standing in standings:
        total_score = _participant_total_score(tournament_id, standing.participant_id)
        name = get_participant_display(standing.participant)["name"]
        enriched.append((standing, total_score, name))

    enriched.sort(key=lambda row: (
        -row[0].points,
        -(row[0].score_difference or 0),
        -row[1],
        row[2] or "",
    ))
    return enriched