# AI Agent Guidance

This file constrains AI agent behavior when working on this codebase.

## Architecture Rules

1. **Backend is the authority** — all validation happens server-side. Frontend validation is a UX convenience only.
2. **No raw SQL** — use SQLAlchemy ORM exclusively. This keeps the database swappable.
3. **Every route uses a schema** — requests are deserialized through Marshmallow. No `request.json` access without validation.
4. **Errors are structured** — every error response follows `{error: string, code: string, details?: object}`. Never return plain strings or HTML errors.
5. **No silent failures** — every exception is caught, logged, and returned as a structured error.

## Code Standards

### Python (Backend)
- Type hints on all function signatures
- Docstrings on all public functions
- No wildcard imports (`from x import *`)
- Models in `models/`, schemas in `schemas/`, routes in `routes/`
- Tests mirror source structure: `tests/test_<module>.py`

### TypeScript (Frontend)
- Strict mode enabled — no `any` types unless explicitly justified
- All API responses typed with interfaces
- Components are functional with hooks — no class components
- API calls isolated in `src/api/` — components never call `fetch` directly

## Validation Constraints

These business rules must be enforced by the backend (Marshmallow schemas):
- `amount` must be a positive number (> 0)
- `description` must be a non-empty string, max 200 characters
- `date` must be a valid ISO date, not in the future
- `category_id` must reference an existing category (foreign key)
- Category `name` must be unique and non-empty, max 50 characters

## What NOT To Do

- Do NOT add authentication — out of scope for this assessment
- Do NOT add pagination — the dataset is small by design
- Do NOT use an ORM migration tool — the schema is stable
- Do NOT add WebSocket or real-time features — unnecessary complexity
- Do NOT introduce environment-specific config files — single config with env var overrides is sufficient
- Do NOT use `print()` for logging — use Python's `logging` module

## Testing Requirements

- Every route must have at least: one success test, one validation failure test
- Schema validation tests are independent of routes
- Use Flask's test client — no HTTP server needed for tests
- Test database is in-memory SQLite (`:memory:`)

## Extension Pattern

When adding a new resource (e.g., "budgets"):
1. Create `models/budget.py` with SQLAlchemy model
2. Create `schemas/budget.py` with Marshmallow schema
3. Create `routes/budget.py` with Flask Blueprint
4. Register blueprint in `app/__init__.py`
5. Add tests in `tests/test_budget.py`
6. No existing files should need modification except `app/__init__.py` for registration