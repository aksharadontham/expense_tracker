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
from database import queries  # noqa: E402
from database.db import create_user, get_db, init_db, seed_db  # noqa: E402
from database.queries import delete_expense_by_id, insert_expense  # noqa: E402

SEED_USER_ID = 1
GROCERIES_ID = 2  # seed: 2026-11-03, Food, 38.50, "Groceries"


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


def all_ids():
    conn = get_db()
    try:
        return [r["id"] for r in conn.execute("SELECT id FROM expenses ORDER BY id")]
    finally:
        conn.close()


def delete(client, expense_id=GROCERIES_ID):
    return client.post(f"/expenses/{expense_id}/delete")


# ------------------------------------------------------------------ #
# delete_expense_by_id                                                #
# ------------------------------------------------------------------ #

def test_delete_removes_the_row_and_returns_one():
    assert delete_expense_by_id(GROCERIES_ID, SEED_USER_ID) == 1
    assert stored(GROCERIES_ID) is None
    assert all_ids() == [1, 3, 4, 5, 6, 7, 8]


def test_delete_with_the_wrong_user_keeps_the_row_and_returns_zero():
    other, _ = other_users_expense()
    before = stored(GROCERIES_ID)
    assert delete_expense_by_id(GROCERIES_ID, other) == 0
    assert stored(GROCERIES_ID) == before


def test_delete_of_a_non_existent_id_returns_zero_and_changes_nothing():
    before = all_ids()
    assert delete_expense_by_id(9999, SEED_USER_ID) == 0
    assert all_ids() == before


def test_deleting_the_same_row_twice_returns_zero_the_second_time():
    assert delete_expense_by_id(GROCERIES_ID, SEED_USER_ID) == 1
    assert delete_expense_by_id(GROCERIES_ID, SEED_USER_ID) == 0


# ------------------------------------------------------------------ #
# POST /expenses/<id>/delete                                          #
# ------------------------------------------------------------------ #

def test_logged_out_post_redirects_to_login_and_deletes_nothing(client):
    response = delete(client)
    assert response.status_code == 302 and response.headers["Location"].endswith("/login")
    assert stored(GROCERIES_ID) is not None


def test_own_expense_is_deleted_and_user_is_redirected_to_profile(client):
    login_as(client)
    response = delete(client)
    assert response.status_code == 302 and response.headers["Location"].endswith("/profile")
    assert stored(GROCERIES_ID) is None
    assert len(all_ids()) == 7


def test_redirect_goes_to_the_unfiltered_profile_page(client):
    login_as(client)
    assert delete(client).headers["Location"] == "/profile"


def test_other_users_expense_gives_404_and_stays(client):
    _, other_expense = other_users_expense()
    before = stored(other_expense)
    login_as(client)
    assert delete(client, other_expense).status_code == 404
    assert stored(other_expense) == before


def test_non_existent_expense_gives_404(client):
    login_as(client)
    assert delete(client, 9999).status_code == 404
    assert len(all_ids()) == 8


def test_stale_session_user_gets_404_and_deletes_nothing(client):
    login_as(client, 999)
    assert delete(client).status_code == 404
    assert len(all_ids()) == 8


def test_deleting_twice_gives_404_the_second_time(client):
    login_as(client)
    assert delete(client).status_code == 302
    assert delete(client).status_code == 404


def test_the_other_user_can_delete_their_own_expense_only(client):
    other, other_expense = other_users_expense()
    login_as(client, other)
    assert delete(client, other_expense).status_code == 302
    assert stored(other_expense) is None
    assert delete(client, GROCERIES_ID).status_code == 404
    assert stored(GROCERIES_ID) is not None


# ------------------------------------------------------------------ #
# Methods                                                             #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_other_methods_give_405_when_logged_in(client, method):
    login_as(client)
    assert getattr(client, method)(f"/expenses/{GROCERIES_ID}/delete").status_code == 405
    assert stored(GROCERIES_ID) is not None


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_other_methods_give_405_when_logged_out(client, method):
    assert getattr(client, method)(f"/expenses/{GROCERIES_ID}/delete").status_code == 405


def test_get_on_an_unknown_id_is_still_405(client):
    login_as(client)
    assert client.get("/expenses/9999/delete").status_code == 405


