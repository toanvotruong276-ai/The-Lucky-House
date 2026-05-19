"""Blueprint quản lý hóa đơn."""

from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from src.extensions import db
from src.models.contract import Contract
from src.models.invoice import Invoice, InvoiceDetail
from src.models.service import Service
from src.utils.helpers import form_float, form_int

invoices_bp = Blueprint("invoices", __name__, url_prefix="/invoices")


@invoices_bp.route("/")
@login_required
def index():
    status_filter = request.args.get("status", "")
    query = Invoice.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    invoices = query.order_by(Invoice.year.desc(), Invoice.month.desc()).all()
    return render_template("invoices/index.html", invoices=invoices, status_filter=status_filter)


@invoices_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        contract_id = form_int("contract_id")
        month = form_int("month")
        year = form_int("year")

        contract = Contract.query.get_or_404(contract_id)

        # Kiểm tra hóa đơn trùng (cùng hợp đồng + tháng + năm)
        existing = Invoice.query.filter_by(
            contract_id=contract_id, month=month, year=year
        ).first()
        if existing:
            flash(
                f"Hóa đơn tháng {month}/{year} cho hợp đồng này đã tồn tại.",
                "warning",
            )
            return redirect(url_for("invoices.detail", id=existing.id))

        invoice = Invoice(
            contract_id=contract_id,
            month=month,
            year=year,
            room_charge=contract.monthly_rent,
            due_date=date(year, month, 10),
        )
        db.session.add(invoice)
        db.session.flush()

        services = Service.query.filter_by(is_active=True).all()
        for svc in services:
            old_r = form_float(f"old_{svc.id}")
            new_r = form_float(f"new_{svc.id}")
            if svc.calc_type == "per_unit":
                qty = max(new_r - old_r, 0)
            else:
                qty = max(form_float(f"qty_{svc.id}", 1.0), 0)

            detail = InvoiceDetail(
                invoice_id=invoice.id,
                service_id=svc.id,
                old_reading=old_r,
                new_reading=new_r,
                quantity=qty,
                unit_price=svc.unit_price,
                amount=qty * svc.unit_price,
            )
            db.session.add(detail)

        db.session.flush()
        invoice.recalculate()
        db.session.commit()
        flash("Tạo hóa đơn thành công!", "success")
        return redirect(url_for("invoices.detail", id=invoice.id))

    contracts = Contract.query.filter_by(status="active").all()
    services = Service.query.filter_by(is_active=True).all()
    today = date.today()
    return render_template(
        "invoices/create.html",
        contracts=contracts,
        services=services,
        current_month=today.month,
        current_year=today.year,
    )


@invoices_bp.route("/<int:id>")
@login_required
def detail(id):
    invoice = Invoice.query.get_or_404(id)
    return render_template("invoices/detail.html", invoice=invoice)


@invoices_bp.route("/<int:id>/pay", methods=["POST"])
@login_required
def pay(id):
    invoice = Invoice.query.get_or_404(id)
    if invoice.status == "paid":
        flash("Hóa đơn này đã được thanh toán trước đó.", "warning")
        return redirect(url_for("invoices.detail", id=id))

    invoice.status = "paid"
    invoice.paid_date = date.today()
    db.session.commit()
    flash("Đã ghi nhận thanh toán!", "success")
    return redirect(url_for("invoices.detail", id=id))


@invoices_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    invoice = Invoice.query.get_or_404(id)
    db.session.delete(invoice)
    db.session.commit()
    flash("Đã xóa hóa đơn.", "info")
    return redirect(url_for("invoices.index"))
