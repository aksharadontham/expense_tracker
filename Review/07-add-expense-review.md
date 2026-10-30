# Review Report: 07-add-expense.md

- **Spec reviewed:** `.claude/specs/07-add-expense.md`
- **Checked against:** `Spec_07-add-expense_prompt.md`
- **Verdict:** Compliant, with two deliberate deviations. All 11 required sections are present, in the order the prompt lists them, with every requested point covered. No blocking issues. The deviations are the form's action and cancel link (`url_for` in place of literal paths) and the test file added under Files to create. The validation rules inherited from the prompt leave two real data-quality holes, described in section 5.

## 1. Section-by-section compliance

| Section | Status | Notes |
|---|---|---|
| Overview | Pass | All five points: dedicated form at `/expenses/add`; GET placeholder upgraded to GET + POST; validated insert and redirect to the profile; reusable `insert_expense()` helper; "Add Expense" button on `profile.html` and nav link in `base.html` |
| Depends on | Pass | Steps 01, 03 and 04 / 05 with the stated reasons |
| Routes | Pass | `GET` and `POST /expenses/add`, both logged-in only |
| Database changes | Pass | No changes; all required columns listed |
| Templates | Pass, with one change | `add_expense.html` with all four fields and their attributes, submit button and cancel link, error block with re-populated values; `profile.html` button; `base.html` nav link visible only when `session.user_id` is set. Form action and cancel link use `url_for` (see section 4) |
| Files to change | Pass | `app.py` (GET with login redirect; POST read, validate, insert, redirect), `database/queries.py`, `templates/profile.html`, `templates/base.html` |
| Files to create | Pass, with one addition | `templates/add_expense.html`; the test file was added (see section 4) |
| New dependencies | Pass | None |
| Rules for implementation | Pass | All 12 rules present (see section 3) |
| Tests to write | Pass | File name; unit-test table with both rows; all ten route tests |
| Definition of done | Pass | All ten checkbox items present with the prompt's wording |

## 2. Format rules

| Rule | Status | Notes |
|---|---|---|
| Output only the Markdown spec | Pass | No prose outside the spec |
| No code | Pass | Only identifiers and short fragments in inline code |
| Bullet lists throughout | Pass | |
| Table for the unit test cases | Pass | Columns Function / Input / Expected output |
| Checkbox list for Definition of done | Pass | |
| Section names exact, no numbers | Pass | Plain headings with the exact names |

## 3. Rules for implementation — detail

| Prompt rule | In spec |
|---|---|
| No SQLAlchemy or ORMs; raw `sqlite3` via `get_db()` | Yes |
| Parameterised queries only | Yes |
| `PRAGMA foreign_keys = ON` on every connection | Yes |
| Unauthenticated GET and POST redirect to `/login` | Yes |
| Validation 1: `amount` required, positive float, `float()` with `ValueError` caught | Yes |
| Validation 2: `category` required, one of the 7 fixed values | Yes |
| Validation 3: `date` required, valid `YYYY-MM-DD` via `datetime.strptime` | Yes |
| Validation 4: `description` optional, stripped, `None` if blank | Yes |
| On error: re-render with message and submitted values pre-filled | Yes |
| On success: redirect to `url_for("profile")`, do not render the form | Yes |
| Currency always ₹ | Yes |
| CSS variables; no inline styles; templates extend `base.html`; `url_for()` for links | Yes |

## 4. Deviations from the prompt

- **Form action and cancel link.** The prompt wrote `action="/expenses/add"` and a cancel link to `/profile`. The same prompt's rules say to use `url_for()` for every internal link and never hardcode paths. The spec uses `url_for('add_expense')` and `url_for('profile')` so the two instructions do not conflict. The route function is assumed to be named `add_expense`, as in the existing `app.py`.
- **Test file under Files to create.** `tests/test_add_expense.py` is listed, since Tests to write needs it. The prompt listed only the template.
- **Document title and inline code.** A `# Spec: Add Expense` heading sits above Overview, and paths and identifiers are in inline code.
- No content was removed.

## 5. Gaps and ambiguities

These are inherited from the prompt. None contradicts it.

1. **Non-finite amounts pass validation.** Python's `float()` accepts the strings "inf" and "infinity". Infinity is greater than zero, so it would pass the positive-amount rule and be stored. There is also no upper limit or decimal-place rule. The HTML `min` and `step` attributes only guard the browser.
2. **Date strings can be stored in the wrong format.** `datetime.strptime` with the `%Y-%m-%d` format accepts values such as `2026-3-5` without leading zeros. Stored as typed, these break the YYYY-MM-DD rule and the string comparisons used by the Step 06 `BETWEEN` filter and newest-first ordering. The spec does not say to re-format the validated date before saving.
3. **Description length is not enforced on the server.** The form carries a 200-character limit, but no validation rule enforces it.
4. **Today's date default.** The date field "defaults to today's date", but the spec does not say who computes it (the route or the template) or what is re-shown after a failure.
5. **Future dates.** They are allowed, with no rule. This matters little for tracking but affects the Step 06 "This Month" results.
6. **Error display mechanism.** The spec says "flash/error message block" without saying whether errors are flashed or passed as a variable, and what happens to a message after a re-render.
7. **No success message.** Nothing says whether the user sees a confirmation after redirecting to the profile.
8. **`insert_expense` return value and cleanup.** The helper's return value (such as the new id) is not stated, nor whether it commits and closes the connection, as Step 05's helpers must.
9. **Test coverage of the navigation changes.** The nav link and profile button appear in the Definition of done but no route test checks them.
10. **Test isolation.** Tests use "the test user", with no statement on a separate test database or how the login session is created in tests.
11. **No CSRF protection.** The POST form has no token. This is acceptable at this stage of the project but is a known gap.

## 6. Cross-spec observations

- **Step 06 filter.** The redirect to `url_for("profile")` carries no filter parameters, so an active filter is lost after adding an expense. A newly added expense dated outside the earlier filter would otherwise be hidden.
- **Step 08 form pattern.** Step 08 reuses this validation list and form layout. Any fix to items 1 to 3 above should be made in both specs.

## 7. Recommendations

- Add a validation rule rejecting non-finite amounts, and optionally a maximum amount and two-decimal rounding.
- State that the validated date is re-formatted to `YYYY-MM-DD` before saving, or compare the input to its re-formatted form.
- Add a server-side check for the 200-character description limit.
- State who supplies the default date and what the error mechanism is.
- Add route tests for the navigation changes, and say whether tests use a separate database.