def test_route_accepts_only_post():
    rule = next(r for r in app_module.app.url_map.iter_rules() if r.endpoint == "delete_expense")
    assert rule.methods - {"OPTIONS"} == {"POST"}


def test_helper_and_route_have_different_names():
    assert app_module.delete_expense is not queries.delete_expense_by_id
    assert not hasattr(queries, "delete_expense")
    assert app_module.delete_expense.__name__ == "delete_expense"


# ------------------------------------------------------------------ #
# After deleting                                                      #
# ------------------------------------------------------------------ #

def test_success_message_is_shown_and_the_expense_is_gone_from_the_list(client):
    login_as(client)
    location = delete(client).headers["Location"]
    html = client.get(location).get_data(as_text=True)
    assert "Expense deleted successfully." in html and "flash-success" in html
    assert "Groceries" not in html
    assert re.findall(r'stat-value">(.*?)<', html) == ["₹307.74", "7", "Bills"]  # 346.24 - 38.50
    assert "Expense deleted successfully." not in client.get("/profile").get_data(as_text=True)


def test_only_the_deleted_expense_disappears_from_the_list(client):
    login_as(client)
    delete(client)
    html = client.get("/profile").get_data(as_text=True)
    tbody = re.search(r"<tbody>(.*?)</tbody>", html, re.S).group(1)
    assert re.findall(r'href="/expenses/(\d+)/edit"', tbody) == ["8", "7", "6", "5", "4", "3", "1"]


def test_deleting_every_expense_leaves_a_working_empty_profile(client):
    login_as(client)
    for expense_id in range(1, 9):
        assert delete(client, expense_id).status_code == 302
    response = client.get("/profile")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert re.findall(r'stat-value">(.*?)<', html) == ["₹0.00", "0", "—"]
    assert "<progress" not in html


def test_deleting_one_users_expense_does_not_change_another_users_totals(client):
    other, other_expense = other_users_expense()
    login_as(client)
    delete(client)
    login_as(client, other)
    html = client.get("/profile").get_data(as_text=True)
    assert re.findall(r'stat-value">(.*?)<', html) == ["₹7.00", "1", "Other"]


# ------------------------------------------------------------------ #
# Profile page: actions column                                        #
# ------------------------------------------------------------------ #

def profile_rows(client):
    login_as(client)
    html = client.get("/profile").get_data(as_text=True)
    tbody = re.search(r"<tbody>(.*?)</tbody>", html, re.S).group(1)
    return html, re.findall(r"<tr>.*?</tr>", tbody, re.S)


def test_every_row_has_both_an_edit_link_and_a_delete_form(client):
    _, rows = profile_rows(client)
    assert len(rows) == 8
    for row in rows:
        expense_id = re.search(r'href="/expenses/(\d+)/edit" class="btn-edit">Edit</a>', row).group(1)
        form = re.search(r"<form[^>]*>", row).group(0)
        assert 'method="post"' in form
        assert f'action="/expenses/{expense_id}/delete"' in form
        assert 'class="inline-form"' in form
        assert "return confirm('Delete this expense?')" in form
        assert '<button type="submit" class="btn-delete">Delete</button>' in row


def test_delete_forms_point_at_the_right_ids_in_row_order(client):
    _, rows = profile_rows(client)
    assert [re.search(r'action="/expenses/(\d+)/delete"', r).group(1) for r in rows] == \
        ["8", "7", "6", "5", "4", "3", "2", "1"]


def test_profile_page_has_no_inline_styles(client):
    html, _ = profile_rows(client)
    assert "style=" not in html and "<style" not in html


def test_template_and_stylesheet_follow_the_colour_and_path_rules():
    root = Path(__file__).resolve().parent.parent
    template = (root / "templates" / "profile.html").read_text(encoding="utf-8")
    css = (root / "static" / "css" / "profile.css").read_text(encoding="utf-8")
    assert "style=" not in template
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", template)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", css)
    assert not re.search(r'(href|src|action)="/', template)
    block = re.search(r"\.btn-delete\s*\{([^}]*)\}", css).group(1)
    assert "var(--danger)" in block
    assert re.search(r"\.inline-form\s*\{[^}]*display:\s*inline", css)
