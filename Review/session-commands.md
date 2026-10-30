# Session Commands

A record of everything asked and run in this Claude Code session (session name: `sdlc`).

- **Part A** lists every prompt you wrote, in the order you sent them.
- **Part B** lists the slash commands, shell commands and file tool operations that were run in response.

Placeholders used in Part B:

- `$PROJECT` = `C:/Users/Surya/Downloads/Expense_Tracker_Basic-main`
- `$SCRATCH` = the session scratchpad folder under `C:/Users/Surya/AppData/Local/Temp/claude/...`

# Part A — Prompts written in this session

Notes:

- Prompts are reproduced verbatim. Where the text came from a paste, the surrounding paste markers are omitted.
- The nine long spec-writing prompts (Steps 01 to 09) are included in full, taken from the prompt files saved in the project root (`Spec_0N_*.md`), which hold the same text as the pasted prompts.

## A1. Add footer links

~~~~text
1. Add two links to the footer in @templates/base.html:

- "Terms and Conditions"
- "Privacy Policy"

Both should be plain text links, no special styling needed for now.
Point both to "#" as placeholder hrefs since the pages don't exist yet.

Do not modify anything else on the page.
~~~~

## A2. Terms and Conditions page

~~~~text
Create a "Terms and Conditions" page for Spendly.

