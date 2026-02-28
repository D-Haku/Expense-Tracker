"""Category model — groups expenses into user-defined buckets."""

from datetime import datetime, timezone

from app.extensions import db


class Category(db.Model):
    """A spending category (e.g., Food, Transport, Entertainment)."""

    __tablename__ = "categories"

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(50), unique=True, nullable=False)
    created_at: datetime = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    expenses = db.relationship("Expense", back_populates="category", lazy="select")

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"