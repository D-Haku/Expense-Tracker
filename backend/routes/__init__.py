"""Flask route blueprints package."""

from routes.categories import categories_bp
from routes.expenses import expenses_bp

__all__ = ["categories_bp", "expenses_bp"]