"""Flask application factory — creates and configures the app."""

import logging
import time
from typing import Tuple

from flask import Flask, Response, jsonify, request
from werkzeug.exceptions import HTTPException

from app.extensions import db, ma


def create_app(config_object: str = "config.Config") -> Flask:
    """Create and configure the Flask application.

    Args:
        config_object: Dotted path to the config class.

    Returns:
        Configured Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)

    # Enable CORS
    from flask_cors import CORS
    CORS(app)

    # Configure logging
    _setup_logging(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Request logging middleware
    _register_request_hooks(app)

    # Create tables
    with app.app_context():
        # Import models so SQLAlchemy knows about them
        from models.category import Category  # noqa: F401
        from models.expense import Expense  # noqa: F401
        db.create_all()

        # Seed default categories if empty (skip in test mode)
        if not app.config.get("TESTING"):
            _seed_default_categories()

    return app


def _setup_logging(app: Flask) -> None:
    """Configure structured logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    app.logger.setLevel(logging.INFO)


def _register_blueprints(app: Flask) -> None:
    """Register all route blueprints."""
    from routes.categories import categories_bp
    from routes.expenses import expenses_bp

    app.register_blueprint(categories_bp)
    app.register_blueprint(expenses_bp)


def _register_error_handlers(app: Flask) -> None:
    """Register centralized error handlers.

    Every error returns structured JSON: {error, code, details?}
    """

    @app.errorhandler(HTTPException)
    def handle_http_error(exc: HTTPException) -> Tuple[Response, int]:
        """Handle all HTTP exceptions as structured JSON."""
        return jsonify({
            "error": exc.description,
            "code": exc.name.upper().replace(" ", "_"),
        }), exc.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(exc: Exception) -> Tuple[Response, int]:
        """Handle unexpected exceptions — log and return 500."""
        app.logger.exception("Unhandled exception: %s", exc)
        return jsonify({
            "error": "An unexpected error occurred.",
            "code": "INTERNAL_ERROR",
        }), 500


def _register_request_hooks(app: Flask) -> None:
    """Log every request with method, path, status, and duration."""

    @app.before_request
    def start_timer() -> None:
        request._start_time = time.time()

    @app.after_request
    def log_request(response: Response) -> Response:
        duration_ms = (time.time() - getattr(request, "_start_time", time.time())) * 1000
        app.logger.info(
            "%s %s → %d (%.1fms)",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response


def _seed_default_categories() -> None:
    """Seed default categories if the table is empty."""
    from models.category import Category

    if Category.query.count() == 0:
        defaults = ["Food", "Transport", "Entertainment", "Utilities", "Shopping", "Health"]
        for name in defaults:
            db.session.add(Category(name=name))
        db.session.commit()
        logging.getLogger(__name__).info("Seeded %d default categories.", len(defaults))