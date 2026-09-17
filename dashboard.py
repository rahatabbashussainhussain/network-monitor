"""
Web dashboard for the network monitoring tool.
Reads results from monitor.db and displays current status + uptime history.

Usage:
    python dashboard.py
    Then open http://127.0.0.1:5000 in your browser.
"""

import sqlite3
from datetime import datetime

from flask import Flask, render_template

DB_PATH = "monitor.db"

app = Flask(__name__)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_latest_status():
    """Latest status per monitored target."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT name, type, target, status, response_time_ms, checked_at
        FROM checks
        WHERE id IN (
            SELECT MAX(id) FROM checks GROUP BY name
        )
        ORDER BY name
        """
    ).fetchall()
    conn.close()
    return rows


def get_uptime_stats():
    """Overall uptime percentage per target across all recorded checks."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            name,
            COUNT(*) AS total_checks,
            SUM(CASE WHEN status = 'UP' THEN 1 ELSE 0 END) AS up_checks
        FROM checks
        GROUP BY name
        ORDER BY name
        """
    ).fetchall()
    conn.close()

    stats = []
    for row in rows:
        uptime_pct = (row["up_checks"] / row["total_checks"] * 100) if row["total_checks"] else 0
        stats.append(
            {
                "name": row["name"],
                "total_checks": row["total_checks"],
                "uptime_pct": round(uptime_pct, 1),
            }
        )
    return stats


def get_recent_history(limit=25):
    conn = get_connection()
    rows = conn.execute(
        "SELECT name, status, response_time_ms, checked_at FROM checks "
        "ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return rows


@app.route("/")
def index():
    latest = get_latest_status()
    uptime_stats = get_uptime_stats()
    history = get_recent_history()
    return render_template(
        "index.html",
        latest=latest,
        uptime_stats=uptime_stats,
        history=history,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


if __name__ == "__main__":
    app.run(debug=True)
