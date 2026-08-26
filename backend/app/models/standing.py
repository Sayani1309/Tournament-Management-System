from app.extensions import db


class Standing(db.Model):
    __tablename__ = "standings"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False, index=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=False, index=True)
    played = db.Column(db.Integer, nullable=False, default=0)
    won = db.Column(db.Integer, nullable=False, default=0)
    drawn = db.Column(db.Integer, nullable=False, default=0)
    lost = db.Column(db.Integer, nullable=False, default=0)
    points = db.Column(db.Integer, nullable=False, default=0)
    score_difference = db.Column(db.Numeric(10, 2), nullable=True, default=0)

    tournament = db.relationship("Tournament", foreign_keys=[tournament_id])
    participant = db.relationship("Participant", foreign_keys=[participant_id])

    __table_args__ = (
        db.UniqueConstraint("tournament_id", "participant_id", name="uq_tournament_standing"),
        db.CheckConstraint("played >= 0", name="ck_standing_played_nonneg"),
        db.CheckConstraint("won >= 0", name="ck_standing_won_nonneg"),
        db.CheckConstraint("drawn >= 0", name="ck_standing_drawn_nonneg"),
        db.CheckConstraint("lost >= 0", name="ck_standing_lost_nonneg"),
        db.CheckConstraint("points >= 0", name="ck_standing_points_nonneg"),
    )

    def __repr__(self):
        return f"<Standing tournament_id={self.tournament_id} participant_id={self.participant_id}>"