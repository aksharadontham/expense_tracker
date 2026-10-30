# Spec: Database Setup

## 1. Overview

This step replaces the stub in `database/db.py` with a working SQLite implementation. It defines the connection helper, creates the `users` and `expenses` tables, and seeds a demo account with sample expenses.

This is the foundational step of Spendly. Authentication (registration and login), the profile page, and all expense tracking features (add, edit, delete, filter, summaries) read from and write to this database, so none of them can be built until it exists.

## 2. Depends on

Nothing. This is the first step and has no prerequisites.

## 3. Routes

No new routes.

The existing placeholder routes in `app.py` remain unchanged.

## 4. Database Schema

### Table A: `users`

| Column | SQLite Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | NOT NULL, UNIQUE |
| password_hash | TEXT | NOT NULL |
| created_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP (UTC, stored as `YYYY-MM-DD HH:MM:SS`) |

### Table B: `expenses`

| Column | SQLite Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| user_id | INTEGER | NOT NULL, FOREIGN KEY → users(id), no cascade (deleting a user who has expenses is rejected) |
| amount | REAL | NOT NULL; must be greater than 0 (validated by the application, not by a CHECK constraint) |
| category | TEXT | NOT NULL; must be one of the 7 fixed categories (validated by the application, not by a CHECK constraint) |
| date | TEXT | NOT NULL; must be in YYYY-MM-DD format (validated by the application, not by a CHECK constraint) |
| description | TEXT | Nullable |
| created_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP (UTC, stored as `YYYY-MM-DD HH:MM:SS`) |

## 5. Functions to Implement (database/db.py)

| Function | Responsibility |
|---|---|
| `get_db()` | Opens `spendly.db` in the project root; sets `row_factory = sqlite3.Row`; enables `PRAGMA foreign_keys = ON`; returns the connection. The project root is the directory that contains `app.py`, resolved from the location of `database/db.py` and never from the current working directory |
| `init_db()` | Creates both tables using `CREATE TABLE IF NOT EXISTS`; safe to call multiple times |
| `seed_db()` | Checks whether the `users` table already has rows and returns early if so; otherwise inserts the demo user and 8 sample expenses (see below) |

**Seed data for `seed_db()`:**

| Item | Details |
|---|---|
| Demo user name | Demo User |
| Demo user email | demo@spendly.com |
| Demo user password | demo123, hashed via werkzeug |
| Sample expenses | 8 expenses linked to the demo user, exactly as listed below |
| Category coverage | All 7 categories appear at least once; Food appears twice to reach 8 |
| Date range | Dates spread across the current month, in YYYY-MM-DD format, using the day-of-month values listed below |
| Total amount | 346.24 |
| Top category by total | Bills (120.00) |

**The 8 seed expenses:**

| Day of current month | Category | Amount | Description |
|---|---|---|---|
| 1 | Bills | 120.00 | Electricity bill |
| 3 | Food | 38.50 | Groceries |
| 5 | Transport | 25.00 | Metro card top-up |
| 8 | Health | 35.00 | Pharmacy |
| 10 | Entertainment | 30.00 | Movie night |
| 12 | Food | 22.75 | Lunch with team |
| 15 | Shopping | 49.99 | Headphones |
| 18 | Other | 25.00 | Gift |

- Each date is built from the current year and month plus the day value above, so every date is unique and in the current month.
- Category totals: Bills 120.00, Food 61.25, Shopping 49.99, Health 35.00, Entertainment 30.00, Transport 25.00, Other 25.00.

## 6. Changes to app.py

- Import `get_db`, `init_db`, and `seed_db` from `database.db`.
- Call `init_db()` and `seed_db()` inside `app.app_context()` on startup.
- The database must be ready before any route is served.

## 7. Files to Change

- `database/db.py`
- `app.py`

## 8. Files to Create

None.

## 9. Dependencies

- No new pip packages.
- Use `sqlite3` (standard library).
- Use `werkzeug.security` (already installed and listed in `requirements.txt`).

## 10. Categories (Fixed List)

These are the only valid values for `expenses.category`:

- Food
- Transport
- Bills
- Health
- Entertainment
- Shopping
- Other

## 11. Rules for Implementation

- No ORM and no SQLAlchemy; use raw `sqlite3` only.
- Parameterized queries only; never use string formatting to build SQL.
- `PRAGMA foreign_keys = ON` must be set on every connection.
- Store `amount` as REAL, not INTEGER.
- Hash passwords with `generate_password_hash` from `werkzeug.security`.
- `seed_db()` must be idempotent (safe to call multiple times).
- Dates must always be stored as YYYY-MM-DD.
- The database does not use CHECK constraints for category, date format or amount; the application layer (later steps) must validate that category is one of the 7 fixed values, the date is a valid YYYY-MM-DD string, and the amount is greater than 0 before inserting.
- Timestamps in `created_at` use the database default (UTC, `YYYY-MM-DD HH:MM:SS`); application code must not write its own format into those columns.
- The database path is resolved from the location of `database/db.py`, so the file is created in the same place however the app is launched.

## 12. Expected Behavior

**Function behavior:**

| Function | When called correctly |
|---|---|
| `get_db()` | Returns an open connection to `spendly.db` in the project root; rows are accessible by column name; foreign keys are enforced |
| `init_db()` | Creates `users` and `expenses` if they do not exist; leaves existing tables and data untouched on repeat calls |
| `seed_db()` | On an empty `users` table, inserts the demo user and 8 sample expenses; on a populated table, does nothing |

**Database-level constraints that must be enforced:**

| Constraint | Enforced by |
|---|---|
| Unique email per user | UNIQUE on `users.email` |
| Required fields present | NOT NULL on all required columns |
| Expense belongs to a real user | FOREIGN KEY on `expenses.user_id` with foreign keys enabled |
| User with expenses cannot be deleted | FOREIGN KEY with no cascade (default restrict behavior) |
| Auto-generated IDs | PRIMARY KEY AUTOINCREMENT on both tables |
| Automatic timestamps | DEFAULT CURRENT_TIMESTAMP on both `created_at` columns |

## 13. Error Handling Expectations

| Scenario | Expected result |
|---|---|
| Insert a user with a duplicate email | UNIQUE constraint failure raised |
| Insert an expense with a `user_id` that does not exist | Foreign key constraint failure raised |
| Delete a user who still has expenses | Foreign key constraint failure raised; no expenses are removed |
| Invalid or malformed query | Error is raised and not swallowed, with a clear message for debugging |

## 14. Definition of Done

- [ ] Database file is created on app startup
- [ ] Both tables exist with the correct schema and constraints
- [ ] Demo user exists with a hashed password
- [ ] 8 sample expenses exist across all 7 categories
- [ ] Seed expenses match the listed table: total 346.24, top category Bills, all dates in the current month
- [ ] `spendly.db` is created in the project root regardless of the directory the app is started from
- [ ] No duplicate seed data on repeated runs
- [ ] App starts without errors
- [ ] Foreign key enforcement works
- [ ] All queries use parameterized SQL
