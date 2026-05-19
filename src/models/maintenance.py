from datetime import datetime
from src.extensions import db


class MaintenanceRequest(db.Model):
    __tablename__ = "maintenance_requests"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default="medium")  # low, medium, high
    status = db.Column(db.String(20), default="pending")  # pending, in_progress, completed
    cost = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    @property
    def priority_label(self):
        labels = {"low": "Thấp", "medium": "Trung bình", "high": "Cao"}
        return labels.get(self.priority, self.priority)

    @property
    def priority_color(self):
        colors = {"low": "info", "medium": "warning", "high": "danger"}
        return colors.get(self.priority, "secondary")

    @property
    def status_label(self):
        labels = {"pending": "Chờ xử lý", "in_progress": "Đang xử lý", "completed": "Hoàn thành"}
        return labels.get(self.status, self.status)

    @property
    def status_color(self):
        colors = {"pending": "warning", "in_progress": "info", "completed": "success"}
        return colors.get(self.status, "secondary")

    def __repr__(self):
        return f"<Maintenance #{self.id}>"
