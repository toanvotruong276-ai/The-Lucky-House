"""Blueprint quản lý nhà (Property)."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.extensions import db
from src.models.floor import Floor
from src.models.property import Property
from src.models.room import Room
from src.utils.helpers import form_float, form_int

properties_bp = Blueprint("properties", __name__, url_prefix="/properties")

_FIXED_ADDRESS = "KDC CITY LAND PARK HILL"


# ---------------------------------------------------------------------------
# Helper nội bộ
# ---------------------------------------------------------------------------

def _add_room(floor_id: int, room_number: str, label: str, area: float, price: float) -> None:
    """Tạo và thêm một phòng vào session (chưa commit)."""
    db.session.add(Room(
        floor_id=floor_id,
        room_number=room_number,
        room_label=label,
        area=area,
        base_price=price,
        max_occupants=2,
    ))


def _auto_create_floors_and_rooms(prop: Property, num_floors: int, has_basement: bool,
                                  base_price: float, room_area: float) -> int:
    """Tự động tạo tầng + phòng cho một nhà mới. Trả về tổng số phòng đã tạo."""
    total_rooms = 0

    if has_basement:
        basement = Floor(property_id=prop.id, floor_name="Hầm", floor_order=-1)
        db.session.add(basement)
        db.session.flush()
        for label in ("A", "B"):
            _add_room(basement.id, f"H-{label}", label, room_area, base_price * 0.7)
        total_rooms += 2

    ground = Floor(property_id=prop.id, floor_name="Trệt", floor_order=0)
    db.session.add(ground)
    db.session.flush()
    for label in ("A", "B"):
        _add_room(ground.id, f"T-{label}", label, room_area, base_price)
    total_rooms += 2

    for i in range(1, num_floors + 1):
        floor = Floor(property_id=prop.id, floor_name=f"Lầu {i}", floor_order=i)
        db.session.add(floor)
        db.session.flush()
        for label in ("A", "B"):
            _add_room(floor.id, f"L{i}-{label}", label, room_area, base_price)
        total_rooms += 2

    return total_rooms


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@properties_bp.route("/")
@login_required
def index():
    properties = Property.query.order_by(Property.house_number).all()
    return render_template("properties/index.html", properties=properties)


@properties_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        house_number = request.form.get("house_number", "").strip()
        if not house_number:
            flash("Số nhà không được để trống.", "danger")
            return redirect(request.url)

        if Property.query.filter_by(house_number=house_number).first():
            flash(f"Nhà số {house_number} đã tồn tại.", "danger")
            return redirect(request.url)

        num_floors = form_int("num_floors", 3)
        has_basement = "has_basement" in request.form
        base_price = form_float("base_price", 5_000_000)
        room_area = form_float("room_area", 25)

        prop = Property(
            name=f"Nhà số {house_number}",
            house_number=house_number,
            address=_FIXED_ADDRESS,
            has_basement=has_basement,
            num_floors=num_floors,
            description=request.form.get("description", ""),
            user_id=current_user.id,
        )
        db.session.add(prop)
        db.session.flush()

        total = _auto_create_floors_and_rooms(prop, num_floors, has_basement, base_price, room_area)
        db.session.commit()
        flash(f"Thêm nhà số {house_number} thành công! ({total} phòng đã tạo tự động)", "success")
        return redirect(url_for("properties.index"))

    return render_template("properties/form.html", property=None)


@properties_bp.route("/<int:id>")
@login_required
def detail(id):
    prop = Property.query.get_or_404(id)
    floors = prop.floors.order_by(Floor.floor_order).all()
    return render_template("properties/detail.html", property=prop, floors=floors)


@properties_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    prop = Property.query.get_or_404(id)
    if request.method == "POST":
        prop.house_number = request.form.get("house_number", "").strip()
        prop.name = f"Nhà số {prop.house_number}"
        prop.description = request.form.get("description", "")
        db.session.commit()
        flash("Cập nhật nhà thành công!", "success")
        return redirect(url_for("properties.detail", id=prop.id))
    return render_template("properties/form.html", property=prop)


@properties_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    prop = Property.query.get_or_404(id)

    # Kiểm tra còn hợp đồng active trước khi xóa
    from src.models.contract import Contract
    active_count = (
        Contract.query
        .join(Room).join(Floor)
        .filter(Floor.property_id == prop.id, Contract.status == "active")
        .count()
    )
    if active_count:
        flash(f"Không thể xóa: nhà này còn {active_count} hợp đồng đang hiệu lực.", "danger")
        return redirect(url_for("properties.detail", id=prop.id))

    db.session.delete(prop)
    db.session.commit()
    flash("Đã xóa nhà.", "info")
    return redirect(url_for("properties.index"))
