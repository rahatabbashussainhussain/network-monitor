# Network & Service Uptime Monitor

A lightweight Python tool that checks the availability of network devices and web
services, logs results to a SQLite database, and displays them on a live web dashboard.

Built to combine practical IT support / networking skills with Python scripting
and SQL — the kind of internal tool used by helpdesk and sysadmin teams to keep
an eye on infrastructure health.

## Features

- Checks hosts via **ICMP ping** (e.g. routers, servers, DNS) and **HTTP** (e.g. websites, APIs)
- Logs every check (status, response time, timestamp) to a SQLite database
- Can run **once** or **continuously on a schedule**
- Web dashboard (Flask) showing:
  - Current status of every monitored target
  - Uptime percentage per target
  - Recent check history
- Auto-refreshing dashboard, no manual page reloads needed

## Tech Stack

- Python 3
- SQLite3 (built-in)
- Flask (dashboard)
- `requests` (HTTP checks)

## Project Structure

```
network-monitor/
├── monitor.py          # Runs checks and writes results to monitor.db
├── dashboard.py         # Flask app that reads monitor.db and renders the dashboard
├── templates/
│   └── index.html        # Dashboard UI
├── requirements.txt
└── README.md
```

## Setup

```bash
git clone https://github.com/<your-username>/network-monitor.git
cd network-monitor
pip install -r requirements.txt
```

## Usage

1. Edit the `TARGETS` list in `monitor.py` to the hosts/services you want to track:

```python
TARGETS = [
    {"name": "Local Router", "type": "ping", "target": "192.168.1.1"},
    {"name": "Company Website", "type": "http", "target": "https://example.com"},
]
```

2. Run a single check:

```bash
python monitor.py
```

Or run continuously (every 60 seconds by default):

```bash
python monitor.py --loop --interval 60
```

3. In a second terminal, start the dashboard:

```bash
python dashboard.py
```

Open **http://127.0.0.1:5000** in your browser.

## Possible Extensions

- Email/Slack alert when a service goes down
- Historical uptime charts (e.g. with Chart.js)
- Docker container for easy deployment on a home server / Raspberry Pi
- Config file (YAML/JSON) instead of hardcoded targets list

## Author

Rahat Abbas Hussain Hussain — ICT graduate, Turku University of Applied Sciences
