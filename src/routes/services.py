"""Blueprint quản lý dịch vụ (điện, nước, internet...)."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from src.extensions import db
from src.models.service import Service
from src.utils.helpers import form_float

services_bp = Blueprint("services", __name__, url_prefix="/services")


@services_bp.route("/")
@login_required
def index():
    services = Service.query.order_by(Service.name).all()
    return render_template("services/index.html", services=services)


@services_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        service = Service(
            name=request.form.get("name", "").strip(),
            unit=request.form.get("unit", "").strip(),
            unit_price=form_float("unit_price"),
            calc_type=request.form.get("calc_type", "per_unit"),
            is_active=True,
        )
        db.session.add(service)
        db.session.commit()
        flash("Thêm dịch vụ thành công!", "success")
        return redirect(url_for("services.index"))
    return render_template("services/form.html", service=None)


@services_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    service = Service.query.get_or_404(id)
    if request.method == "POST":
        service.name = request.form.get("name", "").strip()
        service.unit = request.form.get("unit", "").strip()
        service.unit_price = form_float("unit_price") or service.unit_price
        service.calc_type = request.form.get("calc_type", "per_unit")
        service.is_active = "is_active" in request.form
        db.session.commit()
        flash("Cập nhật dịch vụ thành công!", "success")
        return redirect(url_for("services.index"))
    return render_template("services/form.html", service=service)


@services_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    service = Service.query.get_or_404(id)

    # Không xóa dịch vụ đang được sử dụng trong hóa đơn
    if service.invoice_details.count() > 0:
        flash("Không thể xóa dịch vụ đang được sử dụng trong hóa đơn.", "danger")
        return redirect(url_for("services.index"))

    db.session.delete(service)
    db.session.commit()
    flash("Đã xóa dịch vụ.", "info")
    return redirect(url_for("services.index"))
