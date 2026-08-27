from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.extensions import db, limiter
from app.schemas.auth_schema import (
    RegisterSchema, LoginSchema, UserSchema, ForgotPasswordSchema, ResetPasswordSchema,
)
from app.services.auth_service import (
    register_user, login_user, request_password_reset, reset_password, verify_email, AuthError,
)
from app.models import User, TokenBlocklist
from app.services.participant_service import list_my_tournaments

from app.schemas.tournament_schema import TournamentSchema
auth_bp = Blueprint("auth", __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()
user_schema = UserSchema()
forgot_password_schema = ForgotPasswordSchema()
reset_password_schema = ResetPasswordSchema()
tournament_list_schema = TournamentSchema(many=True)

@auth_bp.route("/auth/register", methods=["POST"])
@limiter.limit("20 per minute")
def register():
    try:
        data = register_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    try:
        user, dev_verification_token = register_user(**data)
    except AuthError as err:
        return jsonify({"error": err.message}), err.status_code

    payload = user_schema.dump(user)
    if dev_verification_token:
        payload["dev_verification_token"] = dev_verification_token
    return jsonify(payload), 201


@auth_bp.route("/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
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


@auth_bp.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    jwt_data = get_jwt()
    db.session.add(TokenBlocklist(
        jti=jwt_data["jti"],
        expires_at=datetime.fromtimestamp(jwt_data["exp"], tz=timezone.utc),
    ))
    db.session.commit()
    return jsonify({"message": "Successfully logged out"}), 200


@auth_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_schema.dump(user)), 200


@auth_bp.route("/auth/forgot-password", methods=["POST"])
def forgot_password():
    try:
        data = forgot_password_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    dev_token = request_password_reset(data["email"])
    response = {"message": "If that email exists, a reset link has been sent."}
    if dev_token:
        response["dev_token"] = dev_token
    return jsonify(response), 200


@auth_bp.route("/auth/reset-password", methods=["POST"])
def reset_password_route():
    try:
        data = reset_password_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    try:
        reset_password(data["token"], data["new_password"])
    except AuthError as err:
        return jsonify({"error": err.message}), err.status_code

    return jsonify({"message": "Password reset successfully"}), 200


@auth_bp.route("/auth/verify-email", methods=["GET"])
def verify_email_route():
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "token query parameter is required"}), 400

    try:
        verify_email(token)
    except AuthError as err:
        return jsonify({"error": err.message}), err.status_code

    return jsonify({"message": "Email verified successfully"}), 200

@auth_bp.route("/auth/me/tournaments", methods=["GET"])
@jwt_required()
def my_tournaments():
    user_id = int(get_jwt_identity())
    result = list_my_tournaments(user_id)
    return jsonify({
        "upcoming": tournament_list_schema.dump(result["upcoming"]),
        "past": tournament_list_schema.dump(result["past"]),
    }), 200