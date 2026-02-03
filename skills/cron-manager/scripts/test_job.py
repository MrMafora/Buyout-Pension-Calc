#!/usr/bin/env python3
"""
Test a scheduled job manually.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

OPENCLAW_DIR = Path.home() / ".openclaw" / "cron-manager"
JOBS_FILE = OPENCLAW_DIR / "jobs.json"

def load_jobs():
    if JOBS_FILE.exists():
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return {"jobs": []}

def test_job(args):
    """Test a job by running it manually."""
    data = load_jobs()
    
    # Find job
    job = None
    for j in data.get("jobs", []):
        if j.get("name") == args.name:
            job = j
            break
    
    if not job:
        print(f"Error: Job '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    
    command = job.get("command")
    
    print(f"Testing job: {args.name}")
    print(f"Schedule: {job.get('schedule')}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=not args.verbose,
            text=True,
            timeout=args.timeout
        )
        
        print("-" * 50)
        
        if result.returncode == 0:
            print(f"✓ Success (exit code {result.returncode})")
        else:
            print(f"✗ Failed (exit code {result.returncode})")
        
        if args.capture_output or args.verbose:
            if result.stdout:
                print("\nSTDOUT:")
                print(result.stdout)
            if result.stderr:
                print("\nSTDERR:")
                print(result.stderr)
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout after {args.timeout}s")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Test a scheduled job manually")
    parser.add_argument("--name", "-n", required=True, help="Job name to test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show live output")
    parser.add_argument("--capture-output", action="store_true", help="Capture and display output")
    parser.add_argument("--timeout", "-t", type=int, default=300, help="Timeout in seconds")
    
    args = parser.parse_args()
    sys.exit(test_job(args))

if __name__ == "__main__":
    main()
