from datetime import datetime
from src.extensions import db


class Tenant(db.Model):
    __tablename__ = "tenants"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    id_card = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    hometown = db.Column(db.String(200))
    occupation = db.Column(db.String(100))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contracts = db.relationship("Contract", backref="tenant", lazy="dynamic")
    maintenance_requests = db.relationship("MaintenanceRequest", backref="tenant", lazy="dynamic")

    @property
    def active_contract(self):
        return self.contracts.filter_by(status="active").first()

    @property
    def current_room(self):
        contract = self.active_contract
        return contract.room if contract else None

    def __repr__(self):
        return f"<Tenant {self.full_name}>"
