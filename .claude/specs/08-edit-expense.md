# Spec: Edit Expense

## Overview

- Step 08 lets a logged-in user edit any of their own expenses via a pre-populated form at `/expenses/<id>/edit`.
- The GET handler loads the existing expense from the database and renders the form with its current values.
- The POST handler validates the submission and updates the row in place.
- Ownership is enforced: a user can only edit expenses that belong to them.
- Two new query helpers are added to `database/queries.py`: `get_expense_by_id` and `update_expense`.
- The transactions table in `profile.html` gains an "Edit" action link per row, which requires `get_recent_transactions` to also return the expense id.

## Depends on

- Step 01 — Database setup (`expenses` table exists with all required columns)
- Step 03 — Login / Logout (`session["user_id"]` is set and enforced)
- Step 05 — Profile page renders transactions (the edit link lives there)
- Step 07 — Add Expense (establishes the form pattern, the validation rules and the shared category list this step follows; the profile page flash block comes from Step 06)

## Routes

- `GET /expenses/<int:id>/edit` — render the edit form pre-populated with existing expense values — logged-in only
- `POST /expenses/<int:id>/edit` — validate and save the updated expense — logged-in only

## Database changes

- No new tables or columns.
- All required columns already exist in `expenses`: `id`, `user_id`, `amount`, `category`, `date`, `description`.

## Templates

- Create: `templates/edit_expense.html`
  - extends `base.html`
  - form with `method="POST"` and the action built with `url_for('edit_expense', id=expense.id)`
  - Fields (identical to `add_expense.html`, all pre-filled with current values):
    - `amount` — number input, `step="0.01"`, `min="0.01"`, required, pre-filled
    - `category` — `<select>` with exactly 7 fixed options, pre-selected to the current value
    - `date` — `<input type="date">`, required, pre-filled to the current value
    - `description` — text input, optional, `maxlength="200"`, pre-filled (an empty field when the stored description is NULL)
  - Submit button labelled "Save Changes" and a cancel link back to the profile page via `url_for('profile')`
  - Block that displays flashed messages (validation errors are flashed with the category "error") and re-populates submitted (not original) values on validation failure
  - The re-rendered form after a failure still receives the expense (for its id), the submitted values and the categories list
- Modify: `templates/profile.html`
  - Add an "Actions" column header to the transactions table `<thead>`
  - Add an "Edit" link cell per row pointing to the edit route for that transaction's id, built with `url_for('edit_expense', id=tx.id)`

## Files to change

- `database/queries.py`
  - Add `get_expense_by_id(expense_id, user_id)`
    - fetches a single expense row only if it belongs to the given user
    - returns `None` if not found or if `user_id` does not match
    - query must scope to `id = ? AND user_id = ?`
  - Add `update_expense(expense_id, user_id, amount, category, date, description)`
    - issues a parameterised UPDATE scoped to `id = ? AND user_id = ?` for ownership safety
    - commits and closes the connection before returning
    - returns the number of rows updated (0 when the expense does not exist or belongs to another user)
  - Modify `get_recent_transactions`
    - add `id` to the SELECT column list so templates can build edit links
- `app.py`
  - Import `get_expense_by_id` and `update_expense` from `database.queries`
  - Replace the GET-only placeholder at `/expenses/<int:id>/edit` with a full GET + POST handler:
    - GET: call `get_expense_by_id`; return 404 if not found or not owned; render `edit_expense.html` with `expense` and the categories list
    - POST, in this order:
      1. redirect to `/login` if not authenticated
      2. call `get_expense_by_id`; return 404 if not found or not owned — before reading or validating any form field
      3. read the form fields and validate them (same rules as Step 07)
      4. call `update_expense`; if it returns 0 rows, return 404
      5. flash "Expense updated successfully." with the category "success" and redirect to `url_for("profile")`
      6. on a validation error, re-render the form with the flashed error, the submitted values, the expense and the categories list
    - The category list is defined once and shared by the add and edit routes, so the two cannot drift apart
    - The route must accept both GET and POST methods
- `templates/profile.html`
  - Add an "Actions" header cell to the table header
  - Add an "Edit" link cell per transaction row

## Files to create

- `templates/edit_expense.html`
- `tests/test_edit_expense.py`

## New dependencies

- None

## Rules for implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`.
- Parameterised queries only — never string-format values into SQL.
- `PRAGMA foreign_keys = ON` must be enabled on every connection (already handled in `get_db()`).
- `get_expense_by_id` must scope its query to `id = ? AND user_id = ?` — return `None` if not found or if the ownership check fails.
- `update_expense` must also include `user_id = ?` in its WHERE clause as a second ownership guard.
- Unauthenticated access to both GET and POST must redirect to `/login`.
- If the expense does not exist or belongs to another user, return 404.
- Ownership is checked (404) before any validation, so a bad submission for another user's expense returns 404, not 200.
- Validation rules for POST (identical to Step 07 add expense, including its fixes):
  1. `amount`: required; must be a finite float greater than 0 and at most 9999999.99; parse with `float()`, catch `ValueError`; reject `nan` and infinity; round to 2 decimal places before saving
  2. `category`: required; must be one of the 7 fixed categories; reject anything else
  3. `date`: required; must be a valid `YYYY-MM-DD` string; parse with `datetime.strptime`; save the parsed date re-formatted as `YYYY-MM-DD`; future dates are allowed
  4. `description`: optional; strip whitespace; must be at most 200 characters; store `None` if blank
