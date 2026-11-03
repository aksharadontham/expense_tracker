import re
import sqlite3
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
from database.queries import insert_expense  # noqa: E402

SEED_USER_ID = 1
CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]
VALID = {"amount": "50.0", "category": "Food", "date": "2026-03-20", "description": "Lunch"}


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


def post(client, **overrides):
    data = dict(VALID)
    data.update(overrides)
    for key in [k for k, v in data.items() if v is None]:
        del data[key]  # simulate a missing form field
    return client.post("/expenses/add", data=data)


def rows(where="1=1", params=()):
    conn = get_db()
    try:
        return conn.execute(f"SELECT * FROM expenses WHERE {where} ORDER BY id", params).fetchall()
    finally:
        conn.close()


def expense_count():
    return len(rows())


def error_message(response):
    return re.findall(r'class="auth-error">(.*?)<', response.get_data(as_text=True))


# ------------------------------------------------------------------ #
# insert_expense                                                      #
# ------------------------------------------------------------------ #

def test_insert_expense_inserts_a_row():
    new_id = insert_expense(SEED_USER_ID, 50.0, "Food", "2026-03-20", "Lunch")
    row = rows("id = ?", (new_id,))[0]
    assert (row["user_id"], row["amount"], row["category"], row["date"], row["description"]) == (
        SEED_USER_ID, 50.0, "Food", "2026-03-20", "Lunch")


def test_insert_expense_without_description_stores_null():
    new_id = insert_expense(SEED_USER_ID, 12.5, "Other", "2026-03-21", None)
    assert rows("id = ?", (new_id,))[0]["description"] is None


def test_insert_expense_returns_the_new_integer_id():
    new_id = insert_expense(SEED_USER_ID, 1.0, "Food", "2026-03-22", "x")
    assert isinstance(new_id, int) and new_id == 9  # the seed data has ids 1 to 8
    assert rows("id = ?", (new_id,))[0]["description"] == "x"


def test_insert_expense_with_unknown_user_raises_foreign_key_error():
    with pytest.raises(sqlite3.IntegrityError):
        insert_expense(999, 1.0, "Food", "2026-03-22", "x")
    assert expense_count() == 8


# ------------------------------------------------------------------ #
# Access control                                                      #
# ------------------------------------------------------------------ #

def test_get_requires_login(client):
    response = client.get("/expenses/add")
    assert response.status_code == 302 and response.headers["Location"].endswith("/login")


def test_post_requires_login_and_inserts_nothing(client):
    response = post(client)
    assert response.status_code == 302 and response.headers["Location"].endswith("/login")
    assert expense_count() == 8


def test_stale_session_user_is_cleared_without_a_crash(client):
    login_as(client, 999)
    response = post(client)
    assert response.status_code == 302 and response.headers["Location"].endswith("/login")
    with client.session_transaction() as sess:
        assert "user_id" not in sess
    assert expense_count() == 8


# ------------------------------------------------------------------ #
# GET /expenses/add                                                   #
# ------------------------------------------------------------------ #

def test_form_page_content(client):
    login_as(client)
    response = client.get("/expenses/add")
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'method="post"' in page and 'action="/expenses/add"' in page
    assert re.findall(r'<option value="(.*?)"', page) == CATEGORIES
    for field in ("amount", "category", "date", "description"):
        assert f'name="{field}"' in page
    amount = re.search(r'<input type="number"[^>]*>', page).group(0)
    assert 'step="0.01"' in amount and 'min="0.01"' in amount and " required" in amount
    assert 'maxlength="200"' in re.search(r'<input type="text" id="description"[^>]*>', page).group(0)
    assert "Save Expense" in page
    assert 'href="/profile"' in page  # cancel link


def test_form_date_defaults_to_today(client):
    login_as(client)
    page = client.get("/expenses/add").get_data(as_text=True)
    assert f'value="{date.today().isoformat()}"' in page


# ------------------------------------------------------------------ #
# POST /expenses/add — success                                        #
# ------------------------------------------------------------------ #

def test_valid_post_saves_and_redirects(client):
    login_as(client)
    response = post(client)
    assert response.status_code == 302 and response.headers["Location"].endswith("/profile")
    saved = rows("id > 8")
    assert len(saved) == 1
    assert (saved[0]["user_id"], saved[0]["amount"], saved[0]["category"],
            saved[0]["date"], saved[0]["description"]) == (SEED_USER_ID, 50.0, "Food", "2026-03-20", "Lunch")


def test_success_message_and_new_expense_on_profile(client):
    login_as(client)
    page = post(client, description="Team lunch").headers["Location"]
    response = client.get(page)
    html = response.get_data(as_text=True)
    assert "Expense added successfully." in html and "flash-success" in html
    assert "Team lunch" in html
    assert re.findall(r'stat-value">(.*?)<', html)[1] == "9"
    # the message is shown once
    assert "Expense added successfully." not in client.get("/profile").get_data(as_text=True)


def test_no_description_saves_null(client):
    login_as(client)
    assert post(client, description="").status_code == 302
    assert rows("id > 8")[0]["description"] is None


def test_missing_description_field_saves_null(client):
    login_as(client)
    assert post(client, description=None).status_code == 302
    assert rows("id > 8")[0]["description"] is None


def test_whitespace_only_description_saves_null(client):
    login_as(client)
    assert post(client, description="   ").status_code == 302
    assert rows("id > 8")[0]["description"] is None


def test_description_is_stripped(client):
    login_as(client)
    post(client, description="  padded  ")
    assert rows("id > 8")[0]["description"] == "padded"


def test_description_of_exactly_200_characters_is_accepted(client):
    login_as(client)
    assert post(client, description="x" * 200).status_code == 302
    assert len(rows("id > 8")[0]["description"]) == 200


