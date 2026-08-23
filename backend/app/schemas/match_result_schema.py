from marshmallow import Schema, fields, validate

from app.constants.enums import ResultType


class ScoreEntrySchema(Schema):
    participant_id = fields.Int(required=True)
    score = fields.Decimal(required=True, places=2, as_string=False)


class MatchResultSubmitSchema(Schema):
    result_type = fields.Str(required=True, validate=validate.OneOf([r.value for r in ResultType]))
    winner_participant_id = fields.Int(required=False, allow_none=True)
    scores = fields.List(fields.Nested(ScoreEntrySchema), required=True, validate=validate.Length(equal=2))


class MatchScoreDumpSchema(Schema):
    participant_id = fields.Method("get_participant_id")
    score = fields.Decimal(as_string=True)

    def get_participant_id(self, obj):
        return obj.match_participant.participant_id


class MatchResultSchema(Schema):
    id = fields.Int(dump_only=True)
    match_id = fields.Int()
    result_type = fields.Method("get_result_type")
    winner_participant_id = fields.Int(allow_none=True)
    submitted_at = fields.DateTime(dump_only=True)

    def get_result_type(self, obj):
        return obj.result_type.value