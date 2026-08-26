import secrets
from datetime import datetime, timezone, timedelta

from app.extensions import db


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.String(64), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used = db.Column(db.Boolean, nullable=False, default=False)

    @staticmethod
    def generate(user_id: int, ttl_minutes: int = 30) -> "PasswordResetToken":
        return PasswordResetToken(
            user_id=user_id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes),
            used=False,
        )

    def is_valid(self) -> bool:
        return not self.used and datetime.now(timezone.utc) < self.expires_at