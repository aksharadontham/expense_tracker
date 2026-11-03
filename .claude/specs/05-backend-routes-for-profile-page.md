# Spec: Backend Routes for Profile Page

## Overview

- Step 05 replaces all hardcoded data in the `/profile` route with live queries against the SQLite database.
- The profile page currently renders a static demo user, fixed summary stats, a hand-typed transaction list, and a hardcoded category breakdown.
- This step wires those four sections to real data so every logged-in user sees their own expenses.
- Three parallel subagents handle the three independent data concerns — transaction history, summary stats, and category breakdown — before being integrated into the single `/profile` route.

## Depends on

- Step 01 — Database setup (tables and `get_db()` exist; the seed user has the 8 listed expenses totalling 346.24 with Bills as the top category; `created_at` is stored as UTC `YYYY-MM-DD HH:MM:SS`)
- Step 02 — Registration (users are stored in the database)
- Step 03 — Login / Logout (`session["user_id"]` is set on login)
- Step 04 — Profile page static UI (template already renders all four sections)

## Routes

- No new routes.
- The existing `GET /profile` route is modified in place.

## Database changes

- No database changes.
- The `users` and `expenses` tables already have all required columns: `user_id`, `amount`, `category`, `date`, `description`, `created_at`.

## Templates

- Modify: `templates/profile.html`
  - Amounts must be rendered with the ₹ symbol (Indian Rupee) — never £ or $.
  - All four dynamic sections are already present in the template — no structural changes needed; only the Jinja variables they consume are now real.

## Files to change

- `app.py` — replace hardcoded data in the `profile()` view with calls to the new query helpers in `database/queries.py`; if `get_user_by_id` returns `None` (a stale session pointing at a user that no longer exists), clear the session and redirect to `/login`
- `templates/profile.html` — confirm the ₹ symbol is used for all currency display

## Files to create

- `database/queries.py` — pure query helpers with no Flask imports; one function per data concern:
  - `get_user_by_id(user_id)`
    - returns a dict with `name`, `email`, `member_since`
  - `get_summary_stats(user_id)`
    - returns a dict with `total_spent`, `transaction_count`, `top_category`
  - `get_recent_transactions(user_id, limit=10)`
    - returns a list of dicts, each with `date`, `description`, `category`, `amount`
    - ordered newest-first by date, then by `id` descending for expenses on the same date
    - only the latest `limit` rows are returned (default 10); the transaction count in the summary stats still covers every expense
  - `get_category_breakdown(user_id)`
    - returns a list of dicts, each with `name`, `amount`, `pct`
    - `pct` is the percentage of total, rounded to the nearest int
    - ordered by amount descending; categories with equal amounts are ordered by name ascending (so Other comes before Transport for the seed user)
- `tests/test_backend_connection.py` — unit and route tests (see Tests to write)

## New dependencies

- None

## Rules for implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`.
- Parameterised queries only — never string-format values into SQL.
- `PRAGMA foreign_keys = ON` must be enabled on every connection (already handled in `get_db()`).
- Currency must always display as ₹ — never £ or $.
- `member_since` must be derived from `users.created_at` (UTC, `YYYY-MM-DD HH:MM:SS`) and formatted as "Month YYYY" (e.g. "January 2026").
- `get_summary_stats` and `get_category_breakdown` cover all of the user's expenses, not only the transactions shown in the table.
- `top_category` is the category with the highest total; on a tie, the category name that sorts first alphabetically wins.
- Amounts and totals are rounded to 2 decimal places before being returned, and shown on the page with two decimals (e.g. ₹346.24, ₹0.00).
- Only calculate `pct` when the total is greater than 0; with a zero total return an empty breakdown.
- The profile route must handle a missing user: if `get_user_by_id` returns `None`, clear the session and redirect to `/login`.
- `pct` values in the category breakdown must sum to 100; use integer rounding and adjust the largest category to absorb any rounding remainder.
- If a user has no expenses, all helpers must return zeros and empty lists — never raise exceptions.
- All helpers in `database/queries.py` must call `get_db()` internally and close the connection before returning.
- Use CSS variables — never hardcode hex values.
- No inline styles.
- All templates extend `base.html`.

## Tests to write

- File: `tests/test_backend_connection.py`
- Tests must run against a temporary database, never the real `spendly.db`; a "user with no expenses" is created in the test with `create_user`.
- Unit tests:

| Function | Input | Expected output |
|---|---|---|
| `get_user_by_id` | Valid `user_id` | Dict with correct `name`, `email`, `member_since` |
| `get_user_by_id` | Non-existent id | `None` |
| `get_summary_stats` | `user_id` with expenses | Correct `total_spent`, `transaction_count`, `top_category` |
| `get_summary_stats` | `user_id` with no expenses | `{"total_spent": 0, "transaction_count": 0, "top_category": "—"}` |
| `get_recent_transactions` | `user_id` with expenses | List ordered newest-first; each item has `date`, `description`, `category`, `amount` |
| `get_recent_transactions` | `user_id` with no expenses | Empty list |
| `get_category_breakdown` | `user_id` with expenses | List ordered by amount descending; `pct` values are integers summing to 100 |
| `get_category_breakdown` | `user_id` with no expenses | Empty list |

- Route tests:
  - `GET /profile` unauthenticated → redirects to `/login` (302)
  - `GET /profile` with a session `user_id` that matches no user → clears the session and redirects to `/login` (302)
  - `GET /profile` authenticated as the seed user:
    - returns 200
    - response contains "Demo User"
    - response contains "demo@spendly.com"
    - response contains the ₹ symbol
    - `total_spent` matches the sum of all seed expenses (346.24)
    - `transaction_count` is 8
    - `top_category` is "Bills" (highest single-category total)
    - transaction list appears in newest-first order (first row is the Other / Gift expense, last row is the Bills / Electricity bill expense)
    - category breakdown contains all 7 categories, with percentages Bills 35, Food 18, Shopping 14, Health 10, Entertainment 9, Other 7, Transport 7 (in that order)

## Definition of done

- [ ] Logging in as `demo@spendly.com` / `demo123` shows "Demo User" and "demo@spendly.com" on the profile page — not the hardcoded strings
- [ ] Total spent displayed on the profile page equals ₹346.24
- [ ] Transaction count displayed is 8
- [ ] Top category displayed is "Bills"
- [ ] Transaction list shows 8 rows ordered newest date first
- [ ] Category breakdown shows 7 categories with percentages that add up to 100%
- [ ] All amounts on the page display the ₹ symbol
- [ ] Registering a brand-new user and visiting `/profile` shows ₹0.00 total spent, 0 transactions, and an empty category breakdown — no errors
- [ ] The first row of the transaction list is the newest expense and same-date expenses are ordered by id, newest first
- [ ] A session pointing at a non-existent user is cleared and redirected to `/login` instead of causing an error
- [ ] Tests run against a temporary database and leave `spendly.db` untouched
