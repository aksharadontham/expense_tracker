from datetime import datetime

from database.db import get_db


def _date_clause(date_from, date_to):
    # Filter only when both bounds are given; the dates are always bound as parameters.
    if date_from is None or date_to is None:
        return "", ()
    return " AND date BETWEEN ? AND ?", (date_from, date_to)


def insert_expense(user_id, amount, category, date, description):
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


def get_expense_by_id(expense_id, user_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id)
        ).fetchone()
    finally:
        conn.close()

    return dict(row) if row else None


def update_expense(expense_id, user_id, amount, category, date, description):
    conn = get_db()
    try:
        with conn:
            cursor = conn.execute(
                "UPDATE expenses SET amount = ?, category = ?, date = ?, description = ?"
                " WHERE id = ? AND user_id = ?",
                (amount, category, date, description, expense_id, user_id),
            )
        return cursor.rowcount
    finally:
        conn.close()


def delete_expense_by_id(expense_id, user_id):
    conn = get_db()
    try:
        with conn:
            cursor = conn.execute(
                "DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id)
            )
        return cursor.rowcount
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    created = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
    return {
        "name": row["name"],
        "email": row["email"],
        "member_since": created.strftime("%B %Y"),
    }


def get_summary_stats(user_id, date_from=None, date_to=None):
    clause, bounds = _date_clause(date_from, date_to)
    conn = get_db()
    try:
        totals = conn.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM(amount), 0) AS total"
            " FROM expenses WHERE user_id = ?" + clause,
            (user_id, *bounds),
        ).fetchone()
        top = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ?" + clause +
            " GROUP BY category"
            " ORDER BY ROUND(SUM(amount), 2) DESC, category ASC LIMIT 1",
            (user_id, *bounds),
        ).fetchone()
    finally:
        conn.close()

    if totals["n"] == 0:
        return {"total_spent": 0, "transaction_count": 0, "top_category": "—"}

    return {
        "total_spent": round(totals["total"], 2),
        "transaction_count": totals["n"],
        "top_category": top["category"],
    }


def get_recent_transactions(user_id, limit=10, date_from=None, date_to=None):
    clause, bounds = _date_clause(date_from, date_to)
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT id, date, description, category, amount FROM expenses"
            " WHERE user_id = ?" + clause +
            " ORDER BY date DESC, id DESC LIMIT ?",
            (user_id, *bounds, limit),
        ).fetchall()
    finally:
        conn.close()

    return [
        {
            "id": row["id"],
            "date": row["date"],
            "description": row["description"] or "",
            "category": row["category"],
            "amount": round(row["amount"], 2),
        }
        for row in rows
    ]


def get_category_breakdown(user_id, date_from=None, date_to=None):
    clause, bounds = _date_clause(date_from, date_to)
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT category, ROUND(SUM(amount), 2) AS total FROM expenses"
            " WHERE user_id = ?" + clause +
            " GROUP BY category"
            " ORDER BY ROUND(SUM(amount), 2) DESC, category ASC",
            (user_id, *bounds),
        ).fetchall()
    finally:
        conn.close()

    total = sum(row["total"] for row in rows)
    if not rows or total <= 0:
        return []

    breakdown = [
        {
            "name": row["category"],
            "amount": row["total"],
            "pct": int(row["total"] / total * 100 + 0.5),
        }
        for row in rows
    ]
    breakdown[0]["pct"] += 100 - sum(item["pct"] for item in breakdown)
    return breakdown
