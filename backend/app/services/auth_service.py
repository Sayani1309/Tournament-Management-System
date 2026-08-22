from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import User
from app.constants.enums import UserRole


class AuthError(Exception):
    """Raised for auth failures the route layer should turn into 4xx responses."""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_user(name: str, email: str, password: str, role: str) -> User:
    existing = User.query.filter_by(email=email).first()
    if existing:
        raise AuthError("A user with this email already exists", status_code=409)

    try:
        role_enum = UserRole(role)
    except ValueError:
        raise AuthError(f"Invalid role: {role}", status_code=400)

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role_enum,
    )
    db.session.add(user)
    db.session.commit()
    return user


def login_user(email: str, password: str) -> str:
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        raise AuthError("Invalid email or password", status_code=401)

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value},
    )
    return access_token