"""Model Property - đại diện 1 căn nhà tại KDC CITY LAND PARK HILL."""
from datetime import datetime
from src.extensions import db


class Property(db.Model):
    """Đại diện cho 1 căn nhà tách lẻ trong KDC CITY LAND PARK HILL."""

    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)  # "Nhà số 1"
    house_number = db.Column(db.String(20), nullable=False, unique=True)
    address = db.Column(db.String(300), default="KDC CITY LAND PARK HILL")
    has_basement = db.Column(db.Boolean, default=False)
    num_floors = db.Column(db.Integer, default=3)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    floors = db.relationship(
        "Floor", backref="property", lazy="dynamic",
        cascade="all, delete-orphan", order_by="Floor.floor_order",
    )

    # --- Computed properties ---

    def _count_rooms(self, status=None):
        """Helper: đếm phòng theo trạng thái."""
        from src.models.room import Room
        from src.models.floor import Floor
        q = Room.query.join(Floor).filter(Floor.property_id == self.id)
        if status:
            q = q.filter(Room.status == status)
        return q.count()

    @property
    def total_rooms(self):
        return self._count_rooms()

    @property
    def available_rooms(self):
        return self._count_rooms("available")

    @property
    def occupied_rooms(self):
        return self._count_rooms("occupied")

    @property
    def display_name(self):
        return f"Nhà {self.house_number}"

    def __repr__(self):
        return f"<Property {self.name}>"
