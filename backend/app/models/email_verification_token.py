import secrets
from datetime import datetime, timezone, timedelta

from app.extensions import db


class EmailVerificationToken(db.Model):
    __tablename__ = "email_verification_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = db.Column(db.String(64), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

    @staticmethod
    def generate(user_id: int, ttl_hours: int = 48) -> "EmailVerificationToken":
        return EmailVerificationToken(
            user_id=user_id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=ttl_hours),
        )

    def is_valid(self) -> bool:
        return datetime.now(timezone.utc) < self.expires_at