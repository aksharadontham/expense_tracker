# Spec: Login and Logout

## Overview

- This step converts the `/login` stub into a functional POST handler that:
  - verifies credentials against the `users` table
  - stores the authenticated user's id in `session["user_id"]`
  - redirects to the landing page (until a dashboard route exists)
- It also implements `/logout`, which clears the session and redirects to `/`.
- After this step the app can distinguish logged-in users from guests.
- This is a prerequisite for all expense features.

## Depends on

- Step 01 — Database Setup (`users` table must exist)
- Step 02 — Registration (`create_user` and password hashing must be in place; a user must exist to log in against; `app.secret_key` must be set so `flash()` and `session` work; emails are stored stripped and lower-cased)

## Routes

- `GET /login` — render the login form — public (a visitor who is already logged in is redirected to the landing page)
- `POST /login` — validate credentials, set session, redirect on success, re-render the form with a flashed error on failure — public
- `GET /logout` — clear session, redirect to `/` — public (no login required)

## Database changes

- No database changes.
- The `users` table from Step 01 already stores `email` and `password_hash`.
- One new DB helper to add to `database/db.py`:
  - `get_user_by_email(email)`
    - queries the `users` table by email
    - returns the matching user row, or `None` if not found
    - must live in `database/db.py`, not inline in the route

## Templates

- Modify `templates/login.html`:
  - add a POST form with `email` and `password` fields
  - set the form action to `url_for('login')` with `method="post"`
  - add a block to display all flashed messages, not only errors, so the "Account created successfully. Please sign in." message flashed by registration is shown here
  - on a failed login, re-fill the `email` field with the submitted value; never re-fill the password field
  - add a link to `/register` for new users
- Modify `templates/base.html` (navbar):
  - when `session["user_id"]` is set, show the logged-in user's name (from `session["user_name"]`) and a "Logout" link pointing to `url_for('logout')`
  - when no user is logged in, keep the existing "Sign in" and "Get started" links
  - keep all existing visual design unchanged

## Files to change

- `app.py` — implement `login()` as a GET+POST handler; implement `logout()`
- `database/db.py` — add the `get_user_by_email()` helper
- `templates/login.html` — add the POST form and flash display
- `templates/base.html` — show the user's name and a logout link in the navbar when logged in

## Files to create

- None

## New dependencies

- None — `werkzeug.security.check_password_hash` is already available

## Rules for implementation

- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()`.
- Parameterised queries only — never use f-strings in SQL.
- Verify passwords with `werkzeug.security.check_password_hash`.
- Before checking credentials, strip leading and trailing whitespace from `email` and convert it to lower case; do not alter `password`.
- A blank `email` or `password` counts as a failed login and shows the same generic error; no database lookup is needed.
- The session key for the logged-in user must be `session["user_id"]` (integer).
- On successful login, call `session.clear()` first, then set `session["user_id"]` and `session["user_name"]` (the user's name, used by the navbar).
- On failed login, re-render the login form with the flashed error — do not redirect.
- Flash errors with the category "error".
- Use `flask.session` — do not roll a custom session mechanism.
- On failed login show a generic flash error: "Invalid email or password."
  - do not reveal which field was wrong
- After successful login redirect to `url_for("landing")` until a dashboard exists.
- `logout()` must call `session.clear()` then redirect to `url_for("landing")`.
- All templates must extend `base.html`.
- Use CSS variables — never hardcode hex values.
- Use `url_for()` for every internal link — never hardcode paths.

## Definition of done

- [ ] `GET /login` renders the login form with email and password fields
- [ ] Submitting with valid credentials (`demo@spendly.com` / `demo123`) sets `session["user_id"]` and redirects to `/`
- [ ] Submitting with a wrong password shows the "Invalid email or password." flash and stays on the login page
- [ ] Submitting with an unregistered email shows the same generic error flash
- [ ] `GET /logout` clears the session and redirects to `/`
- [ ] After logout, `session["user_id"]` is no longer present
- [ ] The `/logout` route no longer returns the raw stub string
- [ ] Submitting with a blank email or password shows the same generic error flash
- [ ] Logging in with `Demo@Spendly.com ` (different case, trailing space) and `demo123` succeeds
- [ ] After a failed login, the email field keeps the submitted value and the password field is empty
- [ ] After registering a new account, the login page shows the "Account created successfully. Please sign in." message
- [ ] A logged-in visitor who opens `/login` is redirected to `/`
- [ ] The navbar shows the user's name and a "Logout" link when logged in, and "Sign in" and "Get started" when logged out
