# Review Report: 04-profile.md

- **Spec reviewed:** `.claude/specs/04-profile.md`
- **Checked against:** `Spec_04_Profilepage_prompt.md`
- **Verdict:** Compliant. All 9 required sections are present, in the order the prompt lists them, with every requested point covered, including the numbered list for the four template sections. No blocking issues. Several gaps and conflicts inherited from the prompt are listed below, the main one being how progress bars can be built without inline styles.

## 1. Section-by-section compliance

| Section | Status | Notes |
|---|---|---|
| Overview | Pass | Replaces the `/profile` stub with a static page; UI before real queries in Step 05; the four sections named; rationale for building UI first |
| Depends on | Pass | Steps 01, 02 and 03 with the stated reasons, including `/profile` as a protected route |
| Routes | Pass | `GET /profile`, logged-in only, redirect to `/login` if not authenticated |
| Database changes | Pass | No changes; existing tables sufficient; no DB queries, all data hardcoded |
| Templates | Pass | `templates/profile.html` extending `base.html`; all four sections as a numbered list with the stated contents and minimum row counts |
| Files to change | Pass | `app.py` view with the auth redirect and the four hardcoded context variables |
| Files to create | Pass | `templates/profile.html` |
| New dependencies | Pass | None |
| Rules for implementation | Pass | All nine rules present (see section 3) |
| Definition of done | Pass | All eight checkbox items present with the prompt's wording |

## 2. Format rules

| Rule | Status | Notes |
|---|---|---|
| Output only the Markdown spec | Pass | No prose outside the spec |
| No code | Pass | Only identifiers and short fragments in inline code |
| Bullet lists throughout | Pass | |
| Numbered list for the four template sections | Pass | Items 1 to 4 under Templates |
| Checkbox list for Definition of done | Pass | |
| Section names exact, no numbers | Pass | Plain headings with the exact names |

## 3. Rules for implementation — detail

| Prompt rule | In spec |
|---|---|
| No SQLAlchemy or ORMs; raw `sqlite3` via `get_db()` if ever needed | Yes |
| Parameterised queries only | Yes |
| Guard with `session.get("user_id")`; else `redirect(url_for("login"))` | Yes |
| All template data is hardcoded dicts/lists in `app.py`, no DB queries | Yes |
| CSS variables, no hardcoded hex | Yes |
| No inline styles anywhere in `profile.html` | Yes |
| Templates extend `base.html` | Yes |
| Category badges use a CSS class, not inline colour | Yes |
| `url_for()` for every internal link | Yes |

## 4. Deviations and additions

- **Document title:** a `# Spec: Profile Page` heading sits above Overview. The prompt did not ask for it.
- **Inline code formatting:** file paths and identifiers are in inline code, where the prompt gave plain text. This is a presentation choice only.
- No content was added or removed beyond that.

## 5. Gaps and conflicts

These are inherited from the prompt. None contradicts it, but several would trip an implementer.

1. **Progress bars conflict with "no inline styles".** Category breakdown may use progress-bar rows. A bar's width normally comes from an inline style set per row. With no inline styles allowed, the spec gives no alternative, such as fixed width classes, a `<progress>` element or a data attribute with a script.
2. **No stylesheet is listed.** The badge classes, card layout, table and bars all need CSS. Neither Files to change nor Files to create names a CSS file, and `profile.html` cannot carry styles (no inline styles). The later specs reference `static/css/profile.css` and `style.css`, so this step leaves the styling home undefined.
3. **Navbar checkbox has no owner.** The last-but-one Definition of done item requires the navbar to show the username and a logout link when logged in. The navbar lives in `base.html`, which is not in Files to change. This also relies on Step 03, which does not change the navbar either.
4. **Hardcoded user vs session user.** The profile card shows a hardcoded name and email, while the navbar would show the session user. The two can disagree on screen. The spec does not say whether they should match.
5. **Hardcoded data consistency.** Nothing says the summary stats should agree with the table and breakdown (for example, total spent equal to the sum of the rows). Inconsistent demo data is easy to produce.
6. **Currency is not stated.** The spec says nothing about the currency symbol. Step 05 later requires ₹ and a rule against £ and $, so hardcoded values in this step may need to be redone.
7. **Avatar initials source is unspecified.** It is unclear whether they are derived from the name in the template or hardcoded as a separate value.
8. **Rule 1 mentions `get_db()`** while the same spec says no DB queries. The wording is only a guard for the future, but it can read as a contradiction.
9. **No tests section.** The prompt did not ask for one.

## 6. Recommendations

- Decide how progress bars get their width without inline styles, for example a set of width classes in 5% or 10% steps, a `<progress>` element, or listed rows as plain numbers.
- Name the stylesheet in Files to change or Files to create (for example `static/css/profile.css`) and say how it is linked.
- Add `templates/base.html` to Files to change, or move the navbar checkbox to a step that does.
- State the currency symbol (₹) from the start so Step 05 only swaps the data source.
- Say whether the hardcoded profile name matches the session user, and that the stats must add up to the rows shown.
