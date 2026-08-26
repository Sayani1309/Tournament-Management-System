from app.extensions import db
from app.constants.enums import ParticipationType


class Participant(db.Model):
    __tablename__ = "participants"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(ParticipationType, name="participant_entity_type"), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=True, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=True, index=True)

    player = db.relationship("Player", foreign_keys=[player_id])
    team = db.relationship("Team", foreign_keys=[team_id])

    __table_args__ = (
        db.CheckConstraint(
            "(type = 'INDIVIDUAL' AND player_id IS NOT NULL AND team_id IS NULL) OR "
            "(type = 'TEAM' AND team_id IS NOT NULL AND player_id IS NULL)",
            name="ck_participant_exactly_one_of_player_or_team",
        ),
    )

    def __repr__(self):
        return f"<Participant id={self.id} type={self.type.value}>"