# backend/app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from marshmallow import Schema  # noqa: F401  (just confirming import works)
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema  # noqa: F401

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()