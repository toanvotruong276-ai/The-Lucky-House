"""Model User - tài khoản quản trị hệ thống."""

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from src.extensions import db, login_manager


class User(UserMixin, db.Model):
    """Tài khoản đăng nhập của người quản lý / quản trị viên."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default="manager")
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    properties = db.relationship("Property", backref="owner", lazy="dynamic")

    # ------------------------------------------------------------------
    # Password helpers
    # ------------------------------------------------------------------

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def __repr__(self) -> str:
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id: str):
    # db.session.get() là cú pháp chuẩn của SQLAlchemy 2.x
    return db.session.get(User, int(user_id))
