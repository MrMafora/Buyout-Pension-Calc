#!/usr/bin/env python3
"""
Cancel a reminder.
"""

import argparse
import json
import sys
from pathlib import Path

OPENCLAW_DIR = Path.home() / ".openclaw" / "cron-manager"
REMINDERS_FILE = OPENCLAW_DIR / "reminders.json"

def load_reminders():
    if REMINDERS_FILE.exists():
        with open(REMINDERS_FILE, 'r') as f:
            return json.load(f)
    return {"reminders": []}

def save_reminders(data):
    with open(REMINDERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def cancel_reminder(args):
    data = load_reminders()
    
    for r in data.get("reminders", []):
        if r.get("id") == args.id:
            r["status"] = "cancelled"
            save_reminders(data)
            print(f"✓ Reminder '{args.id}' cancelled")
            print(f"  Message: {r.get('message', 'N/A')}")
            return
    
    print(f"Error: Reminder '{args.id}' not found.", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Cancel a reminder")
    parser.add_argument("--id", "-i", required=True, help="Reminder ID to cancel")
    args = parser.parse_args()
    cancel_reminder(args)

if __name__ == "__main__":
    main()
