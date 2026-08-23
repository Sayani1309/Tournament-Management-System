from marshmallow import Schema, fields


class MatchParticipantSchema(Schema):
    id = fields.Int(dump_only=True)
    participant_id = fields.Int()


class MatchSchema(Schema):
    id = fields.Int(dump_only=True)
    tournament_id = fields.Int()
    round = fields.Str()
    venue_id = fields.Int(allow_none=True)
    scheduled_at = fields.DateTime(allow_none=True)
    status = fields.Method("get_status")

    def get_status(self, obj):
        return obj.status.value