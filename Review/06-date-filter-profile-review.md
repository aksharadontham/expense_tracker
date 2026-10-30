# Review Report: 06-date-filter-profile.md

- **Spec reviewed:** `.claude/specs/06-date-filter-profile.md`
- **Checked against:** `Spec_06-date-filter-profile_prompt.md`
- **Verdict:** Compliant. All 9 required sections are present, in the order the prompt lists them, with every requested point covered. No blocking issues and no content added beyond the prompt. The gaps below are mostly inherited, and the most important ones concern how the presets compute their date ranges and how the flash message reaches the page.

## 1. Section-by-section compliance

| Section | Status | Notes |
|---|---|---|
| Overview | Pass | All four points: date-range filter on the existing route; query-string parameters `date_from` and `date_to`, no new routes; filter bar with four presets and two date inputs; all three data sections respect the filter |
| Depends on | Pass | Steps 01, 04 and 05 with the stated reasons |
| Routes | Pass | No new routes; both parameters described as ISO `YYYY-MM-DD`, inclusive; fallback to the unfiltered view when absent or malformed |
| Database changes | Pass | No changes; `expenses.date` supports `BETWEEN` |
| Templates | Pass | Filter bar above the summary stats row; four presets as links; "All Time" has no params; custom range sub-form with two date inputs and "Apply"; active state; no structural changes |
| Files to change | Pass | `app.py` (all six points), `database/queries.py` (three helpers with the new parameters), `templates/profile.html`, `static/css/profile.css` |
| Files to create | Pass | None |
| New dependencies | Pass | None |
| Rules for implementation | Pass | All 11 rules present (see section 3) |
| Definition of done | Pass | All eleven checkbox items present with the prompt's wording |

## 2. Format rules

| Rule | Status | Notes |
|---|---|---|
| Output only the Markdown spec | Pass | No prose outside the spec |
| No code | Pass | Only identifiers and short fragments in inline code |
| Bullet lists throughout | Pass | |
| Checkbox list for Definition of done | Pass | |
| Section names exact, no numbers | Pass | Plain headings with the exact names |

## 3. Rules for implementation — detail

| Prompt rule | In spec |
|---|---|
| No SQLAlchemy or ORMs; raw `sqlite3` via `get_db()` | Yes |
| Parameterised queries, `?` placeholders even for date bounds | Yes |
| Validate with `datetime.strptime(value, "%Y-%m-%d")`; `ValueError` means absent | Yes |
| Preset links generated with `url_for("profile", date_from=..., date_to=...)` | Yes |
| Both parameters absent: helpers behave as in Step 05 | Yes |
| `date_from` > `date_to`: treat both as absent and flash "Start date must be before end date." | Yes |
| "All Time" passes no query params | Yes |
| Preset dates computed in `app.py`, not the template | Yes |
| CSS variables, no hardcoded hex | Yes |
| No inline styles | Yes |
| Templates extend `base.html` | Yes |
| `url_for()` for every internal link | Yes |

## 4. Deviations and additions

- **Document title:** a `# Spec: Date Filter for Profile Page` heading sits above Overview.
- **Inline code formatting:** file paths, parameters and identifiers are in inline code, where the prompt gave plain text.
- No content was added or removed beyond that. Duplicated points in the prompt (for example the flash rule and the `strptime` rule appear in both Files to change and Rules) are kept in both places.

## 5. Gaps and ambiguities

These are inherited from the prompt. None contradicts it.

1. **Half-filled range.** Routes says that if either parameter is absent the route falls back to unfiltered. The queries apply the filter only when both are provided. So a custom range with only a start date shows everything. An open-ended range may have been intended, and the spec does not say.
2. **Preset window arithmetic is unspecified.** "3-month window ending today" could mean 90 days or three calendar months back. Calendar months also need a rule for short months (for example three months before 31 May is 28 or 29 February).
3. **"This Month" end date.** The preset is the current calendar month, but `date_to` could be today or the last day of the month. If the seed data places expenses later in the month than today, using today as the end would hide them. Step 01 says seed dates are spread across the current month.
4. **The flash message has no display path.** The spec says to flash an error, but Templates does not add a flash block to `profile.html` and does not say `base.html` renders flashes. The error could be set but never shown.
5. **Custom form method is not stated.** The custom range sub-form must submit by GET for the values to arrive in `request.args`, but the spec does not say so, nor what the form action is.
6. **Active-state logic is undefined.** It is not stated how the page decides which preset is active (compare the validated range to each preset's computed range?), what happens when a custom range happens to equal a preset, or whether the date inputs are pre-filled with the active range.
7. **Transaction count versus table rows.** `limit` stays at 10. The summary count covers every expense in range, while the table shows at most 10, so the two can disagree.
8. **Reversed and malformed behavior differs.** A malformed value falls back silently, while a reversed range flashes an error. This is as the Definition of done states, but the two cases look alike to the user.
9. **"Today" is server time.** Presets depend on the server's date, not the user's, which matters near midnight.
10. **No tests section.** Steps 05 and 07 to 09 include Tests to write; this step does not, although the date logic is the most error-prone part of the project so far.

## 6. Cross-spec observations

- **Filter lost after changes.** Steps 07, 08 and 09 redirect to `url_for("profile")` with no parameters. After adding, editing or deleting an expense, an active filter is dropped.
- **Step 05 test data.** The Step 05 route tests and Definition of done assume the unfiltered view, which stays valid because absent parameters mean unfiltered.

## 7. Recommendations

- Decide the half-filled case (open-ended range or fall back) and write it into Routes.
- Fix the preset arithmetic in one sentence, for example "three calendar months back from today, same day, clamped to the end of a shorter month", and set `date_to` for "This Month".
- Add a flash block to `profile.html` (or confirm `base.html` renders flashes) so the error is visible.
- State that the custom form uses GET and how the active state is derived.
- Add a Tests to write section with the preset ranges, the reversed range, malformed input and the empty-range case.
