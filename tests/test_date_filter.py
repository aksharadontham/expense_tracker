import html as html_lib
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import database.db as db

# app.py runs init_db() and seed_db() when it is imported, so point the
# database at a temporary file first; the real spendly.db is never touched.
db.DB_PATH = Path(tempfile.mkdtemp()) / "import.db"

import app as app_module  # noqa: E402
from database.db import create_user, get_db, init_db, seed_db  # noqa: E402
from database.queries import (  # noqa: E402
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
)

SEED_USER_ID = 1
EMPTY_STATS = {"total_spent": 0, "transaction_count": 0, "top_category": "—"}
TODAY = date.today()
UNFILTERED_STATS = {"total_spent": 346.24, "transaction_count": 8, "top_category": "Bills"}


def day(n):
    """ISO date for day n of the current month (the seed data uses the current month)."""
    return date(TODAY.year, TODAY.month, n).isoformat()


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    init_db()
    seed_db()


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def login_as(client, user_id=SEED_USER_ID):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = "Tester"


def get_profile(client, query="", user_id=SEED_USER_ID):
    login_as(client, user_id)
    response = client.get("/profile" + query)
    assert response.status_code == 200
    return response.get_data(as_text=True)


def stat_values(page):
    return re.findall(r'stat-value">(.*?)<', page)


def table_descriptions(page):
    tbody = re.search(r"<tbody>(.*?)</tbody>", page, re.S).group(1)
    return re.findall(r"<td>\d{2} \w{3} \d{4}</td>\s*<td>(.*?)</td>", tbody)


def progress_count(page):
    return len(re.findall(r"<progress", page))


def filter_buttons(page):
    """Map each filter button label to (href or None, is_active)."""
    buttons = {}
    for href, active, label in re.findall(
        r'<a href="([^"]*)" class="filter-btn( active)?">(.*?)</a>', page
    ):
        buttons[label] = (html_lib.unescape(href), bool(active))
    apply_match = re.search(r'<button type="submit" class="filter-btn( active)?">Apply</button>', page)
    buttons["Apply"] = (None, bool(apply_match.group(1)))
    return buttons


# ------------------------------------------------------------------ #
# Query helpers                                                       #
# ------------------------------------------------------------------ #

def test_summary_stats_without_range_is_unfiltered():
    assert get_summary_stats(SEED_USER_ID) == UNFILTERED_STATS
    assert get_summary_stats(SEED_USER_ID, None, None) == UNFILTERED_STATS


def test_summary_stats_day_1_to_8():
    assert get_summary_stats(SEED_USER_ID, day(1), day(8)) == {
        "total_spent": 218.50,
        "transaction_count": 4,
        "top_category": "Bills",
    }


def test_summary_stats_single_day_inclusive_bounds():
    assert get_summary_stats(SEED_USER_ID, day(3), day(3)) == {
        "total_spent": 38.50,
        "transaction_count": 1,
        "top_category": "Food",
    }


def test_summary_stats_range_with_no_expenses():
    assert get_summary_stats(SEED_USER_ID, "2020-01-01", "2020-01-31") == EMPTY_STATS


def test_summary_stats_single_bound_is_ignored():
    assert get_summary_stats(SEED_USER_ID, date_from=day(8)) == UNFILTERED_STATS
    assert get_summary_stats(SEED_USER_ID, date_to=day(3)) == UNFILTERED_STATS


def test_recent_transactions_day_1_to_8_newest_first():
    rows = get_recent_transactions(SEED_USER_ID, date_from=day(1), date_to=day(8))
    assert [r["category"] for r in rows] == ["Health", "Transport", "Food", "Bills"]


def test_recent_transactions_inclusive_bounds():
    rows = get_recent_transactions(SEED_USER_ID, date_from=day(3), date_to=day(5))
    assert [r["description"] for r in rows] == ["Metro card top-up", "Groceries"]


def test_recent_transactions_limit_still_applies_within_range():
    rows = get_recent_transactions(SEED_USER_ID, limit=2, date_from=day(1), date_to=day(18))
    assert [r["description"] for r in rows] == ["Gift", "Headphones"]


def test_category_breakdown_day_1_to_8():
    breakdown = get_category_breakdown(SEED_USER_ID, day(1), day(8))
    assert [b["name"] for b in breakdown] == ["Bills", "Food", "Health", "Transport"]
    assert [b["pct"] for b in breakdown] == [55, 18, 16, 11]
    assert all(isinstance(b["pct"], int) for b in breakdown)
    assert sum(b["pct"] for b in breakdown) == 100


