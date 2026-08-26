from marshmallow import Schema, fields, validate


class ParticipantRegisterSchema(Schema):
    player_id = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    team_id = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))


class ParticipantSchema(Schema):
    id = fields.Int(dump_only=True)
    type = fields.Method("get_type")
    player_id = fields.Int(allow_none=True)
    team_id = fields.Int(allow_none=True)
    name = fields.Method("get_name")

    def get_type(self, obj):
        return obj.type.value

    def get_name(self, obj):
        from app.services.participant_service import get_participant_display
        return get_participant_display(obj)["name"]


class TournamentParticipantSchema(Schema):
    id = fields.Int(dump_only=True)
    tournament_id = fields.Int()
    participant_id = fields.Int()
    registered_at = fields.DateTime(dump_only=True)
    participant = fields.Nested(ParticipantSchema)