# Review Report: 08-edit-expense.md

- **Spec reviewed:** `.claude/specs/08-edit-expense.md`
- **Checked against:** `Spec_08-edit-expense_prompt.md`
- **Verdict:** Compliant, with three deliberate deviations. All 11 required sections are present, in the order the prompt lists them, with every requested point covered. No blocking issues. The deviations are the `url_for` paths, the route decorator written as prose, and the test file added under Files to create. The most important gap is that the spec does not make the POST handler check ownership before updating, although a test requires a 404 for another user's expense.

## 1. Section-by-section compliance

| Section | Status | Notes |
|---|---|---|
| Overview | Pass | All six points: pre-populated edit form; GET loads the expense; POST validates and updates in place; ownership enforced; `get_expense_by_id` and `update_expense` added; "Edit" link per row needing `get_recent_transactions` to return the id |
| Depends on | Pass | Steps 01, 03, 05 and 07 with the stated reasons |
| Routes | Pass | `GET` and `POST /expenses/<int:id>/edit`, both logged-in only |
| Database changes | Pass | No new tables or columns; required columns listed |
| Templates | Pass, with changes | `edit_expense.html` with all four pre-filled fields, "Save Changes" button, cancel link, error block that shows submitted values; `profile.html` gains an "Actions" column header and an "Edit" cell per row. Paths use `url_for` (see section 4) |
| Files to change | Pass, with one change | `database/queries.py` (both helpers and the `id` column), `app.py` (imports and the GET + POST handler), `templates/profile.html`. The decorator line is described in words (see section 4) |
| Files to create | Pass, with one addition | `templates/edit_expense.html`; the test file was added (see section 4) |
| New dependencies | Pass | None |
| Rules for implementation | Pass | All 14 rules present (see section 3) |
| Tests to write | Pass | File name; unit-test table with all five rows; all thirteen route tests |
| Definition of done | Pass | All ten checkbox items present with the prompt's wording |

## 2. Format rules

| Rule | Status | Notes |
|---|---|---|
| Output only the Markdown spec | Pass | No prose outside the spec |
| No code | Pass | Only identifiers and short fragments in inline code; the decorator line is not shown |
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
| `get_expense_by_id` scoped to `id = ? AND user_id = ?`, `None` otherwise | Yes |
| `update_expense` also includes `user_id = ?` in its WHERE clause | Yes |
| Unauthenticated GET and POST redirect to `/login` | Yes |
| Missing or other user's expense returns 404 | Yes |
| Validation 1 to 4 identical to Step 07 | Yes |
| On error: re-render with message and submitted (not original) values | Yes |
| On success: redirect to `url_for("profile")`, do not render the form | Yes |
| Currency always ₹ | Yes |
| CSS variables; no inline styles; templates extend `base.html`; `url_for()` for links | Yes |

## 4. Deviations from the prompt

- **Paths in templates.** The prompt wrote the form action as `/expenses/{{ expense.id }}/edit`, the Edit link as `/expenses/{{ tx.id }}/edit` and the cancel link as `/profile`. Its own rules say to use `url_for()` for every internal link and never hardcode paths. The spec uses `url_for('edit_expense', id=...)` and `url_for('profile')` so the two instructions do not conflict. The route function is assumed to be named `edit_expense`, as in the existing `app.py`.
- **Route decorator.** The prompt gave the literal `@app.route(...)` line. The spec says "the route must accept both GET and POST methods", to keep code out of the spec.
- **Test file under Files to create.** `tests/test_edit_expense.py` is listed, since Tests to write needs it. The prompt listed only the template.
- **Document title and inline code.** A `# Spec: Edit Expense` heading sits above Overview, and paths and identifiers are in inline code.
- **Repeated profile changes.** The `profile.html` changes appear under both Templates and Files to change, as in the prompt.
- No content was removed.

## 5. Gaps and ambiguities

These are inherited from the prompt. None contradicts it.

1. **POST does not explicitly check ownership first.** The GET flow calls `get_expense_by_id` and returns 404. The POST flow is described as read, validate, call `update_expense`, redirect. But `update_expense` does nothing quietly for the wrong user (as its own unit test states), while the route test expects a 404 for another user's expense on POST. Unless the POST handler loads the expense first, the 404 test fails and the user is redirected as if the edit succeeded.
2. **Order of checks in POST.** It is not stated whether ownership (404) is checked before validation. If validation runs first, a bad submission for someone else's expense would return 200 with an error instead of 404.
3. **The Step 07 validation holes carry over.** "Identical to Step 07" means non-finite amounts such as "inf" pass the positive check, dates without leading zeros are accepted by `strptime` and can be stored in a non-standard format, and the 200-character description limit is not enforced on the server. A fix to Step 07 should be applied here too.
4. **Failed re-render needs the expense id.** The form action depends on `expense.id`, so the re-rendered form on a validation error must still receive the expense id, alongside the submitted values and the category list. The spec says "submitted values" but not this.
5. **Shared category list.** The "categories list" is passed from `app.py`, and Step 07 also has a fixed list. The spec does not say they should share one definition, so the two lists could drift.
6. **`update_expense` return value and cleanup.** Neither the return value (such as rows changed) nor commit and close behavior is stated.
7. **Clearing a description.** A blank description sets the column to NULL, as in Step 07. The spec lists this as a route test but not whether the edit form shows an empty field afterwards, which is the expected outcome.
8. **Existing Step 05 test.** The Step 05 unit test for `get_recent_transactions` expects items with date, description, category and amount only. After this step each item also has `id`. The spec has no test for the `id` field and does not mention updating the earlier test.
9. **Test coverage of the profile changes.** The Definition of done requires an "Edit" link per row, but no route test checks it.
10. **Test isolation.** Tests rely on seed and test users, with no statement on a separate test database or how another user's expense is created.
11. **No CSRF protection.** The POST form has no token. This is acceptable at this stage but is a known gap.

## 6. Cross-spec observations

- **Step 09 shares the helper.** Step 09 reuses `get_expense_by_id` for its ownership check, which is the missing pattern in item 1 above.
- **Step 06 filter.** The redirect to `url_for("profile")` carries no filter parameters, so an active filter is lost after an edit.
- **Step 09 layout.** The Actions column added here is where Step 09 places the Delete button, so any change to its layout affects both.

## 7. Recommendations

- State that the POST handler loads the expense with `get_expense_by_id` and returns 404 before validating or updating.
- Apply the Step 07 validation fixes (finite amounts, standard date format, description length) to both specs together.
- Say that the re-rendered form always receives the expense id and the categories list.
- Define the category list once and share it between the add and edit routes.
- Add route tests for the Edit links on the profile page, and update the Step 05 transaction test for the new `id` field.
