from marshmallow import Schema, fields

from app.extensions import db
from app.models import MatchParticipant, Participant
from app.services.participant_service import get_participant_display


class MatchSchema(Schema):
    id = fields.Int(dump_only=True)
    tournament_id = fields.Int()
    round = fields.Str()
    venue_id = fields.Int(allow_none=True)
    scheduled_at = fields.DateTime(allow_none=True)
    status = fields.Method("get_status")
    participants = fields.Method("get_participants")

    def get_status(self, obj):
        return obj.status.value

    def get_participants(self, obj):
        mps = MatchParticipant.query.filter_by(match_id=obj.id).all()
        result = []
        for mp in mps:
            participant = db.session.get(Participant, mp.participant_id)
            if participant:
                result.append(get_participant_display(participant))
        return result

class MatchScheduleUpdateSchema(Schema):
    venue_id = fields.Int(required=False, allow_none=True)
    scheduled_at = fields.DateTime(required=False, allow_none=True)