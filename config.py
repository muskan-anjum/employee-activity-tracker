import os
import secrets


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        secrets.token_hex(32)
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///employee_tracker.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("COOKIE_SECURE") == "1"
    MAX_CONTENT_LENGTH = 1024 * 1024
