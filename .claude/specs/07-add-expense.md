# Spec: Add Expense

## Overview

- Step 07 lets a logged-in user submit a new expense through a dedicated form page at `/expenses/add`.
- The route already exists as a GET placeholder; this step upgrades it to a full GET + POST handler.
- Validated data is inserted into the `expenses` table and the user is redirected back to the profile page on success.
- A reusable `insert_expense()` query helper is added to `database/queries.py`.
- An "Add Expense" button is added to `profile.html` and a nav link is added to `base.html` so users can navigate to the form.

## Depends on

- Step 01 — Database setup (`expenses` table exists with all required columns)
- Step 03 — Login / Logout (`session["user_id"]` is set and checked)
- Step 04 / 05 — Profile page exists and is the natural redirect target after saving

## Routes

- `GET /expenses/add` — render the add-expense form — logged-in only
- `POST /expenses/add` — validate and insert the new expense — logged-in only

## Database changes

- No database changes.
- The `expenses` table already has all required columns: `id`, `user_id`, `amount`, `category`, `date`, `description`, `created_at`.

## Templates

- Create: `templates/add_expense.html`
  - extends `base.html`
  - form with `method="POST"` and the action set via `url_for('add_expense')`
  - Fields:
    - `amount` — number input, `step="0.01"`, `min="0.01"`, required
    - `category` — `<select>` with exactly 7 fixed options: Food, Transport, Bills, Health, Entertainment, Shopping, Other
    - `date` — `<input type="date">`, required; the route passes today's date (server local date) to the template as the default on GET, and the submitted value is re-shown after a failed submission
    - `description` — text input, optional, `maxlength="200"`
  - Submit button labelled "Save Expense" and a cancel link back to the profile page via `url_for('profile')`
  - Block that displays flashed messages (validation errors are flashed with the category "error"), re-populating previously submitted values on failure; the selected category is kept selected
- Modify: `templates/profile.html`
  - Add an "Add Expense" button/link pointing to the add-expense route, near the transaction table heading
- Modify: `templates/base.html`
  - Add an "Add Expense" link in the navbar visible only when `session.user_id` is set

## Files to change

- `app.py` — replace the GET-only placeholder at `/expenses/add` with a GET + POST handler:
  - GET: render `add_expense.html`; redirect to `/login` if not authenticated
  - POST: read form fields, validate, call `insert_expense()`, redirect to `url_for("profile")` on success
- `database/queries.py` — add `insert_expense(user_id, amount, category, date, description)`; it commits, closes the connection before returning, and returns the new expense's id
- `templates/profile.html` — add the "Add Expense" button
- `templates/base.html` — add the "Add Expense" navbar link for logged-in users

## Files to create

- `templates/add_expense.html`
- `tests/test_add_expense.py`

## New dependencies

- None

## Rules for implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`.
- Parameterised queries only — never string-format values into SQL.
- `PRAGMA foreign_keys = ON` must be enabled on every connection (already handled in `get_db()`).
- Unauthenticated access to both GET and POST `/expenses/add` must redirect to `/login`.
- Validation rules for POST:
  1. `amount`: required; must be a finite float greater than 0 and at most 9999999.99; parse with `float()`, catch `ValueError`; reject `nan` and infinity (e.g. the strings "inf" and "nan"); round to 2 decimal places before saving
  2. `category`: required; must be one of the 7 fixed categories; reject anything else
  3. `date`: required; must be a valid `YYYY-MM-DD` date; parse with `datetime.strptime`; save the parsed date re-formatted as `YYYY-MM-DD` (so "2026-3-5" is stored as "2026-03-05"); future dates are allowed
  4. `description`: optional; strip whitespace; must be at most 200 characters (rejected with an error otherwise); store `None` if blank
- On any validation error, re-render the form with the error message and previously submitted values pre-filled.
- After a successful insert, flash "Expense added successfully." with the category "success" and redirect to `url_for("profile")` — do NOT render the form again. The profile page displays flashed messages (added in Step 06).
- Filter parameters are not carried through the redirect; the profile page opens unfiltered.
- Currency must always display as ₹ — never £ or $.
- Use CSS variables — never hardcode hex values.
- No inline styles.
- All templates extend `base.html`.
- Use `url_for()` for every internal link — never hardcode paths.

