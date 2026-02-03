#!/usr/bin/env python3
"""
Archive old daily memory files to monthly folders.
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
ARCHIVE_DIR = MEMORY_DIR / "archive"

def archive_old_files(days=30, dry_run=False):
    """Archive memory files older than N days."""
    if not MEMORY_DIR.exists():
        print("❌ Memory directory not found")
        return
    
    cutoff = datetime.now() - timedelta(days=days)
    
    files_to_archive = []
    for file_path in MEMORY_DIR.glob("*.md"):
        if file_path.name == "README.md":
            continue
        try:
            date_str = file_path.stem
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date < cutoff:
                files_to_archive.append((file_date, file_path))
        except ValueError:
            continue
    
    if not files_to_archive:
        print(f"📭 No files older than {days} days to archive")
        return
    
    # Group by month
    by_month = {}
    for file_date, file_path in files_to_archive:
        month_key = file_date.strftime("%Y-%m")
        if month_key not in by_month:
            by_month[month_key] = []
        by_month[month_key].append((file_date, file_path))
    
    print(f"📦 Archiving {len(files_to_archive)} files ({len(by_month)} months)")
    
    for month, files in sorted(by_month.items()):
        month_dir = ARCHIVE_DIR / month
        
        if dry_run:
            print(f"\n📁 Would create: {month_dir}")
        else:
            month_dir.mkdir(parents=True, exist_ok=True)
            print(f"\n📁 {month_dir}")
        
        for file_date, file_path in sorted(files):
            dest = month_dir / file_path.name
            
            if dry_run:
                print(f"  → Would move: {file_path.name}")
            else:
                shutil.move(str(file_path), str(dest))
                print(f"  ✓ {file_path.name}")
    
    print(f"\n✅ {'Would archive' if dry_run else 'Archived'} {len(files_to_archive)} files")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Archive old memory files")
    parser.add_argument("--days", type=int, default=30, help="Archive files older than N days")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()
    
    archive_old_files(args.days, args.dry_run)
