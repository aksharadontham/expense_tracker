import calendar
import math
import re
import sqlite3
from datetime import date, datetime

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db
from database.queries import (
    delete_expense_by_id,
    get_category_breakdown,
    get_expense_by_id,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
    insert_expense,
    update_expense,
)

app = Flask(__name__)
app.secret_key = "spendly-dev-secret-key"

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$")

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]
MAX_AMOUNT = 9999999.99
MAX_DESCRIPTION_LENGTH = 200

with app.app_context():
    init_db()
    seed_db()


@app.template_filter("display_date")
def display_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d %b %Y")
    except (TypeError, ValueError):
        return value


def _initials(name):
    return "".join(word[0] for word in name.split()[:2]).upper()


def _parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _validate_expense(form):
    """Return (values, None) for a valid submission, or (None, error message)."""
    raw_amount = form.get("amount", "").strip()
    if not raw_amount:
        return None, "Amount is required."
    try:
        amount = float(raw_amount)
    except ValueError:
        return None, "Please enter a valid amount."
    if not math.isfinite(amount):
        return None, "Please enter a valid amount."
    if amount > MAX_AMOUNT:
        return None, "Amount must be at most 9,999,999.99."
    amount = round(amount, 2)
    if amount < 0.01:
        return None, "Amount must be at least 0.01."

    category = form.get("category", "")
    if category not in CATEGORIES:
        return None, "Please choose a valid category."

    raw_date = form.get("date", "").strip()
    if not raw_date:
        return None, "Date is required."
    parsed = _parse_date(raw_date)
    if parsed is None:
        return None, "Please enter a valid date."

    description = form.get("description", "").strip()
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return None, f"Description must be at most {MAX_DESCRIPTION_LENGTH} characters."

    return {
        "amount": amount,
        "category": category,
        "date": parsed.isoformat(),
        "description": description or None,
    }, None


def _submitted_values(form):
    return {
        "amount": form.get("amount", ""),
        "category": form.get("category", ""),
        "date": form.get("date", ""),
        "description": form.get("description", ""),
    }


def _add_months(day, months):
    index = day.year * 12 + (day.month - 1) + months
    year, month = divmod(index, 12)
    month += 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def _preset_ranges(today):
    month_start = today.replace(day=1)
    month_end = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    return [
        ("This Month", month_start.isoformat(), month_end.isoformat()),
        ("Last 3 Months", _add_months(today, -3).isoformat(), today.isoformat()),
        ("Last 6 Months", _add_months(today, -6).isoformat(), today.isoformat()),
        ("All Time", None, None),
    ]


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method not in ("GET", "POST"):
        abort(405)

    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    error = None
    if not (name and email and password and confirm_password):
        error = "All fields are required."
    elif not EMAIL_PATTERN.match(email):
        error = "Please enter a valid email address."
    elif len(password) < 8:
        error = "Password must be at least 8 characters."
    elif password != confirm_password:
        error = "Passwords do not match."
    else:
        try:
            create_user(name, email, password)
        except sqlite3.IntegrityError:
            error = "Email already registered."

    if error:
        flash(error, "error")
        return render_template("register.html", name=name, email=email)

    flash("Account created successfully. Please sign in.", "success")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("landing"))
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = get_user_by_email(email) if email and password else None
    if user is None or not check_password_hash(user["password_hash"], password):
        flash("Invalid email or password.", "error")
        return render_template("login.html", email=email)

    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("landing"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user = get_user_by_id(user_id)
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    start = _parse_date(request.args.get("date_from"))
    end = _parse_date(request.args.get("date_to"))
    if start and end and start > end:
        flash("Start date must be before end date.", "error")
        start = end = None
    elif not (start and end):
        start = end = None

    date_from = start.isoformat() if start else None
    date_to = end.isoformat() if end else None

    presets = []
    preset_matched = False
    for label, preset_from, preset_to in _preset_ranges(date.today()):
        active = (preset_from, preset_to) == (date_from, date_to)
        preset_matched = preset_matched or active
        presets.append({
            "label": label,
            "url": url_for("profile", date_from=preset_from, date_to=preset_to),
            "active": active,
        })

    user["initials"] = _initials(user["name"])
    return render_template(
        "profile.html",
        user=user,
        stats=get_summary_stats(user_id, date_from, date_to),
        expenses=get_recent_transactions(user_id, date_from=date_from, date_to=date_to),
        categories=get_category_breakdown(user_id, date_from, date_to),
        presets=presets,
        date_from=date_from,
        date_to=date_to,
        custom_active=bool(date_from) and not preset_matched,
    )


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    if get_user_by_id(user_id) is None:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "GET":
        values = {"amount": "", "category": "", "date": date.today().isoformat(), "description": ""}
        return render_template("add_expense.html", values=values, categories=CATEGORIES)

    cleaned, error = _validate_expense(request.form)
    if error:
        flash(error, "error")
        return render_template(
            "add_expense.html", values=_submitted_values(request.form), categories=CATEGORIES
        )

    insert_expense(user_id, **cleaned)
    flash("Expense added successfully.", "success")
    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
def edit_expense(id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    expense = get_expense_by_id(id, user_id)
    if expense is None:
        abort(404)

    if request.method == "GET":
        values = {
            "amount": f"{expense['amount']:.2f}",
            "category": expense["category"],
            "date": expense["date"],
            "description": expense["description"] or "",
        }
        return render_template(
            "edit_expense.html", expense=expense, values=values, categories=CATEGORIES
        )

    cleaned, error = _validate_expense(request.form)
    if error:
        flash(error, "error")
        return render_template(
            "edit_expense.html",
            expense=expense,
            values=_submitted_values(request.form),
            categories=CATEGORIES,
        )

    if update_expense(id, user_id, **cleaned) == 0:
        abort(404)
    flash("Expense updated successfully.", "success")
    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/delete", methods=["POST"])
def delete_expense(id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    if get_expense_by_id(id, user_id) is None:
        abort(404)
    if delete_expense_by_id(id, user_id) == 0:
        abort(404)

    flash("Expense deleted successfully.", "success")
    return redirect(url_for("profile"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
