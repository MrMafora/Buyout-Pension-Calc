#!/usr/bin/env python3
"""
Remove a scheduled job from the cron manager.
"""

import argparse
import json
import sys
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

def remove_job(args):
    """Remove a scheduled job."""
    data = load_jobs()
    
    # Find job
    job_to_remove = None
    for job in data["jobs"]:
        if job.get("name") == args.name:
            job_to_remove = job
            break
    
    if not job_to_remove:
        print(f"Error: Job '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Confirm if requested
    if args.confirm:
        print(f"Job: {job_to_remove['name']}")
        print(f"Schedule: {job_to_remove.get('schedule', 'N/A')}")
        print(f"Command: {job_to_remove.get('command', 'N/A')}")
        confirm = input("Are you sure you want to remove this job? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
    
    # Remove job
    data["jobs"] = [j for j in data["jobs"] if j.get("name") != args.name]
    save_jobs(data)
    
    print(f"✓ Job '{args.name}' removed successfully")

def main():
    parser = argparse.ArgumentParser(description="Remove a scheduled job")
    parser.add_argument("--name", "-n", required=True, help="Job name to remove")
    parser.add_argument("--confirm", action="store_true", help="Prompt for confirmation")
    
    args = parser.parse_args()
    remove_job(args)

if __name__ == "__main__":
    main()
