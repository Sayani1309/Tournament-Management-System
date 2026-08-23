from flask import Blueprint, jsonify

from app.extensions import require_role
from app.schemas.match_schema import MatchSchema
from app.services.fixture_service import generate_fixtures, list_matches, FixtureError
from app.services.tournament_service import TournamentError

match_bp = Blueprint("match", __name__)

match_schema = MatchSchema()
matches_schema = MatchSchema(many=True)


@match_bp.route("/tournaments/<int:tournament_id>/fixtures", methods=["POST"])
@require_role("ORGANIZER")
def post_fixtures(tournament_id):
    try:
        matches = generate_fixtures(tournament_id)
    except (FixtureError, TournamentError) as err:
        return jsonify({"error": err.message}), err.status_code
    return jsonify(matches_schema.dump(matches)), 201


@match_bp.route("/tournaments/<int:tournament_id>/matches", methods=["GET"])
def get_matches(tournament_id):
    try:
        matches = list_matches(tournament_id)
    except TournamentError as err:
        return jsonify({"error": err.message}), err.status_code
    return jsonify(matches_schema.dump(matches)), 200