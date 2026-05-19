"""App factory - THE LUCKY HOUSE."""
import os
from flask import Flask
from .config import config
from .extensions import db, login_manager, migrate

# Tất cả blueprints được import tập trung để dễ quản lý
_BLUEPRINTS = [
    "auth", "dashboard", "properties", "rooms", "tenants",
    "contracts", "invoices", "services", "maintenance", "reports",
]


def create_app(config_name=None):
    """Tạo và cấu hình Flask app."""
    if config_name is None:
        config_name = os.getenv("APP_ENV", "development")

    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
    )
    app.config.from_object(config[config_name])

    _init_extensions(app)
    _register_blueprints(app)
    _register_filters(app)

    with app.app_context():
        db.create_all()

    return app


def _init_extensions(app):
    """Khởi tạo extensions."""
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    # Import models để SQLAlchemy nhận biết
    from . import models  # noqa: F401


def _register_blueprints(app):
    """Đăng ký tất cả blueprints tự động."""
    import importlib
    for name in _BLUEPRINTS:
        module = importlib.import_module(f".routes.{name}", package="src")
        bp = getattr(module, f"{name}_bp")
        app.register_blueprint(bp)


def _register_filters(app):
    """Đăng ký Jinja2 template filters."""

    @app.template_filter("currency")
    def currency_filter(value):
        try:
            return f"{float(value):,.0f} ₫"
        except (ValueError, TypeError):
            return "0 ₫"

    @app.template_filter("phone")
    def phone_filter(value):
        """Format SĐT: 0912345678 → 0912 345 678."""
        if not value or len(value) < 10:
            return value or ""
        return f"{value[:4]} {value[4:7]} {value[7:]}"
