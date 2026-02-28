"""Expense schema — validates and serializes expense data."""

from datetime import date

from marshmallow import Schema, fields, validate, validates, ValidationError, EXCLUDE


class ExpenseSchema(Schema):
    """Schema for expense validation and serialization.

    Validation rules:
    - amount: required, must be > 0
    - description: required, non-empty, max 200 characters
    - date: required, valid ISO date, must not be in the future
    - category_id: required, must reference an existing category (checked at route level)
    """

    id = fields.Integer(dump_only=True)
    amount = fields.Float(
        required=True,
        validate=[
            validate.Range(min=0, min_inclusive=False, error="Amount must be greater than 0."),
        ],
    )
    description = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=200, error="Description must be 1-200 characters."),
        ],
    )
    date = fields.Date(required=True)
    category_id = fields.Integer(required=True, load_only=True)
    created_at = fields.DateTime(dump_only=True)

    # Nested category info in responses
    category_name = fields.String(dump_only=True)

    class Meta:
        unknown = EXCLUDE

    @validates("date")
    def validate_date_not_future(self, value: date) -> None:
        """Ensure the expense date is not in the future."""
        if value > date.today():
            raise ValidationError("Date cannot be in the future.")