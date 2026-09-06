from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from flask_jwt_extended import get_jwt_identity, get_jwt

from app.extensions import db, require_role
from app.utils.pagination import paginate_query
from app.models import Player, Team
from app.services.participant_service import get_player_achievements

player_bp = Blueprint("player", __name__)


class PlayerTeamUpdateSchema(Schema):
    team_id = fields.Int(required=False, allow_none=True)


player_team_update_schema = PlayerTeamUpdateSchema()


@player_bp.route("/players", methods=["GET"])
def get_players():
    result = paginate_query(Player.query.order_by(Player.name))
    result["items"] = [{"id": p.id, "name": p.name, "team_id": p.team_id} for p in result["items"]]
    return jsonify(result), 200


@player_bp.route("/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    player = db.session.get(Player, player_id)
    if not player:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({"id": player.id, "name": player.name, "team_id": player.team_id}), 200


@player_bp.route("/players/<int:player_id>/team", methods=["PUT"])
@require_role("ORGANIZER", "PLAYER")
def update_player_team(player_id):
    player = db.session.get(Player, player_id)
    if not player:
        return jsonify({"error": "Player not found"}), 404

    claims = get_jwt()
    if claims.get("role") == "PLAYER":
        user_id = int(get_jwt_identity())
        if player.user_id != user_id:
            return jsonify({"error": "You can only update your own player profile"}), 403

    try:
        data = player_team_update_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    team_id = data.get("team_id")
    if team_id is not None:
        team = db.session.get(Team, team_id)
        if not team:
            return jsonify({"error": "Team not found"}), 404

    player.team_id = team_id
    db.session.commit()
    return jsonify({"id": player.id, "name": player.name, "team_id": player.team_id}), 200

@player_bp.route("/players/<int:player_id>/profile", methods=["GET"])
def get_player_profile(player_id):
    player = db.session.get(Player, player_id)
    if not player:
        return jsonify({"error": "Player not found"}), 404

    achievements = get_player_achievements(player_id)
    team_name = None
    if player.team_id:
        from app.models import Team
        team = db.session.get(Team, player.team_id)
        team_name = team.name if team else None

    return jsonify({
        "id": player.id,
        "name": player.name,
        "team_id": player.team_id,
        "team_name": team_name,
        "achievements": achievements,
    }), 200