1. Add a new route in [@app.py](http://app.py/):
GET /terms → renders templates/terms.html
2. Create templates/terms.html with generic terms and conditions
content appropriate for a personal expense tracking app.
Include sections like: Acceptance of Terms, Use of Service,
User Data, Limitations of Liability, and Changes to Terms.
Extend base.html if it exists, otherwise match the style of
landing.html.
3. In @templates/landing.html, update the "Terms and Conditions"
footer link href from "#" to "/terms".
Also make sure the appearance of templates/terms.html matches the website theme
~~~~

## A3. Privacy Policy page

~~~~text
. Do the same as you did for the Terms and Conditions page,
but for Privacy Policy.

1. Add a new route in [@app.py](http://app.py/):
GET /privacy → renders templates/privacy.html
2. Create templates/privacy.html with generic privacy policy
content appropriate for a personal expense tracking app.
Include sections like: Data We Collect, How We Use Your Data,
Data Storage, Third Party Services, and Contact Us.
Match the style of terms.html.
3. In @templates/landing.html, update the "Privacy Policy"
footer link href from "#" to "/privacy".
4. Make sure the appearance looks like the website's theme
~~~~

## A4. Rename the session, then Step 01 spec prompt

Slash command: `/rename sdlc`

~~~~text
I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── database/
│   ├── __init__.py
│   └── db.py               ← stub file, functions defined but body is `pass`
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   └── register.html
├── .gitignore
├── app.py                  ← Flask app, placeholder routes only, no DB wired up
├── README.md
└── requirements.txt        ← werkzeug already listed

Write a spec document for Step 1: Replace the stub in database/db.py with a working SQLite implementation.

Save the output as:
  .claude/specs/01-database-setup.md

Create the .claude/specs/ folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use tables for schema definitions
- Use checkbox lists for Definition of Done
- Number all sections exactly as listed below

Include these 14 sections:

1. Overview
   — What this step does and why it is the foundational step
   — Mention that auth, profile, and expense tracking all depend on it

2. Depends on
   — State that this is the first step with no prerequisites

3. Routes
   — No new routes
   — Existing placeholder routes in app.py remain unchanged

4. Database Schema
   — Table A: users (id, name, email, password_hash, created_at)
   — Table B: expenses (id, user_id, amount, category, date, description, created_at)
   — For each column: name, SQLite type, and constraints (PK, autoincrement, NOT NULL, UNIQUE, FK, DEFAULT)
   — expenses.date must note YYYY-MM-DD format requirement

5. Functions to Implement (database/db.py)
   — get_db(): opens spendly.db in project root, sets row_factory = sqlite3.Row,
     enables PRAGMA foreign_keys = ON, returns connection
   — init_db(): creates both tables with CREATE TABLE IF NOT EXISTS, safe to call multiple times
   — seed_db(): checks if users table already has rows — if yes return early;
     otherwise insert one demo user (name: Demo User, email: demo@spendly.com,
     password: demo123 hashed via werkzeug) and 8 sample expenses linked to that user,
     covering all 7 categories, with dates spread across the current month

6. Changes to app.py
   — Import get_db, init_db, seed_db from database.db
   — Call init_db() and seed_db() inside app.app_context() on startup
   — DB must be ready before any route is served

7. Files to Change
   — database/db.py and app.py only

8. Files to Create
   — None

9. Dependencies
   — No new pip packages
   — Use sqlite3 (stdlib) and werkzeug.security (already installed)

10. Categories (Fixed List)
    — Food, Transport, Bills, Health, Entertainment, Shopping, Other
    — These are the only valid values; list them as a bullet list

11. Rules for Implementation
    — No ORM, no SQLAlchemy
    — Parameterized queries only — never string formatting in SQL
    — PRAGMA foreign_keys = ON on every connection
    — Store amount as REAL not INTEGER
    — Hash passwords with generate_password_hash from werkzeug.security
    — seed_db() must be idempotent (safe to call multiple times)
    — Dates must always be YYYY-MM-DD

12. Expected Behavior
    — What get_db(), init_db(), seed_db() must do when called correctly
    — What database-level constraints must enforce

13. Error Handling Expectations
    — Duplicate email insert → UNIQUE constraint failure
    — Expense with invalid user_id → foreign key constraint failure
    — Invalid queries → raise clear errors for debugging

14. Definition of Done
    — Checkbox list:
      - Database file created on app startup
      - Both tables exist with correct schema and constraints
      - Demo user exists with hashed password
      - 8 sample expenses exist across all 7 categories
      - No duplicate seed data on repeated runs
      - App starts without errors
      - Foreign key enforcement works
      - All queries use parameterized SQL
~~~~

## A5. Step 02 spec prompt (registration)

~~~~text
I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── .claude/
│   └── specs/
│       └── 01-database-setup.md   ← already complete
├── database/
│   ├── __init__.py
│   └── db.py                      ← get_db(), init_db(), seed_db() implemented
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   └── register.html              ← stub template, no form action or method yet
├── .gitignore
├── app.py                         ← GET /register exists as a stub route only
├── README.md
└── requirements.txt

Step 01 (database setup) is complete. Now write a spec for Step 02: Implement user registration.

Save the output as:
  .claude/specs/02-registration.md

Create the folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use bullet lists throughout — no tables needed for this spec
- Use a checkbox list for Definition of Done
- Use the section names exactly as listed below (no numbers, just headings)

Include these sections in order:

Overview
  — Describe that this step upgrades the existing stub GET /register route into a
    fully functional form handling both GET and POST
  — The form accepts name, email, password, confirm_password
  — On success: flash a success message and redirect to /login
  — This is the entry point for all authenticated features

Depends on
  — Step 01 — Database setup (users table, get_db())

Routes
  — GET /register — render registration form — public
    (already exists as stub, upgrade it)
  — POST /register — process form, validate input, insert user, redirect to /login — public

Database changes
  — No new tables or columns
  — The existing users table covers all requirements
  — One new DB helper to add to database/db.py:
      create_user(name, email, password)
      — hashes password with werkzeug
      — inserts a row into users
      — returns the new user's id
      — raises sqlite3.IntegrityError if email is already taken (UNIQUE constraint)

Templates
  — Modify templates/register.html:
      — change form action to url_for('register') with method="post"
      — add name attributes to all inputs: name, email, password, confirm_password
      — add a block to display flashed error messages
        (e.g. "Email already registered", "Passwords do not match")
      — keep all existing visual design unchanged

Files to change
  — app.py — upgrade register() to handle GET and POST; add flash + redirect logic
  — database/db.py — add create_user() helper
  — templates/register.html — wire up form action/method and flash message display

Files to create
  — None

New dependencies
  — None — uses werkzeug.security (already installed) and Flask's built-in
    flash, redirect, url_for

Rules for implementation
  — No SQLAlchemy or ORMs
  — Parameterised queries only — never use f-strings in SQL
  — Hash passwords with werkzeug.security.generate_password_hash — never store plaintext
  — app.secret_key must be set in app.py for flash() to work
    (use a hardcoded dev string for now)
  — Server-side validation must check in this order:
      1. All fields are non-empty
      2. password == confirm_password
      3. Email is not already registered (catch sqlite3.IntegrityError)
  — On any validation failure: re-render the form with a flashed error — do not redirect
  — On success: flash a success message and redirect to url_for('login')
  — Use abort(405) if an unsupported HTTP method reaches the route
  — All templates must extend base.html
  — Use CSS variables — never hardcode hex values
  — Use url_for() for every internal link — never hardcode URLs

Definition of done
  — Checkbox list:
    - GET /register renders the registration form without errors
    - Submitting with all valid fields creates a new user in users and redirects to /login
    - Submitting with mismatched passwords re-renders the form with an error, no DB insert
    - Submitting with an already-registered email re-renders with "Email already registered"
    - Submitting with any empty field re-renders with a validation error
    - Password is stored as a hash — never plaintext — verifiable by inspecting spendly.db
    - No duplicate user is created on repeated valid submissions with the same email
~~~~

## A6. Step 03 spec prompt (login and logout)

~~~~text
I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── .claude/
│   └── specs/
│       ├── 01-database-setup.md   ← complete
│       └── 02-registration.md     ← complete
├── database/
│   ├── __init__.py
│   └── db.py                      ← get_db(), init_db(), seed_db(), create_user() implemented
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html                 ← stub template, no form action or method yet
│   └── register.html              ← complete
├── .gitignore
├── app.py                         ← GET /login and GET /logout exist as stubs only
├── README.md
└── requirements.txt

Steps 01 and 02 are complete. Now write a spec for Step 03: Implement login and logout.

Save the output as:
  .claude/specs/03-login_logout.md

Create the folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use bullet lists throughout
- Use a checkbox list for Definition of Done
- Use the exact section names listed below — no numbers, just headings

Include these sections in order:

Overview
  — This step converts the /login stub into a functional POST handler that:
      — verifies credentials against the users table
      — stores the authenticated user's id in session["user_id"]
      — redirects to the landing page (until a dashboard route exists)
  — Also implements /logout, which clears the session and redirects to /
  — After this step the app can distinguish logged-in users from guests
  — This is a prerequisite for all expense features

Depends on
  — Step 01 — Database Setup (users table must exist)
  — Step 02 — Registration (create_user and password hashing must be in place;
    a user must exist to log in against)

Routes
  — GET /login — render login form — public
  — POST /login — validate credentials, set session, redirect — public
  — GET /logout — clear session, redirect to / — public (no login required)

Database changes
  — No database changes
  — The users table from Step 01 already stores email and password_hash
  — One new DB helper to add to database/db.py:
      get_user_by_email(email)
      — queries the users table by email
      — returns the matching user row or None if not found
      — must live in database/db.py, not inline in the route

Templates
  — Modify templates/login.html:
      — add a POST form with email and password fields
      — set form action to url_for('login') with method="post"
      — add a block to display flashed error messages
      — add a link to /register for new users

Files to change
  — app.py — implement login() as GET+POST handler; implement logout()
  — database/db.py — add get_user_by_email() helper
  — templates/login.html — add POST form and flash display

Files to create
  — None

New dependencies
  — None — werkzeug.security.check_password_hash is already available

Rules for implementation
  — No SQLAlchemy or ORMs — use raw sqlite3 via get_db()
  — Parameterised queries only — never use f-strings in SQL
  — Verify passwords with werkzeug.security.check_password_hash
  — Session key for the logged-in user must be session["user_id"] (integer)
  — Use flask.session — do not roll a custom session mechanism
  — On failed login show a generic flash error: "Invalid email or password."
    — do not reveal which field was wrong
  — After successful login redirect to url_for("landing") until a dashboard exists
  — logout() must call session.clear() then redirect to url_for("landing")
  — All templates must extend base.html
  — Use CSS variables — never hardcode hex values
  — Use url_for() for every internal link — never hardcode paths

Definition of done
  — Checkbox list:
    - GET /login renders the login form with email and password fields
    - Submitting with valid credentials (demo@spendly.com / demo123) sets
      session["user_id"] and redirects to /
    - Submitting with a wrong password shows "Invalid email or password." flash
      and stays on the login page
    - Submitting with an unregistered email shows the same generic error flash
    - GET /logout clears the session and redirects to /
    - After logout, session["user_id"] is no longer present
    - The /logout route no longer returns the raw stub string
~~~~

## A7. Review Step 01 spec

~~~~text
review the 01-database-setup.md against spec_01_database_setup_prompt.md and generate review report
~~~~

## A8. Context check, then Step 04 spec prompt (profile page)

Slash command: `/context`

~~~~text
I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── .claude/
│   └── specs/
│       ├── 01-database-setup.md   ← complete
│       ├── 02-registration.md     ← complete
│       └── 03-login_logout.md     ← complete
├── database/
│   ├── __init__.py
│   └── db.py                      ← get_db(), init_db(), seed_db(), create_user(),
│                                     get_user_by_email() all implemented
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html                 ← complete
│   └── register.html              ← complete
├── .gitignore
├── app.py                         ← GET /profile exists as a stub only
├── README.md
└── requirements.txt

Steps 01, 02, and 03 are complete. Now write a spec for Step 04: Implement the profile page with hardcoded UI data.

Save the output as:
  .claude/specs/04-profile.md

Create the folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use bullet lists throughout
- Use a numbered list for the four template sections
- Use a checkbox list for Definition of Done
- Use the exact section names listed below — no numbers, just headings

Include these sections in order:

Overview
  — This step replaces the /profile stub with a fully designed profile page
    showing static, hardcoded data
  — The goal is to establish the complete UI layout before any real DB queries
    are wired up in Step 05
  — Four sections to build: user info card, summary stats, transaction history
    table, category breakdown
  — Building UI first lets the team validate design in isolation and ensures
    templates are ready for the backend-connection step

Depends on
  — Step 01 — Database setup (schema must exist)
  — Step 02 — Registration (user accounts must be creatable)
  — Step 03 — Login + Logout (session must be set; /profile must be a protected route)

Routes
  — GET /profile — render the profile page — logged-in only
    (redirect to /login if not authenticated)

Database changes
  — No database changes
  — The existing users and expenses tables are sufficient
  — No DB queries in this step — all data is hardcoded

Templates
  — Create: templates/profile.html — full profile page extending base.html
  — Must contain four sections:
      1. User info card — avatar initials, name, email, member-since date
         (all hardcoded values)
      2. Summary stats row — total spent, number of transactions, top category
         (all hardcoded values)
      3. Transaction history table — list of recent expenses with date,
         description, category badge, amount (at least 3 hardcoded rows)
      4. Category breakdown — per-category totals as a simple list or
         progress-bar rows (at least 3 hardcoded categories)

Files to change
  — app.py — replace /profile stub with a real view function that:
      — redirects unauthenticated users to /login
      — passes hardcoded context variables (user dict, stats dict, expenses list,
        category breakdown list) to profile.html

Files to create
  — templates/profile.html

New dependencies
  — None

Rules for implementation
  — No SQLAlchemy or ORMs — use raw sqlite3 via get_db() if any DB call is ever needed
  — Parameterised queries only — never string-format SQL
  — Authentication guard: check session.get("user_id"); if absent,
    redirect(url_for("login"))
  — All data passed to the template must be hardcoded Python dicts/lists in
    app.py — no DB queries in this step
  — Use CSS variables — never hardcode hex values
  — No inline styles anywhere in profile.html
  — All templates must extend base.html
  — Category badges must use a CSS class, not inline colour styles
  — Use url_for() for every internal link — never hardcode paths

Definition of done
  — Checkbox list:
    - Visiting /profile without being logged in redirects to /login
    - Visiting /profile while logged in returns HTTP 200
    - The page displays a user info card with a name and email
    - The page displays at least three summary stat values
      (e.g. total spent, transaction count, top category)
    - The page displays a transaction history table with at least three
      hardcoded rows
    - The page displays a category breakdown section with at least three
      categories
    - The navbar shows the logged-in state (username + logout link)
    - No hex colour values appear in profile.html — only CSS variables
~~~~

## A9. Step 05 spec prompt (backend routes for profile page)

~~~~text
I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── .claude/
│   └── specs/
│       ├── 01-database-setup.md   ← complete
│       ├── 02-registration.md     ← complete
│       ├── 03-login_logout.md     ← complete
│       └── 04-profile.md         ← complete
├── database/
│   ├── __init__.py
│   └── db.py                      ← get_db(), init_db(), seed_db(), create_user(),
│                                     get_user_by_email() all implemented
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html                 ← complete
│   ├── register.html              ← complete
│   └── profile.html              ← complete with hardcoded data (Step 04)
├── .gitignore
├── app.py                         ← /profile renders hardcoded data from Step 04
├── README.md
└── requirements.txt

Steps 01 through 04 are complete. Now write a spec for Step 05: Replace all hardcoded
data in the /profile route with live SQLite queries.

Save the output as:
  .claude/specs/05-backend-routes-for-profile-page.md

Create the folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use bullet lists throughout
- Use a table for the unit test cases
- Use a checkbox list for Definition of Done
- Use the exact section names listed below — no numbers, just headings

Include these sections in order:

Overview
  — Step 05 replaces all hardcoded data in the /profile route with live queries
    against the SQLite database
  — The profile page currently renders a static demo user, fixed summary stats,
    a hand-typed transaction list, and a hardcoded category breakdown
  — This step wires those four sections to real data so every logged-in user
    sees their own expenses
  — Three parallel subagents handle the three independent data concerns —
    transaction history, summary stats, and category breakdown — before being
    integrated into the single /profile route

Depends on
  — Step 01 — Database setup (tables and get_db() exist)
  — Step 02 — Registration (users are stored in the database)
  — Step 03 — Login / Logout (session["user_id"] is set on login)
  — Step 04 — Profile page static UI (template already renders all four sections)

Routes
  — No new routes
  — The existing GET /profile route is modified in place

Database changes
  — No database changes
  — The users and expenses tables already have all required columns:
    user_id, amount, category, date, description, created_at

Templates
  — Modify: templates/profile.html
      — Amounts must be rendered with the ₹ symbol (Indian Rupee) — never £ or $
      — All four dynamic sections are already present in the template —
        no structural changes needed, only the Jinja variables they consume
        are now real

Files to change
  — app.py — replace hardcoded data in the profile() view with calls to the
    new query helpers in database/queries.py
  — templates/profile.html — confirm ₹ symbol is used for all currency display

Files to create
  — database/queries.py — pure query helpers with no Flask imports;
    one function per data concern:
      — get_user_by_id(user_id)
          → dict with name, email, member_since
      — get_summary_stats(user_id)
          → dict with total_spent, transaction_count, top_category
      — get_recent_transactions(user_id, limit=10)
          → list of dicts, each with date, description, category, amount
          → ordered newest-first
      — get_category_breakdown(user_id)
          → list of dicts, each with name, amount, pct
          → pct is percentage of total rounded to nearest int
          → ordered by amount descending

New dependencies
  — None

Rules for implementation
  — No SQLAlchemy or ORMs — raw sqlite3 only via get_db()
  — Parameterised queries only — never string-format values into SQL
  — PRAGMA foreign_keys = ON must be enabled on every connection
    (already handled in get_db())
  — Currency must always display as ₹ — never £ or $
  — member_since must be derived from users.created_at and formatted as
    "Month YYYY" (e.g. "January 2026")
  — pct values in category breakdown must sum to 100; use integer rounding
    and adjust the largest category to absorb any rounding remainder
  — If a user has no expenses, all helpers must return zeros and empty lists —
    never raise exceptions
  — All helpers in database/queries.py must call get_db() internally and
    close the connection before returning
  — Use CSS variables — never hardcode hex values
  — No inline styles
  — All templates extend base.html

Tests to write
  — File: tests/test_backend_connection.py
  — Unit tests — format as a table with columns: Function | Input | Expected output:
      — get_user_by_id with valid user_id → dict with correct name, email, member_since
      — get_user_by_id with non-existent id → None
      — get_summary_stats with user_id with expenses →
        correct total_spent, transaction_count, top_category
      — get_summary_stats with user_id with no expenses →
        {"total_spent": 0, "transaction_count": 0, "top_category": "—"}
      — get_recent_transactions with user_id with expenses →
        list ordered newest-first, each item has date, description, category, amount
      — get_recent_transactions with user_id with no expenses → empty list
      — get_category_breakdown with user_id with expenses →
        list ordered by amount desc; pct values are integers summing to 100
      — get_category_breakdown with user_id with no expenses → empty list
  — Route tests:
      — GET /profile unauthenticated → redirects to /login (302)
      — GET /profile authenticated as seed user:
          — returns 200
          — response contains "Demo User"
          — response contains "demo@spendly.com"
          — response contains ₹ symbol
          — total_spent matches sum of all seed expenses (346.24)
          — transaction_count is 8
          — top_category is "Bills" (highest single-category total)
          — transaction list appears in newest-first order
          — category breakdown contains all 7 categories

Definition of done
  — Checkbox list:
    - Logging in as demo@spendly.com / demo123 shows "Demo User" and
      "demo@spendly.com" on the profile page — not the hardcoded strings
    - Total spent displayed on the profile page equals ₹346.24
    - Transaction count displayed is 8
    - Top category displayed is "Bills"
    - Transaction list shows 8 rows ordered newest date first
    - Category breakdown shows 7 categories with percentages that add up to 100%
    - All amounts on the page display the ₹ symbol
    - Registering a brand-new user and visiting /profile shows ₹0.00 total spent,
      0 transactions, and an empty category breakdown — no errors
~~~~

## A10. Step 06 spec prompt (date filter)

~~~~text
I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── .claude/
│   └── specs/
│       ├── 01-database-setup.md              ← complete
│       ├── 02-registration.md                ← complete
│       ├── 03-login_logout.md                ← complete
│       ├── 04-profile.md                     ← complete
│       └── 05-backend-routes-for-profile-page.md  ← complete
├── database/
│   ├── __init__.py
│   ├── db.py                                 ← get_db(), init_db(), seed_db(),
│   │                                           create_user(), get_user_by_email()
│   └── queries.py                            ← get_user_by_id(), get_summary_stats(),
│                                               get_recent_transactions(),
│                                               get_category_breakdown() all implemented
├── static/
│   ├── css/
│   │   └── profile.css                       ← exists, styled with CSS variables
│   └── js/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html                            ← complete
│   ├── register.html                         ← complete
│   └── profile.html                          ← complete, wired to live DB queries
├── tests/
│   └── test_backend_connection.py            ← complete
├── .gitignore
├── app.py                                    ← /profile renders live data from queries.py
├── README.md
└── requirements.txt

Steps 01 through 05 are complete. Now write a spec for Step 06: Add a date-range filter
to the existing /profile route.

Save the output as:
  .claude/specs/06-date-filter-profile.md

Create the folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use bullet lists throughout
- Use a checkbox list for Definition of Done
- Use the exact section names listed below — no numbers, just headings

Include these sections in order:

Overview
  — Step 06 adds a date-range filter to the existing /profile route so users can
    narrow the transaction list, summary stats, and category breakdown to a
    specific period
  — The filter is driven entirely by query-string parameters (date_from and date_to)
    on GET /profile — no new routes required
  — A compact filter bar with four quick-select preset buttons ("This Month",
    "Last 3 Months", "Last 6 Months", "All Time") and two <input type="date">
    fields lets users pick any custom range
  — All three data sections (summary stats, recent transactions, category breakdown)
    must respect the active date filter

Depends on
  — Step 01 — Database setup (expenses table with date column must exist)
  — Step 04 — Profile page UI (template with all four sections must exist)
  — Step 05 — Backend connection (get_summary_stats, get_recent_transactions,
    get_category_breakdown in database/queries.py must exist and be wired to
    the /profile route)

Routes
  — No new routes
  — The existing GET /profile route is modified to read two optional query parameters:
      — date_from — ISO date string YYYY-MM-DD, inclusive lower bound
      — date_to — ISO date string YYYY-MM-DD, inclusive upper bound
  — If either parameter is absent or malformed, the route falls back to an
    unfiltered "All Time" view — never errors out

Database changes
  — No database changes
  — The expenses.date column (TEXT, YYYY-MM-DD) already supports BETWEEN
    comparison in SQLite

Templates
  — Modify: templates/profile.html
      — Add a filter bar section above the summary stats row containing:
          — Four quick-select preset buttons: "This Month", "Last 3 Months",
            "Last 6 Months", "All Time"
            — each is a link to /profile with the appropriate date_from/date_to
              query params computed in app.py
            — "All Time" passes no query params (clean /profile URL)
          — A custom range sub-form with two <input type="date"> fields
            (date_from, date_to) and an "Apply" submit button
          — The currently active preset or custom range must be visually
            highlighted with an active state on the button
      — No structural changes to any existing section — only the Jinja variables
        fed into them change when a filter is active

Files to change
  — app.py
      — In profile() view: read date_from and date_to from request.args
      — Validate both values are well-formed ISO dates using
        datetime.strptime(value, "%Y-%m-%d"); on ValueError treat as absent
      — If date_from > date_to after validation: treat both as absent, flash
        "Start date must be before end date."
      — Compute preset date ranges (e.g. first day of current month for
        "This Month") in app.py — never in the template
      — Pass validated date_from, date_to, and preset URL params back to the
        template so the filter bar can reflect the active state
      — Pass date_from and date_to to each of the three query helpers
  — database/queries.py
      — get_summary_stats(user_id, date_from=None, date_to=None)
          — when both params are provided add AND date BETWEEN ? AND ? to the
            expenses queries
          — when absent behave identically to Step 05 (unfiltered)
      — get_recent_transactions(user_id, limit=10, date_from=None, date_to=None)
          — same pattern; ordering newest-first and limit remain unchanged
      — get_category_breakdown(user_id, date_from=None, date_to=None)
          — same pattern; percentage recalculation logic remains unchanged
  — templates/profile.html — add filter bar (see Templates section above)
  — static/css/profile.css — add styles for filter bar and active-preset button
    state using CSS variables only

Files to create
  — None

New dependencies
  — None

Rules for implementation
  — No SQLAlchemy or ORMs — raw sqlite3 only via get_db()
  — Parameterised queries only — never string-format dates into SQL;
    use ? placeholders even for date-range bounds
  — Date validation in app.py: use datetime.strptime(value, "%Y-%m-%d");
    on ValueError treat the param as absent (fall back to no filter)
  — Preset links must be generated with url_for("profile", date_from=..., date_to=...)
    — never hardcoded URL strings in the template
  — When date_from and date_to are both absent, all three query helpers must
    behave identically to their Step 05 behaviour (unfiltered)
  — If date_from > date_to after validation, treat both as absent and flash:
    "Start date must be before end date."
  — "All Time" preset must pass no query params (clean /profile URL)
  — Preset date calculations must be computed in app.py, not in the template
  — Use CSS variables — never hardcode hex values
  — No inline styles
  — All templates extend base.html
  — Use url_for() for every internal link — never hardcode paths

Definition of done
  — Checkbox list:
    - Visiting /profile with no query params returns the same data as Step 05
      (unfiltered, all expenses)
    - Clicking "This Month" filters all three sections to the current calendar
      month only
    - Clicking "Last 3 Months" filters to expenses in the 3-month window
      ending today
    - Clicking "Last 6 Months" filters to expenses in the 6-month window
      ending today
    - Clicking "All Time" removes any active filter and shows all expenses
    - Submitting a custom date range with valid date_from and date_to shows
      only expenses within that range in all three sections
    - Submitting a range where date_from > date_to shows a flash error and
      falls back to the unfiltered view
    - Submitting a malformed date string (e.g. date_from=not-a-date) does not
      crash the app — it silently falls back to the unfiltered view
    - The active preset button or custom-range fields visually indicate which
      filter is currently applied
    - All amounts continue to display the ₹ symbol regardless of active filter
    - A user with no expenses in the selected range sees ₹0.00 total spent,
      0 transactions, and an empty category breakdown — no errors
~~~~

## A11. Step 07 spec prompt (add expense)

~~~~text
I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── .claude/
│   └── specs/
│       ├── 01-database-setup.md                   ← complete
│       ├── 02-registration.md                     ← complete
│       ├── 03-login_logout.md                     ← complete
│       ├── 04-profile.md                          ← complete
│       ├── 05-backend-routes-for-profile-page.md  ← complete
│       └── 06-date-filter-profile.md              ← complete
├── database/
│   ├── __init__.py
│   ├── db.py                                      ← get_db(), init_db(), seed_db(),
│   │                                                create_user(), get_user_by_email()
│   └── queries.py                                 ← get_user_by_id(), get_summary_stats(),
│                                                    get_recent_transactions(),
│                                                    get_category_breakdown()
├── static/
│   ├── css/
│   │   └── profile.css
│   └── js/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html                                 ← complete
│   ├── register.html                              ← complete
│   └── profile.html                              ← complete, with date-range filter
├── tests/
│   └── test_backend_connection.py                 ← complete
├── .gitignore
├── app.py                                         ← GET /expenses/add exists as a stub only
├── README.md
└── requirements.txt

Steps 01 through 06 are complete. Now write a spec for Step 07: Implement the Add Expense
feature at /expenses/add.

Save the output as:
  .claude/specs/07-add-expense.md

Create the folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use bullet lists throughout
- Use a table for the unit test cases
- Use a checkbox list for Definition of Done
- Use the exact section names listed below — no numbers, just headings

Include these sections in order:

Overview
  — Step 07 lets a logged-in user submit a new expense through a dedicated
    form page at /expenses/add
  — The route already exists as a GET placeholder; this step upgrades it to
    a full GET + POST handler
  — Validated data is inserted into the expenses table and the user is
    redirected back to the profile page on success
  — A reusable insert_expense() query helper is added to database/queries.py
  — An "Add Expense" button is added to profile.html and a nav link is added
    to base.html so users can navigate to the form

Depends on
  — Step 01 — Database setup (expenses table exists with all required columns)
  — Step 03 — Login / Logout (session["user_id"] is set and checked)
  — Step 04 / 05 — Profile page exists and is the natural redirect target
    after saving

Routes
  — GET /expenses/add — render the add-expense form — logged-in only
  — POST /expenses/add — validate and insert the new expense — logged-in only

Database changes
  — No database changes
  — The expenses table already has all required columns:
    id, user_id, amount, category, date, description, created_at

Templates
  — Create: templates/add_expense.html
      — extends base.html
      — form with method="POST" and action="/expenses/add"
      — Fields:
          — amount — number input, step="0.01", min="0.01", required
          — category — <select> with exactly 7 fixed options:
            Food, Transport, Bills, Health, Entertainment, Shopping, Other
          — date — <input type="date">, required, defaults to today's date
          — description — text input, optional, max 200 chars
      — Submit button labelled "Save Expense" and a cancel link back to /profile
      — Flash/error message block to display validation errors,
        re-populating previously submitted values on failure
  — Modify: templates/profile.html
      — Add an "Add Expense" button/link pointing to /expenses/add,
        near the transaction table heading
  — Modify: templates/base.html
      — Add an "Add Expense" link in the navbar visible only when
        session.user_id is set

Files to change
  — app.py — replace the GET-only placeholder at /expenses/add with a
    GET + POST handler:
      — GET: render add_expense.html; redirect to /login if not authenticated
      — POST: read form fields, validate, call insert_expense(),
        redirect to url_for("profile") on success
  — database/queries.py — add insert_expense(user_id, amount, category,
    date, description)
  — templates/profile.html — add "Add Expense" button
  — templates/base.html — add "Add Expense" navbar link for logged-in users

Files to create
  — templates/add_expense.html

New dependencies
  — None

Rules for implementation
  — No SQLAlchemy or ORMs — raw sqlite3 only via get_db()
  — Parameterised queries only — never string-format values into SQL
  — PRAGMA foreign_keys = ON must be enabled on every connection
    (already handled in get_db())
  — Unauthenticated access to both GET and POST /expenses/add must
    redirect to /login
  — Validation rules for POST:
      1. amount: required; must be a positive float greater than 0;
         parse with float(), catch ValueError
      2. category: required; must be one of the 7 fixed categories;
         reject anything else
      3. date: required; must be a valid YYYY-MM-DD date;
         parse with datetime.strptime
      4. description: optional; strip whitespace; store None if blank
  — On any validation error, re-render the form with the error message
    and previously submitted values pre-filled
  — After successful insert, redirect to url_for("profile") —
    do NOT render the form again
  — Currency must always display as ₹ — never £ or $
  — Use CSS variables — never hardcode hex values
  — No inline styles
  — All templates extend base.html
  — Use url_for() for every internal link — never hardcode paths

Tests to write
  — File: tests/test_add_expense.py
  — Unit tests — format as a table with columns: Function | Input | Expected output:
      — insert_expense with valid user_id, amount=50.0, category="Food",
        date="2026-03-20", description="Lunch"
        → row inserted; querying the DB returns the new row
      — insert_expense with description=None
        → row inserted with description stored as NULL
  — Route tests (bullet list):
      — GET /expenses/add unauthenticated → redirects to /login (302)
      — GET /expenses/add authenticated → returns 200; response contains
        the category <select> with all 7 options; response contains
        a form with method POST
      — POST /expenses/add unauthenticated → redirects to /login (302)
      — POST /expenses/add authenticated, valid data
        (amount=50.0, category=Food, date=2026-03-20, description=Lunch)
        → redirects to /profile (302); new expense row exists in the DB
          for the test user
      — POST /expenses/add authenticated, missing amount
        → returns 200; response contains an error message
      — POST /expenses/add authenticated, amount = 0
        → returns 200; response contains an error message
      — POST /expenses/add authenticated, non-numeric amount
        → returns 200; response contains an error message
      — POST /expenses/add authenticated, invalid category (not in fixed list)
        → returns 200; response contains an error message
      — POST /expenses/add authenticated, invalid date string
        → returns 200; response contains an error message
      — POST /expenses/add authenticated, no description (optional field)
        → redirects to /profile (302); row inserted with description = NULL

Definition of done
  — Checkbox list:
    - Visiting /expenses/add while logged out redirects to /login
    - Visiting /expenses/add while logged in shows a form with amount,
      category, date, and description fields
    - The category dropdown contains exactly: Food, Transport, Bills, Health,
      Entertainment, Shopping, Other
    - Submitting a valid expense redirects to /profile and the new expense
      appears in the transaction list
    - Submitting with a missing or zero amount re-renders the form with an
      error and previously entered values retained
    - Submitting with an invalid category re-renders the form with an error
    - Submitting with an invalid date re-renders the form with an error
    - Submitting without a description saves the expense with no error
    - The "Add Expense" button on the profile page navigates to /expenses/add
    - Navbar shows "Add Expense" link when logged in
~~~~

## A12. Step 08 spec prompt (edit expense)

~~~~text
I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── .claude/
│   └── specs/
│       ├── 01-database-setup.md                   ← complete
│       ├── 02-registration.md                     ← complete
│       ├── 03-login_logout.md                     ← complete
│       ├── 04-profile.md                          ← complete
│       ├── 05-backend-routes-for-profile-page.md  ← complete
│       ├── 06-date-filter-profile.md              ← complete
│       └── 07-add-expense.md                      ← complete
├── database/
│   ├── __init__.py
│   ├── db.py                                      ← get_db(), init_db(), seed_db(),
│   │                                                create_user(), get_user_by_email()
│   └── queries.py                                 ← get_user_by_id(), get_summary_stats(),
│                                                    get_recent_transactions(),
│                                                    get_category_breakdown(),
│                                                    insert_expense()
├── static/
│   ├── css/
│   │   └── profile.css
│   └── js/
├── templates/
│   ├── base.html                                  ← has "Add Expense" navbar link
│   ├── landing.html
│   ├── login.html                                 ← complete
│   ├── register.html                              ← complete
│   ├── profile.html                              ← complete, with date filter +
│   │                                               "Add Expense" button
│   └── add_expense.html                          ← complete
├── tests/
│   ├── test_backend_connection.py                 ← complete
│   └── test_add_expense.py                        ← complete
├── .gitignore
├── app.py                                         ← GET /expenses/<id>/edit exists
│                                                    as a stub only
├── README.md
└── requirements.txt

Steps 01 through 07 are complete. Now write a spec for Step 08: Implement the Edit
Expense feature at /expenses/<id>/edit.

Save the output as:
  .claude/specs/08-edit-expense.md

Create the folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use bullet lists throughout
- Use a table for the unit test cases
- Use a checkbox list for Definition of Done
- Use the exact section names listed below — no numbers, just headings

Include these sections in order:

Overview
  — Step 08 lets a logged-in user edit any of their own expenses via a
    pre-populated form at /expenses/<id>/edit
  — The GET handler loads the existing expense from the database and renders
    the form with its current values
  — The POST handler validates the submission and updates the row in place
  — Ownership is enforced: a user can only edit expenses that belong to them
  — Two new query helpers are added to database/queries.py:
    get_expense_by_id and update_expense
  — The transactions table in profile.html gains an "Edit" action link per row,
    which requires get_recent_transactions to also return the expense id

Depends on
  — Step 01 — Database setup (expenses table exists with all required columns)
  — Step 03 — Login / Logout (session["user_id"] is set and enforced)
  — Step 05 — Profile page renders transactions (the edit link lives there)
  — Step 07 — Add Expense (establishes the form pattern this step follows)

Routes
  — GET /expenses/<int:id>/edit — render edit form pre-populated with existing
    expense values — logged-in only
  — POST /expenses/<int:id>/edit — validate and save updated expense —
    logged-in only

Database changes
  — No new tables or columns
  — All required columns already exist in expenses:
    id, user_id, amount, category, date, description

Templates
  — Create: templates/edit_expense.html
      — extends base.html
      — form with method="POST" and action="/expenses/{{ expense.id }}/edit"
      — Fields (identical to add_expense.html, all pre-filled with current values):
          — amount — number input, step="0.01", min="0.01", required, pre-filled
          — category — <select> with exactly 7 fixed options, pre-selected to
            current value
          — date — <input type="date">, required, pre-filled to current value
          — description — text input, optional, max 200 chars, pre-filled
      — Submit button labelled "Save Changes" and a cancel link back to /profile
      — Error message block that re-populates submitted (not original) values
        on validation failure
  — Modify: templates/profile.html
      — Add an "Actions" column header to the transactions table <thead>
      — Add an "Edit" link cell per row pointing to
        /expenses/{{ tx.id }}/edit

Files to change
  — database/queries.py
      — Add get_expense_by_id(expense_id, user_id)
          — fetches a single expense row only if it belongs to the given user
          — returns None if not found or if user_id does not match
          — query must scope to id = ? AND user_id = ?
      — Add update_expense(expense_id, user_id, amount, category, date,
        description)
          — issues a parameterised UPDATE scoped to id = ? AND user_id = ?
            for ownership safety
      — Modify get_recent_transactions
          — add id to the SELECT column list so templates can build edit links
  — app.py
      — Import get_expense_by_id and update_expense from database.queries
      — Replace the GET-only placeholder at /expenses/<int:id>/edit with a
        full GET + POST handler:
          — GET: call get_expense_by_id; return 404 if not found or not owned;
            render edit_expense.html with expense and categories list
          — POST: read form fields, validate (same rules as Step 07),
            call update_expense, redirect to url_for("profile") on success;
            re-render form with errors otherwise
          — Route decorator must accept both methods:
            @app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
  — templates/profile.html
      — Add <th>Actions</th> to the table header
      — Add an "Edit" link cell per transaction row

Files to create
  — templates/edit_expense.html

New dependencies
  — None

Rules for implementation
  — No SQLAlchemy or ORMs — raw sqlite3 only via get_db()
  — Parameterised queries only — never string-format values into SQL
  — PRAGMA foreign_keys = ON must be enabled on every connection
    (already handled in get_db())
  — get_expense_by_id must scope its query to id = ? AND user_id = ? —
    return None if not found or if ownership check fails
  — update_expense must also include user_id = ? in its WHERE clause as a
    second ownership guard
  — Unauthenticated access to both GET and POST must redirect to /login
  — If the expense does not exist or belongs to another user, return 404
  — Validation rules for POST (identical to Step 07 add expense):
      1. amount: required; must be a positive float greater than 0;
         parse with float(), catch ValueError
      2. category: required; must be one of the 7 fixed categories;
         reject anything else
      3. date: required; must be a valid YYYY-MM-DD string;
         parse with datetime.strptime
      4. description: optional; strip whitespace; store None if blank
  — On any validation error, re-render the form with the error message and
    the submitted (not original) values pre-filled
  — After a successful update, redirect to url_for("profile") —
    do NOT render the form again
  — Currency must always display as ₹ — never £ or $
  — Use CSS variables — never hardcode hex values
  — No inline styles
  — All templates extend base.html
  — Use url_for() for every internal link — never hardcode paths

Tests to write
  — File: tests/test_edit_expense.py
  — Unit tests — format as a table with columns: Function | Input | Expected output:
      — get_expense_by_id with valid expense_id and correct user_id
        → returns the matching row as a dict-like object
      — get_expense_by_id with valid expense_id and wrong user_id
        → returns None
      — get_expense_by_id with non-existent expense_id
        → returns None
      — update_expense with valid expense_id, correct user_id, new amount=99.0
        → row in DB reflects updated amount
      — update_expense with valid expense_id, wrong user_id
        → row in DB unchanged (0 rows affected, no error raised)
  — Route tests (bullet list):
      — GET /expenses/<id>/edit unauthenticated → redirects to /login (302)
      — GET /expenses/<id>/edit authenticated, own expense → returns 200;
        response contains form pre-filled with current values; <select> has
        correct category pre-selected
      — GET /expenses/<id>/edit authenticated, other user's expense → returns 404
      — GET /expenses/<id>/edit authenticated, non-existent id → returns 404
      — POST /expenses/<id>/edit unauthenticated → redirects to /login (302)
      — POST /expenses/<id>/edit authenticated, valid data → redirects to
        /profile (302); updated values reflected in the database
      — POST /expenses/<id>/edit authenticated, other user's expense → returns 404
      — POST /expenses/<id>/edit authenticated, missing amount → returns 200;
        response contains an error message
      — POST /expenses/<id>/edit authenticated, amount = 0 → returns 200;
        response contains an error message
      — POST /expenses/<id>/edit authenticated, non-numeric amount → returns 200;
        response contains an error message
      — POST /expenses/<id>/edit authenticated, invalid category → returns 200;
        response contains an error message
      — POST /expenses/<id>/edit authenticated, invalid date string → returns 200;
        response contains an error message
      — POST /expenses/<id>/edit authenticated, no description → redirects to
        /profile (302); row updated with description = NULL

Definition of done
  — Checkbox list:
    - Visiting /expenses/<id>/edit while logged out redirects to /login
    - Visiting /expenses/<id>/edit for a non-existent or other user's expense
      returns 404
    - Visiting /expenses/<id>/edit while logged in shows a form pre-filled
      with the expense's current values
    - The category dropdown has the correct category pre-selected
    - Submitting valid changes redirects to /profile and the updated values
      appear in the transaction list
    - Submitting with a missing or zero amount re-renders the form with an
      error and the submitted values retained
    - Submitting with an invalid category re-renders the form with an error
    - Submitting with an invalid date re-renders the form with an error
    - Submitting without a description saves the expense with no error
    - Each row in the profile transaction table has an "Edit" link pointing
      to the correct URL
~~~~

## A13. Step 09 spec prompt (delete expense)

~~~~text
I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── .claude/
│   └── specs/
│       ├── 01-database-setup.md                   ← complete
│       ├── 02-registration.md                     ← complete
│       ├── 03-login_logout.md                     ← complete
│       ├── 04-profile.md                          ← complete
│       ├── 05-backend-routes-for-profile-page.md  ← complete
│       ├── 06-date-filter-profile.md              ← complete
│       ├── 07-add-expense.md                      ← complete
│       └── 08-edit-expense.md                     ← complete
├── database/
│   ├── __init__.py
│   ├── db.py                                      ← get_db(), init_db(), seed_db(),
│   │                                                create_user(), get_user_by_email()
│   └── queries.py                                 ← get_user_by_id(), get_summary_stats(),
│                                                    get_recent_transactions() [returns id],
│                                                    get_category_breakdown(),
│                                                    insert_expense(),
│                                                    get_expense_by_id(),
│                                                    update_expense()
├── static/
│   ├── css/
│   │   ├── profile.css
│   │   └── style.css
│   └── js/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html                                 ← complete
│   ├── register.html                              ← complete
│   ├── profile.html                              ← complete; transactions table has
│   │                                               "Actions" column with "Edit" links
│   ├── add_expense.html                          ← complete
│   └── edit_expense.html                         ← complete
├── tests/
│   ├── test_backend_connection.py                 ← complete
│   ├── test_add_expense.py                        ← complete
│   └── test_edit_expense.py                       ← complete
├── .gitignore
├── app.py                                         ← GET /expenses/<id>/delete exists
│                                                    as a stub only
├── README.md
└── requirements.txt

Steps 01 through 08 are complete. Now write a spec for Step 09: Implement the Delete
Expense feature at /expenses/<id>/delete.

Save the output as:
  .claude/specs/09-delete-expense.md

Create the folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use bullet lists throughout
- Use a table for the unit test cases
- Use a checkbox list for Definition of Done
- Use the exact section names listed below — no numbers, just headings

Include these sections in order:

Overview
  — Step 09 lets a logged-in user permanently delete one of their own expenses
    directly from the profile transaction table
  — A "Delete" button per row submits a POST request to /expenses/<id>/delete
  — The handler verifies ownership, removes the row from the database, and
    redirects back to /profile
  — There is no separate confirmation page — a browser-side confirm() dialog
    in the button's onclick handler is used to prevent accidental deletions
  — The existing get_expense_by_id helper from Step 08 is reused for ownership
    verification — no new query lookup functions are needed
  — Only one new mutation helper is added: delete_expense in database/queries.py

Depends on
  — Step 01 — Database setup (expenses table exists)
  — Step 03 — Login / Logout (session["user_id"] is set and enforced)
  — Step 05 — Profile page renders transactions (the delete button lives there)
  — Step 08 — Edit Expense (get_expense_by_id is available; the Actions column
    already exists in the profile transactions table)

Routes
  — POST /expenses/<int:id>/delete — verify ownership, delete the expense row,
    redirect to /profile — logged-in only
  — No GET handler — a bare GET to this URL must return 405

Database changes
  — No new tables or columns
  — The expenses table already has all required columns

Templates
  — Modify: templates/profile.html
      — Inside the existing "Actions" <td> per transaction row, add a delete form:
          — <form> with method="POST" and action="/expenses/{{ tx.id }}/delete"
          — style="display:inline" on the <form> tag is the one permitted
            exception to the no-inline-styles rule — it is a layout-utility
            value only, not a design value
          — onsubmit="return confirm('Delete this expense?')" on the <form> tag
            to provide browser-side confirmation before submission
          — A <button type="submit"> with class="btn-delete" and label "Delete"
      — "Edit" link from Step 08 remains alongside the new "Delete" button

Files to change
  — database/queries.py
      — Add delete_expense(expense_id, user_id)
          — issues a parameterised DELETE FROM expenses WHERE id = ? AND user_id = ?
          — the dual-column WHERE clause is the ownership guard
          — commits and closes the connection before returning
  — app.py
      — Import delete_expense from database.queries
      — Replace the GET-only placeholder at /expenses/<int:id>/delete with a
        POST-only handler:
          — Guard: redirect to /login if not authenticated
          — Call get_expense_by_id(id, session["user_id"]); if None, abort(404)
          — Call delete_expense(id, session["user_id"])
          — Redirect to url_for("profile")
      — Route decorator must be:
        @app.route("/expenses/<int:id>/delete", methods=["POST"])
  — templates/profile.html — add the delete form inside the existing Actions <td>
  — static/css/style.css
      — Add a .btn-delete style using CSS variables for danger colour
        (e.g. a red-toned CSS variable) — never hardcode hex values

Files to create
  — None

New dependencies
  — None

Rules for implementation
  — No SQLAlchemy or ORMs — raw sqlite3 only via get_db()
  — Parameterised queries only — never string-format values into SQL
  — PRAGMA foreign_keys = ON must be enabled on every connection
    (already handled in get_db())
  — delete_expense must scope its DELETE to id = ? AND user_id = ? —
    this is the ownership guard that prevents one user deleting another's expense
  — The route must only accept POST — a bare GET to the URL must return 405
  — Unauthenticated access must redirect to /login (302)
  — If the expense does not exist or belongs to another user, return 404
  — After successful deletion, redirect to url_for("profile") —
    do not render a template
  — The only permitted inline style is style="display:inline" on the <form>
    tag — no hex colours or design values may be inlined anywhere
  — Use CSS variables — never hardcode hex values
  — All templates extend base.html
  — Currency must always display as ₹ — never £ or $
  — Use url_for() for every internal link — never hardcode paths

Tests to write
  — File: tests/test_delete_expense.py
  — Unit tests — format as a table with columns: Function | Input | Expected output:
      — delete_expense with valid expense_id and correct user_id
        → row removed from DB
      — delete_expense with valid expense_id and wrong user_id
        → row remains in DB (0 rows deleted, no error raised)
      — delete_expense with non-existent expense_id
        → no error raised, DB unchanged
  — Route tests (bullet list):
      — POST /expenses/<id>/delete unauthenticated → redirects to /login (302)
      — POST /expenses/<id>/delete authenticated, own expense →
        redirects to /profile (302); row no longer exists in the database
      — POST /expenses/<id>/delete authenticated, other user's expense →
        returns 404; row still exists in the database
      — POST /expenses/<id>/delete authenticated, non-existent id → returns 404
      — GET /expenses/<id>/delete any user → returns 405 (Method Not Allowed)

Definition of done
  — Checkbox list:
    - POST /expenses/<id>/delete while logged out redirects to /login
    - POSTing to /expenses/<id>/delete for a non-existent or other user's
      expense returns 404
    - GET /expenses/<id>/delete returns 405
    - Clicking "Delete" on a transaction row and confirming in the browser
      dialog removes that expense from the database
    - After deletion, the user is redirected to /profile and the deleted
      expense no longer appears in the transaction list
    - Cancelling the browser confirm() dialog does not submit the form and
      leaves the expense intact
    - Each transaction row in the profile table now shows both "Edit" and
      "Delete" actions
~~~~

## A14. Review Step 02 spec

~~~~text
review registration.md against spec 02 registration prompt and prepare the report in C:\Users\Surya\Downloads\Expense_Tracker_Basic-main\Review fodler
~~~~

## A15. Review Step 03 spec

~~~~text
review 03-login_logout.md against spec 03 prompt and save report in Review folder
~~~~

## A16. Review Step 04 spec

~~~~text
review 04-profile.md against spec 04 prompt and save report in Review folder
~~~~

## A17. Review Step 05 spec

~~~~text
review 05-backend-routes-for profile-page.md against spec 5 prompt and save report in Review folder
~~~~

## A18. Review Step 06 spec

~~~~text
review 06-date-filter-profile.md against spec 6 prompt and save report in Review folder
~~~~

## A19. Review Step 07 spec

~~~~text
review 07-add-expense.md against spec 7 prompt and save report in Review folder
~~~~

## A20. Review Step 08 spec

~~~~text
review 08-edit-expense.md against spec 8 prompt and save report in Review folder
~~~~

## A21. Review Step 09 spec

~~~~text
review 09-delete-expense.md against spec 9 prompt and save report in Review folder
~~~~

## A22. Apply review findings to the specs

Each of these was a separate prompt, sent in this order:

~~~~text
analyse the 01-databse-setup-review.md and make necessary changes
analyse the 02-registration-review.md and make necessary changes
analyse the 03-login_logout-review.md and make necessary changes
analyse the 04-profile-review.md and make necessary changes
analyse the 05-backend-routes-for-profile-page-review.md and make necessary changes
analyse the 06-date-filter-profile-review.md and make necessary changes
analyse the 07-add-expense-review.md and make necessary changes
analyse the 08-edit-expense-review.md and make necessary changes
analyse the 09-delete-expense-review.md and make necessary changes
~~~~

## A23. Push to GitHub (first attempt)

~~~~text
push the code in github https://github.com/arpanghosh130883/Expense_Tracker_Basic.git
~~~~

## A24. Push to GitHub (second repository)

~~~~text
push the code in github https://github.com/aksharadontham/expense_tracker.git
~~~~

## A25. Verify the pushed version

~~~~text
validate the git version and compare with current changes
~~~~

## A26. Session commands document

~~~~text
can you prepare document with all the commands executed in this session and store in review folder . name as session commands
~~~~

## A27. Add the prompts to the document

~~~~text
i mean i want all the prompts what i written to be recorded in the session-commands.md
~~~~

---

# Part B — Commands and tool operations

## 1. Slash commands

| Command | Purpose |
|---|---|
| `/rename sdlc` | Renamed the session to "sdlc" |
| `/context` | Showed context usage (about 7% of the 1m-token window at the time) |

## 2. Shell commands (Bash tool)

All shell commands in the session were Git or file-inspection commands, run for the GitHub push and the follow-up verification. They are listed in the order they ran.

### 2.1 Inspect the project folder and Git state

```bash
cd "$PROJECT" && git status 2>&1 | head -5; ls -a; cat .gitignore 2>/dev/null | head -20; git --version
```

- Result: the project folder was not a Git repository; Git 2.56.0 (Windows) is installed.

### 2.2 Check what the first remote contained (`arpanghosh130883/Expense_Tracker_Basic`)

```bash
cd "$PROJECT" && git ls-remote https://github.com/arpanghosh130883/Expense_Tracker_Basic.git 2>&1 | head
```

- Result: the remote already had a `main` branch with history.

### 2.3 Clone that remote to the scratchpad and compare with local files

```bash
mkdir -p "$SCRATCH/remote" && cd "$SCRATCH/remote" && git clone https://github.com/arpanghosh130883/Expense_Tracker_Basic.git repo
cd repo && git log --oneline | head -5; git ls-files
diff -rq . "$PROJECT" -x .git | head -40
```

- Result: most files appeared to differ, which turned out to be line endings.

### 2.4 Compare ignoring line endings

```bash
cd "$SCRATCH/remote/repo"
for f in $(git ls-files); do
  if ! diff -q --strip-trailing-cr "$f" "$PROJECT/$f" >/dev/null; then echo "REAL DIFF: $f"; fi
done
git config core.autocrlf
```

- Result: only `app.py`, `static/css/style.css` and `templates/base.html` had real differences, apart from the new files.

### 2.5 Copy local changes into the clone and review pending changes

```bash
cd "$SCRATCH/remote/repo" && cp -r "$PROJECT/.claude" "$PROJECT/Review" "$PROJECT/app.py" "$PROJECT/static" "$PROJECT/templates" . \
  && git add -A && git status --short
git config user.name; git config user.email
```

- Result: 23 files staged (9 specs, 9 reviews, 3 modified files, 2 new templates).

### 2.6 Commit and push to the first remote

```bash
cd "$SCRATCH/remote/repo" && git commit -q -F - <<'EOF'
Add Terms and Privacy pages, step specs and spec reviews
...
Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
git log --oneline | head -2 && git push origin main 2>&1 | tail -5
```

- Result: **failed** with HTTP 403 — the signed-in account `aksharadontham` had no write access to `arpanghosh130883/Expense_Tracker_Basic`. Nothing on that remote changed.

### 2.7 Check the second remote (`aksharadontham/expense_tracker`)

```bash
git ls-remote https://github.com/aksharadontham/expense_tracker.git 2>&1 | head
```

- Result: the remote had a `main` branch with one commit.

### 2.8 Clone the second remote and inspect it

```bash
cd "$SCRATCH/remote" && git clone https://github.com/aksharadontham/expense_tracker.git repo2
cd repo2 && git log --oneline | head; git ls-files
```

- Result: one "Initial commit" containing `.gitignore`, `LICENSE` and `README.md`.

### 2.9 Inspect the starter files that would be replaced

```bash
cd "$SCRATCH/remote/repo2" && wc -l README.md .gitignore LICENSE && cat README.md
```

- Result: `README.md` held only a title line, so it was safe to replace.

### 2.10 Copy the project, commit and push to the second remote

```bash
cd "$SCRATCH/remote/repo2" && cp -r "$PROJECT/." . ; git add -A; git status --short
git commit -q -F - <<'EOF'
Add Spendly Flask expense tracker project
...
Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
git log --oneline | head -3; git push origin main 2>&1 | tail -4
```

- Result: **succeeded** — `00cc5a3..d618d72  main -> main`. Normal push, no force.

### 2.11 Verify the GitHub version against the local project

```bash
mkdir -p "$SCRATCH/verify" && cd "$SCRATCH/verify" && git -c core.autocrlf=false clone -q https://github.com/aksharadontham/expense_tracker.git gh
cd gh && git log --oneline | head -3; git ls-files | wc -l
for f in $(git ls-files); do
  if [ ! -e "$PROJECT/$f" ]; then echo "ONLY ON GITHUB: $f"
  elif ! diff -q --strip-trailing-cr "$f" "$PROJECT/$f" >/dev/null; then echo "DIFFERS: $f"; fi
done
(cd "$PROJECT" && find . -type f -not -path './.git/*' | sed 's|^\./||' | sort) > ../local.txt
git ls-files | sort > ../remote.txt
comm -23 ../local.txt ../remote.txt
```

- Result: 43 tracked files; only `LICENSE` exists on GitHub alone; nothing exists locally that is missing from GitHub.

### 2.12 Byte-level comparison and file counts per folder

```bash
cd "$SCRATCH/verify/gh"
n=0; for f in $(git ls-files); do [ -e "$PROJECT/$f" ] && ! cmp -s "$f" "$PROJECT/$f" && n=$((n+1)); done; echo "$n"
git ls-files | cut -d/ -f1 | sort | uniq -c
```

- Result: 0 files differ byte for byte; counts per top-level folder listed.

## 3. File tool operations (Read, Write, Edit, Glob, Grep)

These are Claude Code tool calls, not shell commands. They are summarised by task.

### 3.1 Footer links, Terms and Privacy pages

| Operation | Target |
|---|---|
| Read | `templates/base.html`, `templates/landing.html`, `app.py`, `static/css/style.css` (parts) |
| Grep | `static/css/style.css` (theme variables and footer rules) |
| Edit | `templates/base.html` (add footer links; later point them at `/terms` and `/privacy` via `url_for`) |
| Edit | `app.py` (add `/terms` and `/privacy` routes) |
| Edit | `static/css/style.css` (add the "Legal pages" styles) |
| Write | `templates/terms.html`, `templates/privacy.html` |

### 3.2 Writing the step specs

| Operation | Target |
|---|---|
| Write | `.claude/specs/01-database-setup.md` |
| Write | `.claude/specs/02-registration.md` |
| Write | `.claude/specs/03-login_logout.md` |
| Write | `.claude/specs/04-profile.md` |
| Write | `.claude/specs/05-backend-routes-for-profile-page.md` |
| Write | `.claude/specs/06-date-filter-profile.md` |
| Write | `.claude/specs/07-add-expense.md` |
| Write | `.claude/specs/08-edit-expense.md` |
| Write | `.claude/specs/09-delete-expense.md` |

### 3.3 Reviewing the specs against their prompts

| Operation | Target |
|---|---|
| Glob | `**/spec_01_database_setup_prompt.md`, `**/*prompt*` in Downloads |
| Read | `Spec_01_database_setup_prompt.md` through `Spec_09-delete-expense_prompt.md` (the prompt files in the project root) |
| Write | `.claude/specs/01-database-setup-review.md` (later superseded by the copy in `Review/`) |
| Write | `Review/02-registration-review.md` through `Review/09-delete-expense-review.md` |
| Read | `Review/01-database-setup-review.md` (existing report in the Review folder) |

### 3.4 Applying the review findings to the specs

| Operation | Target |
|---|---|
| Edit | `.claude/specs/01-database-setup.md` (timestamps, FK behavior, seed data table, database path, new Definition of done items) |
| Edit | `.claude/specs/02-registration.md` (input cleaning, validation order, success message, refill rules) |
| Edit | `.claude/specs/03-login_logout.md` (re-render on failure, email normalisation, navbar, flash block) |
| Edit | `.claude/specs/04-profile.md` (progress bars, `profile.css`, currency, consistent hardcoded data) |
| Edit | `.claude/specs/05-backend-routes-for-profile-page.md` (missing user, rounding, ordering, test isolation) |
| Edit | `.claude/specs/06-date-filter-profile.md` (preset arithmetic, half-filled range, flash block, tests) |
| Edit | `.claude/specs/07-add-expense.md` (finite amounts, date re-format, description limit, tests) |
| Edit | `.claude/specs/08-edit-expense.md` (ownership check order, update return value, shared categories, tests) |
| Read, then Write | `.claude/specs/09-delete-expense.md` (full rewrite: helper renamed to `delete_expense_by_id`, inline style removed) |
| Grep | `.claude/specs/02-registration.md`, `.claude/specs/07-add-expense.md` (to find exact text after an edit mismatch) |
| Read | `.claude/specs/01-database-setup.md`, `.claude/specs/08-edit-expense.md` (before editing) |

### 3.5 This document

| Operation | Target |
|---|---|
| Write | `Review/session-commands.md` |

## 4. Notes

- No commands were run against the real `spendly.db`; it does not exist yet, because `database/db.py` is still the stub.
- The `Review/session-commands.md` file was created after the GitHub push, so it is **not** in the pushed commit `d618d72`. Add and push it if you want it on GitHub.
- No destructive Git commands (force push, reset, rebase) were used.
