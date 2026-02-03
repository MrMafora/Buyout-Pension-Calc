#!/usr/bin/env python3
"""
Review recent daily memory files and extract important entries.
Suggests updates for MEMORY.md based on tagged content.
"""

import os
import re
import sys
import glob
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
MEMORY_FILE = Path("/root/.openclaw/workspace/MEMORY.md")

TAGS = {
    "DECISION": "📋 Decision",
    "EVENT": "📅 Event",
    "LESSON": "💡 Lesson",
    "PROJECT": "📁 Project",
    "MEETING": "🤝 Meeting",
    "MILESTONE": "🏆 Milestone",
    "TODO": "✅ Todo"
}

def get_recent_files(days=7):
    """Get memory files from the last N days."""
    files = []
    cutoff = datetime.now() - timedelta(days=days)
    
    if not MEMORY_DIR.exists():
        return files
    
    for file_path in MEMORY_DIR.glob("*.md"):
        if file_path.name == "README.md":
            continue
        try:
            # Parse date from filename (YYYY-MM-DD.md)
            date_str = file_path.stem
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date >= cutoff:
                files.append((file_date, file_path))
        except ValueError:
            continue
    
    return sorted(files, reverse=True)

def extract_tagged_entries(content):
    """Extract entries with standard tags."""
    entries = []
    
    for tag, display_name in TAGS.items():
        # Match [TAG: details] or [TAG] patterns
        pattern = rf'\[{tag}([^\]]*)\](.*?)(?=\n\[|\Z)'
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            details = match.group(1).strip(": ")
            content_text = match.group(2).strip()
            entries.append({
                "tag": tag,
                "display": display_name,
                "details": details,
                "content": content_text
            })
    
    return entries

def review_recent(days=7):
    """Review recent memory files."""
    files = get_recent_files(days)
    
    if not files:
        print(f"No memory files found in the last {days} days.")
        return
    
    print(f"📚 Memory Review: Last {days} days")
    print("=" * 50)
    
    all_entries = []
    
    for file_date, file_path in files:
        print(f"\n📄 {file_path.name}")
        
        try:
            content = file_path.read_text()
            entries = extract_tagged_entries(content)
            
            if entries:
                for entry in entries:
                    print(f"  {entry['display']}: {entry['details'] or entry['content'][:60]}...")
                    all_entries.append((file_date, entry))
            else:
                print("  (no tagged entries)")
        except Exception as e:
            print(f"  ⚠️ Error reading file: {e}")
    
    print("\n" + "=" * 50)
    print(f"\n📊 Summary: {len(files)} files, {len(all_entries)} tagged entries")
    
    # Group by tag type
    by_tag = {}
    for _, entry in all_entries:
        tag = entry["tag"]
        if tag not in by_tag:
            by_tag[tag] = []
        by_tag[tag].append(entry)
    
    print("\n🏷️  By Category:")
    for tag, entries in sorted(by_tag.items()):
        print(f"  {TAGS[tag]}: {len(entries)} entries")
    
    # Suggest MEMORY.md updates
    print("\n💡 Suggested MEMORY.md Updates:")
    print("-" * 40)
    
    if "DECISION" in by_tag:
        print("\n📝 Add to 'Key Decisions' section:")
        for entry in by_tag["DECISION"][:3]:
            print(f"  - {entry['details']}: {entry['content'][:80]}...")
    
    if "LESSON" in by_tag:
        print("\n💡 Add to 'Lessons Learned' section:")
        for entry in by_tag["LESSON"][:3]:
            print(f"  - {entry['content'][:80]}...")
    
    if "EVENT" in by_tag:
        print("\n📅 Add to 'Important Events' section:")
        for entry in by_tag["EVENT"][:3]:
            print(f"  - {entry['details']}: {entry['content'][:80]}...")
    
    if "PROJECT" in by_tag:
        print("\n📁 Update 'Active Projects' section:")
        for entry in by_tag["PROJECT"][:3]:
            print(f"  - {entry['details']}: {entry['content'][:80]}...")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Review recent memory files")
    parser.add_argument("--days", type=int, default=7, help="Number of days to review")
    args = parser.parse_args()
    
    review_recent(args.days)
