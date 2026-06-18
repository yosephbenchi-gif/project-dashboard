#!/usr/bin/env python3
"""
Dashboard sync script.
Collects all status.json files from a list of project directories (or a
GitHub repo root) and outputs a single dashboard-data.json that the
HTML dashboard reads.

Usage:
  python sync.py                     # reads paths from config.json
  python sync.py --dirs path1 path2  # pass project dirs directly
"""

import json
import os
import sys
import glob
import argparse
from datetime import datetime, timezone


CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "docs", "dashboard-data.json")
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "docs", "dashboard-history.json")


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {"project_dirs": [], "owner": "Team"}


def find_status_files(dirs):
    files = []
    for d in dirs:
        pattern = os.path.join(d, "status.json")
        matches = glob.glob(pattern)
        files.extend(matches)
        # also search one level deep
        pattern2 = os.path.join(d, "*", "status.json")
        files.extend(glob.glob(pattern2))
    return list(set(files))


def load_status(path):
    try:
        with open(path) as f:
            data = json.load(f)
        # Validate required fields, fill defaults if missing
        defaults = {
            "project_name": "Unnamed Project",
            "project_id": "unknown",
            "owner": "Unknown",
            "status": "Unknown",
            "priority": "Medium",
            "progress_percent": 0,
            "last_updated": "Unknown",
            "due_date": None,
            "is_overdue": False,
            "current_focus": "",
            "completed_work": [],
            "next_steps": [],
            "blockers": [],
            "risks": [],
            "important_links": [],
            "recent_updates": [],
            "summary_for_manager": ""
        }
        for k, v in defaults.items():
            if k not in data:
                data[k] = v
        # Recalculate is_overdue
        if data["due_date"]:
            try:
                due = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
                today = datetime.now(timezone.utc).date()
                data["is_overdue"] = (due < today and data["status"] != "Completed")
            except ValueError:
                pass
        data["_source_path"] = path
        return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"WARNING: Could not load {path}: {e}", file=sys.stderr)
        return None


def compute_summary(projects):
    total = len(projects)
    by_status = {}
    for p in projects:
        s = p.get("status", "Unknown")
        by_status[s] = by_status.get(s, 0) + 1
    overdue = sum(1 for p in projects if p.get("is_overdue"))
    blocked = sum(1 for p in projects if p.get("status") == "Blocked")

    all_blockers = []
    for p in projects:
        for b in p.get("blockers", []):
            all_blockers.append({
                "project": p["project_name"],
                **b
            })

    # Upcoming deadlines (next 14 days)
    today = datetime.now(timezone.utc).date()
    upcoming = []
    for p in projects:
        if p.get("due_date") and p["status"] not in ("Completed",):
            try:
                due = datetime.strptime(p["due_date"], "%Y-%m-%d").date()
                days_left = (due - today).days
                if 0 <= days_left <= 14:
                    upcoming.append({
                        "project": p["project_name"],
                        "due_date": p["due_date"],
                        "days_left": days_left,
                        "status": p["status"]
                    })
            except ValueError:
                pass
    upcoming.sort(key=lambda x: x["days_left"])

    return {
        "total": total,
        "by_status": by_status,
        "overdue": overdue,
        "blocked": blocked,
        "all_blockers": all_blockers,
        "upcoming_deadlines": upcoming,
        "in_progress": by_status.get("In Progress", 0),
        "completed": by_status.get("Completed", 0)
    }


def save_history(projects):
    """Append a snapshot to history for "what changed this week" tracking."""
    now = datetime.now(timezone.utc).isoformat()
    snapshot = {
        "timestamp": now,
        "projects": [
            {
                "project_id": p["project_id"],
                "status": p["status"],
                "progress_percent": p["progress_percent"],
                "last_updated": p["last_updated"]
            }
            for p in projects
        ]
    }
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []
    history.append(snapshot)
    # Keep last 100 snapshots
    history = history[-100:]
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Sync project status files to dashboard.")
    parser.add_argument("--dirs", nargs="*", help="Project directories to scan")
    args = parser.parse_args()

    config = load_config()
    dirs = args.dirs if args.dirs else config.get("project_dirs", [])

    if not dirs:
        print("No project directories configured. Edit scripts/config.json or pass --dirs.", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {len(dirs)} director(ies)...")
    status_files = find_status_files(dirs)
    print(f"Found {len(status_files)} status.json file(s).")

    projects = []
    for path in status_files:
        data = load_status(path)
        if data:
            projects.append(data)
            print(f"  ✓ {data['project_name']} ({data['status']}, {data['progress_percent']}%)")
        else:
            print(f"  ✗ Skipped: {path}")

    summary = compute_summary(projects)
    save_history(projects)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "owner": config.get("owner", "Team"),
        "summary": summary,
        "projects": projects
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nDashboard data written to: {OUTPUT_FILE}")
    print(f"Summary: {summary['total']} total, {summary['in_progress']} in progress, "
          f"{summary['blocked']} blocked, {summary['overdue']} overdue.")


if __name__ == "__main__":
    main()
