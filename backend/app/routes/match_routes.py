from flask_jwt_extended import get_jwt_identity

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.extensions import require_role
from app.schemas.match_schema import MatchSchema
from app.schemas.match_result_schema import MatchResultSubmitSchema, MatchResultSchema
from app.services.fixture_service import generate_fixtures, list_matches, FixtureError
from app.services.result_service import submit_result, get_match_result, ResultError
from app.services.tournament_service import TournamentError

match_bp = Blueprint("match", __name__)

match_schema = MatchSchema()
matches_schema = MatchSchema(many=True)
result_submit_schema = MatchResultSubmitSchema()
result_schema = MatchResultSchema()


# ---------- Fixtures ----------

@match_bp.route("/tournaments/<int:tournament_id>/fixtures", methods=["POST"])
@require_role("ORGANIZER")
def post_fixtures(tournament_id):
    organizer_id = int(get_jwt_identity())
    try:
        matches = generate_fixtures(tournament_id, organizer_id)
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


# ---------- Results ----------

@match_bp.route("/matches/<int:match_id>/result", methods=["POST"])
@require_role("ORGANIZER")
def post_result(match_id):
    try:
        data = result_submit_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    organizer_id = int(get_jwt_identity())

    try:
        result = submit_result(
            match_id=match_id,
            organizer_id=organizer_id,
            scores=data["scores"],
            result_type=data["result_type"],
            winner_participant_id=data.get("winner_participant_id"),
        )
    except ResultError as err:
        return jsonify({"error": err.message}), err.status_code

    return jsonify(result_schema.dump(result)), 201


@match_bp.route("/matches/<int:match_id>/result", methods=["GET"])
def get_result(match_id):
    try:
        result = get_match_result(match_id)
    except ResultError as err:
        return jsonify({"error": err.message}), err.status_code

    return jsonify(result_schema.dump(result)), 200