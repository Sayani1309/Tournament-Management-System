from datetime import datetime, timezone

from app.extensions import db


class TournamentParticipant(db.Model):
    __tablename__ = "tournament_participants"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False, index=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=False, index=True)
    registered_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    tournament = db.relationship("Tournament", foreign_keys=[tournament_id])
    participant = db.relationship("Participant", foreign_keys=[participant_id])

    __table_args__ = (
        db.UniqueConstraint("tournament_id", "participant_id", name="uq_tournament_participant"),
    )

    def __repr__(self):
        return f"<TournamentParticipant tournament_id={self.tournament_id} participant_id={self.participant_id}>"