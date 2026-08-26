from app.extensions import db


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=True, index=True
    )
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=True, index=True)

    user = db.relationship("User", back_populates="player", foreign_keys=[user_id])
    team = db.relationship("Team", back_populates="players", foreign_keys=[team_id])

    def __repr__(self):
        return f"<Player id={self.id} name={self.name} team_id={self.team_id}>"