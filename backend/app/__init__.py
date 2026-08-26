import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask

from .config import config_by_name
from .extensions import db, migrate, jwt, cors, limiter


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    limiter.init_app(app)

    from . import models  # noqa: F401

    from .routes.health_routes import health_bp
    from .routes.auth_routes import auth_bp
    from .routes.tournament_routes import tournament_bp
    from .routes.venue_routes import venue_bp
    from .routes.participant_routes import participant_bp
    from .routes.match_routes import match_bp
    from .routes.standings_routes import standings_bp
    from .routes.player_routes import player_bp
    from .routes.team_routes import team_bp

    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1")
    app.register_blueprint(tournament_bp, url_prefix="/api/v1")
    app.register_blueprint(venue_bp, url_prefix="/api/v1")
    app.register_blueprint(participant_bp, url_prefix="/api/v1")
    app.register_blueprint(match_bp, url_prefix="/api/v1")
    app.register_blueprint(standings_bp, url_prefix="/api/v1")
    app.register_blueprint(player_bp, url_prefix="/api/v1")
    app.register_blueprint(team_bp, url_prefix="/api/v1")

    return app