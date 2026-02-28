"""Tests for category routes — success, validation, and edge cases."""

import json


class TestListCategories:
    """GET /api/categories"""

    def test_returns_empty_list_when_no_categories(self, client, db):
        """Empty database returns empty array, not an error."""
        resp = client.get("/api/categories")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_returns_categories_ordered_by_name(self, client, seed_category, db):
        """Categories are returned alphabetically."""
        from models.category import Category
        db.session.add(Category(name="Transport"))
        db.session.commit()

        resp = client.get("/api/categories")
        data = resp.get_json()
        assert len(data) == 2
        assert data[0]["name"] == "Food"
        assert data[1]["name"] == "Transport"


class TestCreateCategory:
    """POST /api/categories"""

    def test_create_valid_category(self, client, db):
        """Valid name creates a category and returns 201."""
        resp = client.post(
            "/api/categories",
            data=json.dumps({"name": "Food"}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Food"
        assert "id" in data

    def test_create_duplicate_returns_409(self, client, seed_category):
        """Duplicate category name returns conflict error."""
        resp = client.post(
            "/api/categories",
            data=json.dumps({"name": "Food"}),
            content_type="application/json",
        )
        assert resp.status_code == 409
        assert resp.get_json()["code"] == "DUPLICATE_CATEGORY"

    def test_create_empty_name_returns_400(self, client, db):
        """Empty name fails validation."""
        resp = client.post(
            "/api/categories",
            data=json.dumps({"name": ""}),
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert resp.get_json()["code"] == "VALIDATION_ERROR"

    def test_create_missing_name_returns_400(self, client, db):
        """Missing name field fails validation."""
        resp = client.post(
            "/api/categories",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_create_name_too_long_returns_400(self, client, db):
        """Name exceeding 50 characters fails validation."""
        resp = client.post(
            "/api/categories",
            data=json.dumps({"name": "x" * 51}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_create_non_json_returns_error(self, client, db):
        """Non-JSON request body returns an error (400 or 415)."""
        resp = client.post(
            "/api/categories",
            data="not json",
            content_type="text/plain",
        )
        assert resp.status_code in (400, 415)


class TestGetCategory:
    """GET /api/categories/<id>"""

    def test_get_existing_category(self, client, seed_category):
        """Valid ID returns the category."""
        resp = client.get(f"/api/categories/{seed_category.id}")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Food"

    def test_get_nonexistent_returns_404(self, client, db):
        """Invalid ID returns not found."""
        resp = client.get("/api/categories/999")
        assert resp.status_code == 404
        assert resp.get_json()["code"] == "NOT_FOUND"


class TestUpdateCategory:
    """PUT /api/categories/<id>"""

    def test_update_valid_category(self, client, seed_category):
        """Valid update changes the name."""
        resp = client.put(
            f"/api/categories/{seed_category.id}",
            data=json.dumps({"name": "Groceries"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Groceries"

    def test_update_nonexistent_returns_404(self, client, db):
        """Updating a non-existent category returns 404."""
        resp = client.put(
            "/api/categories/999",
            data=json.dumps({"name": "Test"}),
            content_type="application/json",
        )
        assert resp.status_code == 404


class TestDeleteCategory:
    """DELETE /api/categories/<id>"""

    def test_delete_empty_category(self, client, seed_category):
        """Category with no expenses can be deleted."""
        resp = client.delete(f"/api/categories/{seed_category.id}")
        assert resp.status_code == 200

    def test_delete_nonexistent_returns_404(self, client, db):
        """Deleting non-existent category returns 404."""
        resp = client.delete("/api/categories/999")
        assert resp.status_code == 404

    def test_delete_category_with_expenses_returns_409(self, client, seed_category, db):
        """Cannot delete a category that has expenses."""
        from models.expense import Expense
        from datetime import date

        expense = Expense(
            amount=10.0,
            description="Test",
            date=date(2024, 1, 1),
            category_id=seed_category.id,
        )
        db.session.add(expense)
        db.session.commit()

        resp = client.delete(f"/api/categories/{seed_category.id}")
        assert resp.status_code == 409
        assert resp.get_json()["code"] == "HAS_DEPENDENCIES"