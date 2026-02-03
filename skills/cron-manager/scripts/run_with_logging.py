#!/usr/bin/env python3
"""
Run a job with logging and capture output.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

OPENCLAW_DIR = Path.home() / ".openclaw" / "cron-manager"
HISTORY_FILE = OPENCLAW_DIR / "history.json"

def ensure_dir():
    OPENCLAW_DIR.mkdir(parents=True, exist_ok=True)

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {"runs": [], "version": "1.0"}

def save_history(data):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def run_with_logging(args):
    """Run a command with logging."""
    ensure_dir()
    
    job_name = args.job or "unnamed"
    command = args.command
    
    print(f"Running: {command}")
    
    # Record start
    start_time = datetime.now()
    
    try:
        # Run command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=args.timeout
        )
        
        # Calculate duration
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Record run
        run_record = {
            "job_name": job_name,
            "command": command,
            "started_at": start_time.isoformat(),
            "finished_at": end_time.isoformat(),
            "duration_ms": duration_ms,
            "status": "success" if result.returncode == 0 else "failed",
            "exit_code": result.returncode,
            "output": result.stdout[-500:] if result.stdout else "",  # Last 500 chars
            "error": result.stderr[-500:] if result.stderr else ""
        }
        
        data = load_history()
        data["runs"].append(run_record)
        
        # Trim history
        max_history = 1000
        if len(data["runs"]) > max_history:
            data["runs"] = data["runs"][-max_history:]
        
        save_history(data)
        
        # Output
        if args.verbose:
            if result.stdout:
                print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✓ Success ({duration_ms}ms)")
        else:
            print(f"✗ Failed with exit code {result.returncode} ({duration_ms}ms)")
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        run_record = {
            "job_name": job_name,
            "command": command,
            "started_at": start_time.isoformat(),
            "finished_at": end_time.isoformat(),
            "duration_ms": duration_ms,
            "status": "failed",
            "exit_code": -1,
            "error": "Timeout"
        }
        
        data = load_history()
        data["runs"].append(run_record)
        save_history(data)
        
        print(f"✗ Timeout after {args.timeout}s")
        return 1
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Run a job with logging")
    parser.add_argument("--job", "-j", help="Job name for logging")
    parser.add_argument("--command", "-c", required=True, help="Command to run")
    parser.add_argument("--timeout", "-t", type=int, default=300, help="Timeout in seconds")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show output")
    
    args = parser.parse_args()
    sys.exit(run_with_logging(args))

if __name__ == "__main__":
    main()
