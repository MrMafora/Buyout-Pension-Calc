#!/usr/bin/env python3
"""
List active reminders.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

OPENCLAW_DIR = Path.home() / ".openclaw" / "cron-manager"
REMINDERS_FILE = OPENCLAW_DIR / "reminders.json"

def load_reminders():
    if REMINDERS_FILE.exists():
        with open(REMINDERS_FILE, 'r') as f:
            return json.load(f)
    return {"reminders": []}

def list_reminders(args):
    data = load_reminders()
    reminders = data.get("reminders", [])
    
    # Filter by status
    if args.status:
        reminders = [r for r in reminders if r.get("status") == args.status]
    else:
        # Default: show only active
        reminders = [r for r in reminders if r.get("status") == "active"]
    
    if not reminders:
        print("No reminders found.")
        return
    
    print(f"\n{'ID':<10} {'Message':<35} {'Time':<20} {'Channel':<10}")
    print("-" * 80)
    
    for r in reminders:
        rid = r.get("id", "-")[:9]
        msg = r.get("message", "-")[:34]
        time_val = r.get("time", "-")
        
        # Format time
        if isinstance(time_val, str) and 'T' in time_val:
            try:
                dt = datetime.fromisoformat(time_val)
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = str(time_val)[:19]
        elif isinstance(time_val, dict):
            time_str = f"every {time_val.get('interval', '?')} {time_val.get('unit', '?')}"
        else:
            time_str = str(time_val)[:19]
        
        channel = r.get("channel", "console")
        
        print(f"{rid:<10} {msg:<35} {time_str:<20} {channel:<10}")
    
    print(f"\nTotal: {len(reminders)} reminder(s)")

def main():
    parser = argparse.ArgumentParser(description="List active reminders")
    parser.add_argument("--status", choices=["active", "completed", "cancelled", "all"], help="Filter by status")
    
    args = parser.parse_args()
    list_reminders(args)

if __name__ == "__main__":
    main()
