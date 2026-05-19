from datetime import datetime, date
from src.extensions import db


class Contract(db.Model):
    __tablename__ = "contracts"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    monthly_rent = db.Column(db.Float, nullable=False)
    deposit = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default="active")  # active, expired, terminated
    terms = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    invoices = db.relationship("Invoice", backref="contract", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def is_expiring_soon(self):
        """Check if contract expires within 30 days."""
        if self.status != "active":
            return False
        delta = self.end_date - date.today()
        return 0 <= delta.days <= 30

    @property
    def days_remaining(self):
        if self.status != "active":
            return 0
        delta = self.end_date - date.today()
        return max(delta.days, 0)

    @property
    def status_label(self):
        labels = {
            "active": "Đang hiệu lực",
            "expired": "Hết hạn",
            "terminated": "Đã chấm dứt",
        }
        return labels.get(self.status, self.status)

    @property
    def status_color(self):
        colors = {"active": "success", "expired": "secondary", "terminated": "danger"}
        return colors.get(self.status, "secondary")

    def __repr__(self):
        return f"<Contract #{self.id}>"
