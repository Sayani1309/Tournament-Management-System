from app.extensions import db


class MatchScore(db.Model):
    __tablename__ = "match_scores"

    id = db.Column(db.Integer, primary_key=True)
    match_participant_id = db.Column(
        db.Integer, db.ForeignKey("match_participants.id"), unique=True, nullable=False
    )
    score = db.Column(db.Numeric(10, 2), nullable=False)

    match_participant = db.relationship("MatchParticipant", foreign_keys=[match_participant_id])

    def __repr__(self):
        return f"<MatchScore match_participant_id={self.match_participant_id} score={self.score}>"