def test_category_breakdown_range_with_no_expenses():
    assert get_category_breakdown(SEED_USER_ID, "2020-01-01", "2020-01-31") == []


def test_category_breakdown_without_range_is_unfiltered():
    assert len(get_category_breakdown(SEED_USER_ID)) == 7


def test_filter_only_counts_the_users_own_expenses():
    other = create_user("Other Person", "other@example.com", "password1")
    conn = get_db()
    with conn:
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
            (other, 5.00, "Food", day(3)),
        )
    conn.close()
    assert get_summary_stats(other, day(1), day(8))["transaction_count"] == 1
    assert get_summary_stats(SEED_USER_ID, day(3), day(3))["transaction_count"] == 1


# ------------------------------------------------------------------ #
# Preset date ranges                                                  #
# ------------------------------------------------------------------ #

def presets_for(today):
    return {label: (start, end) for label, start, end in app_module._preset_ranges(today)}


def test_presets_for_a_normal_day():
    presets = presets_for(date(2026, 11, 3))
    assert presets["This Month"] == ("2026-11-01", "2026-11-30")
    assert presets["Last 3 Months"] == ("2026-08-03", "2026-11-03")
    assert presets["Last 6 Months"] == ("2026-05-03", "2026-11-03")
    assert presets["All Time"] == (None, None)


def test_presets_clamp_to_the_end_of_a_shorter_month():
    assert presets_for(date(2026, 5, 31))["Last 3 Months"][0] == "2026-02-28"
    assert presets_for(date(2026, 8, 31))["Last 6 Months"][0] == "2026-02-28"


def test_presets_use_leap_day_in_a_leap_year():
    assert presets_for(date(2028, 5, 31))["Last 3 Months"][0] == "2028-02-29"


def test_presets_cross_a_year_boundary():
    presets = presets_for(date(2026, 2, 15))
    assert presets["Last 3 Months"][0] == "2025-11-15"
    assert presets["Last 6 Months"][0] == "2025-08-15"


def test_this_month_runs_to_the_last_day_of_the_month():
    assert presets_for(date(2028, 2, 10))["This Month"] == ("2028-02-01", "2028-02-29")
    assert presets_for(date(2026, 12, 31))["This Month"] == ("2026-12-01", "2026-12-31")


def test_preset_order_and_labels():
    labels = [label for label, _, _ in app_module._preset_ranges(date(2026, 11, 3))]
    assert labels == ["This Month", "Last 3 Months", "Last 6 Months", "All Time"]


# ------------------------------------------------------------------ #
# GET /profile with filters                                           #
# ------------------------------------------------------------------ #

def test_no_parameters_matches_step_05(client):
    page = get_profile(client)
    assert stat_values(page) == ["₹346.24", "8", "Bills"]
    assert len(table_descriptions(page)) == 8
    assert progress_count(page) == 7
    assert "Start date must be before end date." not in page


def test_valid_range_filters_all_three_sections(client):
    page = get_profile(client, f"?date_from={day(1)}&date_to={day(8)}")
    assert stat_values(page) == ["₹218.50", "4", "Bills"]
    assert table_descriptions(page) == ["Pharmacy", "Metro card top-up", "Groceries", "Electricity bill"]
    assert progress_count(page) == 4
    assert "Gift" not in page and "Headphones" not in page


def test_reversed_range_flashes_error_and_shows_everything(client):
    page = get_profile(client, f"?date_from={day(8)}&date_to={day(1)}")
    assert "Start date must be before end date." in page
    assert stat_values(page) == ["₹346.24", "8", "Bills"]
    assert filter_buttons(page)["All Time"][1] is True


def test_malformed_date_falls_back_silently(client):
    page = get_profile(client, f"?date_from=not-a-date&date_to={day(8)}")
    assert stat_values(page) == ["₹346.24", "8", "Bills"]
    assert "Start date must be before end date." not in page


def test_both_dates_malformed_fall_back_silently(client):
    page = get_profile(client, "?date_from=abc&date_to=xyz")
    assert stat_values(page) == ["₹346.24", "8", "Bills"]


def test_half_filled_range_falls_back_silently(client):
    for query in (f"?date_from={day(8)}", f"?date_to={day(8)}", f"?date_from={day(8)}&date_to="):
        page = get_profile(client, query)
        assert stat_values(page) == ["₹346.24", "8", "Bills"]
        assert "Start date must be before end date." not in page


