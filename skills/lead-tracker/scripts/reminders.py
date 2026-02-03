#!/usr/bin/env python3
"""List follow-up reminders."""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
LEADS_FILE = DATA_DIR / "leads.json"

def load_leads():
    """Load all leads from file."""
    if not LEADS_FILE.exists():
        return []
    with open(LEADS_FILE, 'r') as f:
        return json.load(f)

def list_reminders(due_only=False, upcoming_days=7):
    """List follow-up reminders."""
    leads = load_leads()
    now = datetime.utcnow()
    
    reminders = []
    for lead in leads:
        follow_up = lead.get('follow_up_date')
        if not follow_up:
            continue
        
        try:
            follow_up_dt = datetime.fromisoformat(follow_up.replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            continue
        
        days_until = (follow_up_dt - now).days
        
        if due_only and days_until > 0:
            continue
        
        if days_until > upcoming_days:
            continue
        
        reminders.append({
            'lead': lead,
            'follow_up_date': follow_up_dt,
            'days_until': days_until
        })
    
    # Sort by due date
    reminders.sort(key=lambda x: x['follow_up_date'])
    
    if not reminders:
        if due_only:
            print("No overdue reminders!")
        else:
            print(f"No reminders in the next {upcoming_days} days.")
        return
    
    print(f"\n{'='*80}")
    print(f"Follow-up Reminders")
    print(f"{'='*80}\n")
    
    for r in reminders:
        lead = r['lead']
        days_until = r['days_until']
        
        if days_until < 0:
            status = f"OVERDUE ({abs(days_until)} days)"
            emoji = "🔴"
        elif days_until == 0:
            status = "TODAY"
            emoji = "🟠"
        else:
            status = f"in {days_until} days"
            emoji = "🟡"
        
        print(f"{emoji} Lead #{lead['id']} | {lead['name']}")
        print(f"   Due: {status}")
        print(f"   Date: {r['follow_up_date'].strftime('%Y-%m-%d')}")
        print(f"   Note: {lead.get('follow_up_note', 'No note')}")
        print(f"   Status: {lead.get('status', 'new')}")
        print()

def main():
    parser = argparse.ArgumentParser(description='List follow-up reminders')
    parser.add_argument('--due', action='store_true', help='Show only overdue reminders')
    parser.add_argument('--upcoming', type=int, default=7, help='Days to look ahead')
    
    args = parser.parse_args()
    list_reminders(args.due, args.upcoming)

if __name__ == '__main__':
    main()
