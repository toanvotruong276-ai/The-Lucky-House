"""Blueprint quản lý hợp đồng thuê phòng."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from src.extensions import db
from src.models.contract import Contract
from src.models.floor import Floor
from src.models.property import Property
from src.models.room import Room
from src.models.tenant import Tenant
from src.utils.helpers import form_date, form_float, form_int

contracts_bp = Blueprint("contracts", __name__, url_prefix="/contracts")


@contracts_bp.route("/")
@login_required
def index():
    status_filter = request.args.get("status", "")
    query = Contract.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    contracts = query.order_by(Contract.created_at.desc()).all()
    return render_template("contracts/index.html", contracts=contracts, status_filter=status_filter)


@contracts_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        room_id = form_int("room_id")
        tenant_id = form_int("tenant_id")
        start_date = form_date("start_date")
        end_date = form_date("end_date")
        monthly_rent = form_float("monthly_rent")

        # --- Validation ---
        if not all([room_id, tenant_id, start_date, end_date, monthly_rent]):
            flash("Vui lòng điền đầy đủ thông tin bắt buộc.", "danger")
            return redirect(request.url)

        if start_date >= end_date:
            flash("Ngày kết thúc phải sau ngày bắt đầu.", "danger")
            return redirect(request.url)

        room = db.session.get(Room, room_id)
        if not room:
            flash("Phòng không tồn tại.", "danger")
            return redirect(request.url)

        # Kiểm tra phòng đã có hợp đồng active chưa
        if room.active_contract:
            flash("Phòng này đang có hợp đồng hiệu lực. Vui lòng chấm dứt hợp đồng cũ trước.", "danger")
            return redirect(request.url)

        contract = Contract(
            room_id=room_id,
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
            monthly_rent=monthly_rent,
            deposit=form_float("deposit"),
            terms=request.form.get("terms", ""),
        )
        db.session.add(contract)
        room.status = "occupied"
        db.session.commit()
        flash("Tạo hợp đồng thành công!", "success")
        return redirect(url_for("contracts.index"))

    rooms = (
        Room.query.filter_by(status="available")
        .join(Floor).join(Property)
        .order_by(Property.house_number, Floor.floor_order, Room.room_label)
        .all()
    )
    tenants = Tenant.query.filter_by(is_active=True).order_by(Tenant.full_name).all()
    return render_template("contracts/form.html", contract=None, rooms=rooms, tenants=tenants)


@contracts_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    contract = Contract.query.get_or_404(id)
    if request.method == "POST":
        start_date = form_date("start_date")
        end_date = form_date("end_date")

        if start_date and end_date and start_date >= end_date:
            flash("Ngày kết thúc phải sau ngày bắt đầu.", "danger")
            return redirect(request.url)

        contract.start_date = start_date or contract.start_date
        contract.end_date = end_date or contract.end_date
        contract.monthly_rent = form_float("monthly_rent") or contract.monthly_rent
        contract.deposit = form_float("deposit")
        contract.terms = request.form.get("terms", "")
        db.session.commit()
        flash("Cập nhật hợp đồng thành công!", "success")
        return redirect(url_for("contracts.index"))

    rooms = (
        Room.query.join(Floor).join(Property)
        .order_by(Property.house_number, Floor.floor_order, Room.room_label)
        .all()
    )
    tenants = Tenant.query.filter_by(is_active=True).order_by(Tenant.full_name).all()
    return render_template("contracts/form.html", contract=contract, rooms=rooms, tenants=tenants)


@contracts_bp.route("/<int:id>/terminate", methods=["POST"])
@login_required
def terminate(id):
    contract = Contract.query.get_or_404(id)
    if contract.status != "active":
        flash("Hợp đồng này không ở trạng thái hiệu lực.", "warning")
        return redirect(url_for("contracts.index"))

    contract.status = "terminated"

    # Trả phòng về trạng thái trống
    room = db.session.get(Room, contract.room_id)
    if room:
        room.status = "available"

    db.session.commit()
    flash("Đã chấm dứt hợp đồng.", "info")
    return redirect(url_for("contracts.index"))
