# backend/app/extensions.py
from functools import wraps

from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from flask_cors import CORS
from marshmallow import Schema  # noqa: F401  (just confirming import works)
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema  # noqa: F401

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

def require_role(*allowed_roles):
    """Usage: @require_role("ORGANIZER")  or  @require_role("ORGANIZER", "PLAYER")"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role not in allowed_roles:
                return jsonify({"error": "Forbidden: insufficient role"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator