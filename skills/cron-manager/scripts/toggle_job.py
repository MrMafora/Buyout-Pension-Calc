#!/usr/bin/env python3
"""
Enable or disable a scheduled job.
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

def set_job_status(name, enabled):
    """Set job enabled status."""
    data = load_jobs()
    
    for job in data["jobs"]:
        if job.get("name") == name:
            job["enabled"] = enabled
            job["updated_at"] = datetime.now().isoformat()
            save_jobs(data)
            status = "enabled" if enabled else "disabled"
            print(f"✓ Job '{name}' {status}")
            return
    
    print(f"Error: Job '{name}' not found.", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Enable or disable a scheduled job")
    parser.add_argument("--name", "-n", required=True, help="Job name")
    
    subparsers = parser.add_subparsers(dest='action')
    
    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable a job')
    enable_parser.add_argument("--name", "-n", required=True, help="Job name")
    
    # Disable command  
    disable_parser = subparsers.add_parser('disable', help='Disable a job')
    disable_parser.add_argument("--name", "-n", required=True, help="Job name")
    
    args = parser.parse_args()
    
    if args.action == 'enable' or (hasattr(args, 'enable') and args.enable is not False):
        set_job_status(args.name, True)
    elif args.action == 'disable':
        set_job_status(args.name, False)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
