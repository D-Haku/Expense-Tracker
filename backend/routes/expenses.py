"""Expense routes — CRUD operations and summary aggregation."""

import logging
from typing import Tuple

from flask import Blueprint, Response, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import func

from app.extensions import db
from models.category import Category
from models.expense import Expense
from schemas.expense import ExpenseSchema

logger = logging.getLogger(__name__)

expenses_bp = Blueprint("expenses", __name__, url_prefix="/api/expenses")

expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)


def _serialize_expense(expense: Expense) -> dict:
    """Serialize an expense, including the category name."""
    data = expense_schema.dump(expense)
    data["category_name"] = expense.category.name if expense.category else None
    data["category_id"] = expense.category_id
    return data


@expenses_bp.route("", methods=["GET"])
def list_expenses() -> Tuple[Response, int]:
    """Return all expenses ordered by date descending."""
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    result = [_serialize_expense(e) for e in expenses]
    return jsonify(result), 200


@expenses_bp.route("", methods=["POST"])
def create_expense() -> Tuple[Response, int]:
    """Create a new expense.

    Request body: { "amount": 42.50, "description": "Lunch", "date": "2024-01-15", "category_id": 1 }
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Request body must be JSON.", "code": "INVALID_JSON"}), 400

    try:
        data = expense_schema.load(json_data)
    except ValidationError as err:
        logger.warning("Expense validation failed: %s", err.messages)
        return jsonify({
            "error": "Validation failed.",
            "code": "VALIDATION_ERROR",
            "details": err.messages,
        }), 400

    # Verify category exists
    category = db.session.get(Category, data["category_id"])
    if not category:
        return jsonify({
            "error": f"Category with id {data['category_id']} not found.",
            "code": "INVALID_CATEGORY",
        }), 400

    expense = Expense(
        amount=data["amount"],
        description=data["description"],
        date=data["date"],
        category_id=data["category_id"],
    )
    db.session.add(expense)
    db.session.commit()

    logger.info("Created expense id=%d amount=%.2f", expense.id, expense.amount)
    return jsonify(_serialize_expense(expense)), 201


@expenses_bp.route("/<int:expense_id>", methods=["GET"])
def get_expense(expense_id: int) -> Tuple[Response, int]:
    """Return a single expense by ID."""
    expense = db.session.get(Expense, expense_id)
    if not expense:
        return jsonify({"error": "Expense not found.", "code": "NOT_FOUND"}), 404
    return jsonify(_serialize_expense(expense)), 200


@expenses_bp.route("/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id: int) -> Tuple[Response, int]:
    """Update an existing expense."""
    expense = db.session.get(Expense, expense_id)
    if not expense:
        return jsonify({"error": "Expense not found.", "code": "NOT_FOUND"}), 404

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Request body must be JSON.", "code": "INVALID_JSON"}), 400

    try:
        data = expense_schema.load(json_data)
    except ValidationError as err:
        return jsonify({
            "error": "Validation failed.",
            "code": "VALIDATION_ERROR",
            "details": err.messages,
        }), 400

    # Verify category exists
    category = db.session.get(Category, data["category_id"])
    if not category:
        return jsonify({
            "error": f"Category with id {data['category_id']} not found.",
            "code": "INVALID_CATEGORY",
        }), 400

    expense.amount = data["amount"]
    expense.description = data["description"]
    expense.date = data["date"]
    expense.category_id = data["category_id"]
    db.session.commit()

    logger.info("Updated expense id=%d", expense.id)
    return jsonify(_serialize_expense(expense)), 200


@expenses_bp.route("/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id: int) -> Tuple[Response, int]:
    """Delete an expense by ID."""
    expense = db.session.get(Expense, expense_id)
    if not expense:
        return jsonify({"error": "Expense not found.", "code": "NOT_FOUND"}), 404

    db.session.delete(expense)
    db.session.commit()
    logger.info("Deleted expense id=%d", expense_id)
    return jsonify({"message": "Expense deleted."}), 200


@expenses_bp.route("/summary", methods=["GET"])
def expense_summary() -> Tuple[Response, int]:
    """Return spending summary grouped by category.

    Returns: [{ "category": "Food", "total": 150.00, "count": 3 }, ...]
    """
    results = (
        db.session.query(
            Category.name,
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count"),
        )
        .join(Expense, Expense.category_id == Category.id)
        .group_by(Category.name)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    summary = [
        {"category": name, "total": round(total, 2), "count": count}
        for name, total, count in results
    ]
    return jsonify(summary), 200