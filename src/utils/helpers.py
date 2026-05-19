"""Các hàm tiện ích dùng chung trong toàn bộ ứng dụng."""

from datetime import datetime
from urllib.parse import urlparse

from flask import request


# ---------------------------------------------------------------------------
# Parse form data an toàn (tránh crash khi người dùng nhập sai kiểu dữ liệu)
# ---------------------------------------------------------------------------

def form_int(key: str, default: int = 0) -> int:
    """Đọc giá trị integer từ form; trả về ``default`` nếu không hợp lệ."""
    try:
        return int(request.form.get(key, default))
    except (ValueError, TypeError):
        return default


def form_float(key: str, default: float = 0.0) -> float:
    """Đọc giá trị float từ form; trả về ``default`` nếu không hợp lệ."""
    try:
        return float(request.form.get(key, default))
    except (ValueError, TypeError):
        return default


def form_date(key: str, fmt: str = "%Y-%m-%d"):
    """Đọc và parse ngày từ form; trả về ``None`` nếu không có hoặc sai định dạng."""
    raw = request.form.get(key, "").strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw, fmt).date()
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Bảo mật redirect
# ---------------------------------------------------------------------------

def safe_redirect_url(fallback: str) -> str:
    """Trả về URL ``next`` từ query string, chỉ khi thuộc cùng host (tránh open redirect).

    Nếu URL ``next`` trỏ ra domain ngoài, trả về ``fallback``.
    """
    next_url = request.args.get("next", "")
    if not next_url:
        return fallback
    parsed = urlparse(next_url)
    # Chỉ cho phép relative URL (không có scheme/netloc)
    if parsed.scheme or parsed.netloc:
        return fallback
    return next_url
