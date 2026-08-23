from datetime import datetime, timezone

from app.extensions import db
from app.constants.enums import ParticipationType, TournamentFormat, TournamentStatus


class Tournament(db.Model):
    __tablename__ = "tournaments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    sport = db.Column(db.String(100), nullable=False)
    format = db.Column(db.Enum(TournamentFormat, name="tournament_format"), nullable=False)
    participant_type = db.Column(
        db.Enum(ParticipationType, name="participation_type"), nullable=False
    )
    status = db.Column(
        db.Enum(TournamentStatus, name="tournament_status"),
        nullable=False,
        default=TournamentStatus.DRAFT,
    )
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    organizer = db.relationship("User", foreign_keys=[organizer_id])

    def __repr__(self):
        return f"<Tournament id={self.id} name={self.name} status={self.status.value}>"