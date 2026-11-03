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
    get_expense_by_id,
    get_recent_transactions,
    insert_expense,
    update_expense,
)

SEED_USER_ID = 1
GROCERIES_ID = 2  # seed: 2026-11-03, Food, 38.50, "Groceries"
CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]
VALID = {"amount": "99.5", "category": "Bills", "date": "2026-12-01", "description": "Updated"}


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


def other_users_expense():
    """Create a second user with one expense and return (user_id, expense_id)."""
    other = create_user("Other Person", "other@example.com", "password1")
    return other, insert_expense(other, 7.0, "Other", "2026-11-09", "Private")


def stored(expense_id):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def edit(client, expense_id=GROCERIES_ID, **overrides):
    data = dict(VALID)
    data.update(overrides)
    for key in [k for k, v in data.items() if v is None]:
        del data[key]  # simulate a missing form field
    return client.post(f"/expenses/{expense_id}/edit", data=data)


def error_message(response):
    return re.findall(r'class="auth-error">(.*?)<', response.get_data(as_text=True))


# ------------------------------------------------------------------ #
# get_expense_by_id                                                   #
# ------------------------------------------------------------------ #

def test_get_expense_by_id_returns_the_row_for_its_owner():
    expense = get_expense_by_id(GROCERIES_ID, SEED_USER_ID)
    assert expense["id"] == GROCERIES_ID and expense["user_id"] == SEED_USER_ID
    assert (expense["amount"], expense["category"], expense["date"], expense["description"]) == (
        38.5, "Food", "2026-11-03", "Groceries")


def test_get_expense_by_id_wrong_user_returns_none():
    other, _ = other_users_expense()
    assert get_expense_by_id(GROCERIES_ID, other) is None


def test_get_expense_by_id_non_existent_returns_none():
    assert get_expense_by_id(9999, SEED_USER_ID) is None


# ------------------------------------------------------------------ #
# update_expense                                                      #
# ------------------------------------------------------------------ #

def test_update_expense_changes_the_row_and_returns_one():
    assert update_expense(GROCERIES_ID, SEED_USER_ID, 99.0, "Bills", "2026-12-01", "New") == 1
    row = stored(GROCERIES_ID)
    assert (row["amount"], row["category"], row["date"], row["description"]) == (99.0, "Bills", "2026-12-01", "New")


def test_update_expense_wrong_user_changes_nothing_and_returns_zero():
    other, _ = other_users_expense()
    before = stored(GROCERIES_ID)
    assert update_expense(GROCERIES_ID, other, 99.0, "Bills", "2026-12-01", "Hacked") == 0
    assert stored(GROCERIES_ID) == before


def test_update_expense_non_existent_returns_zero():
    assert update_expense(9999, SEED_USER_ID, 1.0, "Food", "2026-12-01", "x") == 0


def test_update_expense_can_store_a_null_description():
    assert update_expense(GROCERIES_ID, SEED_USER_ID, 38.5, "Food", "2026-11-03", None) == 1
    assert stored(GROCERIES_ID)["description"] is None


def test_update_expense_leaves_other_rows_and_created_at_alone():
    others_before = [stored(i) for i in range(1, 9) if i != GROCERIES_ID]
    created_at = stored(GROCERIES_ID)["created_at"]
    update_expense(GROCERIES_ID, SEED_USER_ID, 1.0, "Other", "2026-12-01", "x")
    assert [stored(i) for i in range(1, 9) if i != GROCERIES_ID] == others_before
    assert stored(GROCERIES_ID)["created_at"] == created_at


def test_recent_transactions_include_the_expense_id():
    rows = get_recent_transactions(SEED_USER_ID)
    assert all(stored(r["id"])["description"] == (r["description"] or None) for r in rows)
    assert {r["id"] for r in rows} == set(range(1, 9))


# ------------------------------------------------------------------ #
# Access control and 404s                                             #
# ------------------------------------------------------------------ #

def test_get_requires_login(client):
    response = client.get(f"/expenses/{GROCERIES_ID}/edit")
    assert response.status_code == 302 and response.headers["Location"].endswith("/login")


def test_post_requires_login_and_changes_nothing(client):
    before = stored(GROCERIES_ID)
    response = edit(client)
    assert response.status_code == 302 and response.headers["Location"].endswith("/login")
    assert stored(GROCERIES_ID) == before


def test_logged_out_request_for_an_unknown_id_redirects_to_login(client):
    assert client.get("/expenses/9999/edit").status_code == 302


def test_get_other_users_expense_is_404(client):
    _, other_expense = other_users_expense()
    login_as(client)
    assert client.get(f"/expenses/{other_expense}/edit").status_code == 404


def test_get_non_existent_expense_is_404(client):
    login_as(client)
    assert client.get("/expenses/9999/edit").status_code == 404


