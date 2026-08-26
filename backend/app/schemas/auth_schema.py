from marshmallow import Schema, fields, validate, validates_schema, ValidationError

from app.constants.enums import UserRole, ParticipationType


class RegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    role = fields.Str(required=True, validate=validate.OneOf([r.value for r in UserRole]))

    participation_type = fields.Str(
        required=False, allow_none=True,
        validate=validate.OneOf([p.value for p in ParticipationType]),
    )
    team_option = fields.Str(required=False, allow_none=True, validate=validate.OneOf(["NEW", "EXISTING"]))
    team_name = fields.Str(required=False, allow_none=True, validate=validate.Length(min=1, max=120))
    team_id = fields.Int(required=False, allow_none=True)

    @validates_schema
    def validate_role_specific_fields(self, data, **kwargs):
        role = data.get("role")

        if role == UserRole.PLAYER.value:
            participation_type = data.get("participation_type")
            if not participation_type:
                raise ValidationError(
                    "participation_type is required when registering as a PLAYER",
                    field_name="participation_type",
                )
            if participation_type == ParticipationType.TEAM.value:
                team_option = data.get("team_option")
                if not team_option:
                    raise ValidationError(
                        "team_option is required when participation_type is TEAM",
                        field_name="team_option",
                    )
                if team_option == "NEW" and not data.get("team_name"):
                    raise ValidationError(
                        "team_name is required when team_option is NEW", field_name="team_name"
                    )
                if team_option == "EXISTING" and not data.get("team_id"):
                    raise ValidationError(
                        "team_id is required when team_option is EXISTING", field_name="team_id"
                    )
        else:
            player_only_fields = ["participation_type", "team_option", "team_name", "team_id"]
            if any(data.get(f) for f in player_only_fields):
                raise ValidationError(
                    "Organizers cannot register with player/team fields", field_name="role"
                )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8))


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    email = fields.Email()
    role = fields.Str()
    is_verified = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)