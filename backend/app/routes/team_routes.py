from flask import Blueprint, jsonify

from app.models import Team

team_bp = Blueprint("team", __name__)


@team_bp.route("/teams", methods=["GET"])
def get_teams():
    teams = Team.query.order_by(Team.name).all()
    return jsonify([{"id": t.id, "name": t.name} for t in teams]), 200