from marshmallow import Schema, fields, validate

from app.constants.enums import TournamentFormat, ParticipationType, TournamentStatus


class TournamentCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(required=False, allow_none=True)
    sport = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    format = fields.Str(required=True, validate=validate.OneOf([f.value for f in TournamentFormat]))
    participant_type = fields.Str(
        required=True, validate=validate.OneOf([p.value for p in ParticipationType])
    )
    start_date = fields.Date(required=False, allow_none=True)
    end_date = fields.Date(required=False, allow_none=True)


class TournamentUpdateSchema(Schema):
    name = fields.Str(required=False, allow_none=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(required=False, allow_none=True)
    sport = fields.Str(required=False, allow_none=True)
    format = fields.Str(required=False, allow_none=True, validate=validate.OneOf([f.value for f in TournamentFormat]))
    participant_type = fields.Str(
        required=False, allow_none=True, validate=validate.OneOf([p.value for p in ParticipationType])
    )
    start_date = fields.Date(required=False, allow_none=True)
    end_date = fields.Date(required=False, allow_none=True)


class TournamentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str(allow_none=True)
    sport = fields.Str()
    format = fields.Method("get_format")
    participant_type = fields.Method("get_participant_type")
    status = fields.Method("get_status")
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)
    organizer_id = fields.Int()
    organizer_name = fields.Method("get_organizer_name")
    organizer_email = fields.Method("get_organizer_email")
    created_at = fields.DateTime(dump_only=True)

    def get_format(self, obj):
        return obj.format.value

    def get_participant_type(self, obj):
        return obj.participant_type.value

    def get_status(self, obj):
        return obj.status.value

    def get_organizer_name(self, obj):
        return obj.organizer.name if obj.organizer else None

    def get_organizer_email(self, obj):
        return obj.organizer.email if obj.organizer else None