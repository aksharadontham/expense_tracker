# Review Report: 05-backend-routes-for-profile-page.md

- **Spec reviewed:** `.claude/specs/05-backend-routes-for-profile-page.md`
- **Checked against:** `Spec_05-backend-routes-for-profile-page_prompt.md`
- **Verdict:** Compliant. All 10 required sections are present, in the order the prompt lists them, with every requested point covered, including the unit-test table and the route tests. No blocking issues. One deliberate addition (the test file under Files to create) and several gaps are listed below. The main risk is that the seed-data expectations (₹346.24, "Bills") are not backed by the Step 01 spec.

## 1. Section-by-section compliance

| Section | Status | Notes |
|---|---|---|
| Overview | Pass | All four points: live queries replace hardcoded data; the four static sections named; every user sees their own expenses; three parallel subagents integrated into one `/profile` route |
| Depends on | Pass | Steps 01, 02, 03 and 04 with the stated reasons |
| Routes | Pass | No new routes; `GET /profile` modified in place |
| Database changes | Pass | No changes; required columns listed |
| Templates | Pass | ₹ symbol rule; no structural changes, only the Jinja variables become real |
| Files to change | Pass | `app.py` and `templates/profile.html` with the stated purposes |
| Files to create | Pass, with one addition | `database/queries.py` with all four helpers and their return shapes; the test file was added (see section 4) |
| New dependencies | Pass | None |
| Rules for implementation | Pass | All 11 rules present (see section 3) |
| Tests to write | Pass | File name; unit-test table with all eight rows; route tests for the unauthenticated and seed-user cases |
| Definition of done | Pass | All eight checkbox items present with the prompt's wording |

## 2. Format rules

| Rule | Status | Notes |
|---|---|---|
| Output only the Markdown spec | Pass | No prose outside the spec |
| No code | Pass | Only identifiers, one empty-result literal from the prompt, and short fragments |
| Bullet lists throughout | Pass | |
| Table for the unit test cases | Pass | Columns Function / Input / Expected output, as the prompt specifies |
| Checkbox list for Definition of done | Pass | |
| Section names exact, no numbers | Pass | Plain headings with the exact names |

## 3. Rules for implementation — detail

| Prompt rule | In spec |
|---|---|
| No SQLAlchemy or ORMs; raw `sqlite3` via `get_db()` | Yes |
| Parameterised queries only | Yes |
| `PRAGMA foreign_keys = ON` on every connection (handled in `get_db()`) | Yes |
| Currency always ₹, never £ or $ | Yes |
| `member_since` from `users.created_at`, formatted "Month YYYY" | Yes |
| `pct` values sum to 100, integer rounding, largest category absorbs remainder | Yes |
| No expenses: zeros and empty lists, never raise | Yes |
| Helpers call `get_db()` internally and close before returning | Yes |
| CSS variables, no hardcoded hex | Yes |
| No inline styles | Yes |
| Templates extend `base.html` | Yes |

## 4. Deviations and additions

- **Test file under Files to create:** `tests/test_backend_connection.py` is listed there, since the Tests to write section requires it. The prompt listed only `database/queries.py`.
- **Document title:** a `# Spec: Backend Routes for Profile Page` heading sits above Overview.
- **Inline code formatting:** paths and identifiers are in inline code, where the prompt gave plain text.
- No content was removed.

## 5. Gaps and ambiguities

1. **Seed-data expectations are not backed by Step 01.** The tests and Definition of done require a total of 346.24, a count of 8 and "Bills" as the top category. The Step 01 spec fixes only the count (8) and the category coverage (all 7); it does not fix amounts. If `seed_db()` uses different amounts these checks fail even if the queries are correct.
2. **"Bills" depends on the category split.** Eight expenses across seven categories means one category appears twice. If that category is not Bills, or its total exceeds Bills, the expected top category is wrong. The rule "highest single-category total" does not state a tie-break either.
3. **Missing user is not handled in the route.** `get_user_by_id` returns `None` for a non-existent id, but no rule says what `/profile` does when the session points at a deleted or stale user (redirect to `/login`, clear the session or 404). The template would otherwise fail on `None`.
4. **`member_since` parsing is undefined.** The format is "Month YYYY", but the source `created_at` string format is not stated, so the parse depends on the default timestamp format chosen in Step 01.
5. **Money formatting is loose.** The tests expect `total_spent` to equal 346.24 and the page to show ₹346.24 and ₹0.00, but nothing fixes two-decimal formatting or floating-point rounding when summing REAL values. The empty case returns the integer 0 while the page shows ₹0.00.
6. **Ordering ties.** "Newest-first" does not say how same-date expenses are ordered (for example by `id` or `created_at`). The test for newest-first order may be flaky if two seed expenses share a date.
7. **Row limit.** `get_recent_transactions` defaults to `limit=10`. The seed has 8, so the tests pass, but a user with more than 10 expenses sees only the latest 10 with no mention of a "view all" path.
8. **Summary stats scope.** It is not stated whether `total_spent` and the category breakdown cover all time or only the transactions shown. As written they cover all expenses, which is the intent, but it is implicit.
9. **Rounding edge case.** The percentage rule does not cover a zero total. With the empty-user rule this should not arise, since the list is empty, but a user whose expenses are all zero would divide by zero.
10. **Test database isolation.** Tests rely on the seed user in `spendly.db`. The spec does not say whether tests use a separate test database or how the unit tests create a "user with no expenses".
11. **Query helpers split across files.** `get_user_by_email` lives in `database/db.py`, but `get_user_by_id` is placed in `database/queries.py`. This is as the prompt specifies, and may confuse later readers.
12. **Overview wording on subagents.** The three parallel subagents describe how the work is built, not app behavior, and there are four helpers for three subagents. This is as written in the prompt. `get_user_by_id` appears to be handled with the integration.

## 6. Cross-spec observations

- **Later signature changes:** Step 06 adds `date_from` and `date_to` parameters to three of these helpers, and Step 08 changes `get_recent_transactions` to also return `id`. The Step 05 return shape for `get_recent_transactions` (`date`, `description`, `category`, `amount`) omits `id`, so the Step 08 change is a deliberate extension.
- **`profile.html` currency:** Step 04 hardcoded values without a symbol rule, so the ₹ requirement in this step may mean reworking the template as well as the data source.

## 7. Recommendations

- Add the 8 seed expenses (amounts, categories and dates) to the Step 01 spec, or restate them in this spec, so 346.24 and "Bills" are checkable.
- Add a rule for a missing user in the profile route (clear the session and redirect to `/login` is the simplest).
- State the `created_at` format and the "Month YYYY" conversion in one place.
- State two-decimal rounding for amounts and totals, and a tie-break for same-date ordering.
- Say whether tests use a separate test database and how a no-expenses user is created.
