# Spec: Date Filter for Profile Page

## Overview

- Step 06 adds a date-range filter to the existing `/profile` route so users can narrow the transaction list, summary stats, and category breakdown to a specific period.
- The filter is driven entirely by query-string parameters (`date_from` and `date_to`) on `GET /profile` — no new routes required.
- A compact filter bar with four quick-select preset buttons ("This Month", "Last 3 Months", "Last 6 Months", "All Time") and two `<input type="date">` fields lets users pick any custom range.
- All three data sections (summary stats, recent transactions, category breakdown) must respect the active date filter.

## Depends on

- Step 01 — Database setup (`expenses` table with `date` column must exist)
- Step 04 — Profile page UI (template with all four sections must exist)
- Step 05 — Backend connection (`get_summary_stats`, `get_recent_transactions`, `get_category_breakdown` in `database/queries.py` must exist and be wired to the `/profile` route)

## Routes

- No new routes.
- The existing `GET /profile` route is modified to read two optional query parameters:
  - `date_from` — ISO date string `YYYY-MM-DD`, inclusive lower bound
  - `date_to` — ISO date string `YYYY-MM-DD`, inclusive upper bound
- If either parameter is absent or malformed, the route falls back to an unfiltered "All Time" view — never errors out.
  - this includes a half-filled range: if only one of `date_from` and `date_to` is valid, the filter is ignored and the unfiltered view is shown (open-ended ranges are not supported)
- "Today" means the server's local date.

## Database changes

- No database changes.
- The `expenses.date` column (TEXT, `YYYY-MM-DD`) already supports `BETWEEN` comparison in SQLite.

## Templates

- Modify: `templates/profile.html`
  - Add a block that displays flashed messages above the filter bar, so "Start date must be before end date." is visible
  - Add a filter bar section above the summary stats row containing:
    - Four quick-select preset buttons: "This Month", "Last 3 Months", "Last 6 Months", "All Time"
      - each is a link to `/profile` with the appropriate `date_from`/`date_to` query params computed in `app.py`
      - "All Time" passes no query params (clean `/profile` URL)
    - A custom range sub-form with two `<input type="date">` fields (`date_from`, `date_to`) and an "Apply" submit button
      - the form uses `method="get"` with the action built by `url_for('profile')`, so the values arrive as query parameters
      - both date fields are required, so a half-filled range cannot be submitted
      - the fields are pre-filled with the active `date_from` and `date_to` when a filter is applied, and empty otherwise
    - The currently active preset or custom range must be visually highlighted with an active state on the button
      - a preset is active when the validated range equals that preset's computed range
      - "All Time" is active when no filter is applied
      - any other valid range is a custom range, and the "Apply" button shows the active state
  - No structural changes to any existing section — only the Jinja variables fed into them change when a filter is active.

## Files to change

- `app.py`
  - In the `profile()` view: read `date_from` and `date_to` from `request.args`
  - Validate both values are well-formed ISO dates using `datetime.strptime(value, "%Y-%m-%d")`; on `ValueError` treat as absent
  - If `date_from` > `date_to` after validation: treat both as absent and flash "Start date must be before end date."
  - Compute preset date ranges in `app.py` — never in the template:
    - "This Month": `date_from` is the first day of the current month and `date_to` is the last day of the current month, so expenses dated later in the month are included
    - "Last 3 Months": `date_from` is the same day three calendar months before today (clamped to the last day of the month if that month is shorter) and `date_to` is today
    - "Last 6 Months": same rule, six calendar months back, and `date_to` is today
    - "All Time": no parameters
  - Pass validated `date_from`, `date_to`, and preset URL params back to the template so the filter bar can reflect the active state
  - Pass `date_from` and `date_to` to each of the three query helpers
- `database/queries.py`
  - `get_summary_stats(user_id, date_from=None, date_to=None)`
    - when both params are provided, add `AND date BETWEEN ? AND ?` to the expenses queries
    - when absent, behave identically to Step 05 (unfiltered)
  - `get_recent_transactions(user_id, limit=10, date_from=None, date_to=None)`
    - same pattern; ordering newest-first and limit remain unchanged
  - `get_category_breakdown(user_id, date_from=None, date_to=None)`
    - same pattern; percentage recalculation logic remains unchanged
- `templates/profile.html` — add the filter bar (see Templates section above)
- `static/css/profile.css` — add styles for the filter bar and active-preset button state using CSS variables only

## Files to create

- `tests/test_date_filter.py`

## New dependencies

- None

