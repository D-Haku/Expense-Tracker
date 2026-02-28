# Expense Tracker

A personal expense tracking application built for the Better Software engineering assessment.

## Product Choice

An expense tracker was chosen because:
- **Well-bounded domain** — expenses, categories, and summaries have clear rules
- **Small enough to structure well** — no feature bloat, just clean CRUD + aggregation
- **Demonstrates real constraints** — amounts must be positive, dates valid, categories enforced

## Architecture

```
┌─────────────┐     HTTP/JSON      ┌─────────────┐     SQLAlchemy     ┌──────────┐
│   React UI  │  ◄──────────────►  │  Flask API  │  ◄──────────────►  │  SQLite  │
│ (TypeScript)│                    │  (Python)   │                    │          │
└─────────────┘                    └─────────────┘                    └──────────┘
```

### Backend (Python + Flask)
- **Flask Blueprints** for route organization (expenses, categories)
- **SQLAlchemy ORM** for database access — no raw SQL, migrations-friendly
- **Marshmallow schemas** for request validation and response serialization
- **Centralized error handling** — all errors return structured JSON with codes
- **Structured logging** — every request logged with method, path, status, duration

### Frontend (React + TypeScript)
- **TypeScript throughout** — catches type mismatches at compile time
- **Custom hooks** for data fetching — separates API logic from UI
- **Component boundaries** — form, list, and summary are independent components

### Database (SQLite)
- **SQLite chosen for zero-setup** — no external process needed, file-based
- **Foreign key constraints enforced** — categories must exist before referencing
- **SQLAlchemy makes switching trivial** — change one connection string to use PostgreSQL

## Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| SQLite over PostgreSQL | Zero setup, portable, sufficient for single-user app. SQLAlchemy abstracts the difference. |
| Marshmallow for validation | Separates validation logic from routes. Schemas are testable independently. |
| Flask Blueprints | Each resource gets its own module. Adding a new resource doesn't touch existing code. |
| TypeScript on frontend | Catches category ID mismatches, missing fields at build time rather than runtime. |
| No ORM lazy loading | All relationships use `joinedload` explicitly — no N+1 surprise queries. |
| Centralized error handler | Every error returns `{error, code, details}` — frontend never gets raw HTML errors. |

## Tradeoffs & Weaknesses

- **No authentication** — intentionally omitted to keep scope small. Would add Flask-JWT-Extended.
- **SQLite limitations** — no concurrent writes, but acceptable for single-user.
- **No pagination** — expenses list loads all records. Would add cursor-based pagination for scale.
- **No CI/CD** — tests run locally. Would add GitHub Actions.
- **Minimal UI styling** — functional CSS only. The focus is on structure, not polish.

## Running the Project

### Prerequisites
- Python 3.9+
- Node.js 18+

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
# API runs on http://localhost:5000
```

### Frontend
```bash
cd frontend
npm install
npm start
# UI runs on http://localhost:3000
```

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## Extension Approach

To extend this system:
1. **New resource** — add a model, schema, and blueprint. Register in `app/__init__.py`.
2. **New validation rule** — add to the Marshmallow schema. Existing routes don't change.
3. **Switch database** — change `SQLALCHEMY_DATABASE_URI` in config. No code changes.
4. **Add auth** — wrap routes with a decorator. Route logic stays untouched.

## AI Usage

AI (Claude) was used to accelerate development:
- **Scaffolding** — initial project structure and boilerplate
- **Code generation** — models, schemas, routes, React components
- **Test generation** — test cases for validation edge cases

All generated code was reviewed for:
- Correct validation rules (amounts > 0, dates not in future)
- Proper error handling (no silent failures)
- Consistent API response format
- No unnecessary dependencies