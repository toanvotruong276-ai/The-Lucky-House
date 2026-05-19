from datetime import datetime
from src.extensions import db


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey("contracts.id"), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    room_charge = db.Column(db.Float, default=0)
    service_total = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default="pending")  # pending, paid, overdue
    due_date = db.Column(db.Date)
    paid_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    details = db.relationship("InvoiceDetail", backref="invoice", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def period_label(self):
        return f"Tháng {self.month}/{self.year}"

    @property
    def status_label(self):
        labels = {"pending": "Chưa thanh toán", "paid": "Đã thanh toán", "overdue": "Quá hạn"}
        return labels.get(self.status, self.status)

    @property
    def status_color(self):
        colors = {"pending": "warning", "paid": "success", "overdue": "danger"}
        return colors.get(self.status, "secondary")

    def recalculate(self):
        self.service_total = sum(d.amount for d in self.details.all())
        self.total_amount = self.room_charge + self.service_total

    def __repr__(self):
        return f"<Invoice #{self.id} - {self.period_label}>"


class InvoiceDetail(db.Model):
    __tablename__ = "invoice_details"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    old_reading = db.Column(db.Float, default=0)
    new_reading = db.Column(db.Float, default=0)
    quantity = db.Column(db.Float, default=0)
    unit_price = db.Column(db.Float, default=0)
    amount = db.Column(db.Float, default=0)

    def calculate(self):
        if self.service and self.service.calc_type == "per_unit":
            self.quantity = self.new_reading - self.old_reading
        self.amount = self.quantity * self.unit_price

    def __repr__(self):
        return f"<InvoiceDetail #{self.id}>"
