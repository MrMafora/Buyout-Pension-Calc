#!/usr/bin/env python3
"""
Update an existing scheduled job.
Supports modifying schedule, command, tags, and status.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

OPENCLAW_DIR = Path.home() / ".openclaw" / "cron-manager"
JOBS_FILE = OPENCLAW_DIR / "jobs.json"

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

def find_job(data, name):
    """Find job by name."""
    for i, job in enumerate(data["jobs"]):
        if job.get("name") == name:
            return i, job
    return None, None

def update_job(args):
    """Update an existing job."""
    data = load_jobs()
    
    idx, job = find_job(data, args.name)
    if idx is None:
        print(f"Error: Job '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    
    changes = []
    
    # Update schedule
    if args.schedule:
        job["schedule"] = args.schedule
        changes.append(f"schedule -> {args.schedule}")
    
    # Update command
    if args.command:
        job["command"] = args.command
        changes.append(f"command updated")
    
    # Update description
    if args.description is not None:
        job["description"] = args.description
        changes.append("description updated")
    
    # Update enabled status
    if args.enabled is not None:
        enabled = args.enabled.lower() in ('true', 'yes', '1', 'on')
        job["enabled"] = enabled
        changes.append(f"status -> {'enabled' if enabled else 'disabled'}")
    
    # Add tags
    if args.add_tags:
        new_tags = args.add_tags.split(',')
        existing_tags = set(job.get("tags", []))
        existing_tags.update(new_tags)
        job["tags"] = list(existing_tags)
        changes.append(f"tags added: {args.add_tags}")
    
    # Remove tags
    if args.remove_tags:
        remove_tags = args.remove_tags.split(',')
        job["tags"] = [t for t in job.get("tags", []) if t not in remove_tags]
        changes.append(f"tags removed: {args.remove_tags}")
    
    # Update category
    if args.category:
        job["category"] = args.category
        changes.append(f"category -> {args.category}")
    
    # Update timestamp
    job["updated_at"] = datetime.now().isoformat()
    
    # Save changes
    data["jobs"][idx] = job
    save_jobs(data)
    
    if changes:
        print(f"✓ Job '{args.name}' updated:")
        for change in changes:
            print(f"  • {change}")
    else:
        print(f"No changes made to job '{args.name}'")
        print("Use --help to see available options")

def main():
    parser = argparse.ArgumentParser(description="Update an existing scheduled job")
    parser.add_argument("--name", "-n", required=True, help="Job name to update")
    parser.add_argument("--schedule", "-s", help="New cron schedule")
    parser.add_argument("--command", "-c", help="New command")
    parser.add_argument("--description", "-d", help="New description")
    parser.add_argument("--enabled", choices=["true", "false", "yes", "no"], help="Enable/disable job")
    parser.add_argument("--add-tags", help="Comma-separated tags to add")
    parser.add_argument("--remove-tags", help="Comma-separated tags to remove")
    parser.add_argument("--category", help="Set category")
    
    args = parser.parse_args()
    update_job(args)

if __name__ == "__main__":
    main()
