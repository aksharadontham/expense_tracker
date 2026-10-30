# Review Report: 09-delete-expense.md

- **Spec reviewed:** `.claude/specs/09-delete-expense.md`
- **Checked against:** `Spec_09-delete-expense_prompt.md`
- **Verdict:** Compliant, with four deliberate deviations. All 11 required sections are present, in the order the prompt lists them, with every requested point covered. No blocking issues in the spec itself. The two issues most worth attention are a name clash between the route function and the new query helper, and an inline-style exception that conflicts with an earlier step.

## 1. Section-by-section compliance

| Section | Status | Notes |
|---|---|---|
| Overview | Pass, with one reconciliation | All six points: delete from the profile table; POST "Delete" button per row; ownership check, delete and redirect; no confirmation page, only a `confirm()` dialog; reuse of `get_expense_by_id`; one new helper `delete_expense`. The prompt names the button's `onclick` here and the form's `onsubmit` under Templates; see section 4 |
| Depends on | Pass | Steps 01, 03, 05 and 08 with the stated reasons |
| Routes | Pass | `POST /expenses/<int:id>/delete`, logged-in only; no GET handler, a bare GET returns 405 |
| Database changes | Pass | No new tables or columns |
| Templates | Pass, with one change | Delete form inside the Actions cell with `method="POST"`, the inline-style exception, the `onsubmit` confirm, and a `btn-delete` submit button; "Edit" link stays. The form action uses `url_for` (see section 4) |
| Files to change | Pass, with one change | `database/queries.py` (parameterised DELETE with the dual-column guard, commit and close), `app.py` (import, POST-only handler with the four steps), `templates/profile.html`, `static/css/style.css`. The decorator line is described in words |
| Files to create | Pass, with one addition | The test file was added (see section 4) |
| New dependencies | Pass | None |
| Rules for implementation | Pass | All 13 rules present (see section 3) |
| Tests to write | Pass | File name; unit-test table with all three rows; all five route tests |
| Definition of done | Pass | All seven checkbox items present with the prompt's wording |

## 2. Format rules

| Rule | Status | Notes |
|---|---|---|
| Output only the Markdown spec | Pass | No prose outside the spec |
| No code | Pass | Only identifiers, the permitted inline-style and `onsubmit` fragments, and short SQL fragments the prompt supplied |
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
| `delete_expense` scoped to `id = ? AND user_id = ?` as the ownership guard | Yes |
| POST only; a bare GET returns 405 | Yes |
| Unauthenticated access redirects to `/login` (302) | Yes |
| Missing or other user's expense returns 404 | Yes |
| After deletion redirect to `url_for("profile")`, no template | Yes |
| Only inline style permitted is `display:inline` on the `<form>`; no hex or design values inline | Yes |
| CSS variables, no hardcoded hex | Yes |
| Templates extend `base.html` | Yes |
| Currency always ₹ | Yes |
| `url_for()` for every internal link | Yes |

## 4. Deviations from the prompt

- **Where the confirm lives.** The prompt's Overview puts the `confirm()` in "the button's onclick handler", while its Templates section puts it in `onsubmit` on the `<form>`. The spec's Overview says the form's `onsubmit` handler, matching the Templates detail. This reconciles the two in favor of the more specific instruction.
- **Form action.** The prompt wrote `action="/expenses/{{ tx.id }}/delete"`. Its own rules say never hardcode paths, so the spec uses `url_for('delete_expense', id=tx.id)`.
- **Route decorator.** The prompt gave the literal `@app.route(...)` line. The spec says "the route must accept only the POST method".
- **Test file under Files to create.** `tests/test_delete_expense.py` is listed, since Tests to write needs it. The prompt said "None".
- **Document title and inline code.** A `# Spec: Delete Expense` heading sits above Overview, and paths and identifiers are in inline code.
- No content was removed.

## 5. Gaps and ambiguities

These are inherited from the prompt. None contradicts it.

1. **Name clash between the route and the helper.** The existing stub route in `app.py` is a function called `delete_expense`, and the new query helper is also called `delete_expense`. Importing the helper into `app.py` and then defining the route function of the same name makes one overwrite the other, and the route would call itself or fail. One must be renamed or imported under an alias. The spec does not mention this.
2. **The inline-style exception is avoidable and conflicts with Step 04.** Step 04 forbids inline styles anywhere in `profile.html`. This spec allows one, `style="display:inline"`, but the same effect can come from a CSS class (for example an inline-form class in the stylesheet). A class keeps the rule intact and removes the exception.
3. **Wrong stylesheet, but it works.** `.btn-delete` goes in `static/css/style.css`, while the profile page's own styles live in `profile.css`. `base.html` already loads `style.css`, so the style applies. It is simply not where the profile styles are. The existing `--danger` and `--danger-light` variables supply the danger colour, so no new variable is needed.
4. **405 comes before login.** A GET returns 405 even when logged out, because the method check runs before the handler. The Definition of done requires 405 for any user, so this is intended, but a logged-out GET never reaches the `/login` redirect.
5. **Double ownership check.** The handler calls `get_expense_by_id` and then `delete_expense`, both scoped to the user. This is deliberate (404 for the wrong user, and the delete is also guarded) and costs one extra query.
6. **No-JavaScript deletion.** The confirm dialog is browser-side only. With scripts disabled the form submits without confirmation. The server has no second confirmation step.
7. **`delete_expense` return value.** It is not stated whether the helper returns the number of rows deleted. The unit tests only check that no error is raised and the database is correct.
8. **Success feedback.** There is no flash message after a deletion, so the only sign is the row disappearing.
9. **Hard delete.** Deletion is permanent with no undo or soft delete, as the prompt states.
10. **Two Definition of done items are manual.** Confirming and cancelling the browser dialog cannot be checked by the route tests, and no test checks that each row shows both "Edit" and "Delete".
11. **No CSRF protection.** A POST form with no token can be submitted from another site while the user is logged in. This is a known gap for this stage of the project.
12. **Test isolation.** Tests use a seeded user and another user's expense, with no statement on a separate test database.

## 6. Cross-spec observations

- **Step 06 filter.** The redirect to `url_for("profile")` carries no filter parameters, so an active filter is lost after deleting an expense.
- **Step 08 Actions column.** This step builds on the column added there; the Edit link and the Delete form share one table cell.
- **Step 07 and 08 validation holes.** They do not apply here, because delete takes no user input beyond the id.

## 7. Recommendations

- Rename the query helper (for example `delete_expense_by_id`) or the route function, and say so in Files to change.
- Replace the inline `display:inline` with a CSS class, and drop the exception from the rules.
- Optionally put `.btn-delete` in `profile.css` alongside the other profile styles.
- State whether the helper returns the number of rows deleted.
- Add a route test that the profile page shows both actions, and optionally a flash message after deletion.
