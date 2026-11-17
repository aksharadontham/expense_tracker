# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
pip install -r requirements.txt          # flask, werkzeug, pytest, pytest-flask
python app.py                            # dev server on http://localhost:5001 (debug=True)
python -m pytest tests -q                # whole suite
python -m pytest tests/test_delete_expense.py::test_name   # single test
```

Demo login (seeded on first start): `demo@spendly.com` / `demo123`. There is no linter or build step.

## Architecture

Spendly is a small Flask + raw `sqlite3` expense tracker (no ORM, no blueprints). Server-rendered Jinja templates, one stylesheet per page group (`static/css/style.css`, plus `profile.css`).

- `app.py` holds every route, the form validation (`_validate_expense`) and the profile date-preset logic. It calls `init_db()` and `seed_db()` **at import time**.
- `database/db.py`: `DB_PATH` (`spendly.db` in the project root), `get_db()`, schema, seeding, and the user helpers `create_user` / `get_user_by_email`.
- `database/queries.py`: expense and profile helpers (no Flask imports). Every helper opens its own connection via `get_db()` and closes it in `finally`. All of them scope by `user_id`; the expense update and delete helpers filter on `id AND user_id` and return `rowcount`, which routes turn into 404.
- Profile page (`/profile`) takes optional `date_from` and `date_to`. A filter applies only when **both** dates are valid; the stats, the transaction list and the category breakdown all use the same range. The list is capped at 10 rows.
- Auth is session-based (`session["user_id"]`, `session["user_name"]`). Protected routes redirect to `/login`; the profile and add routes also clear a stale session whose user no longer exists. Delete is POST-only (`/expenses/<id>/delete`).
- Templates extend `base.html`. Errors and successes use `flash()` with categories `"error"` / `"success"`. Use CSS variables from `style.css`, never hardcoded hex values or inline `style=` (tests scan for this).
- Currency is shown as ₹ with two decimals; dates are stored as `YYYY-MM-DD` and shown through the `display_date` filter.

## Testing conventions

Every test file must point the database at a temporary file **before** `import app`:

```python
import database.db as db
db.DB_PATH = Path(tempfile.mkdtemp()) / "import.db"
import app as app_module
```

and then monkeypatch `db.DB_PATH` per test (autouse fixture calling `init_db()` and `seed_db()`). Otherwise importing `app` seeds the real `spendly.db`. Seed data is 8 expenses for the demo user totalling ₹346.24 (top category Bills); several tests assert these exact values.

## Spec-driven workflow

Work is organised as numbered steps (01–09): spec in `.claude/specs/NN-name.md`, plan in `.claude/plans/NN-name-plan.md` (git-ignored), implementation review in `Review/`. The `/code-review-feature <spec-name>` command (`.claude/commands/`) runs security and quality reviewers in parallel over `git diff` and refers to subagents (`spendly-security-reviewer`, `spendly-quality-reviewer`) that are not defined in this repo.

## Known gaps

`app.secret_key` is hardcoded, `debug=True` is on, and there is no CSRF protection. `spendly.db` is git-ignored on the remote's `.gitignore` only after the latest push; keep it out of commits.
