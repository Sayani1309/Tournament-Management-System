from marshmallow import Schema, fields, validate

from app.constants.enums import UserRole


class RegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    role = fields.Str(
        required=True,
        validate=validate.OneOf([r.value for r in UserRole]),
    )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    email = fields.Email()
    role = fields.Str()
    created_at = fields.DateTime(dump_only=True)