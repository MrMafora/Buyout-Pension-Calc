#!/usr/bin/env python3
"""
Extract important tagged entries from memory files.
"""

import os
import re
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")

TAGS = ["DECISION", "EVENT", "LESSON", "PROJECT", "MEETING", "MILESTONE", "TODO"]

def get_files(days=None):
    """Get memory files, optionally filtered by days."""
    files = []
    
    if not MEMORY_DIR.exists():
        return files
    
    cutoff = None
    if days:
        cutoff = datetime.now() - timedelta(days=days)
    
    for file_path in MEMORY_DIR.glob("*.md"):
        if file_path.name == "README.md":
            continue
        try:
            date_str = file_path.stem
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if cutoff is None or file_date >= cutoff:
                files.append((file_date, file_path))
        except ValueError:
            continue
    
    return sorted(files, reverse=True)

def extract_entries(file_path, tag_filter=None):
    """Extract tagged entries from a file."""
    content = file_path.read_text()
    entries = []
    
    tags_to_search = [tag_filter] if tag_filter else TAGS
    
    for tag in tags_to_search:
        pattern = rf'\[{tag}([^\]]*)\](.*?)(?=\n\[|\Z)'
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            details = match.group(1).strip(": ")
            content_text = match.group(2).strip()
            entries.append({
                "tag": tag,
                "details": details,
                "content": content_text,
                "source": file_path.name
            })
    
    return entries

def extract_important(days=None, tag=None, output_format="text"):
    """Extract important entries from memory files."""
    files = get_files(days)
    
    all_entries = []
    for file_date, file_path in files:
        entries = extract_entries(file_path, tag)
        for entry in entries:
            entry["date"] = file_date.strftime("%Y-%m-%d")
            all_entries.append(entry)
    
    if output_format == "json":
        print(json.dumps(all_entries, indent=2))
    else:
        print(f"📋 Extracted {len(all_entries)} entries")
        print("=" * 60)
        
        for entry in all_entries:
            print(f"\n🏷️  [{entry['tag']}] {entry['details']}")
            print(f"📅 {entry['date']} | 📄 {entry['source']}")
            print(f"📝 {entry['content'][:200]}...")
            print("-" * 40)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract important tagged entries")
    parser.add_argument("--days", type=int, help="Number of days to search")
    parser.add_argument("--tag", help="Filter by specific tag")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    extract_important(args.days, args.tag, "json" if args.json else "text")
