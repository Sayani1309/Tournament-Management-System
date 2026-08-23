from app.extensions import db
from app.constants.enums import MatchStatus


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    round = db.Column(db.String(50), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=True)
    scheduled_at = db.Column(db.DateTime(timezone=True), nullable=True)
    status = db.Column(
        db.Enum(MatchStatus, name="match_status"),
        nullable=False,
        default=MatchStatus.SCHEDULED,
    )

    tournament = db.relationship("Tournament", foreign_keys=[tournament_id])
    venue = db.relationship("Venue", foreign_keys=[venue_id])

    def __repr__(self):
        return f"<Match id={self.id} tournament_id={self.tournament_id} round={self.round}>"