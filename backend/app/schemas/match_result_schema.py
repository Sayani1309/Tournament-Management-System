from marshmallow import Schema, fields, validate

from app.constants.enums import ResultType
from app.extensions import db
from app.models import Participant, MatchParticipant, MatchScore
from app.services.participant_service import get_participant_display


class ScoreEntrySchema(Schema):
    participant_id = fields.Int(required=True)
    score = fields.Decimal(required=True, places=2, as_string=False)


class MatchResultSubmitSchema(Schema):
    result_type = fields.Str(required=True, validate=validate.OneOf([r.value for r in ResultType]))
    winner_participant_id = fields.Int(required=False, allow_none=True)
    scores = fields.List(fields.Nested(ScoreEntrySchema), required=True, validate=validate.Length(equal=2))


class MatchResultSchema(Schema):
    id = fields.Int(dump_only=True)
    match_id = fields.Int()
    result_type = fields.Method("get_result_type")
    winner_participant_id = fields.Int(allow_none=True)
    winner = fields.Method("get_winner")
    scores = fields.Method("get_scores")
    submitted_at = fields.DateTime(dump_only=True)

    def get_result_type(self, obj):
        return obj.result_type.value

    def get_winner(self, obj):
        if obj.winner_participant_id is None:
            return None
        participant = db.session.get(Participant, obj.winner_participant_id)
        return get_participant_display(participant)

    def get_scores(self, obj):
        mps = MatchParticipant.query.filter_by(match_id=obj.match_id).all()
        result = []
        for mp in mps:
            score_row = MatchScore.query.filter_by(match_participant_id=mp.id).first()
            participant = db.session.get(Participant, mp.participant_id)
            result.append({
                "participant": get_participant_display(participant),
                "score": float(score_row.score) if score_row else None,
            })
        return result