def test_post_other_users_expense_is_404_and_unchanged(client):
    _, other_expense = other_users_expense()
    before = stored(other_expense)
    login_as(client)
    assert edit(client, other_expense).status_code == 404
    assert stored(other_expense) == before


def test_post_other_users_expense_with_invalid_data_is_404_not_200(client):
    _, other_expense = other_users_expense()
    before = stored(other_expense)
    login_as(client)
    assert edit(client, other_expense, amount="abc", category="Nope", date="x").status_code == 404
    assert stored(other_expense) == before


def test_post_non_existent_expense_is_404(client):
    login_as(client)
    assert edit(client, 9999).status_code == 404


def test_stale_session_user_gets_404(client):
    login_as(client, 999)
    assert client.get(f"/expenses/{GROCERIES_ID}/edit").status_code == 404
    assert edit(client).status_code == 404


def test_the_other_user_can_edit_their_own_expense(client):
    other, other_expense = other_users_expense()
    login_as(client, other)
    assert edit(client, other_expense).status_code == 302
    assert stored(other_expense)["description"] == "Updated"
    assert stored(GROCERIES_ID)["description"] == "Groceries"


# ------------------------------------------------------------------ #
# GET /expenses/<id>/edit                                             #
# ------------------------------------------------------------------ #

def test_form_is_prefilled_with_the_current_values(client):
    login_as(client)
    response = client.get(f"/expenses/{GROCERIES_ID}/edit")
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'method="post"' in page and f'action="/expenses/{GROCERIES_ID}/edit"' in page
    assert 'value="38.50"' in page and 'value="2026-11-03"' in page and 'value="Groceries"' in page
    assert re.search(r'<option value="Food" selected>', page) and page.count(" selected>") == 1
    assert re.findall(r'<option value="(.*?)"', page) == CATEGORIES
    assert "Save Changes" in page and 'href="/profile"' in page


def test_the_correct_category_is_preselected_for_each_expense(client):
    login_as(client)
    for expense_id, category in [(1, "Bills"), (3, "Transport"), (8, "Other")]:
        page = client.get(f"/expenses/{expense_id}/edit").get_data(as_text=True)
        assert re.search(rf'<option value="{category}" selected>', page), expense_id


def test_null_description_shows_an_empty_field(client):
    update_expense(GROCERIES_ID, SEED_USER_ID, 38.5, "Food", "2026-11-03", None)
    login_as(client)
    page = client.get(f"/expenses/{GROCERIES_ID}/edit").get_data(as_text=True)
    field = re.search(r'<input type="text" id="description"[^>]*>', page).group(0)
    assert 'value=""' in field and "None" not in field


def test_add_and_edit_pages_share_one_category_list(client):
    login_as(client)
    add_page = client.get("/expenses/add").get_data(as_text=True)
    edit_page = client.get(f"/expenses/{GROCERIES_ID}/edit").get_data(as_text=True)
    assert re.findall(r'<option value="(.*?)"', add_page) == re.findall(r'<option value="(.*?)"', edit_page) == CATEGORIES


# ------------------------------------------------------------------ #
# POST /expenses/<id>/edit — success                                  #
# ------------------------------------------------------------------ #

def test_valid_edit_updates_the_database_and_redirects(client):
    login_as(client)
    response = edit(client)
    assert response.status_code == 302 and response.headers["Location"].endswith("/profile")
    row = stored(GROCERIES_ID)
    assert (row["amount"], row["category"], row["date"], row["description"]) == (99.5, "Bills", "2026-12-01", "Updated")
    assert row["user_id"] == SEED_USER_ID


def test_success_message_and_updated_values_on_profile(client):
    login_as(client)
    location = edit(client, description="Weekly shop").headers["Location"]
    html = client.get(location).get_data(as_text=True)
    assert "Expense updated successfully." in html and "flash-success" in html
    assert "Weekly shop" in html and "₹99.50" in html
    assert "Expense updated successfully." not in client.get("/profile").get_data(as_text=True)


def test_editing_does_not_add_or_remove_rows(client):
    login_as(client)
    edit(client)
    assert len(get_recent_transactions(SEED_USER_ID, limit=50)) == 8


def test_no_description_saves_null(client):
    login_as(client)
    assert edit(client, description="").status_code == 302
    assert stored(GROCERIES_ID)["description"] is None


def test_missing_description_field_saves_null(client):
    login_as(client)
    assert edit(client, description=None).status_code == 302
    assert stored(GROCERIES_ID)["description"] is None


def test_unpadded_date_is_saved_in_iso_form(client):
    login_as(client)
    assert edit(client, date="2026-3-5").status_code == 302
    assert stored(GROCERIES_ID)["date"] == "2026-03-05"


def test_amount_is_rounded_to_two_decimals(client):
    login_as(client)
    edit(client, amount="10.456")
    assert stored(GROCERIES_ID)["amount"] == 10.46


