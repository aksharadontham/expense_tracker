# Review Report: 01-database-setup.md

- **Spec reviewed:** `.claude/specs/01-database-setup.md`
- **Checked against:** `Spec_01_database_setup_prompt.md`
- **Verdict:** Compliant. All 14 required sections are present, in order, with every requested point covered. No blocking issues. A few minor gaps and ambiguities are listed below.

## 1. Section-by-section compliance

| # | Section | Status | Notes |
|---|---|---|---|
| 1 | Overview | Pass | States what the step does, why it is foundational, and that auth, profile and expense tracking depend on it |
| 2 | Depends on | Pass | States first step, no prerequisites |
| 3 | Routes | Pass | No new routes; placeholder routes unchanged |
| 4 | Database Schema | Pass | Both tables as tables; every column has name, type, constraints; `expenses.date` notes YYYY-MM-DD |
| 5 | Functions to Implement | Pass | `get_db()`, `init_db()`, `seed_db()` all covered with every listed behavior and the demo user details |
| 6 | Changes to app.py | Pass | Imports, startup calls inside `app.app_context()`, DB ready before routes |
| 7 | Files to Change | Pass | `database/db.py` and `app.py` only |
| 8 | Files to Create | Pass | None |
| 9 | Dependencies | Pass | No new packages; `sqlite3` and `werkzeug.security` |
| 10 | Categories (Fixed List) | Pass | Seven categories as a bullet list, stated as the only valid values |
| 11 | Rules for Implementation | Pass | All seven rules present |
| 12 | Expected Behavior | Pass | Function behavior and database-level constraints both covered |
| 13 | Error Handling Expectations | Pass | All three scenarios covered |
| 14 | Definition of Done | Pass | Checkbox list with all eight items, worded as in the prompt |

## 2. Format rules

| Rule | Status | Notes |
|---|---|---|
| Output only the Markdown spec | Pass | No prose outside the spec |
| No code | Pass | Only identifiers and SQL keywords in inline code (e.g. function names, `PRAGMA foreign_keys = ON`); no code blocks |
| Tables for schema definitions | Pass | |
| Checkbox list for Definition of Done | Pass | |
| Numbered sections exactly as listed | Pass | Titles and numbering match the prompt |

## 3. Additions beyond the prompt

- **Document title:** a `# Spec: Database Setup` heading above section 1.
- **Extra tables:** sections 5, 12 and 13 use tables for functions, constraints and error scenarios. The prompt asked for tables only for schema; this is not prohibited.
- **Seed coverage:** section 5 states that all seven categories appear at least once and one appears twice, to reach eight expenses. This is a reasonable inference from "8 expenses covering all 7 categories", but the prompt does not say it.
- **Extra constraint rows in section 12:** NOT NULL, auto-generated IDs and automatic timestamps are listed as enforced constraints. They follow from the schema.
- **Nullable description:** `expenses.description` is marked nullable. The prompt did not specify.

## 4. Gaps and ambiguities

1. **Timestamp default is unspecified.** The `created_at` columns say "DEFAULT current timestamp" without naming the expression or format. Date strings elsewhere must be YYYY-MM-DD, so the timestamp format could be inconsistent.
2. **Category is not enforced at the database level.** Section 10 says the seven values are the only valid ones, but the schema has no CHECK constraint and section 12 lists none. Invalid categories would only be rejected if application code does so.
3. **Date format is not enforced at the database level.** Same pattern: YYYY-MM-DD is a rule, with no constraint behind it.
4. **Amount sign is not constrained.** Nothing prevents zero or negative amounts.
5. **Foreign key delete behavior is unspecified.** The spec does not say what happens to a user's expenses if the user is deleted (reject, cascade or other).
6. **Seed data detail is thin.** Amounts, descriptions and exact dates for the 8 expenses are left to the implementer, so the Definition of Done "dates spread across the current month" is only loosely testable.
7. **Database path is loosely defined.** "Project root" is stated, but not how it is resolved (e.g. relative to `db.py` or to the working directory), which affects where the file appears depending on how the app is launched.

## 5. Recommendations

- Decide on items 2 to 5. If the app layer will validate categories, dates and amounts, add a line in section 11 saying so; otherwise add CHECK constraints to section 4.
- Name the timestamp default and format in section 4.
- Optionally list the 8 seed expenses in section 5 so the Definition of Done can be checked exactly.
- State the database path resolution rule in section 5.
