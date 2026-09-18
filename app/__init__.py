from flask import Flask

from .extensions import db, login_manager


def create_app(config_object="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .routes import register_blueprints
    register_blueprints(app)

    from .services.data import format_period
    app.jinja_env.filters["period"] = format_period

    @app.cli.command("init-db")
    def init_db():
        """테이블 생성 (raw_exhibitions는 scripts/crawl/sync_to_db.py가 채움)."""
        from . import models  # noqa: F401  (모델 등록을 위해 import)
        db.create_all()
        print("DB 초기화 완료:", app.config["SQLALCHEMY_DATABASE_URI"])

    return app
