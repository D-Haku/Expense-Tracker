"""Category routes — CRUD operations for spending categories."""

import logging
from typing import Tuple

from flask import Blueprint, Response, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from models.category import Category
from schemas.category import CategorySchema

logger = logging.getLogger(__name__)

categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)


@categories_bp.route("", methods=["GET"])
def list_categories() -> Tuple[Response, int]:
    """Return all categories ordered by name."""
    categories = Category.query.order_by(Category.name).all()
    return jsonify(categories_schema.dump(categories)), 200


@categories_bp.route("", methods=["POST"])
def create_category() -> Tuple[Response, int]:
    """Create a new category.

    Request body: { "name": "Food" }
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Request body must be JSON.", "code": "INVALID_JSON"}), 400

    try:
        data = category_schema.load(json_data)
    except ValidationError as err:
        logger.warning("Category validation failed: %s", err.messages)
        return jsonify({
            "error": "Validation failed.",
            "code": "VALIDATION_ERROR",
            "details": err.messages,
        }), 400

    category = Category(name=data["name"])

    try:
        db.session.add(category)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        logger.warning("Duplicate category name: %s", data["name"])
        return jsonify({
            "error": f"Category '{data['name']}' already exists.",
            "code": "DUPLICATE_CATEGORY",
        }), 409

    logger.info("Created category id=%d name=%r", category.id, category.name)
    return jsonify(category_schema.dump(category)), 201


@categories_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id: int) -> Tuple[Response, int]:
    """Return a single category by ID."""
    category = db.session.get(Category, category_id)
    if not category:
        return jsonify({"error": "Category not found.", "code": "NOT_FOUND"}), 404
    return jsonify(category_schema.dump(category)), 200


@categories_bp.route("/<int:category_id>", methods=["PUT"])
def update_category(category_id: int) -> Tuple[Response, int]:
    """Update a category's name."""
    category = db.session.get(Category, category_id)
    if not category:
        return jsonify({"error": "Category not found.", "code": "NOT_FOUND"}), 404

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Request body must be JSON.", "code": "INVALID_JSON"}), 400

    try:
        data = category_schema.load(json_data)
    except ValidationError as err:
        return jsonify({
            "error": "Validation failed.",
            "code": "VALIDATION_ERROR",
            "details": err.messages,
        }), 400

    category.name = data["name"]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": f"Category '{data['name']}' already exists.",
            "code": "DUPLICATE_CATEGORY",
        }), 409

    logger.info("Updated category id=%d name=%r", category.id, category.name)
    return jsonify(category_schema.dump(category)), 200


@categories_bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id: int) -> Tuple[Response, int]:
    """Delete a category. Fails if expenses reference it."""
    category = db.session.get(Category, category_id)
    if not category:
        return jsonify({"error": "Category not found.", "code": "NOT_FOUND"}), 404

    if category.expenses:
        return jsonify({
            "error": "Cannot delete category with existing expenses.",
            "code": "HAS_DEPENDENCIES",
        }), 409

    db.session.delete(category)
    db.session.commit()
    logger.info("Deleted category id=%d", category_id)
    return jsonify({"message": "Category deleted."}), 200