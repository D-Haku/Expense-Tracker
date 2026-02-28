"""Application configuration.

Single config module with environment variable overrides.
No environment-specific config files — keeps things simple.
"""

import os


class Config:
    """Base configuration."""

    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:///expenses.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    TESTING: bool = False


class TestConfig(Config):
    """Test configuration — uses in-memory SQLite."""

    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    TESTING: bool = True