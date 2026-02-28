"""Expense model — a single spending record tied to a category."""

from datetime import date, datetime, timezone

from app.extensions import db


class Expense(db.Model):
    """A single expense entry with amount, description, date, and category."""

    __tablename__ = "expenses"

    id: int = db.Column(db.Integer, primary_key=True)
    amount: float = db.Column(db.Float, nullable=False)
    description: str = db.Column(db.String(200), nullable=False)
    date: date = db.Column(db.Date, nullable=False)
    category_id: int = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=False
    )
    created_at: datetime = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    category = db.relationship("Category", back_populates="expenses", lazy="joined")

    def __repr__(self) -> str:
        return f"<Expense id={self.id} amount={self.amount} desc={self.description!r}>"