- Any later change to these rules must be made in both Step 07 and Step 08.
- On any validation error, re-render the form with the error message and the submitted (not original) values pre-filled.
- After a successful update, redirect to `url_for("profile")` — do NOT render the form again.
- Currency must always display as ₹ — never £ or $.
- Use CSS variables — never hardcode hex values.
- No inline styles.
- All templates extend `base.html`.
- Use `url_for()` for every internal link — never hardcode paths.

## Tests to write

- File: `tests/test_edit_expense.py`
- Tests run against a temporary database seeded with the demo user; a second user is created with `create_user` so another user's expense can be tested; authenticated tests log in through the test client (or set the session `user_id`), never touching the real `spendly.db`.
- The Step 05 test for `get_recent_transactions` is updated so each item is expected to include `id` as well as `date`, `description`, `category` and `amount`.
- Unit tests:

| Function | Input | Expected output |
|---|---|---|
| `get_expense_by_id` | Valid `expense_id` and correct `user_id` | Returns the matching row as a dict-like object |
| `get_expense_by_id` | Valid `expense_id` and wrong `user_id` | Returns `None` |
| `get_expense_by_id` | Non-existent `expense_id` | Returns `None` |
| `update_expense` | Valid `expense_id`, correct `user_id`, new `amount=99.0` | Row in DB reflects the updated amount; returns 1 |
| `update_expense` | Valid `expense_id`, wrong `user_id` | Row in DB unchanged; returns 0; no error raised |
| `update_expense` | Valid `expense_id`, correct `user_id`, `description=None` | `description` stored as NULL; returns 1 |
| `get_recent_transactions` | Seed user | Each item includes `id` matching the expense row |

- Route tests:
  - `GET /expenses/<id>/edit` unauthenticated → redirects to `/login` (302)
  - `GET /expenses/<id>/edit` authenticated, own expense → returns 200; response contains the form pre-filled with current values; `<select>` has the correct category pre-selected
  - `GET /expenses/<id>/edit` authenticated, other user's expense → returns 404
  - `GET /expenses/<id>/edit` authenticated, non-existent id → returns 404
  - `POST /expenses/<id>/edit` unauthenticated → redirects to `/login` (302)
  - `POST /expenses/<id>/edit` authenticated, valid data → redirects to `/profile` (302); updated values reflected in the database
  - `POST /expenses/<id>/edit` authenticated, other user's expense with valid data → returns 404; the row is unchanged
  - `POST /expenses/<id>/edit` authenticated, other user's expense with invalid data → returns 404 (not 200)
  - `POST /expenses/<id>/edit` authenticated, non-existent id → returns 404
  - `POST /expenses/<id>/edit` authenticated, missing amount → returns 200; response contains an error message
  - `POST /expenses/<id>/edit` authenticated, `amount` = 0 → returns 200; response contains an error message
  - `POST /expenses/<id>/edit` authenticated, non-numeric amount → returns 200; response contains an error message
  - `POST /expenses/<id>/edit` authenticated, invalid category → returns 200; response contains an error message
  - `POST /expenses/<id>/edit` authenticated, invalid date string → returns 200; response contains an error message
  - `POST /expenses/<id>/edit` authenticated, no description → redirects to `/profile` (302); row updated with `description` = NULL
  - `POST /expenses/<id>/edit` authenticated, `amount=inf` or `amount=nan` → returns 200; response contains an error message; row unchanged
  - `POST /expenses/<id>/edit` authenticated, `date=2026-3-5` → redirects to `/profile` (302); the stored date is `2026-03-05`
  - `POST /expenses/<id>/edit` authenticated, description longer than 200 characters → returns 200; response contains an error message; row unchanged
  - `POST /expenses/<id>/edit` authenticated, invalid data → the re-rendered form shows the submitted values and still posts to the same expense's edit URL
  - `GET /expenses/<id>/edit` authenticated, expense with a NULL description → the description field is empty
  - `GET /profile` authenticated → each transaction row contains an "Edit" link to `/expenses/<id>/edit` for that row's id
  - After a successful edit, following the redirect shows "Expense updated successfully." on the profile page

## Definition of done

- [ ] Visiting `/expenses/<id>/edit` while logged out redirects to `/login`
- [ ] Visiting `/expenses/<id>/edit` for a non-existent or other user's expense returns 404
- [ ] Visiting `/expenses/<id>/edit` while logged in shows a form pre-filled with the expense's current values
- [ ] The category dropdown has the correct category pre-selected
- [ ] Submitting valid changes redirects to `/profile` and the updated values appear in the transaction list
- [ ] Submitting with a missing or zero amount re-renders the form with an error and the submitted values retained
- [ ] Submitting with an invalid category re-renders the form with an error
- [ ] Submitting with an invalid date re-renders the form with an error
- [ ] Submitting without a description saves the expense with no error
- [ ] Each row in the profile transaction table has an "Edit" link pointing to the correct URL
- [ ] POSTing to another user's expense returns 404 even when the submitted data is invalid, and the expense is not changed
- [ ] Submitting an infinite amount, an over-long description or an unpadded date behaves as in Step 07 (rejected, or saved in `YYYY-MM-DD` form)
- [ ] After a validation error the form still posts to the correct expense and keeps the submitted values
- [ ] After a successful edit, the profile page shows "Expense updated successfully."
- [ ] The add and edit routes share one category list
- [ ] Tests pass against a temporary database
