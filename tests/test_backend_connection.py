import re
import sys
import tempfile
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
    get_user_by_id,
)

SEED_USER_ID = 1
EMPTY_STATS = {"total_spent": 0, "transaction_count": 0, "top_category": "—"}
SEED_BREAKDOWN = [
    ("Bills", 120.00, 35),
    ("Food", 61.25, 18),
    ("Shopping", 49.99, 14),
    ("Health", 35.00, 10),
    ("Entertainment", 30.00, 9),
    ("Other", 25.00, 7),  # ties with Transport; equal amounts sort by name
    ("Transport", 25.00, 7),
]


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    init_db()
    seed_db()


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def new_user():
    return create_user("New Person", "new@example.com", "password1")


def add_expense(user_id, amount, category, date, description="Test"):
    conn = get_db()
    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description)"
                " VALUES (?, ?, ?, ?, ?)",
                (user_id, amount, category, date, description),
            )
        return cursor.lastrowid
    finally:
        conn.close()


def login_as(client, user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = "Tester"


def profile_html(client, user_id=SEED_USER_ID):
    login_as(client, user_id)
    response = client.get("/profile")
    assert response.status_code == 200
    return response.get_data(as_text=True)


# ------------------------------------------------------------------ #
# get_user_by_id                                                      #
# ------------------------------------------------------------------ #

def test_get_user_by_id_valid():
    conn = get_db()
    with conn:
        conn.execute("UPDATE users SET created_at = '2026-01-15 10:30:00' WHERE id = ?", (SEED_USER_ID,))
    conn.close()

    assert get_user_by_id(SEED_USER_ID) == {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "member_since": "January 2026",
    }


def test_get_user_by_id_not_found():
    assert get_user_by_id(9999) is None


# ------------------------------------------------------------------ #
# get_summary_stats                                                   #
# ------------------------------------------------------------------ #

def test_summary_stats_with_expenses():
    assert get_summary_stats(SEED_USER_ID) == {
        "total_spent": 346.24,
        "transaction_count": 8,
        "top_category": "Bills",
    }


def test_summary_stats_no_expenses():
    assert get_summary_stats(new_user()) == EMPTY_STATS


def test_summary_stats_tie_picks_alphabetically_first_category():
    user_id = new_user()
    add_expense(user_id, 10.00, "Food", "2026-11-01")
    add_expense(user_id, 10.00, "Bills", "2026-11-02")
    assert get_summary_stats(user_id)["top_category"] == "Bills"


# ------------------------------------------------------------------ #
# get_recent_transactions                                             #
# ------------------------------------------------------------------ #

def test_recent_transactions_with_expenses():
    rows = get_recent_transactions(SEED_USER_ID)
    assert len(rows) == 8
    assert all(set(r) == {"id", "date", "description", "category", "amount"} for r in rows)
    assert [r["id"] for r in rows] == [8, 7, 6, 5, 4, 3, 2, 1]  # newest first, matching the stored ids
    assert [r["date"] for r in rows] == sorted((r["date"] for r in rows), reverse=True)
    assert rows[0]["description"] == "Gift" and rows[0]["category"] == "Other"
    assert rows[-1]["description"] == "Electricity bill" and rows[-1]["category"] == "Bills"


def test_recent_transactions_no_expenses():
    assert get_recent_transactions(new_user()) == []


def test_recent_transactions_same_date_ordered_by_id_desc():
    user_id = new_user()
    add_expense(user_id, 1.00, "Food", "2026-11-30", "first")
    add_expense(user_id, 2.00, "Food", "2026-11-30", "second")
    assert [r["description"] for r in get_recent_transactions(user_id)] == ["second", "first"]


def test_recent_transactions_respects_limit():
    rows = get_recent_transactions(SEED_USER_ID, limit=3)
    assert [r["description"] for r in rows] == ["Gift", "Headphones", "Lunch with team"]


def test_recent_transactions_null_description_becomes_empty_string():
    user_id = new_user()
    add_expense(user_id, 3.00, "Other", "2026-11-05", None)
    assert get_recent_transactions(user_id)[0]["description"] == ""


# ------------------------------------------------------------------ #
# get_category_breakdown                                              #
# ------------------------------------------------------------------ #

def test_category_breakdown_with_expenses():
    breakdown = get_category_breakdown(SEED_USER_ID)
    assert [(b["name"], b["amount"], b["pct"]) for b in breakdown] == SEED_BREAKDOWN
    assert all(isinstance(b["pct"], int) for b in breakdown)
    assert sum(b["pct"] for b in breakdown) == 100
    amounts = [b["amount"] for b in breakdown]
    assert amounts == sorted(amounts, reverse=True)


def test_category_breakdown_no_expenses():
    assert get_category_breakdown(new_user()) == []


def test_category_breakdown_remainder_goes_to_largest_category():
    user_id = new_user()
    for category in ("Food", "Bills", "Health"):
        add_expense(user_id, 10.00, category, "2026-11-01")
    breakdown = get_category_breakdown(user_id)
    assert [(b["name"], b["pct"]) for b in breakdown] == [("Bills", 34), ("Food", 33), ("Health", 33)]
    assert sum(b["pct"] for b in breakdown) == 100


# ------------------------------------------------------------------ #
# GET /profile                                                        #
# ------------------------------------------------------------------ #

def test_profile_unauthenticated_redirects_to_login(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_profile_with_unknown_user_clears_session_and_redirects(client):
    login_as(client, 9999)
    response = client.get("/profile")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_profile_seed_user(client):
    html = profile_html(client)

    assert "Demo User" in html and "demo@spendly.com" in html
    assert ">DU<" in html
    assert "₹" in html

    stat_values = re.findall(r'stat-value">(.*?)<', html)
    assert stat_values == ["₹346.24", "8", "Bills"]

    tbody = re.search(r"<tbody>(.*?)</tbody>", html, re.S).group(1)
    descriptions = re.findall(r"<td>\d{2} \w{3} \d{4}</td>\s*<td>(.*?)</td>", tbody)
    assert len(descriptions) == 8
    assert descriptions[0] == "Gift" and descriptions[-1] == "Electricity bill"

    names = re.findall(r'class="cat-name"><span class="badge badge-\w+">(\w+)<', html)
    pcts = [int(p) for p in re.findall(r'value="(\d+)" max="100"', html)]
    assert list(zip(names, pcts)) == [(n, p) for n, _, p in SEED_BREAKDOWN]
    assert sum(pcts) == 100


def test_profile_new_user_shows_zeros_without_errors(client):
    html = profile_html(client, new_user())

    assert re.findall(r'stat-value">(.*?)<', html) == ["₹0.00", "0", "—"]
    assert "<progress" not in html
    tbody = re.search(r"<tbody>(.*?)</tbody>", html, re.S).group(1)
    assert "<tr>" not in tbody


def test_profile_only_shows_the_logged_in_users_expenses(client):
    other = new_user()
    add_expense(other, 5.00, "Food", "2026-11-04", "OnlyOther")

    seed_html = profile_html(client)
    assert "OnlyOther" not in seed_html

    other_html = profile_html(client, other)
    assert "OnlyOther" in other_html
    assert "Gift" not in other_html
    assert re.findall(r'stat-value">(.*?)<', other_html) == ["₹5.00", "1", "Food"]
    assert "New Person" in other_html
