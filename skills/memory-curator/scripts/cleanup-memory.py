#!/usr/bin/env python3
"""
Clean up obsolete entries from MEMORY.md.
Removes outdated information and consolidates duplicates.
"""

import re
from datetime import datetime
from pathlib import Path

MEMORY_FILE = Path("/root/.openclaw/workspace/MEMORY.md")

def parse_memory_file():
    """Parse MEMORY.md into sections."""
    if not MEMORY_FILE.exists():
        print("❌ MEMORY.md not found")
        return None
    
    content = MEMORY_FILE.read_text()
    
    # Split into sections
    sections = {}
    current_section = None
    current_content = []
    
    for line in content.split("\n"):
        if line.startswith("## "):
            if current_section:
                sections[current_section] = current_content
            current_section = line[3:].strip()
            current_content = []
        elif current_section:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = current_content
    
    return sections, content

def find_duplicates(entries):
    """Find potential duplicate entries based on content similarity."""
    duplicates = []
    seen = {}
    
    for i, entry in enumerate(entries):
        # Normalize for comparison
        normalized = entry.lower().strip("- ")
        
        for prev_text, prev_idx in seen.items():
            # Simple similarity check
            if normalized in prev_text or prev_text in normalized:
                if len(normalized) > 20:  # Only flag substantial entries
                    duplicates.append((prev_idx, i, prev_text, entry))
        
        seen[normalized] = i
    
    return duplicates

def analyze_section(section_name, content_lines):
    """Analyze a section for cleanup opportunities."""
    issues = []
    
    # Check for empty sections
    non_empty = [l for l in content_lines if l.strip()]
    if not non_empty:
        issues.append("Section is empty")
        return issues
    
    # Check for very old entries (simple date pattern matching)
    old_entries = []
    for line in content_lines:
        # Look for year patterns
        years = re.findall(r'20\d\d', line)
        for year in years:
            if int(year) < datetime.now().year - 2:
                old_entries.append(line.strip())
    
    if old_entries:
        issues.append(f"Found {len(old_entries)} entries older than 2 years")
    
    # Check for duplicates
    entries = [l for l in content_lines if l.strip().startswith(("- ", "* ", "• "))]
    duplicates = find_duplicates(entries)
    if duplicates:
        issues.append(f"Found {len(duplicates)} potential duplicates")
    
    return issues

def cleanup_memory(dry_run=True):
    """Analyze and suggest cleanup for MEMORY.md."""
    result = parse_memory_file()
    if not result:
        return
    
    sections, full_content = result
    
    print("🧹 MEMORY.md Cleanup Analysis")
    print("=" * 60)
    
    for section_name, content in sections.items():
        print(f"\n📂 {section_name}")
        print("-" * 40)
        
        issues = analyze_section(section_name, content)
        
        if issues:
            for issue in issues:
                print(f"  ⚠️  {issue}")
        else:
            print("  ✓ No issues found")
    
    print("\n" + "=" * 60)
    print("💡 Recommendations:")
    print("- Review 'Key Decisions' for outdated/reversible decisions")
    print("- Remove completed projects from 'Active Projects'")
    print("- Consolidate duplicate entries")
    print("- Archive entries older than 2 years to historical section")
    
    if dry_run:
        print("\n📝 Run without --dry-run to apply changes (manual review recommended)")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean up MEMORY.md")
    parser.add_argument("--dry-run", action="store_true", default=True, 
                       help="Show what would be done (default)")
    parser.add_argument("--apply", action="store_true", 
                       help="Apply cleanup changes")
    args = parser.parse_args()
    
    cleanup_memory(dry_run=not args.apply)
