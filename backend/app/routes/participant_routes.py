from flask_jwt_extended import get_jwt_identity
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.extensions import require_role
from app.schemas.participant_schema import ParticipantRegisterSchema, TournamentParticipantSchema
from app.services.participant_service import register_participant, list_participants, ParticipantError
from app.services.tournament_service import TournamentError

participant_bp = Blueprint("participant", __name__)

register_schema = ParticipantRegisterSchema()
tp_schema = TournamentParticipantSchema()
tps_schema = TournamentParticipantSchema(many=True)


@participant_bp.route("/tournaments/<int:tournament_id>/participants", methods=["GET"])
def get_participants(tournament_id):
    try:
        registrations = list_participants(tournament_id)
    except TournamentError as err:
        return jsonify({"error": err.message}), err.status_code
    return jsonify(tps_schema.dump(registrations)), 200


@participant_bp.route("/tournaments/<int:tournament_id>/participants", methods=["POST"])
@require_role("ORGANIZER")
def post_participant(tournament_id):
    try:
        data = register_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    
    organizer_id = int(get_jwt_identity())

    try:
        registration = register_participant(tournament_id=tournament_id,organizer_id=organizer_id, **data)
    except (ParticipantError, TournamentError) as err:
        return jsonify({"error": err.message}), err.status_code

    return jsonify(tp_schema.dump(registration)), 201