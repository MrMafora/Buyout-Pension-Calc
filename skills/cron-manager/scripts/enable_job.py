#!/usr/bin/env python3
"""Enable a scheduled job."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

OPENCLAW_DIR = Path.home() / ".openclaw" / "cron-manager"
JOBS_FILE = OPENCLAW_DIR / "jobs.json"

def load_jobs():
    if JOBS_FILE.exists():
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return {"jobs": [], "version": "1.0"}

def save_jobs(data):
    with open(JOBS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def enable_job(args):
    data = load_jobs()
    
    for job in data["jobs"]:
        if job.get("name") == args.name:
            job["enabled"] = True
            job["updated_at"] = datetime.now().isoformat()
            save_jobs(data)
            print(f"✓ Job '{args.name}' enabled")
            return
    
    print(f"Error: Job '{args.name}' not found.", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Enable a scheduled job")
    parser.add_argument("--name", "-n", required=True, help="Job name to enable")
    args = parser.parse_args()
    enable_job(args)

if __name__ == "__main__":
    main()
