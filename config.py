import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    RAW_DB_PATH = os.environ.get(
        "RAW_DB_PATH", os.path.join(BASE_DIR, "instance", "sabuzak.db")
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{RAW_DB_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
