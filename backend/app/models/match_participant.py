from app.extensions import db


class MatchParticipant(db.Model):
    __tablename__ = "match_participants"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=False, index=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=False, index=True)

    match = db.relationship("Match", foreign_keys=[match_id])
    participant = db.relationship("Participant", foreign_keys=[participant_id])

    __table_args__ = (
        db.UniqueConstraint("match_id", "participant_id", name="uq_match_participant"),
    )

    def __repr__(self):
        return f"<MatchParticipant match_id={self.match_id} participant_id={self.participant_id}>"