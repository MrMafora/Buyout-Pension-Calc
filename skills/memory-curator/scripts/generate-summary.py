#!/usr/bin/env python3
"""
Generate a summary report from recent memory files.
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")

TAGS = {
    "DECISION": "Decisions",
    "EVENT": "Events",
    "LESSON": "Lessons",
    "PROJECT": "Projects",
    "MEETING": "Meetings",
    "MILESTONE": "Milestones",
    "TODO": "Todos"
}

def generate_summary(days=7):
    """Generate summary of recent memory activity."""
    if not MEMORY_DIR.exists():
        print("❌ Memory directory not found")
        return
    
    cutoff = datetime.now() - timedelta(days=days)
    
    files = []
    for file_path in MEMORY_DIR.glob("*.md"):
        if file_path.name == "README.md":
            continue
        try:
            date_str = file_path.stem
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date >= cutoff:
                files.append((file_date, file_path))
        except ValueError:
            continue
    
    files.sort(reverse=True)
    
    # Collect statistics
    stats = defaultdict(lambda: {"count": 0, "entries": []})
    total_entries = 0
    
    for file_date, file_path in files:
        content = file_path.read_text()
        
        for tag in TAGS.keys():
            pattern = rf'\[{tag}([^\]]*)\]'
            matches = re.findall(pattern, content, re.IGNORECASE)
            stats[tag]["count"] += len(matches)
            for match in matches:
                stats[tag]["entries"].append({
                    "date": file_date.strftime("%Y-%m-%d"),
                    "details": match.strip(": ")
                })
            total_entries += len(matches)
    
    # Generate report
    print("=" * 60)
    print(f"📊 MEMORY SUMMARY: Last {days} days")
    print("=" * 60)
    print(f"\n📁 Files reviewed: {len(files)}")
    print(f"🏷️  Tagged entries: {total_entries}")
    
    print("\n" + "-" * 60)
    print("📈 Activity by Category")
    print("-" * 60)
    
    for tag, display in TAGS.items():
        count = stats[tag]["count"]
        bar = "█" * count + "░" * (10 - min(count, 10))
        print(f"  {display:12} │{bar}│ {count}")
    
    print("\n" + "-" * 60)
    print("📅 Timeline")
    print("-" * 60)
    
    for file_date, file_path in files[:7]:  # Show last 7 days
        date_str = file_date.strftime("%a %m/%d")
        content = file_path.read_text()
        entry_count = len(re.findall(r'\[\w+', content))
        print(f"  {date_str}: {entry_count} entries")
    
    # Highlights
    print("\n" + "-" * 60)
    print("⭐ Highlights")
    print("-" * 60)
    
    if stats["MILESTONE"]["count"] > 0:
        print("\n🏆 Milestones:")
        for entry in stats["MILESTONE"]["entries"][:3]:
            print(f"  • {entry['date']}: {entry['details']}")
    
    if stats["DECISION"]["count"] > 0:
        print("\n📝 Key Decisions:")
        for entry in stats["DECISION"]["entries"][:3]:
            print(f"  • {entry['date']}: {entry['details']}")
    
    if stats["LESSON"]["count"] > 0:
        print("\n💡 Lessons Learned:")
        for entry in stats["LESSON"]["entries"][:3]:
            print(f"  • {entry['date']}: {entry['details']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate memory summary")
    parser.add_argument("--days", type=int, default=7, help="Days to summarize")
    args = parser.parse_args()
    
    generate_summary(args.days)
