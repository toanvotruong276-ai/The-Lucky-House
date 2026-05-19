from src.extensions import db


class Floor(db.Model):
    """Dai dien cho 1 tang trong nha (Ham, Tret, Lau 1, Lau 2...)."""
    __tablename__ = "floors"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)
    floor_name = db.Column(db.String(50), nullable=False)  # "Ham", "Tret", "Lau 1"
    floor_order = db.Column(db.Integer, default=0)  # -1=Ham, 0=Tret, 1+=Lau
    description = db.Column(db.Text)

    rooms = db.relationship("Room", backref="floor", lazy="dynamic",
                            cascade="all, delete-orphan", order_by="Room.room_label")

    @property
    def floor_type(self):
        if self.floor_order < 0:
            return "basement"
        elif self.floor_order == 0:
            return "ground"
        return "upper"

    @property
    def floor_type_label(self):
        labels = {"basement": "Hầm xe", "ground": "Trệt", "upper": "Lầu"}
        return labels.get(self.floor_type, "")

    @property
    def available_rooms(self):
        return self.rooms.filter_by(status="available").count()

    def __repr__(self):
        return f"<Floor {self.floor_name} @ Property {self.property_id}>"
