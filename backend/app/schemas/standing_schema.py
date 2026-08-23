from marshmallow import Schema, fields


class StandingSchema(Schema):
    participant_id = fields.Int()
    name = fields.Str()
    played = fields.Int()
    won = fields.Int()
    drawn = fields.Int()
    lost = fields.Int()
    points = fields.Int()
    score_difference = fields.Float()
    total_score = fields.Float()