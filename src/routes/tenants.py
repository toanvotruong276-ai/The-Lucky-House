"""Blueprint quản lý khách thuê."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from src.extensions import db
from src.models.tenant import Tenant
from src.utils.helpers import form_date

tenants_bp = Blueprint("tenants", __name__, url_prefix="/tenants")


def _apply_form_to_tenant(tenant: Tenant) -> None:
    """Gán dữ liệu từ form vào đối tượng Tenant (dùng chung cho create & edit)."""
    tenant.full_name = request.form.get("full_name", "").strip()
    tenant.phone = request.form.get("phone", "").strip()
    tenant.email = request.form.get("email", "").strip()
    tenant.id_card = request.form.get("id_card", "").strip()
    tenant.date_of_birth = form_date("date_of_birth")
    tenant.hometown = request.form.get("hometown", "").strip()
    tenant.occupation = request.form.get("occupation", "").strip()
    tenant.notes = request.form.get("notes", "").strip()


@tenants_bp.route("/")
@login_required
def index():
    search = request.args.get("search", "")
    query = Tenant.query
    if search:
        query = query.filter(
            Tenant.full_name.ilike(f"%{search}%") | Tenant.phone.ilike(f"%{search}%")
        )
    tenants = query.order_by(Tenant.created_at.desc()).all()
    return render_template("tenants/index.html", tenants=tenants, search=search)


@tenants_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        tenant = Tenant()
        _apply_form_to_tenant(tenant)
        db.session.add(tenant)
        db.session.commit()
        flash("Thêm khách thuê thành công!", "success")
        return redirect(url_for("tenants.index"))
    return render_template("tenants/form.html", tenant=None)


@tenants_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    tenant = Tenant.query.get_or_404(id)
    if request.method == "POST":
        _apply_form_to_tenant(tenant)
        db.session.commit()
        flash("Cập nhật khách thuê thành công!", "success")
        return redirect(url_for("tenants.index"))
    return render_template("tenants/form.html", tenant=tenant)


@tenants_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    tenant = Tenant.query.get_or_404(id)

    # Không cho xóa khách đang có hợp đồng active
    if tenant.active_contract:
        flash("Không thể xóa khách thuê đang có hợp đồng hiệu lực.", "danger")
        return redirect(url_for("tenants.index"))

    db.session.delete(tenant)
    db.session.commit()
    flash("Đã xóa khách thuê.", "info")
    return redirect(url_for("tenants.index"))
