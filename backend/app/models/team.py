from datetime import datetime, timezone

from app.extensions import db


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Team 1 ── N Player
    players = db.relationship("Player", back_populates="team", foreign_keys="Player.team_id")

    def __repr__(self):
        return f"<Team id={self.id} name={self.name}>"