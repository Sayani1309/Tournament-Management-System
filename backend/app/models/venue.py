from app.extensions import db


class Venue(db.Model):
    __tablename__ = "venues"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.Integer, nullable=True)

    __table_args__ = (
        db.CheckConstraint("capacity IS NULL OR capacity >= 0", name="ck_venue_capacity_nonneg"),
    )

    def __repr__(self):
        return f"<Venue id={self.id} name={self.name}>"