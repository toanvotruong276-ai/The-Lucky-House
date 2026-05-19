"""
THE LUCKY HOUSE - Entry Point
==============================
Hỗ trợ 2 chế độ:
  - development : Flask dev server (auto-reload)
  - production  : Waitress WSGI (ổn định cho mạng nội bộ)

Cách chạy:
  python run.py                       # Dev mode (mặc định)
  APP_ENV=production python run.py    # Production mode
"""

import os
import socket

from dotenv import load_dotenv

load_dotenv()


def get_local_ip() -> str:
    """Lấy địa chỉ IP nội bộ của máy chủ."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def main() -> None:
    env = os.getenv("APP_ENV", "development")
    host = "0.0.0.0"
    port = int(os.getenv("PORT", 5000))
    local_ip = get_local_ip()

    from src import create_app

    app = create_app(env)

    if env == "production":
        from waitress import serve

        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "sqlite (default)")
        print("=" * 55)
        print("  THE LUCKY HOUSE - Production Server")
        print("=" * 55)
        print(f"  LAN:      http://{local_ip}:{port}")
        print(f"  Local:    http://localhost:{port}")
        print(f"  Database: {db_uri}")
        print(f"  Threads:  4")
        print("=" * 55)
        serve(app, host=host, port=port, threads=4)
    else:
        print(f"  [DEV] http://localhost:{port}")
        print(f"  [DEV] http://{local_ip}:{port}")
        app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
    main()
