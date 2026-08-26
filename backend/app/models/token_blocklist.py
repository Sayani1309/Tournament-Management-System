from datetime import datetime, timezone

from app.extensions import db


class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    @staticmethod
    def purge_expired():
        """Delete blocklist entries whose original token has already naturally
        expired — safe to call periodically, since an expired token can't be
        used regardless of blocklist status. Not wired to a scheduler in this
        project; call manually or from a future maintenance script."""
        TokenBlocklist.query.filter(
            TokenBlocklist.expires_at < datetime.now(timezone.utc)
        ).delete()
        db.session.commit()