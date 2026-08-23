from marshmallow import Schema, fields, validate


class ParticipantRegisterSchema(Schema):
    player_id = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    team_id = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))


class ParticipantSchema(Schema):
    id = fields.Int(dump_only=True)
    type = fields.Method("get_type")
    player_id = fields.Int(allow_none=True)
    team_id = fields.Int(allow_none=True)

    def get_type(self, obj):
        return obj.type.value


class TournamentParticipantSchema(Schema):
    id = fields.Int(dump_only=True)
    tournament_id = fields.Int()
    participant_id = fields.Int()
    registered_at = fields.DateTime(dump_only=True)
    participant = fields.Nested(ParticipantSchema)