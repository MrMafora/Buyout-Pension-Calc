#!/usr/bin/env python3
"""
List all scheduled cron jobs with details.
Supports filtering, formatting, and export options.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

OPENCLAW_DIR = Path.home() / ".openclaw" / "cron-manager"
JOBS_FILE = OPENCLAW_DIR / "jobs.json"

def ensure_dir():
    """Ensure the cron-manager directory exists."""
    OPENCLAW_DIR.mkdir(parents=True, exist_ok=True)

def load_managed_jobs():
    """Load OpenClaw-managed jobs from JSON."""
    if JOBS_FILE.exists():
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return {"jobs": [], "version": "1.0"}

def parse_crontab():
    """Parse system crontab entries."""
    jobs = []
    try:
        result = subprocess.run(
            ['crontab', '-l'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse cron line
                    parts = line.split()
                    if len(parts) >= 6:
                        schedule = ' '.join(parts[:5])
                        command = ' '.join(parts[5:])
                        jobs.append({
                            "schedule": schedule,
                            "command": command,
                            "source": "crontab",
                            "enabled": True
                        })
    except FileNotFoundError:
        pass
    return jobs

def format_schedule(schedule):
    """Format cron schedule for display."""
    # Common patterns
    patterns = {
        "* * * * *": "Every minute",
        "0 * * * *": "Every hour",
        "0 0 * * *": "Daily at midnight",
        "0 12 * * *": "Daily at noon",
        "0 9 * * 1": "Weekly (Mon 9AM)",
        "0 0 1 * *": "Monthly (1st)",
        "*/15 * * * *": "Every 15 minutes",
        "*/30 * * * *": "Every 30 minutes",
        "0 9-17 * * 1-5": "Hourly 9-5 weekdays",
    }
    return patterns.get(schedule, schedule)

def list_jobs(args):
    """List all jobs based on filters."""
    ensure_dir()
    
    managed = load_managed_jobs()
    all_jobs = []
    
    # Add OpenClaw-managed jobs
    for job in managed.get("jobs", []):
        job["source"] = "openclaw"
        all_jobs.append(job)
    
    # Add system crontab jobs if not filtered
    if not args.openclaw_only:
        system_jobs = parse_crontab()
        for job in system_jobs:
            job["name"] = job.get("command", "")[:30]
        all_jobs.extend(system_jobs)
    
    # Filter by tag
    if args.tag:
        all_jobs = [j for j in all_jobs if args.tag in j.get("tags", [])]
    
    # Filter by category
    if args.category:
        all_jobs = [j for j in all_jobs if j.get("category") == args.category]
    
    # Filter by name
    if args.name:
        all_jobs = [j for j in all_jobs if args.name.lower() in j.get("name", "").lower()]
    
    # Filter by status
    if args.status:
        enabled = args.status == "enabled"
        all_jobs = [j for j in all_jobs if j.get("enabled", True) == enabled]
    
    # Output format
    if args.format == "json":
        print(json.dumps(all_jobs, indent=2))
        return
    
    # Table format
    if not all_jobs:
        print("No jobs found.")
        return
    
    print(f"\n{'Name':<25} {'Schedule':<20} {'Status':<10} {'Source':<10}")
    print("-" * 70)
    
    for job in all_jobs:
        name = job.get("name", "unnamed")[:24]
        schedule = format_schedule(job.get("schedule", "-"))[:19]
        status = "enabled" if job.get("enabled", True) else "disabled"
        source = job.get("source", "unknown")
        
        print(f"{name:<25} {schedule:<20} {status:<10} {source:<10}")
        
        if args.verbose:
            if job.get("description"):
                print(f"  Description: {job['description']}")
            if job.get("command"):
                print(f"  Command: {job['command'][:60]}")
            if job.get("tags"):
                print(f"  Tags: {', '.join(job['tags'])}")
            if job.get("last_run"):
                print(f"  Last run: {job['last_run']}")
            print()
    
    print(f"\nTotal: {len(all_jobs)} job(s)")

def main():
    parser = argparse.ArgumentParser(description="List scheduled cron jobs")
    parser.add_argument("--format", choices=["table", "json"], default="table")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full details")
    parser.add_argument("--openclaw-only", action="store_true", help="Show only OpenClaw managed jobs")
    parser.add_argument("--tag", help="Filter by tag")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--name", help="Filter by name (partial match)")
    parser.add_argument("--status", choices=["enabled", "disabled"], help="Filter by status")
    
    args = parser.parse_args()
    list_jobs(args)

if __name__ == "__main__":
    main()
