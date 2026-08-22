import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask

from .config import config_by_name
from .extensions import db, migrate, jwt, cors


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})  # tighten origins before deploy

    from . import models  # noqa: F401  — registers models with SQLAlchemy metadata

    from .routes.health_routes import health_bp
    from .routes.auth_routes import auth_bp
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1")

    return app