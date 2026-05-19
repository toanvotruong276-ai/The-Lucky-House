"""Seed database - THE LUCKY HOUSE - KDC CITY LAND PARK HILL."""
from datetime import date, timedelta
from src import create_app
from src.extensions import db
from src.models.user import User
from src.models.property import Property
from src.models.floor import Floor
from src.models.room import Room
from src.models.tenant import Tenant
from src.models.contract import Contract
from src.models.service import Service
from src.models.invoice import Invoice, InvoiceDetail

FIXED_ADDRESS = "KDC CITY LAND PARK HILL"


def create_house(user_id, house_number, num_floors, has_basement, base_price=5000000, room_area=25):
    prop = Property(
        name=f"Nh\u00e0 s\u1ed1 {house_number}",
        house_number=str(house_number),
        address=FIXED_ADDRESS,
        has_basement=has_basement,
        num_floors=num_floors,
        user_id=user_id,
    )
    db.session.add(prop)
    db.session.flush()

    all_rooms = []

    if has_basement:
        basement = Floor(property_id=prop.id, floor_name="H\u1ea7m", floor_order=-1)
        db.session.add(basement)
        db.session.flush()
        for label in ["A", "B"]:
            room = Room(
                floor_id=basement.id, room_number=f"H-{label}", room_label=label,
                area=room_area, base_price=base_price * 0.7, max_occupants=2,
            )
            db.session.add(room)
            all_rooms.append(room)

    ground = Floor(property_id=prop.id, floor_name="Tr\u1ec7t", floor_order=0)
    db.session.add(ground)
    db.session.flush()
    for label in ["A", "B"]:
        room = Room(
            floor_id=ground.id, room_number=f"T-{label}", room_label=label,
            area=room_area, base_price=base_price, max_occupants=2,
        )
        db.session.add(room)
        all_rooms.append(room)

    for i in range(1, num_floors + 1):
        floor = Floor(property_id=prop.id, floor_name=f"L\u1ea7u {i}", floor_order=i)
        db.session.add(floor)
        db.session.flush()
        for label in ["A", "B"]:
            room = Room(
                floor_id=floor.id, room_number=f"L{i}-{label}", room_label=label,
                area=room_area, base_price=base_price, max_occupants=2,
            )
            db.session.add(room)
            all_rooms.append(room)

    db.session.flush()
    return prop, all_rooms


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # --- Admin ---
        admin = User(
            username="admin", full_name="Nguy\u1ec5n V\u0103n Admin",
            email="admin@luckyhouse.vn", phone="0901234567", role="admin",
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.flush()

        # --- Houses ---
        h1, rooms1 = create_house(admin.id, "1", num_floors=3, has_basement=True, base_price=5000000)
        h2, rooms2 = create_house(admin.id, "2", num_floors=3, has_basement=False, base_price=5500000)
        h3, rooms3 = create_house(admin.id, "3", num_floors=2, has_basement=True, base_price=4500000)

        all_rooms = rooms1 + rooms2 + rooms3

        # --- Tenants ---
        tenants_data = [
            ("Tr\u1ea7n Th\u1ecb Mai", "0912345678", "034567890123", "H\u00e0 N\u1ed9i", "Nh\u00e2n vi\u00ean v\u0103n ph\u00f2ng"),
            ("L\u00ea V\u0103n H\u00f9ng", "0923456789", "034567890124", "\u0110\u00e0 N\u1eb5ng", "Sinh vi\u00ean"),
            ("Ph\u1ea1m Th\u1ecb Lan", "0934567890", "034567890125", "Hu\u1ebf", "Gi\u00e1o vi\u00ean"),
            ("Nguy\u1ec5n V\u0103n \u0110\u1ee9c", "0945678901", "034567890126", "Ngh\u1ec7 An", "K\u1ef9 s\u01b0 IT"),
            ("Ho\u00e0ng Th\u1ecb Hoa", "0956789012", "034567890127", "H\u1ea3i Ph\u00f2ng", "B\u00e1c s\u0129"),
            ("V\u00f5 V\u0103n Tu\u1ea5n", "0967890123", "034567890128", "C\u1ea7n Th\u01a1", "K\u1ebf to\u00e1n"),
            ("\u0110\u1eb7ng Th\u1ecb Ng\u1ecdc", "0978901234", "034567890129", "B\u00ecnh D\u01b0\u01a1ng", "Nh\u00e2n vi\u00ean"),
        ]
        tenants = []
        for name, phone, idc, hometown, occ in tenants_data:
            t = Tenant(
                full_name=name, phone=phone, id_card=idc,
                hometown=hometown, occupation=occ, date_of_birth=date(1995, 5, 15),
            )
            tenants.append(t)
        db.session.add_all(tenants)
        db.session.flush()

        # --- Services ---
        services = [
            Service(name="Ti\u1ec1n \u0111i\u1ec7n", unit="kWh", unit_price=3500, calc_type="per_unit"),
            Service(name="Ti\u1ec1n n\u01b0\u1edbc", unit="m\u00b3", unit_price=15000, calc_type="per_unit"),
            Service(name="Internet", unit="th\u00e1ng", unit_price=100000, calc_type="fixed"),
            Service(name="R\u00e1c", unit="th\u00e1ng", unit_price=20000, calc_type="fixed"),
            Service(name="Gi\u1eef xe", unit="th\u00e1ng", unit_price=100000, calc_type="fixed"),
        ]
        db.session.add_all(services)
        db.session.flush()

        # --- Contracts ---
        today = date.today()
        contract_rooms = [rooms1[2], rooms1[4], rooms2[0], rooms2[3], rooms3[1]]
        contracts = []
        for i, room in enumerate(contract_rooms):
            end_days = 275 if i < 3 else 20
            c = Contract(
                room_id=room.id, tenant_id=tenants[i].id,
                start_date=today - timedelta(days=90),
                end_date=today + timedelta(days=end_days),
                monthly_rent=room.base_price, deposit=room.base_price,
            )
            room.status = "occupied"
            contracts.append(c)
        db.session.add_all(contracts)
        db.session.flush()

        # --- Invoice ---
        inv = Invoice(
            contract_id=contracts[0].id, month=today.month, year=today.year,
            room_charge=contracts[0].monthly_rent, due_date=date(today.year, today.month, 10),
        )
        db.session.add(inv)
        db.session.flush()
        details = [
            InvoiceDetail(invoice_id=inv.id, service_id=services[0].id, old_reading=100, new_reading=180, quantity=80, unit_price=3500, amount=280000),
            InvoiceDetail(invoice_id=inv.id, service_id=services[1].id, old_reading=50, new_reading=58, quantity=8, unit_price=15000, amount=120000),
            InvoiceDetail(invoice_id=inv.id, service_id=services[2].id, quantity=1, unit_price=100000, amount=100000),
        ]
        db.session.add_all(details)
        db.session.flush()
        inv.recalculate()

        rooms1[0].status = "maintenance"
        db.session.commit()

        total_rooms = len(all_rooms)
        print("[OK] Seed data created successfully!")
        print(f"    Address: {FIXED_ADDRESS}")
        print(f"    Houses: 3 | Total rooms: {total_rooms}")
        print(f"    Tenants: {len(tenants)} | Contracts: {len(contracts)}")
        print(f"    Services: {len(services)} | Invoices: 1")
        print(f"    Admin login: admin / admin123")


if __name__ == "__main__":
    seed()
