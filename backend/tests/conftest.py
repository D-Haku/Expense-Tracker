"""Shared test fixtures — app, client, and database setup."""

import pytest

from app import create_app
from app.extensions import db as _db
from models.category import Category


@pytest.fixture(scope="function")
def app():
    """Create a test app with in-memory SQLite."""
    app = create_app("config.TestConfig")
    yield app


@pytest.fixture(scope="function")
def client(app):
    """Flask test client — no HTTP server needed."""
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    """Provide a clean database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture()
def seed_category(db):
    """Create a default 'Food' category for tests that need one."""
    category = Category(name="Food")
    db.session.add(category)
    db.session.commit()
    return category