def test_unpadded_dates_are_normalised(client):
    month = TODAY.month
    page = get_profile(client, f"?date_from={TODAY.year}-{month}-1&date_to={TODAY.year}-{month}-8")
    assert stat_values(page) == ["₹218.50", "4", "Bills"]
    inputs = re.findall(r'<input type="date"[^>]*value="([^"]*)"', page)
    assert inputs == [day(1), day(8)]


def test_single_day_range_is_valid(client):
    page = get_profile(client, f"?date_from={day(3)}&date_to={day(3)}")
    assert stat_values(page) == ["₹38.50", "1", "Food"]
    assert "Start date must be before end date." not in page


def test_this_month_preset_includes_days_after_today(client):
    buttons = filter_buttons(get_profile(client))
    href = buttons["This Month"][0]
    assert f"date_from={day(1)}" in href
    page = get_profile(client, href[len("/profile"):])
    assert stat_values(page) == ["₹346.24", "8", "Bills"]
    assert len(table_descriptions(page)) == 8


def test_preset_links_come_from_url_for(client):
    buttons = filter_buttons(get_profile(client))
    assert buttons["All Time"][0] == "/profile"
    for label in ("This Month", "Last 3 Months", "Last 6 Months"):
        assert buttons[label][0].startswith("/profile?date_from=") and "&date_to=" in buttons[label][0]


def test_last_3_months_preset_hides_future_dated_rows(client):
    # the window ends today, so seed rows dated after today are outside it
    href = filter_buttons(get_profile(client))["Last 3 Months"][0]
    page = get_profile(client, href[len("/profile"):])
    expected = [i for i in (1, 3, 5, 8, 10, 12, 15, 18) if i <= TODAY.day]
    assert int(stat_values(page)[1]) == len(expected)


def test_empty_range_shows_zeros_without_errors(client):
    page = get_profile(client, "?date_from=2020-01-01&date_to=2020-01-31")
    assert stat_values(page) == ["₹0.00", "0", "—"]
    assert progress_count(page) == 0
    assert table_descriptions(page) == []


def test_active_state_all_time_with_no_filter(client):
    buttons = filter_buttons(get_profile(client))
    assert buttons["All Time"][1] is True
    assert not any(active for label, (_, active) in buttons.items() if label != "All Time")


def test_active_state_for_an_applied_preset(client):
    href = filter_buttons(get_profile(client))["This Month"][0]
    buttons = filter_buttons(get_profile(client, href[len("/profile"):]))
    assert buttons["This Month"][1] is True
    assert not any(active for label, (_, active) in buttons.items() if label != "This Month")


def test_active_state_for_a_custom_range(client):
    buttons = filter_buttons(get_profile(client, f"?date_from={day(1)}&date_to={day(8)}"))
    assert buttons["Apply"][1] is True
    assert not any(active for label, (_, active) in buttons.items() if label != "Apply")


def test_custom_form_uses_get_and_is_prefilled(client):
    page = get_profile(client, f"?date_from={day(1)}&date_to={day(8)}")
    form = re.search(r'<form class="filter-form"[^>]*>', page).group(0)
    assert 'method="get"' in form and 'action="/profile"' in form
    inputs = re.findall(r'<input type="date"[^>]*>', page)
    assert len(inputs) == 2 and all(" required" in i for i in inputs)
    assert f'value="{day(1)}"' in inputs[0] and f'value="{day(8)}"' in inputs[1]


def test_custom_form_is_empty_without_a_filter(client):
    page = get_profile(client)
    inputs = re.findall(r'<input type="date"[^>]*>', page)
    assert all('value=""' in i for i in inputs)


def test_amounts_keep_the_rupee_symbol_when_filtered(client):
    page = get_profile(client, f"?date_from={day(1)}&date_to={day(8)}")
    assert "₹" in page and "£" not in page and "$" not in page
    assert page.count("₹") >= 1 + 4 + 4  # total + table rows + breakdown rows


def test_filtered_page_has_no_inline_styles(client):
    page = get_profile(client, f"?date_from={day(1)}&date_to={day(8)}")
    assert "style=" not in page and "<style" not in page


def test_filter_requires_login(client):
    response = client.get(f"/profile?date_from={day(1)}&date_to={day(8)}")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
