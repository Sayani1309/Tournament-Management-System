from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import User, Player, Team
from app.constants.enums import UserRole, ParticipationType


class AuthError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_user(name: str, email: str, password: str, role: str,
                   participation_type: str = None, team_option: str = None,
                   team_name: str = None, team_id: int = None) -> User:
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