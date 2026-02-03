#!/usr/bin/env python3
"""
View job execution history.
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

OPENCLAW_DIR = Path.home() / ".openclaw" / "cron-manager"
HISTORY_FILE = OPENCLAW_DIR / "history.json"

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {"runs": [], "version": "1.0"}

def parse_since(since_str):
    """Parse since string like '24h', '7d', '1w'."""
    if since_str.endswith('h'):
        hours = int(since_str[:-1])
        return datetime.now() - timedelta(hours=hours)
    elif since_str.endswith('d'):
        days = int(since_str[:-1])
        return datetime.now() - timedelta(days=days)
    elif since_str.endswith('w'):
        weeks = int(since_str[:-1])
        return datetime.now() - timedelta(weeks=weeks)
    return None

def view_history(args):
    data = load_history()
    runs = data.get("runs", [])
    
    # Filter by job name
    if args.job:
        runs = [r for r in runs if r.get("job_name") == args.job]
    
    # Filter by status
    if args.status:
        runs = [r for r in runs if r.get("status") == args.status]
    
    # Filter by time
    if args.since:
        cutoff = parse_since(args.since)
        if cutoff:
            runs = [r for r in runs if datetime.fromisoformat(r.get("started_at", "1970-01-01")) > cutoff]
    
    # Sort by time (newest first)
    runs = sorted(runs, key=lambda x: x.get("started_at", ""), reverse=True)
    
    # Limit results
    if args.limit:
        runs = runs[:args.limit]
    
    # Export format
    if args.export:
        if args.format == "json":
            print(json.dumps(runs, indent=2))
        elif args.format == "csv":
            print("job_name,started_at,status,duration_ms,exit_code")
            for r in runs:
                print(f"{r.get('job_name','')},{r.get('started_at','')},{r.get('status','')},{r.get('duration_ms',0)},{r.get('exit_code','')}")
        return
    
    # Table format
    if not runs:
        print("No history found.")
        return
    
    print(f"\n{'Job Name':<25} {'Started':<20} {'Status':<10} {'Duration':<12}")
    print("-" * 70)
    
    for r in runs:
        name = r.get("job_name", "-")[:24]
        started = r.get("started_at", "-")
        try:
            dt = datetime.fromisoformat(started)
            started = dt.strftime("%Y-%m-%d %H:%M")
        except:
            pass
        status = r.get("status", "-")
        duration = r.get("duration_ms", 0)
        if duration:
            if duration > 60000:
                duration_str = f"{duration/60000:.1f}m"
            else:
                duration_str = f"{duration/1000:.1f}s"
        else:
            duration_str = "-"
        
        status_icon = "✓" if status == "success" else "✗" if status == "failed" else "○"
        print(f"{name:<25} {started:<20} {status_icon} {status:<8} {duration_str:<12}")
        
        if args.verbose and r.get("output"):
            print(f"  Output: {r.get('output', '')[:100]}")
    
    print(f"\nTotal: {len(runs)} run(s)")
    
    # Summary
    success = len([r for r in runs if r.get("status") == "success"])
    failed = len([r for r in runs if r.get("status") == "failed"])
    print(f"Success: {success}, Failed: {failed}")

def main():
    parser = argparse.ArgumentParser(description="View job execution history")
    parser.add_argument("--job", "-j", help="Filter by job name")
    parser.add_argument("--status", choices=["success", "failed", "running"], help="Filter by status")
    parser.add_argument("--since", "-s", help="Show runs since time (e.g., '24h', '7d')")
    parser.add_argument("--limit", "-l", type=int, help="Limit number of results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show output details")
    parser.add_argument("--export", action="store_true", help="Export to file/stdout")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Export format")
    
    args = parser.parse_args()
    view_history(args)

if __name__ == "__main__":
    main()
