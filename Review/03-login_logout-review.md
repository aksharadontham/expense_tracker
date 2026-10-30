# Review Report: 03-login_logout.md

- **Spec reviewed:** `.claude/specs/03-login_logout.md`
- **Checked against:** `Spec_03_login_logout_prompt.md`
- **Verdict:** Compliant. All 9 required sections are present, in the order the prompt lists them, with every requested point covered. No blocking issues. A few gaps and one cross-spec issue are listed below.

## 1. Section-by-section compliance

| Section | Status | Notes |
|---|---|---|
| Overview | Pass | Converts the `/login` stub; verifies credentials, stores `session["user_id"]`, redirects to the landing page; implements `/logout`; guests vs logged-in users; prerequisite for expense features |
| Depends on | Pass | Step 01 (`users` table) and Step 02 (`create_user`, password hashing, a user to log in against) |
| Routes | Pass | `GET /login`, `POST /login`, `GET /logout` with the stated purposes, all public |
| Database changes | Pass | No database changes; `get_user_by_email(email)` with all three points (queries by email, returns row or `None`, lives in `database/db.py`) |
| Templates | Pass | All four items: POST form with email and password, action `url_for('login')` with `method="post"`, flash block, link to `/register` |
| Files to change | Pass | `app.py`, `database/db.py`, `templates/login.html` with the stated purposes |
| Files to create | Pass | None |
| New dependencies | Pass | None; names `werkzeug.security.check_password_hash` |
| Rules for implementation | Pass | All 11 rules present (see section 3) |
| Definition of done | Pass | All seven checkbox items present with the prompt's wording |

## 2. Format rules

| Rule | Status | Notes |
|---|---|---|
| Output only the Markdown spec | Pass | No prose outside the spec |
| No code | Pass | Only identifiers and short fragments in inline code; no code blocks |
| Bullet lists throughout | Pass | |
| Checkbox list for Definition of done | Pass | |
| Section names exact, no numbers | Pass | Plain headings with the exact names |

## 3. Rules for implementation — detail

| Prompt rule | In spec |
|---|---|
| No SQLAlchemy or ORMs, raw `sqlite3` via `get_db()` | Yes |
| Parameterised queries only | Yes |
| Verify with `check_password_hash` | Yes |
| Session key is `session["user_id"]` (integer) | Yes |
| Use `flask.session`, no custom mechanism | Yes |
| Generic failure flash "Invalid email or password.", reveal nothing about which field | Yes |
| Redirect to `url_for("landing")` after login | Yes |
| `logout()` calls `session.clear()` then redirects to `url_for("landing")` | Yes |
| Templates extend `base.html` | Yes |
| CSS variables, no hardcoded hex | Yes |
| `url_for()` for every internal link | Yes |

## 4. Deviations and additions

- **Document title:** a `# Spec: Login and Logout` heading sits above Overview. The prompt did not ask for it.
- **Inline code formatting:** file paths and identifiers are in inline code, where the prompt gave plain text. This is a presentation choice only.
- No content was added or removed beyond that.

## 5. Gaps and ambiguities

These are inherited from the prompt. None contradicts it.

1. **Failure behavior is implicit.** The Definition of done says a failed login "stays on the login page", and the flash is generic, but no rule says the route must re-render the form instead of redirecting. Step 02 states this outright; Step 03 does not. An implementer could redirect to `/login`, which also satisfies the wording.
2. **Overview says "POST handler" but Routes list GET and POST.** The Files to change section says GET+POST, so this is consistent in the end, but the Overview wording is narrower.
3. **`secret_key` is an unlisted dependency.** Flash messages and the session both need `app.secret_key`, which Step 02 sets. Depends on names only `create_user` and hashing from Step 02, not the secret key.
4. **Email matching rules are undefined.** Nothing says whether the email is trimmed or compared case-insensitively. If registration stores a mixed-case email, login with a different case would fail.
5. **Empty submissions are not covered.** There is no rule for blank email or password. They would fall under "Invalid email or password.", but it is not stated.
6. **Already signed-in visitors.** Nothing says what `/login` does for a user who is already logged in.
7. **Logout by GET.** `/logout` is a plain GET, so any link or image can log a user out. This is as the prompt specifies, and is acceptable for now.
8. **No tests section.** The prompt did not ask for one, so verification rests on the Definition of done.

## 6. Cross-spec observation

- **Navbar logged-in state.** The Step 04 spec expects the navbar to show the username and a logout link. No step so far changes `base.html` to do that, and Step 03's Files to change does not include it. The first spec to touch the navbar is Step 07, which adds an "Add Expense" link. Either Step 03 or Step 04 should own the navbar change.

## 7. Recommendations

- Add a rule that failed logins re-render the form with the flash, matching Step 02.
- Decide whether email is trimmed and lower-cased on both registration and login, and write it into both specs.
- Add "`app.secret_key` set in Step 02" to Depends on, or restate it in the rules.
- Assign the navbar logged-in state to a specific step by adding `templates/base.html` to its Files to change.
- Optionally add a Tests to write section, as in the later specs.