def test_unpadded_date_is_saved_in_iso_form(client):
    login_as(client)
    assert post(client, date="2026-3-5").status_code == 302
    assert rows("id > 8")[0]["date"] == "2026-03-05"


def test_future_date_is_allowed(client):
    login_as(client)
    assert post(client, date="2999-12-31").status_code == 302
    assert rows("id > 8")[0]["date"] == "2999-12-31"


def test_amount_is_rounded_to_two_decimals(client):
    login_as(client)
    post(client, amount="10.456")
    assert rows("id > 8")[0]["amount"] == 10.46


def test_amount_with_surrounding_spaces_is_accepted(client):
    login_as(client)
    assert post(client, amount=" 25 ").status_code == 302
    assert rows("id > 8")[0]["amount"] == 25.0


def test_maximum_amount_is_accepted(client):
    login_as(client)
    assert post(client, amount="9999999.99").status_code == 302


@pytest.mark.parametrize("category", CATEGORIES)
def test_every_fixed_category_is_accepted(client, category):
    login_as(client)
    assert post(client, category=category).status_code == 302
    assert rows("id > 8")[0]["category"] == category


# ------------------------------------------------------------------ #
# POST /expenses/add — validation failures                            #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("overrides, message", [
    ({"amount": None}, "Amount is required."),
    ({"amount": ""}, "Amount is required."),
    ({"amount": "   "}, "Amount is required."),
    ({"amount": "0"}, "Amount must be at least 0.01."),
    ({"amount": "0.00"}, "Amount must be at least 0.01."),
    ({"amount": "0.001"}, "Amount must be at least 0.01."),
    ({"amount": "-5"}, "Amount must be at least 0.01."),
    ({"amount": "abc"}, "Please enter a valid amount."),
    ({"amount": "12abc"}, "Please enter a valid amount."),
    ({"amount": "inf"}, "Please enter a valid amount."),
    ({"amount": "-inf"}, "Please enter a valid amount."),
    ({"amount": "Infinity"}, "Please enter a valid amount."),
    ({"amount": "nan"}, "Please enter a valid amount."),
    ({"amount": "10000000"}, "Amount must be at most 9,999,999.99."),
    ({"category": "Gadgets"}, "Please choose a valid category."),
    ({"category": "food"}, "Please choose a valid category."),
    ({"category": ""}, "Please choose a valid category."),
    ({"category": None}, "Please choose a valid category."),
    ({"date": ""}, "Date is required."),
    ({"date": None}, "Date is required."),
    ({"date": "not-a-date"}, "Please enter a valid date."),
    ({"date": "2026-13-45"}, "Please enter a valid date."),
    ({"date": "20/03/2026"}, "Please enter a valid date."),
    ({"description": "x" * 201}, "Description must be at most 200 characters."),
])
def test_invalid_submission_shows_error_and_saves_nothing(client, overrides, message):
    login_as(client)
    response = post(client, **overrides)
    assert response.status_code == 200
    assert error_message(response) == [message]
    assert expense_count() == 8


def test_submitted_values_are_shown_again_after_an_error(client):
    login_as(client)
    response = post(client, amount="abc", category="Bills", date="2026-03-20", description="Dinner")
    page = response.get_data(as_text=True)
    assert 'value="abc"' in page
    assert 'value="2026-03-20"' in page
    assert 'value="Dinner"' in page
    assert re.search(r'<option value="Bills" selected>', page)
    assert page.count(" selected>") == 1


def test_other_fields_are_kept_when_only_the_category_is_wrong(client):
    login_as(client)
    page = post(client, category="Gadgets", description="Keep me").get_data(as_text=True)
    assert 'value="50.0"' in page and 'value="Keep me"' in page
    assert " selected>" not in page  # the invalid category is not among the options


def test_html_in_submitted_values_is_escaped(client):
    login_as(client)
    page = post(client, amount="abc", description='"><script>alert(1)</script>').get_data(as_text=True)
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


def test_only_the_logged_in_user_gets_the_expense(client):
    other = create_user("Other Person", "other@example.com", "password1")
    login_as(client, other)
    post(client)
    saved = rows("id > 8")
    assert len(saved) == 1 and saved[0]["user_id"] == other


# ------------------------------------------------------------------ #
# Navigation                                                          #
# ------------------------------------------------------------------ #

def nav(html):
    return re.search(r"<nav.*?</nav>", html, re.S).group(0)


def test_profile_page_has_an_add_expense_button(client):
    login_as(client)
    page = client.get("/profile").get_data(as_text=True)
    assert re.search(r'<a href="/expenses/add" class="btn-add">Add Expense</a>', page)


def test_navbar_link_shown_when_logged_in(client):
    login_as(client)
    for path in ("/", "/profile", "/terms", "/expenses/add"):
        html = client.get(path).get_data(as_text=True)
        assert 'href="/expenses/add">Add Expense</a>' in nav(html), path


def test_navbar_link_hidden_when_logged_out(client):
    for path in ("/", "/login", "/register", "/terms", "/privacy"):
        html = client.get(path).get_data(as_text=True)
        assert "Add Expense" not in nav(html), path


# ------------------------------------------------------------------ #
# Template rules                                                      #
# ------------------------------------------------------------------ #

def test_form_page_has_no_inline_styles_or_hex_colours(client):
    login_as(client)
    page = client.get("/expenses/add").get_data(as_text=True)
    assert "style=" not in page and "<style" not in page
    template = (Path(__file__).resolve().parent.parent / "templates" / "add_expense.html").read_text(encoding="utf-8")
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", template)
    assert not re.search(r'(href|src|action)="/', template)
