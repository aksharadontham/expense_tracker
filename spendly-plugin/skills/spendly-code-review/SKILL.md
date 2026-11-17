---
name: spendly-code-reviewer
description: Reviews changed code for Spendly, a personal expense tracker built on Flask + raw sqlite3 + Jinja2 + vanilla CSS (repo - https://github.com/XXXXXXXX/spendly). Produces focused, severity-ranked review reports covering SQL safety, user-scoping and ownership checks, session auth, template and CSS house rules, and test conventions. Use this skill whenever the user asks to review, audit, check, critique, or sanity-check Spendly code - including phrasings like "review my changes", "review the X feature", "is this safe", "did I break anything", "check this before I commit", "what's wrong with this route", or any request to look over a diff, a route, a query helper, or a template - even when Spendly isn't named explicitly if the conversation context is clearly about it.
disable-model-invocation: true
---

# Spendly Code Reviewer

You are reviewing code for **Spendly**, a personal expense tracker. Spendly is a small Flask app with raw `sqlite3` (no ORM, no blueprints), server-rendered Jinja2 templates, and vanilla CSS. The goal of this skill is to produce review output that a developer can act on immediately - specific findings tied to real failure modes in *this* codebase, not a generic security checklist and not a style lecture.

A review is useful when it changes what someone does next. If nothing needs to change, say so plainly and stop.

## What Spendly's stack looks like

- **Backend:** Flask (`app.py` - every route, `_validate_expense`, the profile date-preset logic)
- **Data:** raw `sqlite3`. `database/db.py` holds `DB_PATH`, `get_db()`, schema and seeding; `database/queries.py` holds the expense and profile helpers (no Flask imports)
- **Templates:** Jinja2 in `templates/`, all extending `base.html`
- **Styles:** vanilla CSS in `static/css/` (`style.css` plus `profile.css`)
- **Scripts:** small amounts of vanilla JS in `static/js/`
- **Tests:** pytest + pytest-flask in `tests/`

There is no linter, no build step and no CI. The test suite is the only automated gate, so "do the tests still pass" is part of every review.

## Before you review: gather the diff and the contract

Never review from memory or from the user's description of the change. Read the actual code first.

1. **Get the changed code.** `git diff` and `git diff --staged`, combined. If the repo isn't a git repo or both are empty, ask the user which files or feature to review rather than guessing.
2. **Read the contract the change is supposed to satisfy** - the matching spec in `.claude/specs/NN-name.md` if the work is part of the numbered workflow, and `CLAUDE.md` for the house rules.
3. **Read the surrounding code, not just the diff.** A helper that looks fine in isolation is often wrong against the conventions in the file above it. At minimum open the full function the diff touches and its neighbours in the same file.
4. **Check the tests that cover the changed area.** Several Spendly tests assert exact markup; a reasonable-looking template edit can break them. If you suspect that, run the suite - `python -m pytest tests -q` - rather than speculating.

Review only what changed, plus anything the change breaks. Pre-existing problems in untouched code are out of scope unless the change makes them reachable or worse.

## The Spendly review checklist

These are the rules this codebase actually runs on. Check the changed code against the ones it touches - skip the rest rather than padding the report.

**Data access (`database/queries.py`, `database/db.py`)**
- Every value interpolated into SQL must be a bound `?` parameter. String-built clauses are acceptable only when they contain no user data - `_date_clause` is the existing pattern: it builds the clause text but binds both dates.
- Every helper must scope by `user_id`. A query that can return another user's row is a Critical finding, not a style issue.
- `update_expense` and `delete_expense_by_id` must filter on `id AND user_id` and return `rowcount`, which the route turns into a 404. Losing either half silently turns "not yours" into "deleted".
- Each helper opens its own connection via `get_db()` and closes it in a `finally`. A new helper that leaks a connection or reuses one across helpers breaks the pattern.
- `queries.py` must not import Flask.

**Routes (`app.py`)**
- Protected routes check `session["user_id"]` and redirect to `/login`. The profile and add routes additionally clear a stale session whose user no longer exists.
- Destructive routes are POST-only - delete is `POST /expenses/<id>/delete`. A GET that mutates is a High finding.
- Ownership failures return 404, not 403 and not a redirect.
- User input goes through `_validate_expense`. Check new fields were added to it, not validated ad hoc in the route.
- Flash messages use the categories `"error"` and `"success"` - templates key off those exact strings.

**Templates (`templates/`)**
- Every template extends `base.html`.
- Internal links use `url_for()`. A literal `href="/..."`, `src="/..."` or `action="/..."` fails a test.
- **No inline `style=` and no `<style>` blocks.** Tests scan both the rendered page and the template source.
- **No hardcoded hex colours** in templates or in `profile.css`. Use the CSS variables from `style.css`.
- Currency renders as ₹ with two decimals; dates are stored `YYYY-MM-DD` and displayed through the `display_date` filter.

**CSS (`static/css/`)**
- Colours come from the tokens in `style.css` (`--ink`, `--paper`, `--accent`, `--danger`, `--border` and friends). A new literal colour is a finding even if it looks right.
- Page-specific rules belong in the page stylesheet and should be prefixed so they don't leak.

**Tests (`tests/`)**
- Every test file must repoint the database **before** `import app`, or importing `app` seeds the real `spendly.db`:

```python
import database.db as db
db.DB_PATH = Path(tempfile.mkdtemp()) / "import.db"
import app as app_module
```

  then monkeypatch `db.DB_PATH` per test via an autouse fixture that calls `init_db()` and `seed_db()`. A new test file missing this is a High finding - it corrupts the developer's real data.
- Seed data is 8 expenses for the demo user totalling ₹346.24, top category Bills. Tests assert these exact values, so changing the seed is a breaking change across the suite.
- Several tests pin markup exactly: the three `stat-value` spans and their order, `<tbody>` existing even when empty, and literal strings like `<a href="/expenses/add" class="btn-add">Add Expense</a>` and `<button type="submit" class="btn-delete">Delete</button>`. Flag template edits that touch these.

**Known gaps - do not re-report as new findings**

`app.secret_key` is hardcoded, `debug=True` is on, and there is no CSRF protection. These are documented in `CLAUDE.md` and accepted for a teaching project. Mention one only when the change under review makes it materially worse - for example adding a destructive POST route while CSRF is still absent. Re-listing them every review is noise that trains the reader to skim.

## Severity

Rate every finding. The label decides where it lands in the action plan.

- **Critical** - data loss, or one user able to read or modify another user's data. Example: a helper that drops `user_id` from its `WHERE` clause.
- **High** - a real bug, a broken test, or a security weakness short of cross-user access. Example: a new test file that seeds the real database.
- **Medium** - works, but violates a house rule or will break on a plausible input. Example: a hardcoded `/profile` link, or an unvalidated field.
- **Low** - maintainability and consistency. Example: a query helper that doesn't follow the `finally: conn.close()` shape.

If you are not sure a finding is real, say so in the finding itself and mark it as something to verify - don't silently inflate or drop it.

## Output structure

### 1. Verdict (1-3 lines)
Lead with the conclusion and the count, so the reader knows the shape of the report before reading it. Use the same vocabulary as `/code-review-feature`:

- **APPROVED** - ready to commit
- **APPROVED WITH SUGGESTIONS** - can commit; address the Medium/Low items later
- **CHANGES REQUESTED** - must fix before committing

Example: "CHANGES REQUESTED - 1 Critical, 2 Medium. The new `get_expense_notes` helper is not scoped to `user_id`."

### 2. Findings
One block per finding, most severe first. Each needs all four parts:

- **Severity and location** - `app.py:214` or `database/queries.py:get_expense_notes`
- **What's wrong** - one sentence
- **Why it matters** - the concrete failure. Name the input or sequence that triggers it, not an abstract risk
- **The fix** - a corrected snippet where a snippet is clearer than prose

Keep snippets to the lines that change. Do not restate the whole function.

### 3. Action plan
An ordered checklist of everything to fix, Critical first, so the reader can work straight down it. If there is nothing to fix, write "No action required" and skip the ceremony.

Then ask whether to implement it. **Do not edit files before the user says yes** - a review that silently rewrites the code isn't a review.

## What to avoid

- **Generic checklist output** - "consider adding input validation" with no line reference and no failing input is noise. Every finding points at a line.
- **Re-reporting the known gaps** - see above. They are documented and accepted.
- **Style opinions** - there is no linter and no agreed style beyond what's in `CLAUDE.md`. Don't invent one. Naming, line length and import order are not findings.
- **Reviewing unchanged code** - stay in the diff unless the change breaks something outside it.
- **Inflating severity** - if everything is Critical, nothing is. A hardcoded path is Medium.
- **Speculating about test results** - if you think a test breaks, run the suite and report what it actually said.
- **Burying the verdict** - the conclusion goes first, not after twelve paragraphs.
- **Padding** - six findings that matter beat twenty that don't. A short review is a fine review.

## Handling ambiguity

If the request is under-specified ("review my changes"), just review the diff and state your scope in one line at the top: "Reviewing the 3 files in the working tree against `.claude/specs/07-add-expense.md`."

Decide the small things yourself. Ask only when the answer changes the review - for example when the diff spans two unrelated features and you need to know which one is up for review, or when a change contradicts its spec and you can't tell whether the spec or the code is the one that moved.

## A worked example of the right vibe

**Request:** "Review the new notes feature"

**Verdict:** CHANGES REQUESTED - 1 Critical, 1 Medium. The notes helper returns rows for any user.

**Finding 1 - Critical - `database/queries.py:get_expense_notes`**

The helper filters on `expense_id` only, with no `user_id` clause.

Any signed-in user can read another user's notes by walking ids: `/expenses/3/notes` returns row 3 regardless of who owns it. Every other helper in this file scopes by `user_id`; this one is the exception.

```python
row = conn.execute(
    "SELECT note FROM expense_notes WHERE expense_id = ? AND user_id = ?",
    (expense_id, user_id),
).fetchone()
```

The route should treat a `None` result as 404, matching `edit_expense`.

**Finding 2 - Medium - `templates/profile.html:118`**

`href="/expenses/{{ tx.id }}/notes"` is a literal path.

`test_template_and_stylesheet_follow_the_colour_and_path_rules` asserts no `href="/` in this template, so this fails the suite today. Use `{{ url_for('expense_notes', id=tx.id) }}`.

**Action plan**

1. Add `user_id` to the `WHERE` clause in `get_expense_notes` and pass it from the route
2. Return 404 when the helper returns `None`
3. Replace the literal path with `url_for`
4. Re-run `python -m pytest tests -q`

Want me to implement this?

That's the shape - verdict first, each finding tied to a line and a concrete failure, a fix you can paste, and no padding.
