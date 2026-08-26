from datetime import datetime, timezone

from app.extensions import db
from app.constants.enums import UserRole


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole, name="user_role"), nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    player = db.relationship(
        "Player", back_populates="user", uselist=False, foreign_keys="Player.user_id"
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role.value}>"