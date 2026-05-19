"""Cấu hình ứng dụng THE LUCKY HOUSE."""

import os

from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Đường dẫn tuyệt đối đến file SQLite
_SQLITE_PATH = os.path.join(basedir, "instance", "lucky_house.db")
_DEFAULT_DB = f"sqlite:///{_SQLITE_PATH}"


def _resolve_db_uri() -> str:
    """Xử lý DATABASE_URL từ .env, tự chuyển đường dẫn tương đối thành tuyệt đối."""
    uri = os.getenv("DATABASE_URL", "").strip()
    if not uri:
        return _DEFAULT_DB
    # Render.com dùng 'postgres://' nhưng SQLAlchemy 2.x yêu cầu 'postgresql://'
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    # Nếu là sqlite với đường dẫn tương đối, chuyển thành tuyệt đối
    if uri.startswith("sqlite:///") and not os.path.isabs(uri[10:]):
        abs_path = os.path.join(basedir, uri[10:])
        # Tạo thư mục cha nếu chưa tồn tại
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        return f"sqlite:///{abs_path}"
    return uri


class Config:
    """Cấu hình chung."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = _resolve_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
