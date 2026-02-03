#!/usr/bin/env python3
"""
Health check for scheduled jobs.
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

OPENCLAW_DIR = Path.home() / ".openclaw" / "cron-manager"
JOBS_FILE = OPENCLAW_DIR / "jobs.json"
HISTORY_FILE = OPENCLAW_DIR / "history.json"

def load_jobs():
    if JOBS_FILE.exists():
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return {"jobs": []}

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {"runs": []}

def health_check(args):
    """Check health of scheduled jobs."""
    jobs_data = load_jobs()
    history_data = load_history()
    
    jobs = jobs_data.get("jobs", [])
    runs = history_data.get("runs", [])
    
    # Only check enabled jobs
    enabled_jobs = [j for j in jobs if j.get("enabled", True)]
    
    issues = []
    healthy = []
    
    for job in enabled_jobs:
        job_name = job.get("name")
        
        # Get recent runs for this job
        job_runs = [r for r in runs if r.get("job_name") == job_name]
        job_runs = sorted(job_runs, key=lambda x: x.get("started_at", ""), reverse=True)
        
        # Check if job has ever run
        if not job_runs:
            issues.append({
                "job": job_name,
                "issue": "Never run",
                "severity": "warning"
            })
            continue
        
        # Check last run status
        last_run = job_runs[0]
        if last_run.get("status") == "failed":
            issues.append({
                "job": job_name,
                "issue": f"Last run failed (exit code {last_run.get('exit_code', '?')})",
                "severity": "error"
            })
            continue
        
        # Check for repeated failures
        recent_runs = job_runs[:5]
        failed_count = sum(1 for r in recent_runs if r.get("status") == "failed")
        if failed_count >= 3:
            issues.append({
                "job": job_name,
                "issue": f"{failed_count}/5 recent runs failed",
                "severity": "error"
            })
            continue
        
        # Check if job is overdue (simplified)
        last_run_time = datetime.fromisoformat(last_run.get("started_at", "1970-01-01"))
        days_since = (datetime.now() - last_run_time).days
        
        if job.get("schedule") == "0 0 * * *" and days_since > 2:  # Daily job
            issues.append({
                "job": job_name,
                "issue": f"Overdue by {days_since} days",
                "severity": "warning"
            })
            continue
        
        healthy.append(job_name)
    
    # Filter by severity if requested
    if args.critical_only:
        issues = [i for i in issues if i["severity"] == "error"]
    
    # Output
    if issues:
        print("\nHealth Issues Found:")
        print("=" * 50)
        for issue in issues:
            icon = "✗" if issue["severity"] == "error" else "⚠"
            print(f"{icon} {issue['job']}: {issue['issue']}")
    else:
        print("\n✓ All jobs healthy")
    
    if not args.critical_only and healthy:
        print(f"\nHealthy jobs: {len(healthy)}")
    
    print(f"\nTotal checked: {len(enabled_jobs)}")
    print(f"Issues: {len(issues)}")

def main():
    parser = argparse.ArgumentParser(description="Check health of scheduled jobs")
    parser.add_argument("--critical-only", "-c", action="store_true", help="Show only critical issues")
    
    args = parser.parse_args()
    health_check(args)

if __name__ == "__main__":
    main()