def test_description_is_stripped_and_200_characters_are_accepted(client):
    login_as(client)
    edit(client, description="  padded  ")
    assert stored(GROCERIES_ID)["description"] == "padded"
    assert edit(client, description="x" * 200).status_code == 302
    assert len(stored(GROCERIES_ID)["description"]) == 200


def test_saving_unchanged_values_still_succeeds(client):
    login_as(client)
    assert edit(client, amount="38.50", category="Food", date="2026-11-03", description="Groceries").status_code == 302
    assert stored(GROCERIES_ID)["amount"] == 38.5


# ------------------------------------------------------------------ #
# POST /expenses/<id>/edit — validation failures                      #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("overrides, message", [
    ({"amount": None}, "Amount is required."),
    ({"amount": ""}, "Amount is required."),
    ({"amount": "0"}, "Amount must be at least 0.01."),
    ({"amount": "-5"}, "Amount must be at least 0.01."),
    ({"amount": "abc"}, "Please enter a valid amount."),
    ({"amount": "inf"}, "Please enter a valid amount."),
    ({"amount": "nan"}, "Please enter a valid amount."),
    ({"amount": "10000000"}, "Amount must be at most 9,999,999.99."),
    ({"category": "Gadgets"}, "Please choose a valid category."),
    ({"category": None}, "Please choose a valid category."),
    ({"date": ""}, "Date is required."),
    ({"date": "not-a-date"}, "Please enter a valid date."),
    ({"date": "2026-13-45"}, "Please enter a valid date."),
    ({"description": "x" * 201}, "Description must be at most 200 characters."),
])
def test_invalid_submission_shows_error_and_leaves_the_row_unchanged(client, overrides, message):
    login_as(client)
    before = stored(GROCERIES_ID)
    response = edit(client, **overrides)
    assert response.status_code == 200
    assert error_message(response) == [message]
    assert stored(GROCERIES_ID) == before


def test_after_an_error_the_form_shows_the_submitted_values_not_the_original(client):
    login_as(client)
    response = edit(client, amount="abc", category="Shopping", date="2026-12-24", description="Typed")
    page = response.get_data(as_text=True)
    assert 'value="abc"' in page and 'value="2026-12-24"' in page and 'value="Typed"' in page
    assert re.search(r'<option value="Shopping" selected>', page) and page.count(" selected>") == 1
    assert 'value="Groceries"' not in page and 'value="38.50"' not in page


def test_after_an_error_the_form_still_posts_to_the_same_expense(client):
    login_as(client)
    page = edit(client, amount="abc").get_data(as_text=True)
    assert f'action="/expenses/{GROCERIES_ID}/edit"' in page


def test_html_in_submitted_values_is_escaped(client):
    login_as(client)
    page = edit(client, amount="abc", description='"><script>alert(1)</script>').get_data(as_text=True)
    assert "<script>alert(1)</script>" not in page and "&lt;script&gt;" in page


# ------------------------------------------------------------------ #
# Profile page links                                                  #
# ------------------------------------------------------------------ #

def test_every_profile_row_has_an_edit_link_to_its_own_id(client):
    login_as(client)
    page = client.get("/profile").get_data(as_text=True)
    tbody = re.search(r"<tbody>(.*?)</tbody>", page, re.S).group(1)
    links = re.findall(r'<a href="(/expenses/(\d+)/edit)" class="btn-edit">Edit</a>', tbody)
    assert [int(i) for _, i in links] == [8, 7, 6, 5, 4, 3, 2, 1]  # one per row, newest first
    assert len(re.findall(r"<tr>", tbody)) == 8


def test_actions_column_header_is_present(client):
    login_as(client)
    page = client.get("/profile").get_data(as_text=True)
    assert '<th class="tx-actions">Actions</th>' in page


def test_profile_row_links_work_for_a_filtered_view(client):
    login_as(client)
    page = client.get("/profile?date_from=2026-11-01&date_to=2026-11-03").get_data(as_text=True)
    assert re.findall(r'href="/expenses/(\d+)/edit"', page) == ["2", "1"]


# ------------------------------------------------------------------ #
# Template rules                                                      #
# ------------------------------------------------------------------ #

def test_edit_template_has_no_inline_styles_hex_colours_or_hardcoded_paths(client):
    login_as(client)
    page = client.get(f"/expenses/{GROCERIES_ID}/edit").get_data(as_text=True)
    assert "style=" not in page and "<style" not in page
    root = Path(__file__).resolve().parent.parent
    for name in ("edit_expense.html", "profile.html"):
        template = (root / "templates" / name).read_text(encoding="utf-8")
        assert not re.search(r"#[0-9a-fA-F]{3,8}\b", template), name
        assert not re.search(r'(href|src|action)="/', template), name
