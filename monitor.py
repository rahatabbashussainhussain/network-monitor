"""
Network & System Monitoring Tool
----------------------------------
Checks the availability of a list of hosts/services (via ping and/or HTTP)
and logs the results to a SQLite database with timestamps.

Usage:
    python monitor.py            # run one check cycle
    python monitor.py --loop     # run continuously every INTERVAL seconds
"""

import argparse
import platform
import sqlite3
import subprocess
import time
from datetime import datetime

import requests

DB_PATH = "monitor.db"
INTERVAL_SECONDS = 60

# Add / edit the hosts and services you want to monitor here.
TARGETS = [
    {"name": "Google DNS", "type": "ping", "target": "8.8.8.8"},
    {"name": "Cloudflare DNS", "type": "ping", "target": "1.1.1.1"},
    {"name": "Local Router", "type": "ping", "target": "192.168.1.1"},
    {"name": "GitHub", "type": "http", "target": "https://github.com"},
    {"name": "Google", "type": "http", "target": "https://www.google.com"},
]


def init_db():
    """Create the results table if it doesn't already exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            target TEXT NOT NULL,
            status TEXT NOT NULL,
            response_time_ms REAL,
            checked_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def check_ping(host, timeout=2):
    """Return (is_up, response_time_ms) using the system ping command."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
    command = ["ping", param, "1", timeout_param, str(timeout), host]

    start = time.time()
    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout + 2
        )
        elapsed_ms = (time.time() - start) * 1000
        return (result.returncode == 0, round(elapsed_ms, 2))
    except (subprocess.TimeoutExpired, OSError):
        return (False, None)


def check_http(url, timeout=5):
    """Return (is_up, response_time_ms) using an HTTP GET request."""
    start = time.time()
    try:
        response = requests.get(url, timeout=timeout)
        elapsed_ms = (time.time() - start) * 1000
        is_up = response.status_code < 400
        return (is_up, round(elapsed_ms, 2))
    except requests.RequestException:
        return (False, None)


def run_checks():
    """Run one full cycle of checks across all targets and store results."""
    conn = sqlite3.connect(DB_PATH)
    timestamp = datetime.now().isoformat(timespec="seconds")

    for item in TARGETS:
        if item["type"] == "ping":
            is_up, response_time = check_ping(item["target"])
        elif item["type"] == "http":
            is_up, response_time = check_http(item["target"])
        else:
            continue

        status = "UP" if is_up else "DOWN"
        conn.execute(
            "INSERT INTO checks (name, type, target, status, response_time_ms, checked_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (item["name"], item["type"], item["target"], status, response_time, timestamp),
        )
        print(f"[{timestamp}] {item['name']:<20} {status:<5} {response_time or '-'} ms")

    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Network & system uptime monitor")
    parser.add_argument("--loop", action="store_true", help="run continuously")
    parser.add_argument(
        "--interval", type=int, default=INTERVAL_SECONDS, help="seconds between checks in loop mode"
    )
    args = parser.parse_args()

    init_db()

    if args.loop:
        print(f"Starting continuous monitoring every {args.interval}s. Ctrl+C to stop.")
        try:
            while True:
                run_checks()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nStopped monitoring.")
    else:
        run_checks()


if __name__ == "__main__":
    main()