## Tests to write

- File: `tests/test_add_expense.py`
- Tests run against a temporary database seeded with the demo user; authenticated tests log in as the demo user through the test client (or set the session `user_id`), never touching the real `spendly.db`.
- Unit tests:

| Function | Input | Expected output |
|---|---|---|
| `insert_expense` | Valid `user_id`, `amount=50.0`, `category="Food"`, `date="2026-03-20"`, `description="Lunch"` | Row inserted; querying the DB returns the new row |
| `insert_expense` | `description=None` | Row inserted with `description` stored as NULL |
| `insert_expense` | Valid input | Returns the new expense's integer id, which matches the inserted row |
| `insert_expense` | `user_id` that does not exist | Foreign key constraint failure raised |

- Route tests:
  - `GET /expenses/add` unauthenticated → redirects to `/login` (302)
  - `GET /expenses/add` authenticated → returns 200; response contains the category `<select>` with all 7 options; response contains a form with method POST
  - `POST /expenses/add` unauthenticated → redirects to `/login` (302)
  - `POST /expenses/add` authenticated, valid data (`amount=50.0`, `category=Food`, `date=2026-03-20`, `description=Lunch`) → redirects to `/profile` (302); new expense row exists in the DB for the test user
  - `POST /expenses/add` authenticated, missing amount → returns 200; response contains an error message
  - `POST /expenses/add` authenticated, `amount` = 0 → returns 200; response contains an error message
  - `POST /expenses/add` authenticated, non-numeric amount → returns 200; response contains an error message
  - `POST /expenses/add` authenticated, invalid category (not in fixed list) → returns 200; response contains an error message
  - `POST /expenses/add` authenticated, invalid date string → returns 200; response contains an error message
  - `POST /expenses/add` authenticated, no description (optional field) → redirects to `/profile` (302); row inserted with `description` = NULL
  - `POST /expenses/add` authenticated, `amount=inf` or `amount=nan` → returns 200; response contains an error message; no row inserted
  - `POST /expenses/add` authenticated, `date=2026-3-5` → redirects to `/profile` (302); the stored date is `2026-03-05`
  - `POST /expenses/add` authenticated, description longer than 200 characters → returns 200; response contains an error message; no row inserted
  - `POST /expenses/add` authenticated, invalid data → the submitted `amount`, `category`, `date` and `description` are shown again in the re-rendered form
  - `GET /profile` authenticated → response contains a link to `/expenses/add` (the "Add Expense" button)
  - Any page rendered while authenticated contains the "Add Expense" navbar link; any page rendered while logged out does not
  - After a successful add, following the redirect shows "Expense added successfully." on the profile page

## Definition of done

- [ ] Visiting `/expenses/add` while logged out redirects to `/login`
- [ ] Visiting `/expenses/add` while logged in shows a form with amount, category, date, and description fields
- [ ] The category dropdown contains exactly: Food, Transport, Bills, Health, Entertainment, Shopping, Other
- [ ] Submitting a valid expense redirects to `/profile` and the new expense appears in the transaction list
- [ ] Submitting with a missing or zero amount re-renders the form with an error and previously entered values retained
- [ ] Submitting with an invalid category re-renders the form with an error
- [ ] Submitting with an invalid date re-renders the form with an error
- [ ] Submitting without a description saves the expense with no error
- [ ] The "Add Expense" button on the profile page navigates to `/expenses/add`
- [ ] Navbar shows the "Add Expense" link when logged in
- [ ] Submitting an infinite or non-numeric amount is rejected and nothing is saved
- [ ] A date entered without leading zeros is saved in `YYYY-MM-DD` form
- [ ] A description longer than 200 characters is rejected on the server
- [ ] The date field defaults to today's date on a fresh form
- [ ] After a successful add, the profile page shows "Expense added successfully."
- [ ] Tests pass against a temporary database
