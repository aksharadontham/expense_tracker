# Review Report: 02-registration.md

- **Spec reviewed:** `.claude/specs/02-registration.md`
- **Checked against:** `Spec_02_Registration.prompt.md`
- **Verdict:** Compliant. All 10 required sections are present, in the order the prompt lists them, with every requested point covered. No blocking issues. Minor deviations and gaps are listed below.

## 1. Section-by-section compliance

| Section | Status | Notes |
|---|---|---|
| Overview | Pass | All four points: upgrade of the stub into a GET + POST handler; the four form fields; flash and redirect to `/login` on success; entry point for all authenticated features |
| Depends on | Pass | Step 01 — Database setup (`users` table, `get_db()`) |
| Routes | Pass | `GET /register` (upgrade of the stub) and `POST /register`, both public |
| Database changes | Pass | No new tables or columns; `create_user(name, email, password)` with all four behaviors (hashes, inserts, returns id, raises `sqlite3.IntegrityError` on duplicate email) |
| Templates | Pass | Form action and method, `name` attributes on all four inputs, flashed-error block with example messages, visual design unchanged |
| Files to change | Pass | `app.py`, `database/db.py`, `templates/register.html` with the stated purposes |
| Files to create | Pass | None |
| New dependencies | Pass | None; names `werkzeug.security` and Flask's `flash`, `redirect`, `url_for` |
| Rules for implementation | Pass | All 12 rules present (see section 3) |
| Definition of done | Pass | All seven checkbox items present with the prompt's wording |

## 2. Format rules

| Rule | Status | Notes |
|---|---|---|
| Output only the Markdown spec | Pass | No prose outside the spec |
| No code | Pass | Only identifiers and short fragments in inline code; no code blocks |
| Bullet lists throughout, no tables | Pass | |
| Checkbox list for Definition of done | Pass | |
| Section names exact, no numbers | Pass | Headings use the exact names as plain headings |

## 3. Rules for implementation — detail

| Prompt rule | In spec |
|---|---|
| No SQLAlchemy or ORMs | Yes |
| Parameterised queries only, no f-strings in SQL | Yes |
| Hash with `generate_password_hash`, never plaintext | Yes |
| `app.secret_key` set in `app.py`, hardcoded dev string | Yes |
| Validation order: non-empty, passwords match, email not registered | Yes, as three nested items |
| Failure: re-render with flashed error, no redirect | Yes |
| Success: flash and redirect to `url_for('login')` | Yes |
| `abort(405)` for unsupported methods | Yes |
| Templates extend `base.html` | Yes |
| CSS variables, no hardcoded hex | Yes |
| `url_for()` for every internal link | Yes |

## 4. Deviations and additions

- **Document title:** a `# Spec: Registration` heading sits above Overview. The prompt did not ask for it.
- **Validation order as nested bullets:** the three ordered checks appear as bullets that begin with "1.", "2." and "3." under one parent bullet. This keeps to "bullet lists throughout" while preserving the order. The Markdown renders as bullets, not a numbered list.
- **Path style:** all file paths and identifiers are in inline code. The prompt gave them unformatted. This is a presentation choice only.

## 5. Gaps and ambiguities

These are gaps in the prompt that the spec inherits. None contradicts the prompt.

1. **`abort(405)` is redundant.** If the route only declares GET and POST, Flask already returns 405 for other methods. The rule is kept as written, but an implementer may not know where the `abort` would ever run.
2. **No form re-population.** On a validation failure the form is re-rendered, but nothing says the submitted name and email should be kept in the fields. Users would retype everything.
3. **"Non-empty" is undefined.** Nothing says whether whitespace-only values count as empty or whether inputs are trimmed.
4. **No email checks.** There is no format check, no lower-casing and no trimming. `Demo@Spendly.com` and `demo@spendly.com` would be two different accounts.
5. **No password rules.** There is no minimum length or strength requirement.
6. **Success message wording is unspecified.** Error examples are given; the success text is not.
7. **No guard for logged-in visitors.** Nothing says what happens if a signed-in user opens `/register`. This only matters once Step 03 sets the session.
8. **No test section.** The prompt did not ask for one, and the definition of done is the only verification.
9. **Flash category and styling.** The spec does not say whether errors and success messages use different categories, or how the flash block is styled beyond "keep existing design".

## 6. Recommendations

- Decide on items 2 to 5 and add a short rule for each, for example "trim all fields", "lower-case the email" and "keep submitted name and email on failure".
- State the success message text, so the Definition of done can check it.
- Either remove the `abort(405)` rule or explain that it covers a method fallback, to avoid confusion.
- Optionally add a Tests to write section, as the later specs (05 onward) have.
