#!/usr/bin/env python3
"""
Manage heartbeat-driven tasks defined in HEARTBEAT.md.
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

OPENCLAW_DIR = Path.home() / ".openclaw"
CRON_MANAGER_DIR = OPENCLAW_DIR / "cron-manager"
HEARTBEAT_FILE = OPENCLAW_DIR / "HEARTBEAT.md"
TASKS_FILE = CRON_MANAGER_DIR / "heartbeat_tasks.json"

def ensure_dir():
    CRON_MANAGER_DIR.mkdir(parents=True, exist_ok=True)

def load_tasks():
    if TASKS_FILE.exists():
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return {"tasks": [], "version": "1.0"}

def save_tasks(data):
    with open(TASKS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def parse_heartbeat_md():
    """Parse HEARTBEAT.md for task definitions."""
    if not HEARTBEAT_FILE.exists():
        return []
    
    with open(HEARTBEAT_FILE, 'r') as f:
        content = f.read()
    
    tasks = []
    
    # Look for patterns like:
    # - [ ] Task description (every 30m)
    # - [ ] Check emails (every hour)
    # - [x] Completed task
    
    pattern = r'-\s*\[\s*([ x])\s*\]\s*(.+?)(?:\s*\(([^)]+)\))?$'
    
    for line in content.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            status, desc, freq = match.groups()
            tasks.append({
                "description": desc.strip(),
                "frequency": freq.strip() if freq else "",
                "completed": status == 'x',
                "source": "HEARTBEAT.md"
            })
    
    return tasks

def list_tasks(args):
    """List all heartbeat tasks."""
    ensure_dir()
    
    # Load from file
    data = load_tasks()
    
    # Optionally sync with HEARTBEAT.md
    if args.sync:
        md_tasks = parse_heartbeat_md()
        # Merge tasks
        existing_descs = {t["description"] for t in data["tasks"]}
        for task in md_tasks:
            if task["description"] not in existing_descs:
                task["id"] = f"hb-{len(data['tasks'])+1:03d}"
                task["enabled"] = True
                task["last_run"] = None
                data["tasks"].append(task)
        save_tasks(data)
        print(f"✓ Synced {len(md_tasks)} tasks from HEARTBEAT.md")
    
    tasks = data.get("tasks", [])
    
    if args.status:
        tasks = [t for t in tasks if t.get("status") == args.status]
    
    if not tasks:
        print("No heartbeat tasks found.")
        if not HEARTBEAT_FILE.exists():
            print(f"\nTip: Create {HEARTBEAT_FILE} to define heartbeat tasks")
        return
    
    print(f"\n{'ID':<10} {'Status':<10} {'Frequency':<15} {'Description':<35}")
    print("-" * 75)
    
    for t in tasks:
        tid = t.get("id", "-")[:9]
        status = "enabled" if t.get("enabled", True) else "disabled"
        freq = t.get("frequency", "-")[:14]
        desc = t.get("description", "-")[:34]
        print(f"{tid:<10} {status:<10} {freq:<15} {desc:<35}")
    
    print(f"\nTotal: {len(tasks)} task(s)")

def add_task(args):
    """Add a new heartbeat task."""
    ensure_dir()
    data = load_tasks()
    
    task = {
        "id": f"hb-{len(data['tasks'])+1:03d}",
        "description": args.description,
        "frequency": args.frequency or "",
        "enabled": True,
        "created_at": datetime.now().isoformat(),
        "last_run": None,
        "source": "manual"
    }
    
    data["tasks"].append(task)
    save_tasks(data)
    
    print(f"✓ Heartbeat task added")
    print(f"  ID: {task['id']}")
    print(f"  Description: {args.description}")
    if args.frequency:
        print(f"  Frequency: {args.frequency}")

def toggle_task(args, enabled):
    """Enable or disable a task."""
    data = load_tasks()
    
    for t in data["tasks"]:
        if t.get("id") == args.id:
            t["enabled"] = enabled
            save_tasks(data)
            status = "enabled" if enabled else "disabled"
            print(f"✓ Task '{args.id}' {status}")
            return
    
    print(f"Error: Task '{args.id}' not found.", file=sys.stderr)

def show_status(args):
    """Show heartbeat system status."""
    ensure_dir()
    data = load_tasks()
    
    total = len(data.get("tasks", []))
    enabled = len([t for t in data.get("tasks", []) if t.get("enabled", True)])
    disabled = total - enabled
    
    print("Heartbeat Task Status")
    print("=" * 30)
    print(f"Total tasks: {total}")
    print(f"Enabled: {enabled}")
    print(f"Disabled: {disabled}")
    
    if HEARTBEAT_FILE.exists():
        print(f"\nHEARTBEAT.md: Found")
        md_tasks = parse_heartbeat_md()
        print(f"Tasks defined: {len(md_tasks)}")
    else:
        print(f"\nHEARTBEAT.md: Not found")
    
    print("\nTip: Run with --sync to sync tasks from HEARTBEAT.md")

def main():
    parser = argparse.ArgumentParser(description="Manage heartbeat-driven tasks")
    subparsers = parser.add_subparsers(dest='action')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List heartbeat tasks')
    list_parser.add_argument("--sync", "-s", action="store_true", help="Sync with HEARTBEAT.md")
    list_parser.add_argument("--status", choices=["enabled", "disabled"], help="Filter by status")
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a heartbeat task')
    add_parser.add_argument("--description", "-d", required=True, help="Task description")
    add_parser.add_argument("--frequency", "-f", help="Task frequency (e.g., 'every 30m')")
    
    # Enable/Disable commands
    enable_parser = subparsers.add_parser('enable', help='Enable a task')
    enable_parser.add_argument("--id", "-i", required=True, help="Task ID")
    
    disable_parser = subparsers.add_parser('disable', help='Disable a task')
    disable_parser.add_argument("--id", "-i", required=True, help="Task ID")
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    args = parser.parse_args()
    
    if args.action == 'list' or args.action is None:
        list_tasks(args)
    elif args.action == 'add':
        add_task(args)
    elif args.action == 'enable':
        toggle_task(args, True)
    elif args.action == 'disable':
        toggle_task(args, False)
    elif args.action == 'status':
        show_status(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