## Rules for implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`.
- Parameterised queries only — never string-format dates into SQL; use `?` placeholders even for date-range bounds.
- Date validation in `app.py`: use `datetime.strptime(value, "%Y-%m-%d")`; on `ValueError` treat the param as absent (fall back to no filter).
- Preset links must be generated with `url_for("profile", date_from=..., date_to=...)` — never hardcoded URL strings in the template.
- When `date_from` and `date_to` are both absent, all three query helpers must behave identically to their Step 05 behaviour (unfiltered).
- If `date_from` > `date_to` after validation, treat both as absent and flash: "Start date must be before end date."
- "All Time" preset must pass no query params (clean `/profile` URL).
- Preset date calculations must be computed in `app.py`, not in the template.
- The filter applies to a range only when both dates are valid; a half-filled or malformed range is ignored.
- The summary stats and category breakdown cover every expense in the active range; the transaction table still shows only the latest 10 of them, so the transaction count can exceed the rows shown.
- Filter parameters are not carried through other routes; adding, editing or deleting an expense returns to the unfiltered profile page.
- Use CSS variables — never hardcode hex values.
- No inline styles.
- All templates extend `base.html`.
- Use `url_for()` for every internal link — never hardcode paths.

## Tests to write

- File: `tests/test_date_filter.py`
- Tests run against a temporary database seeded with the Step 01 demo data (8 expenses on days 1, 3, 5, 8, 10, 12, 15 and 18 of the current month).
- Unit tests:

| Function | Input | Expected output |
|---|---|---|
| `get_summary_stats` | No `date_from` or `date_to` | Same result as Step 05: total 346.24, count 8, top category "Bills" |
| `get_summary_stats` | Range from day 1 to day 8 of the current month | Total 218.50, count 4, top category "Bills" |
| `get_summary_stats` | Range from day 3 to day 3 (single day, inclusive bounds) | Total 38.50, count 1, top category "Food" |
| `get_summary_stats` | Range with no expenses | `{"total_spent": 0, "transaction_count": 0, "top_category": "—"}` |
| `get_recent_transactions` | Range from day 1 to day 8 | 4 rows, newest first (Health, Transport, Food, Bills) |
| `get_category_breakdown` | Range from day 1 to day 8 | 4 categories; `pct` values are integers summing to 100 |
| `get_category_breakdown` | Range with no expenses | Empty list |

- Route tests:
  - `GET /profile` with no parameters → 200; same data as Step 05
  - `GET /profile` with a valid `date_from` and `date_to` → 200; only expenses within the range appear in all three sections
  - `GET /profile` with `date_from` later than `date_to` → 200; response contains "Start date must be before end date."; unfiltered data shown
  - `GET /profile` with `date_from=not-a-date` → 200; unfiltered data shown, no error message
  - `GET /profile` with only `date_from` → 200; unfiltered data shown
  - `GET /profile` for the "This Month" preset → all 8 seed expenses appear
  - The "Last 3 Months" preset range starts on the same day three calendar months ago, clamped for shorter months (for example 31 May gives 28 or 29 February)
  - The filter bar marks "All Time" active with no parameters, a preset active when its range is applied, and the custom range active for any other valid range

## Definition of done

- [ ] Visiting `/profile` with no query params returns the same data as Step 05 (unfiltered, all expenses)
- [ ] Clicking "This Month" filters all three sections to the current calendar month only
- [ ] Clicking "Last 3 Months" filters to expenses in the 3-month window ending today
- [ ] Clicking "Last 6 Months" filters to expenses in the 6-month window ending today
- [ ] Clicking "All Time" removes any active filter and shows all expenses
- [ ] Submitting a custom date range with valid `date_from` and `date_to` shows only expenses within that range in all three sections
- [ ] Submitting a range where `date_from` > `date_to` shows a flash error and falls back to the unfiltered view
- [ ] Submitting a malformed date string (e.g. `date_from=not-a-date`) does not crash the app — it silently falls back to the unfiltered view
- [ ] The active preset button or custom-range fields visually indicate which filter is currently applied
- [ ] All amounts continue to display the ₹ symbol regardless of active filter
- [ ] A user with no expenses in the selected range sees ₹0.00 total spent, 0 transactions, and an empty category breakdown — no errors
- [ ] A half-filled range (only one date) shows the unfiltered view with no error
- [ ] The "Start date must be before end date." message is visible on the page when a reversed range is submitted
- [ ] The custom range form submits by GET and its fields are pre-filled with the active range
- [ ] Expenses dated later in the current month than today still appear under "This Month"
- [ ] Tests pass against a temporary database
