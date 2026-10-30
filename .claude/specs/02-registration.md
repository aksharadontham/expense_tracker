# Spec: Registration

## Overview

- This step upgrades the existing stub `GET /register` route into a fully functional registration flow that handles both GET and POST.
- The form accepts `name`, `email`, `password`, and `confirm_password`.
- On success, a success message is flashed and the user is redirected to `/login`.
- This is the entry point for all authenticated features: login, profile, and expense tracking all require a registered user.

## Depends on

- Step 01 — Database setup (`users` table, `get_db()`)

## Routes

- `GET /register` — render the registration form — public (already exists as a stub; upgrade it)
- `POST /register` — process the form, validate input, insert the user, redirect to `/login` — public

## Database changes

- No new tables or columns.
- The existing `users` table covers all requirements.
- One new DB helper to add to `database/db.py`:
  - `create_user(name, email, password)`
    - hashes the password with werkzeug
    - inserts a row into `users`
    - returns the new user's id
    - raises `sqlite3.IntegrityError` if the email is already taken (UNIQUE constraint)

## Templates

- Modify `templates/register.html`:
  - change the form action to `url_for('register')` with `method="post"`
  - add `name` attributes to all inputs: `name`, `email`, `password`, `confirm_password`
  - add a block to display flashed error messages (e.g. "Email already registered", "Passwords do not match")
  - on a validation failure, re-fill the `name` and `email` fields with the submitted values; never re-fill the password fields
  - keep all existing visual design unchanged

## Files to change

- `app.py` — upgrade `register()` to handle GET and POST; add flash and redirect logic
- `database/db.py` — add the `create_user()` helper
- `templates/register.html` — wire up form action/method and flash message display

## Files to create

- None

## New dependencies

- None — uses `werkzeug.security` (already installed) and Flask's built-in `flash`, `redirect`, and `url_for`

## Rules for implementation

- No SQLAlchemy or ORMs.
- Parameterised queries only — never use f-strings in SQL.
- Hash passwords with `werkzeug.security.generate_password_hash` — never store plaintext.
- `app.secret_key` must be set in `app.py` for `flash()` to work (use a hardcoded dev string for now).
- Before validating, normalise the input:
  - strip leading and trailing whitespace from `name` and `email`
  - convert `email` to lower case so the same address cannot be registered twice in different cases
  - do not strip or alter `password` or `confirm_password`
  - a field that is empty after stripping counts as empty
- Server-side validation must check in this order:
  - 1. All fields are non-empty
  - 2. `email` has a basic valid shape: one `@` with text before it and a dot-separated domain after it
  - 3. `password` is at least 8 characters
  - 4. `password` equals `confirm_password`
  - 5. Email is not already registered (catch `sqlite3.IntegrityError`)
- On any validation failure: re-render the form with a flashed error and the submitted `name` and `email` — do not redirect.
- Flash errors with the category "error" and the success message with the category "success".
- On success: flash the message "Account created successfully. Please sign in." and redirect to `url_for('login')`.
- The route declares only GET and POST, so Flask rejects other methods with 405 automatically; keep `abort(405)` as an explicit fallback branch for any other method that reaches the handler.
- All templates must extend `base.html`.
- Use CSS variables — never hardcode hex values.
- Use `url_for()` for every internal link — never hardcode URLs.

## Definition of done

- [ ] `GET /register` renders the registration form without errors
- [ ] Submitting with all valid fields creates a new user in `users` and redirects to `/login`
- [ ] Submitting with mismatched passwords re-renders the form with an error, with no DB insert
- [ ] Submitting with an already-registered email re-renders with "Email already registered"
- [ ] Submitting with any empty field re-renders with a validation error
- [ ] Submitting a field containing only spaces is treated as empty
- [ ] Submitting a password shorter than 8 characters re-renders the form with an error and no DB insert
- [ ] Submitting an email that is not in a valid shape re-renders the form with an error
- [ ] After any validation failure, the `name` and `email` fields keep the submitted values and the password fields are empty
- [ ] Registering `Demo@Spendly.com` when `demo@spendly.com` already exists is rejected with "Email already registered"
- [ ] After a successful registration, the login page shows "Account created successfully. Please sign in."
- [ ] Password is stored as a hash — never plaintext — verifiable by inspecting `spendly.db`
- [ ] No duplicate user is created on repeated valid submissions with the same email
