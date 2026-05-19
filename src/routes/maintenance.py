"""Blueprint quản lý yêu cầu bảo trì."""

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from src.extensions import db
from src.models.maintenance import MaintenanceRequest
from src.models.room import Room
from src.models.tenant import Tenant
from src.utils.helpers import form_float, form_int

maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/maintenance")


@maintenance_bp.route("/")
@login_required
def index():
    status_filter = request.args.get("status", "")
    query = MaintenanceRequest.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    requests_list = query.order_by(MaintenanceRequest.created_at.desc()).all()
    return render_template("maintenance/index.html", requests=requests_list, status_filter=status_filter)


@maintenance_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        tenant_id_raw = request.form.get("tenant_id")
        mr = MaintenanceRequest(
            room_id=form_int("room_id"),
            tenant_id=int(tenant_id_raw) if tenant_id_raw else None,
            title=request.form.get("title", "").strip(),
            description=request.form.get("description", "").strip(),
            priority=request.form.get("priority", "medium"),
            cost=form_float("cost"),
        )
        db.session.add(mr)
        db.session.commit()
        flash("Tạo yêu cầu bảo trì thành công!", "success")
        return redirect(url_for("maintenance.index"))

    rooms = Room.query.order_by(Room.room_number).all()
    tenants = Tenant.query.filter_by(is_active=True).order_by(Tenant.full_name).all()
    return render_template("maintenance/form.html", mr=None, rooms=rooms, tenants=tenants)


@maintenance_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    mr = MaintenanceRequest.query.get_or_404(id)
    if request.method == "POST":
        new_status = request.form.get("status", mr.status)
        mr.title = request.form.get("title", "").strip()
        mr.description = request.form.get("description", "").strip()
        mr.priority = request.form.get("priority", "medium")
        mr.cost = form_float("cost")

        # Ghi thời điểm hoàn thành khi chuyển sang "completed"
        if new_status == "completed" and mr.status != "completed":
            mr.resolved_at = datetime.utcnow()
        # Xóa resolved_at nếu trạng thái bị đổi lại (ví dụ: reopen)
        elif new_status != "completed":
            mr.resolved_at = None

        mr.status = new_status
        db.session.commit()
        flash("Cập nhật yêu cầu bảo trì thành công!", "success")
        return redirect(url_for("maintenance.index"))

    rooms = Room.query.order_by(Room.room_number).all()
    tenants = Tenant.query.filter_by(is_active=True).order_by(Tenant.full_name).all()
    return render_template("maintenance/form.html", mr=mr, rooms=rooms, tenants=tenants)


@maintenance_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    mr = MaintenanceRequest.query.get_or_404(id)
    db.session.delete(mr)
    db.session.commit()
    flash("Đã xóa yêu cầu bảo trì.", "info")
    return redirect(url_for("maintenance.index"))
