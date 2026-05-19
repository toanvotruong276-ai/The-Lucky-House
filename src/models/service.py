from src.extensions import db


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(30))  # kWh, m3, thang
    unit_price = db.Column(db.Float, nullable=False)
    calc_type = db.Column(db.String(20), default="per_unit")  # per_unit, fixed
    is_active = db.Column(db.Boolean, default=True)

    invoice_details = db.relationship("InvoiceDetail", backref="service", lazy="dynamic")

    @property
    def calc_type_label(self):
        labels = {"per_unit": "Theo đơn vị", "fixed": "Cố định"}
        return labels.get(self.calc_type, self.calc_type)

    def __repr__(self):
        return f"<Service {self.name}>"
