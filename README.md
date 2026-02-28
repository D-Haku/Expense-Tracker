# 💰 Expense Tracker

A small, well-structured expense tracking application built as an assessment for **Better Software**. Prioritizes **correctness, structure, and simplicity** over feature count.

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Backend  | Python 3 + Flask                  |
| Frontend | React 18 + TypeScript (strict)    |
| Database | SQLite via SQLAlchemy ORM         |
| Testing  | pytest (47 automated tests)       |

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS/Linux
pip install -r requirements.txt
python run.py                   # Starts on http://localhost:5001
```

### Frontend

```bash
cd frontend
npm install
npm start                       # Starts on http://localhost:3000
```

The backend seeds 6 default categories on first run: Food, Transport, Entertainment, Utilities, Shopping, Health.

## Project Structure

```
backend/
  app/               → Flask app factory + extensions
  models/            → SQLAlchemy models (Category, Expense)
  schemas/           → Marshmallow validation schemas
  routes/            → Flask Blueprints (expenses, categories)
  tests/             → 47 tests (routes, schemas, validation)
  config.py          → Configuration with env var overrides
  run.py             → Entry point

frontend/
  src/
    api/client.ts    → All HTTP calls isolated here
    components/      → ExpenseForm, ExpenseList, ExpenseSummary
    types.ts         → TypeScript interfaces for API data
    App.tsx          → Main app shell
```

## Key Technical Decisions

### 1. Backend is the authority
All validation happens server-side via Marshmallow schemas. Frontend validation is a UX convenience only — the backend enforces every constraint:
- `amount` must be > 0
- `description` must be 1–200 characters, non-empty
- `date` must be a valid ISO date, not in the future
- `category_id` must reference an existing category

### 2. No raw SQL
SQLAlchemy ORM exclusively. The database is swappable from SQLite to PostgreSQL by changing one config variable.

### 3. Structured error responses
Every error follows `{error: string, code: string, details?: object}`. No plain strings or HTML errors ever leave the API.

### 4. API calls isolated
Frontend components never call `fetch` directly. All HTTP is in `src/api/client.ts`, typed with TypeScript interfaces. This makes it trivial to swap HTTP libraries or add interceptors.

### 5. SQLite for simplicity
For a small dataset, SQLite is the right choice. No installation, no server process, zero config. The ORM abstraction means switching to PostgreSQL requires only a connection string change.

### 6. Port 5001 (not 5000)
macOS uses port 5000 for AirPlay Receiver. The backend runs on port 5001 to avoid conflicts.

## Testing

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

**47 tests** covering:
- **Route tests** — success paths, validation failures, 404s, dependency constraints
- **Schema tests** — every validation rule independently verified
- All tests use in-memory SQLite (`:memory:`) — no external dependencies

### Test coverage includes:
- Create/Read/Delete expenses and categories
- Validation: negative amounts, future dates, empty descriptions, long strings
- Referential integrity: can't delete a category with expenses
- Spending summary aggregation
- Schema serialization (dump-only fields like `id`, `created_at`)

## Tradeoffs and Known Limitations

| Decision | Tradeoff |
|----------|----------|
| No authentication | Out of scope — simplifies the system, focuses on data correctness |
| No pagination | Dataset is small by design; adding later requires only route changes |
| No update endpoint | DELETE + re-create is sufficient for this scope |
| SQLite | Not suitable for concurrent writes at scale, but perfect for assessment scope |
| react-scripts | Heavier than Vite, but zero-config and battle-tested |

## Extension Pattern

Adding a new resource (e.g., "budgets"):
1. Create `models/budget.py` with SQLAlchemy model
2. Create `schemas/budget.py` with Marshmallow schema
3. Create `routes/budget.py` with Flask Blueprint
4. Register blueprint in `app/__init__.py`
5. Add tests in `tests/test_budget.py`

No existing files need modification except `app/__init__.py` for blueprint registration.

## AI Usage

This project was built with AI assistance (Claude via Cline). AI was used for:
- **Code generation**: Models, schemas, routes, components, tests
- **Architecture guidance**: File structure, separation of concerns
- **Debugging**: Port conflicts, CORS issues, test failures

All generated code was reviewed against the constraints in `AGENTS.md`, which defines:
- Architecture rules (backend authority, no raw SQL, schema validation)
- Validation constraints (business rules enforced by Marshmallow)
- What NOT to do (no auth, no pagination, no WebSockets)
- Extension patterns for new resources

The `AGENTS.md` file serves as a guardrail — it constrains AI behavior to prevent over-engineering and ensure the system stays simple and correct.

## API Endpoints

| Method | Endpoint              | Description                    |
|--------|-----------------------|--------------------------------|
| GET    | `/api/categories`     | List all categories            |
| POST   | `/api/categories`     | Create a category              |
| DELETE | `/api/categories/:id` | Delete a category (if no expenses) |
| GET    | `/api/expenses`       | List all expenses              |
| POST   | `/api/expenses`       | Create an expense              |
| DELETE | `/api/expenses/:id`   | Delete an expense              |
| GET    | `/api/expenses/summary` | Spending by category         |