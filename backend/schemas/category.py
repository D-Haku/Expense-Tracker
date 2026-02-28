"""Category schema — validates and serializes category data."""

from marshmallow import Schema, fields, validate, EXCLUDE


class CategorySchema(Schema):
    """Schema for category validation and serialization.

    Validation rules:
    - name: required, non-empty, max 50 characters, unique (enforced at DB level)
    """

    id = fields.Integer(dump_only=True)
    name = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=50, error="Name must be 1-50 characters."),
        ],
    )
    created_at = fields.DateTime(dump_only=True)

    class Meta:
        unknown = EXCLUDE
