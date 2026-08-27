from flask_jwt_extended import get_jwt_identity, get_jwt
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.extensions import require_role
from app.schemas.participant_schema import ParticipantRegisterSchema, TournamentParticipantSchema
from app.services.participant_service import register_participant, list_participants, ParticipantError
from app.services.tournament_service import TournamentError
from app.services.participant_service import remove_participant

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
@require_role("ORGANIZER","PLAYER")
def post_participant(tournament_id):
    try:
        data = register_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    requester_user_id = int(get_jwt_identity())
    requester_role = get_jwt().get("role")

    try:
        registration = register_participant(
            tournament_id=tournament_id,
            requester_user_id=requester_user_id,
            requester_role=requester_role,
            **data,
        )
    except (ParticipantError, TournamentError) as err:
        return jsonify({"error": err.message}), err.status_code

    return jsonify(tp_schema.dump(registration)), 201

@participant_bp.route("/tournaments/<int:tournament_id>/participants/<int:participant_id>", methods=["DELETE"])
@require_role("ORGANIZER")
def delete_participant(tournament_id, participant_id):
    organizer_id = int(get_jwt_identity())
    try:
        remove_participant(tournament_id, participant_id, organizer_id)
    except ParticipantError as err:
        return jsonify({"error": err.message}), err.status_code
    return "", 204