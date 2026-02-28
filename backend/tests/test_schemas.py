"""Tests for Marshmallow schemas — independent of routes."""

from datetime import date, timedelta

import pytest
from marshmallow import ValidationError

from schemas.category import CategorySchema
from schemas.expense import ExpenseSchema


class TestCategorySchema:
    """CategorySchema validation tests."""

    def test_valid_category(self):
        schema = CategorySchema()
        result = schema.load({"name": "Food"})
        assert result["name"] == "Food"

    def test_empty_name_rejected(self):
        schema = CategorySchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"name": ""})
        assert "name" in exc_info.value.messages

    def test_name_too_long_rejected(self):
        schema = CategorySchema()
        with pytest.raises(ValidationError):
            schema.load({"name": "x" * 51})

    def test_missing_name_rejected(self):
        schema = CategorySchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({})
        assert "name" in exc_info.value.messages

    def test_id_is_dump_only(self):
        """id field should be ignored on load (excluded by Meta.unknown=EXCLUDE)."""
        schema = CategorySchema()
        result = schema.load({"name": "Food", "id": 99})
        # id is dump_only and unknown fields are excluded, so id should not appear in loaded data
        assert "id" not in result


class TestExpenseSchema:
    """ExpenseSchema validation tests."""

    def test_valid_expense(self):
        schema = ExpenseSchema()
        result = schema.load({
            "amount": 42.50,
            "description": "Lunch",
            "date": "2024-01-15",
            "category_id": 1,
        })
        assert result["amount"] == 42.50
        assert result["date"] == date(2024, 1, 15)

    def test_zero_amount_rejected(self):
        schema = ExpenseSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                "amount": 0,
                "description": "Test",
                "date": "2024-01-15",
                "category_id": 1,
            })
        assert "amount" in exc_info.value.messages

    def test_negative_amount_rejected(self):
        schema = ExpenseSchema()
        with pytest.raises(ValidationError):
            schema.load({
                "amount": -5,
                "description": "Test",
                "date": "2024-01-15",
                "category_id": 1,
            })

    def test_future_date_rejected(self):
        schema = ExpenseSchema()
        future = (date.today() + timedelta(days=10)).isoformat()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                "amount": 10,
                "description": "Test",
                "date": future,
                "category_id": 1,
            })
        assert "date" in exc_info.value.messages

    def test_today_date_accepted(self):
        """Today's date should be valid."""
        schema = ExpenseSchema()
        result = schema.load({
            "amount": 10,
            "description": "Test",
            "date": date.today().isoformat(),
            "category_id": 1,
        })
        assert result["date"] == date.today()

    def test_empty_description_rejected(self):
        schema = ExpenseSchema()
        with pytest.raises(ValidationError):
            schema.load({
                "amount": 10,
                "description": "",
                "date": "2024-01-15",
                "category_id": 1,
            })

    def test_description_too_long_rejected(self):
        schema = ExpenseSchema()
        with pytest.raises(ValidationError):
            schema.load({
                "amount": 10,
                "description": "x" * 201,
                "date": "2024-01-15",
                "category_id": 1,
            })

    def test_missing_required_fields(self):
        schema = ExpenseSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({})
        errors = exc_info.value.messages
        assert "amount" in errors
        assert "description" in errors
        assert "date" in errors
        assert "category_id" in errors