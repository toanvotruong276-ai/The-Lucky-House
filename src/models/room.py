from datetime import datetime
from src.extensions import db


class Room(db.Model):
    """Dai dien cho 1 phong trong tang (moi tang co 2 phong: A va B)."""
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    floor_id = db.Column(db.Integer, db.ForeignKey("floors.id"), nullable=False)
    room_number = db.Column(db.String(20), nullable=False)  # "T-A", "L1-B", "H-A"
    room_label = db.Column(db.String(5), default="A")  # "A" or "B"
    area = db.Column(db.Float, default=0)
    base_price = db.Column(db.Float, nullable=False)
    max_occupants = db.Column(db.Integer, default=2)
    status = db.Column(db.String(20), default="available")
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contracts = db.relationship("Contract", backref="room", lazy="dynamic")
    maintenance_requests = db.relationship("MaintenanceRequest", backref="room", lazy="dynamic")

    @property
    def house(self):
        """Convenience: truy cap nha tu phong."""
        return self.floor.property if self.floor else None

    @property
    def full_name(self):
        """VD: 'Nha 1 > Lau 2 > Phong B'."""
        house = self.house
        house_name = f"Nhà {house.house_number}" if house else "?"
        floor_name = self.floor.floor_name if self.floor else "?"
        return f"{house_name} - {floor_name} - Phòng {self.room_label}"

    @property
    def short_name(self):
        """VD: 'N1-L2B'."""
        house = self.house
        h = house.house_number if house else "?"
        return f"N{h}-{self.room_number}"

    @property
    def active_contract(self):
        return self.contracts.filter_by(status="active").first()

    @property
    def current_tenant(self):
        contract = self.active_contract
        return contract.tenant if contract else None

    @property
    def status_label(self):
        labels = {
            "available": "Trống",
            "occupied": "Đang thuê",
            "maintenance": "Bảo trì",
        }
        return labels.get(self.status, self.status)

    @property
    def status_color(self):
        colors = {
            "available": "success",
            "occupied": "primary",
            "maintenance": "warning",
        }
        return colors.get(self.status, "secondary")

    def __repr__(self):
        return f"<Room {self.room_number}>"
