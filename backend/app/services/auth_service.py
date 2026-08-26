import os

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import User, Player, Team, PasswordResetToken, EmailVerificationToken
from app.constants.enums import UserRole, ParticipationType


class AuthError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_user(name: str, email: str, password: str, role: str,
                   participation_type: str = None, team_option: str = None,
                   team_name: str = None, team_id: int = None):
    """Returns (user, dev_verification_token). dev_verification_token is only
    populated when FLASK_ENV=development, since there's no real email delivery
    configured — see docs/change-log.md for the documented dev-only behavior."""
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
    db.session.flush()  # get user.id without a full commit yet

    verification_token = EmailVerificationToken.generate(user.id)
    db.session.add(verification_token)

    if role_enum == UserRole.PLAYER:
        linked_team_id = None

        if participation_type == ParticipationType.TEAM.value:
            if team_option == "NEW":
                if Team.query.filter_by(name=team_name).first():
                    raise AuthError("A team with this name already exists", status_code=409)
                team = Team(name=team_name)
                db.session.add(team)
                db.session.flush()
                linked_team_id = team.id
            elif team_option == "EXISTING":
                team = db.session.get(Team, team_id)
                if not team:
                    raise AuthError("Selected team does not exist", status_code=404)
                linked_team_id = team.id

        player = Player(name=name, user_id=user.id, team_id=linked_team_id)
        db.session.add(player)

    db.session.commit()

    dev_verification_token = None
    if os.environ.get("FLASK_ENV") == "development":
        dev_verification_token = verification_token.token

    return user, dev_verification_token


def login_user(email: str, password: str) -> str:
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        raise AuthError("Invalid email or password", status_code=401)

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value},
    )
    return access_token


def request_password_reset(email: str):
    """Returns the raw token only in development mode. In production this would
    email the token and return None, never exposing it via the API response."""
    user = User.query.filter_by(email=email).first()
    if not user:
        return None  # deliberately don't reveal whether the email exists

    # Invalidate any previously issued, still-unused reset tokens for this user
    PasswordResetToken.query.filter_by(user_id=user.id, used=False).update({"used": True})

    reset_token = PasswordResetToken.generate(user.id)
    db.session.add(reset_token)
    db.session.commit()

    if os.environ.get("FLASK_ENV") == "development":
        return reset_token.token
    return None


def reset_password(token: str, new_password: str):
    record = PasswordResetToken.query.filter_by(token=token).first()
    if not record or not record.is_valid():
        raise AuthError("Invalid or expired reset token", status_code=400)

    user = db.session.get(User, record.user_id)
    user.password_hash = generate_password_hash(new_password)
    record.used = True
    db.session.commit()


def verify_email(token: str):
    record = EmailVerificationToken.query.filter_by(token=token).first()
    if not record or not record.is_valid():
        raise AuthError("Invalid or expired verification token", status_code=400)

    user = db.session.get(User, record.user_id)
    user.is_verified = True
    db.session.delete(record)
    db.session.commit()