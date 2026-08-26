from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity

from app.extensions import require_role
from app.utils.pagination import paginate_query
from app.schemas.tournament_schema import (
    TournamentCreateSchema, TournamentUpdateSchema, TournamentSchema,
)
from app.services.tournament_service import (
    create_tournament, update_tournament, advance_lifecycle,
    list_tournaments, get_tournament_or_404, TournamentError,
)
from app.constants.enums import TournamentStatus

tournament_bp = Blueprint("tournament", __name__)

create_schema = TournamentCreateSchema()
update_schema = TournamentUpdateSchema()
tournament_schema = TournamentSchema()
tournaments_schema = TournamentSchema(many=True)


@tournament_bp.route("/tournaments", methods=["GET"])
def get_tournaments():
    query = list_tournaments()
    result = paginate_query(query)
    result["items"] = tournaments_schema.dump(result["items"])
    return jsonify(result), 200


@tournament_bp.route("/tournaments/<int:tournament_id>", methods=["GET"])
def get_tournament(tournament_id):
    try:
        tournament = get_tournament_or_404(tournament_id)
    except TournamentError as err:
        return jsonify({"error": err.message}), err.status_code
    return jsonify(tournament_schema.dump(tournament)), 200


@tournament_bp.route("/tournaments", methods=["POST"])
@require_role("ORGANIZER")
def post_tournament():
    try:
        data = create_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    organizer_id = int(get_jwt_identity())
    try:
        tournament = create_tournament(organizer_id=organizer_id, **data)
    except TournamentError as err:
        return jsonify({"error": err.message}), err.status_code

    return jsonify(tournament_schema.dump(tournament)), 201


@tournament_bp.route("/tournaments/<int:tournament_id>", methods=["PUT"])
@require_role("ORGANIZER")
def put_tournament(tournament_id):
    try:
        data = update_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    organizer_id = int(get_jwt_identity())
    try:
        tournament = update_tournament(tournament_id, organizer_id, **data)
    except TournamentError as err:
        return jsonify({"error": err.message}), err.status_code

    return jsonify(tournament_schema.dump(tournament)), 200


@tournament_bp.route("/tournaments/<int:tournament_id>/open-registration", methods=["POST"])
@require_role("ORGANIZER")
def open_registration(tournament_id):
    organizer_id = int(get_jwt_identity())
    try:
        tournament = advance_lifecycle(
            tournament_id, TournamentStatus.REGISTRATION_OPEN, organizer_id
        )
    except TournamentError as err:
        return jsonify({"error": err.message}), err.status_code
    return jsonify(tournament_schema.dump(tournament)), 200


@tournament_bp.route("/tournaments/<int:tournament_id>/start", methods=["POST"])
@require_role("ORGANIZER")
def start_tournament(tournament_id):
    organizer_id = int(get_jwt_identity())
    try:
        tournament = advance_lifecycle(
            tournament_id, TournamentStatus.ONGOING, organizer_id
        )
    except TournamentError as err:
        return jsonify({"error": err.message}), err.status_code
    return jsonify(tournament_schema.dump(tournament)), 200