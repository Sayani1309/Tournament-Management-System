from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, validate, ValidationError

from app.extensions import db, require_role
from app.models import Venue

venue_bp = Blueprint("venue", __name__)


class VenueSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    location = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    capacity = fields.Int(required=False, allow_none=True, validate=validate.Range(min=0))


venue_schema = VenueSchema()
venues_schema = VenueSchema(many=True)


@venue_bp.route("/venues", methods=["GET"])
def get_venues():
    venues = Venue.query.order_by(Venue.name).all()
    return jsonify(venues_schema.dump(venues)), 200


@venue_bp.route("/venues", methods=["POST"])
@require_role("ORGANIZER")
def post_venue():
    try:
        data = venue_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    if Venue.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "A venue with this name already exists"}), 409

    venue = Venue(**data)
    db.session.add(venue)
    db.session.commit()
    return jsonify(venue_schema.dump(venue)), 201