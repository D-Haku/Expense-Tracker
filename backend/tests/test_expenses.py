"""Tests for expense routes — success, validation, and edge cases."""

import json
from datetime import date, timedelta


class TestListExpenses:
    """GET /api/expenses"""

    def test_returns_empty_list(self, client, db):
        """Empty database returns empty array."""
        resp = client.get("/api/expenses")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_returns_expenses_with_category_name(self, client, seed_category, db):
        """Expenses include the category name in the response."""
        from models.expense import Expense

        expense = Expense(
            amount=25.0,
            description="Lunch",
            date=date(2024, 1, 15),
            category_id=seed_category.id,
        )
        db.session.add(expense)
        db.session.commit()

        resp = client.get("/api/expenses")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["category_name"] == "Food"
        assert data[0]["amount"] == 25.0


class TestCreateExpense:
    """POST /api/expenses"""

    def test_create_valid_expense(self, client, seed_category):
        """Valid expense data creates an expense and returns 201."""
        resp = client.post(
            "/api/expenses",
            data=json.dumps({
                "amount": 42.50,
                "description": "Grocery shopping",
                "date": "2024-01-15",
                "category_id": seed_category.id,
            }),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["amount"] == 42.50
        assert data["description"] == "Grocery shopping"
        assert data["category_name"] == "Food"

    def test_create_with_zero_amount_returns_400(self, client, seed_category):
        """Amount of zero fails validation."""
        resp = client.post(
            "/api/expenses",
            data=json.dumps({
                "amount": 0,
                "description": "Free lunch",
                "date": "2024-01-15",
                "category_id": seed_category.id,
            }),
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert "amount" in resp.get_json()["details"]

    def test_create_with_negative_amount_returns_400(self, client, seed_category):
        """Negative amount fails validation."""
        resp = client.post(
            "/api/expenses",
            data=json.dumps({
                "amount": -10,
                "description": "Refund",
                "date": "2024-01-15",
                "category_id": seed_category.id,
            }),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_create_with_future_date_returns_400(self, client, seed_category):
        """Future date fails validation."""
        future = (date.today() + timedelta(days=10)).isoformat()
        resp = client.post(
            "/api/expenses",
            data=json.dumps({
                "amount": 10,
                "description": "Future expense",
                "date": future,
                "category_id": seed_category.id,
            }),
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert "date" in resp.get_json()["details"]

    def test_create_with_empty_description_returns_400(self, client, seed_category):
        """Empty description fails validation."""
        resp = client.post(
            "/api/expenses",
            data=json.dumps({
                "amount": 10,
                "description": "",
                "date": "2024-01-15",
                "category_id": seed_category.id,
            }),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_create_with_long_description_returns_400(self, client, seed_category):
        """Description exceeding 200 characters fails validation."""
        resp = client.post(
            "/api/expenses",
            data=json.dumps({
                "amount": 10,
                "description": "x" * 201,
                "date": "2024-01-15",
                "category_id": seed_category.id,
            }),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_create_with_invalid_category_returns_400(self, client, db):
        """Non-existent category ID returns 400."""
        resp = client.post(
            "/api/expenses",
            data=json.dumps({
                "amount": 10,
                "description": "Test",
                "date": "2024-01-15",
                "category_id": 999,
            }),
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert resp.get_json()["code"] == "INVALID_CATEGORY"

    def test_create_missing_fields_returns_400(self, client, db):
        """Missing required fields return validation error."""
        resp = client.post(
            "/api/expenses",
            data=json.dumps({"amount": 10}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_create_non_json_returns_error(self, client, db):
        """Non-JSON body returns an error (400 or 415)."""
        resp = client.post(
            "/api/expenses",
            data="not json",
            content_type="text/plain",
        )
        assert resp.status_code in (400, 415)


class TestGetExpense:
    """GET /api/expenses/<id>"""

    def test_get_existing_expense(self, client, seed_category, db):
        """Valid ID returns the expense."""
        from models.expense import Expense

        expense = Expense(
            amount=10.0,
            description="Test",
            date=date(2024, 1, 1),
            category_id=seed_category.id,
        )
        db.session.add(expense)
        db.session.commit()

        resp = client.get(f"/api/expenses/{expense.id}")
        assert resp.status_code == 200
        assert resp.get_json()["amount"] == 10.0

    def test_get_nonexistent_returns_404(self, client, db):
        """Invalid ID returns 404."""
        resp = client.get("/api/expenses/999")
        assert resp.status_code == 404


class TestUpdateExpense:
    """PUT /api/expenses/<id>"""

    def test_update_valid_expense(self, client, seed_category, db):
        """Valid update changes expense fields."""
        from models.expense import Expense

        expense = Expense(
            amount=10.0,
            description="Old",
            date=date(2024, 1, 1),
            category_id=seed_category.id,
        )
        db.session.add(expense)
        db.session.commit()

        resp = client.put(
            f"/api/expenses/{expense.id}",
            data=json.dumps({
                "amount": 20.0,
                "description": "Updated",
                "date": "2024-02-01",
                "category_id": seed_category.id,
            }),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.get_json()["amount"] == 20.0
        assert resp.get_json()["description"] == "Updated"

    def test_update_nonexistent_returns_404(self, client, db):
        """Updating non-existent expense returns 404."""
        resp = client.put(
            "/api/expenses/999",
            data=json.dumps({
                "amount": 10,
                "description": "Test",
                "date": "2024-01-01",
                "category_id": 1,
            }),
            content_type="application/json",
        )
        assert resp.status_code == 404


class TestDeleteExpense:
    """DELETE /api/expenses/<id>"""

    def test_delete_existing_expense(self, client, seed_category, db):
        """Deleting an existing expense returns 200."""
        from models.expense import Expense

        expense = Expense(
            amount=10.0,
            description="Test",
            date=date(2024, 1, 1),
            category_id=seed_category.id,
        )
        db.session.add(expense)
        db.session.commit()

        resp = client.delete(f"/api/expenses/{expense.id}")
        assert resp.status_code == 200

        # Verify it's gone
        resp = client.get(f"/api/expenses/{expense.id}")
        assert resp.status_code == 404

    def test_delete_nonexistent_returns_404(self, client, db):
        """Deleting non-existent expense returns 404."""
        resp = client.delete("/api/expenses/999")
        assert resp.status_code == 404


class TestExpenseSummary:
    """GET /api/expenses/summary"""

    def test_summary_empty_database(self, client, db):
        """Empty database returns empty summary."""
        resp = client.get("/api/expenses/summary")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_summary_groups_by_category(self, client, seed_category, db):
        """Summary groups expenses by category with totals."""
        from models.expense import Expense
        from models.category import Category

        transport = Category(name="Transport")
        db.session.add(transport)
        db.session.commit()

        expenses = [
            Expense(amount=10.0, description="A", date=date(2024, 1, 1), category_id=seed_category.id),
            Expense(amount=20.0, description="B", date=date(2024, 1, 2), category_id=seed_category.id),
            Expense(amount=15.0, description="C", date=date(2024, 1, 3), category_id=transport.id),
        ]
        db.session.add_all(expenses)
        db.session.commit()

        resp = client.get("/api/expenses/summary")
        data = resp.get_json()
        assert len(data) == 2

        # Ordered by total descending
        assert data[0]["category"] == "Food"
        assert data[0]["total"] == 30.0
        assert data[0]["count"] == 2
        assert data[1]["category"] == "Transport"
        assert data[1]["total"] == 15.0
        assert data[1]["count"] == 1