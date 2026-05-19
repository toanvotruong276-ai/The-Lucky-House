"""Blueprint quản lý phòng."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from src.extensions import db
from src.models.floor import Floor
from src.models.property import Property
from src.models.room import Room
from src.utils.helpers import form_float, form_int

rooms_bp = Blueprint("rooms", __name__, url_prefix="/rooms")


@rooms_bp.route("/")
@login_required
def index():
    status_filter = request.args.get("status", "")
    property_filter = request.args.get("property_id", "")

    properties = Property.query.order_by(Property.house_number).all()

    prop_query = (
        Property.query.filter_by(id=int(property_filter))
        if property_filter
        else Property.query.order_by(Property.house_number)
    )

    grouped = []
    for prop in prop_query.all():
        floors_data = []
        for floor in prop.floors.order_by(Floor.floor_order).all():
            room_query = floor.rooms
            if status_filter:
                room_query = room_query.filter_by(status=status_filter)
            rooms = room_query.order_by(Room.room_label).all()
            if rooms or not status_filter:
                floors_data.append({"floor": floor, "rooms": rooms})
        if floors_data:
            grouped.append({"property": prop, "floors": floors_data})

    return render_template(
        "rooms/index.html",
        grouped=grouped,
        properties=properties,
        status_filter=status_filter,
        property_filter=property_filter,
    )


@rooms_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    room = Room.query.get_or_404(id)
    if request.method == "POST":
        room.area = form_float("area")
        room.base_price = form_float("base_price") or room.base_price
        room.max_occupants = form_int("max_occupants", 2)
        room.status = request.form.get("status", room.status)
        room.description = request.form.get("description", "")
        db.session.commit()
        flash("Cập nhật phòng thành công!", "success")
        return redirect(url_for("rooms.index"))
    return render_template("rooms/form.html", room=room)


@rooms_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    room = Room.query.get_or_404(id)

    # Không cho xóa phòng đang có hợp đồng active
    if room.active_contract:
        flash("Không thể xóa phòng đang có hợp đồng hiệu lực.", "danger")
        return redirect(url_for("rooms.index"))

    db.session.delete(room)
    db.session.commit()
    flash("Đã xóa phòng.", "info")
    return redirect(url_for("rooms.index"))
