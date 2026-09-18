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

    return app
