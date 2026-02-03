#!/usr/bin/env python3
"""
Full memory maintenance - comprehensive review and cleanup.
Run this during heartbeat maintenance cycles.
"""

import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path("/root/.openclaw/workspace/skills/memory-curator")

def run_script(script_name, *args):
    """Run a maintenance script."""
    script_path = SKILL_DIR / "scripts" / script_name
    cmd = [sys.executable, str(script_path)] + list(args)
    
    print(f"\n{'='*60}")
    print(f"🔄 Running: {script_name}")
    print('='*60)
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0

def full_maintenance(days=30):
    """Run complete memory maintenance cycle."""
    print("🔧 FULL MEMORY MAINTENANCE")
    print("=" * 60)
    print(f"Review period: last {days} days")
    print("=" * 60)
    
    steps = [
        ("Review recent files", "review-recent.py", [f"--days={days}"]),
        ("Extract important entries", "extract-important.py", [f"--days={days}"]),
        ("Generate summary", "generate-summary.py", [f"--days={days}"]),
        ("Archive old files", "archive-old.py", [f"--days={days}"]),
        ("Analyze cleanup needs", "cleanup-memory.py", ["--dry-run"]),
    ]
    
    results = []
    for step_name, script, args in steps:
        success = run_script(script, *args)
        results.append((step_name, success))
    
    print("\n" + "=" * 60)
    print("📋 MAINTENANCE SUMMARY")
    print("=" * 60)
    
    for step_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {step_name}")
    
    print("\n" + "=" * 60)
    print("💡 NEXT STEPS:")
    print("-" * 60)
    print("1. Review extracted entries above")
    print("2. Update MEMORY.md with important decisions/events")
    print("3. Check archive/ folder was created properly")
    print("4. Run cleanup-memory.py --apply if cleanup looks good")
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Full memory maintenance")
    parser.add_argument("--days", type=int, default=30, 
                       help="Days to review (default: 30)")
    args = parser.parse_args()
    
    full_maintenance(args.days)
