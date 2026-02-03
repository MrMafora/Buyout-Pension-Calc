#!/usr/bin/env python3
"""
Add one-time or recurring reminders.
"""

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

OPENCLAW_DIR = Path.home() / ".openclaw" / "cron-manager"
REMINDERS_FILE = OPENCLAW_DIR / "reminders.json"

def ensure_dir():
    OPENCLAW_DIR.mkdir(parents=True, exist_ok=True)

def load_reminders():
    if REMINDERS_FILE.exists():
        with open(REMINDERS_FILE, 'r') as f:
            return json.load(f)
    return {"reminders": [], "version": "1.0"}

def save_reminders(data):
    with open(REMINDERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def parse_time(time_str):
    """Parse time string to datetime."""
    time_str = time_str.strip()
    
    # Relative time: +2h, +30m, +1d
    rel_match = re.match(r'\+(\d+)([hmd])', time_str)
    if rel_match:
        amount = int(rel_match.group(1))
        unit = rel_match.group(2)
        now = datetime.now()
        
        if unit == 'h':
            return now + timedelta(hours=amount)
        elif unit == 'm':
            return now + timedelta(minutes=amount)
        elif unit == 'd':
            return now + timedelta(days=amount)
    
    # Absolute time: 2026-02-03 14:30
    try:
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        pass
    
    # Time only: 14:30 (assumes today, or tomorrow if passed)
    try:
        t = datetime.strptime(time_str, "%H:%M").time()
        now = datetime.now()
        dt = datetime.combine(now.date(), t)
        if dt < now:
            dt += timedelta(days=1)
        return dt
    except ValueError:
        pass
    
    # Recurring patterns
    patterns = {
        r'every (\d+) minutes?': lambda m: ('minutes', int(m.group(1))),
        r'every (\d+) hours?': lambda m: ('hours', int(m.group(1))),
        r'hourly': lambda m: ('hours', 1),
        r'daily': lambda m: ('days', 1),
        r'weekly': lambda m: ('weeks', 1),
    }
    
    for pattern, parser in patterns.items():
        match = re.match(pattern, time_str.lower())
        if match:
            unit, interval = parser(match)
            return {"recurring": True, "unit": unit, "interval": interval}
    
    return None

def add_reminder(args):
    """Add a new reminder."""
    ensure_dir()
    
    # Parse time
    parsed = parse_time(args.time)
    
    if parsed is None:
        print(f"Error: Could not parse time: {args.time}", file=sys.stderr)
        print("Formats: '2026-02-03 14:30', '14:30', '+30m', '+2h', '+1d', 'every hour'", file=sys.stderr)
        sys.exit(1)
    
    data = load_reminders()
    
    reminder = {
        "id": str(uuid.uuid4())[:8],
        "message": args.message,
        "time": parsed.isoformat() if isinstance(parsed, datetime) else parsed,
        "channel": args.channel or os.environ.get("OPENCLAW_CRON_CHANNEL", "console"),
        "target": args.target,
        "related_to": args.related_to,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    data["reminders"].append(reminder)
    save_reminders(data)
    
    if isinstance(parsed, datetime):
        time_str = parsed.strftime("%Y-%m-%d %H:%M")
    else:
        time_str = f"every {parsed['interval']} {parsed['unit']}"
    
    print(f"✓ Reminder set")
    print(f"  Message: {args.message}")
    print(f"  Time: {time_str}")
    print(f"  Channel: {reminder['channel']}")
    if args.target:
        print(f"  Target: {args.target}")
    print(f"  ID: {reminder['id']}")

def main():
    parser = argparse.ArgumentParser(description="Add a one-time or recurring reminder")
    parser.add_argument("--message", "-m", required=True, help="Reminder message")
    parser.add_argument("--time", "-t", required=True, help="When to trigger (e.g., '2026-02-03 14:30', '+30m', 'every hour')")
    parser.add_argument("--channel", "-c", help="Notification channel (whatsapp, console, etc.)")
    parser.add_argument("--target", help="Target recipient/channel ID")
    parser.add_argument("--related-to", help="Related entity (e.g., 'lead-tracker:123')")
    
    args = parser.parse_args()
    add_reminder(args)

if __name__ == "__main__":
    main()
