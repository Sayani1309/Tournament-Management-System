from flask import Blueprint, jsonify

from app.models import Team

team_bp = Blueprint("team", __name__)


@team_bp.route("/teams", methods=["GET"])
def get_teams():
    teams = Team.query.order_by(Team.name).all()
    return jsonify([{"id": t.id, "name": t.name} for t in teams]), 200


@team_bp.route("/teams/<int:team_id>", methods=["GET"])
def get_team(team_id):
    team = Team.query.get(team_id)
    if not team:
        return jsonify({"error": "Team not found"}), 404
    return jsonify({"id": team.id, "name": team.name}), 200