from datetime import datetime, timezone

from app.extensions import db
from app.constants.enums import ResultType


class MatchResult(db.Model):
    __tablename__ = "match_results"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), unique=True, nullable=False)
    winner_participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=True)
    result_type = db.Column(db.Enum(ResultType, name="result_type"), nullable=False)
    submitted_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    match = db.relationship("Match", foreign_keys=[match_id])
    winner = db.relationship("Participant", foreign_keys=[winner_participant_id])

    __table_args__ = (
        db.CheckConstraint(
            "(result_type = 'WIN' AND winner_participant_id IS NOT NULL) OR "
            "(result_type = 'DRAW' AND winner_participant_id IS NULL)",
            name="ck_match_result_winner_consistency",
        ),
    )

    def __repr__(self):
        return f"<MatchResult match_id={self.match_id} result_type={self.result_type.value}>"