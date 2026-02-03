#!/usr/bin/env python3
"""
Add a new scheduled job to the cron manager.
Supports standard cron syntax and natural language schedules.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import uuid

OPENCLAW_DIR = Path.home() / ".openclaw" / "cron-manager"
JOBS_FILE = OPENCLAW_DIR / "jobs.json"

def ensure_dir():
    """Ensure the cron-manager directory exists."""
    OPENCLAW_DIR.mkdir(parents=True, exist_ok=True)

def load_jobs():
    """Load existing jobs."""
    if JOBS_FILE.exists():
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return {"jobs": [], "version": "1.0"}

def save_jobs(data):
    """Save jobs to file."""
    with open(JOBS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def parse_natural_language(schedule):
    """Convert natural language to cron expression."""
    schedule = schedule.lower().strip()
    
    patterns = {
        r'every minute': '* * * * *',
        r'every (\d+) minutes?': lambda m: f'*/{m.group(1)} * * * *',
        r'every hour': '0 * * * *',
        r'every (\d+) hours?': lambda m: f'0 */{m.group(1)} * * *',
        r'daily|every day': '0 0 * * *',
        r'daily at (\d+)(?::00)?\s*(am|pm)?': lambda m: parse_time(m.group(1), m.group(2), daily=True),
        r'every day at (\d+):(\d+)\s*(am|pm)?': lambda m: parse_time_minutes(m.group(1), m.group(2), m.group(3), daily=True),
        r'weekly|every week': '0 0 * * 0',
        r'weekly on (\w+)(?: at (\d+):(\d+))?': parse_weekly,
        r'monthly|every month': '0 0 1 * *',
        r'every monday': '0 0 * * 1',
        r'every tuesday': '0 0 * * 2',
        r'every wednesday': '0 0 * * 3',
        r'every thursday': '0 0 * * 4',
        r'every friday': '0 0 * * 5',
        r'every saturday': '0 0 * * 6',
        r'every sunday': '0 0 * * 0',
        r'hourly': '0 * * * *',
        r'@reboot': '@reboot',
        r'@yearly|@annually': '@yearly',
        r'@monthly': '@monthly',
        r'@weekly': '@weekly',
        r'@daily|@midnight': '@daily',
        r'@hourly': '@hourly',
    }
    
    for pattern, replacement in patterns.items():
        match = re.match(pattern, schedule)
        if match:
            if callable(replacement):
                return replacement(match)
            return replacement
    
    # If no match, assume it's already a cron expression
    return schedule

def parse_time(hour, ampm, daily=False):
    """Parse time string to cron hour."""
    hour = int(hour)
    if ampm:
        if ampm.lower() == 'pm' and hour != 12:
            hour += 12
        elif ampm.lower() == 'am' and hour == 12:
            hour = 0
    return f'0 {hour} * * *' if daily else f'0 {hour}'

def parse_time_minutes(hour, minutes, ampm, daily=False):
    """Parse time with minutes."""
    hour = int(hour)
    minutes = int(minutes)
    if ampm:
        if ampm.lower() == 'pm' and hour != 12:
            hour += 12
        elif ampm.lower() == 'am' and hour == 12:
            hour = 0
    return f'{minutes} {hour} * * *' if daily else f'{minutes} {hour}'

def parse_weekly(match):
    """Parse weekly schedule with day."""
    day_map = {
        'monday': 1, 'mon': 1,
        'tuesday': 2, 'tue': 2, 'tues': 2,
        'wednesday': 3, 'wed': 3,
        'thursday': 4, 'thu': 4, 'thurs': 4,
        'friday': 5, 'fri': 5,
        'saturday': 6, 'sat': 6,
        'sunday': 0, 'sun': 0,
    }
    day_name = match.group(1).lower()
    day_num = day_map.get(day_name, 1)
    
    if match.group(2):
        hour = int(match.group(2))
        minutes = int(match.group(3)) if match.group(3) else 0
        return f'{minutes} {hour} * * {day_num}'
    return f'0 0 * * {day_num}'

def validate_cron(schedule):
    """Validate cron expression."""
    # Special keywords
    if schedule.startswith('@'):
        valid = ['@reboot', '@yearly', '@annually', '@monthly', '@weekly', '@daily', '@midnight', '@hourly']
        return schedule in valid
    
    # Standard cron: 5 fields
    parts = schedule.split()
    if len(parts) != 5:
        return False
    
    # Basic pattern validation
    field_patterns = [
        r'^(\*|\*/\d+|\d+|\d+-\d+|\d+,\d+)$',  # minute
        r'^(\*|\*/\d+|\d+|\d+-\d+|\d+,\d+)$',  # hour
        r'^(\*|\*/\d+|\d+|\d+-\d+|\d+,\d+)$',  # day of month
        r'^(\*|\*/\d+|\d+|\d+-\d+|\d+,\d+)$',  # month
        r'^(\*|\*/\d+|\d+|\d+-\d+|\d+,\d+)$',  # day of week
    ]
    
    for part, pattern in zip(parts, field_patterns):
        if not re.match(pattern, part):
            return False
    
    return True

def add_to_crontab(schedule, command):
    """Add job to system crontab."""
    try:
        # Get current crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current = result.stdout if result.returncode == 0 else ""
        
        # Add new entry
        new_entry = f"{schedule} {command}\n"
        new_crontab = current + new_entry
        
        # Install new crontab
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_crontab)
        
        return process.returncode == 0
    except Exception as e:
        print(f"Error adding to crontab: {e}", file=sys.stderr)
        return False

def add_job(args):
    """Add a new scheduled job."""
    ensure_dir()
    
    # Parse schedule
    schedule = parse_natural_language(args.schedule)
    
    if not validate_cron(schedule):
        print(f"Error: Invalid schedule expression: {schedule}", file=sys.stderr)
        print("Use --help for examples or use cron_helper.py to validate.", file=sys.stderr)
        sys.exit(1)
    
    # Load existing jobs
    data = load_jobs()
    
    # Check for duplicate names
    existing = [j for j in data["jobs"] if j.get("name") == args.name]
    if existing:
        print(f"Error: Job '{args.name}' already exists.", file=sys.stderr)
        print(f"Use update_job.py to modify or remove_job.py to delete.", file=sys.stderr)
        sys.exit(1)
    
    # Create job entry
    job = {
        "id": str(uuid.uuid4())[:8],
        "name": args.name,
        "schedule": schedule,
        "command": args.command,
        "description": args.description or "",
        "enabled": args.enabled,
        "tags": args.tags.split(',') if args.tags else [],
        "category": args.category or "",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "run_count": 0,
    }
    
    # Add to managed jobs
    data["jobs"].append(job)
    save_jobs(data)
    
    # Add to system crontab if enabled
    if args.enabled and args.system:
        if add_to_crontab(schedule, args.command):
            print(f"✓ Added to system crontab")
        else:
            print(f"⚠ Added to OpenClaw jobs but failed to add to system crontab")
    
    print(f"✓ Job '{args.name}' created successfully")
    print(f"  Schedule: {schedule}")
    print(f"  Command: {args.command}")
    print(f"  Status: {'enabled' if args.enabled else 'disabled'}")
    
    if args.tags:
        print(f"  Tags: {args.tags}")

def main():
    parser = argparse.ArgumentParser(description="Add a new scheduled job")
    parser.add_argument("--name", "-n", required=True, help="Unique job name")
    parser.add_argument("--schedule", "-s", required=True, help="Cron schedule or natural language (e.g., 'daily at 9am')")
    parser.add_argument("--command", "-c", required=True, help="Command to execute")
    parser.add_argument("--description", "-d", help="Job description")
    parser.add_argument("--tags", "-t", help="Comma-separated tags")
    parser.add_argument("--category", help="Job category")
    parser.add_argument("--enabled", action="store_true", default=True, help="Enable job immediately")
    parser.add_argument("--system", action="store_true", help="Also add to system crontab")
    
    args = parser.parse_args()
    add_job(args)

if __name__ == "__main__":
    main()
