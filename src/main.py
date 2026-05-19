from __future__ import annotations

import os

from dotenv import load_dotenv


def greeting(name: str = "Python") -> str:
    return f"Hello, {name}!"


def main() -> None:
    load_dotenv()
    app_env = os.getenv("APP_ENV", "development")
    print(greeting(app_env))


if __name__ == "__main__":
    main()
