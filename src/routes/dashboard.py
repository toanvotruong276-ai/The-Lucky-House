"""Blueprint trang tổng quan (Dashboard)."""

from datetime import date, timedelta

from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from src.extensions import db
from src.models.contract import Contract
from src.models.floor import Floor
from src.models.invoice import Invoice
from src.models.maintenance import MaintenanceRequest
from src.models.property import Property
from src.models.room import Room
from src.models.tenant import Tenant

dashboard_bp = Blueprint("dashboard", __name__)


def _revenue_for(month: int, year: int) -> float:
    """Truy vấn tổng doanh thu đã thanh toán trong một tháng/năm cụ thể."""
    result = db.session.query(
        func.coalesce(func.sum(Invoice.total_amount), 0)
    ).filter(
        Invoice.status == "paid",
        Invoice.month == month,
        Invoice.year == year,
    ).scalar()
    return float(result)


def _last_n_months(n: int, today: date) -> list[tuple[int, int]]:
    """Trả về danh sách (month, year) của ``n`` tháng gần nhất, kết thúc tại ``today``."""
    months = []
    for i in range(n - 1, -1, -1):
        m = today.month - i
        y = today.year
        if m <= 0:
            m += 12
            y -= 1
        months.append((m, y))
    return months


@dashboard_bp.route("/")
@login_required
def index():
    today = date.today()

    # --- Thống kê phòng ---
    total_rooms = Room.query.count()
    available_rooms = Room.query.filter_by(status="available").count()
    occupied_rooms = Room.query.filter_by(status="occupied").count()
    maintenance_rooms = Room.query.filter_by(status="maintenance").count()
    total_houses = Property.query.count()

    # --- Thống kê hợp đồng / khách ---
    total_tenants = Tenant.query.filter_by(is_active=True).count()
    active_contracts = Contract.query.filter_by(status="active").count()

    # --- Doanh thu tháng này ---
    monthly_revenue = _revenue_for(today.month, today.year)

    # --- Hóa đơn ---
    pending_invoices = Invoice.query.filter_by(status="pending").count()
    overdue_invoices = Invoice.query.filter_by(status="overdue").count()

    # --- Hợp đồng sắp hết hạn (30 ngày tới) ---
    expiry_date = today + timedelta(days=30)
    expiring_contracts = (
        Contract.query
        .filter(
            Contract.status == "active",
            Contract.end_date >= today,
            Contract.end_date <= expiry_date,
        )
        .order_by(Contract.end_date.asc())
        .all()
    )

    # --- Bảo trì chưa xử lý ---
    pending_maintenance = (
        MaintenanceRequest.query
        .filter(MaintenanceRequest.status.in_(["pending", "in_progress"]))
        .order_by(MaintenanceRequest.created_at.desc())
        .limit(5)
        .all()
    )

    # --- Biểu đồ doanh thu 6 tháng gần nhất ---
    month_list = _last_n_months(6, today)
    chart_labels = [f"T{m}/{y}" for m, y in month_list]
    chart_data = [_revenue_for(m, y) for m, y in month_list]

    return render_template(
        "dashboard/index.html",
        total_rooms=total_rooms,
        available_rooms=available_rooms,
        occupied_rooms=occupied_rooms,
        maintenance_rooms=maintenance_rooms,
        total_houses=total_houses,
        total_tenants=total_tenants,
        active_contracts=active_contracts,
        monthly_revenue=monthly_revenue,
        pending_invoices=pending_invoices,
        overdue_invoices=overdue_invoices,
        expiring_contracts=expiring_contracts,
        pending_maintenance=pending_maintenance,
        chart_labels=chart_labels,
        chart_data=chart_data,
    )
