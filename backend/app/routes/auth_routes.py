from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.extensions import db
from app.schemas.auth_schema import RegisterSchema, LoginSchema, UserSchema
from app.services.auth_service import register_user, login_user, AuthError
from app.models import User


auth_bp = Blueprint("auth", __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()
user_schema = UserSchema()


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    try:
        data = register_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    try:
        user = register_user(**data)
    except AuthError as err:
        return jsonify({"error": err.message}), err.status_code

    return jsonify(user_schema.dump(user)), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    try:
        data = login_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    try:
        token = login_user(**data)
    except AuthError as err:
        return jsonify({"error": err.message}), err.status_code

    return jsonify({"access_token": token}), 200




@auth_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_schema.dump(user)), 200