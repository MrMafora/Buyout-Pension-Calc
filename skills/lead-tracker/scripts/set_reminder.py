#!/usr/bin/env python3
"""Set or update follow-up reminder for a lead."""

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

def save_leads(leads):
    """Save leads to file."""
    with open(LEADS_FILE, 'w') as f:
        json.dump(leads, f, indent=2)

def set_reminder(lead_id, days=3, note=""):
    """Set a follow-up reminder for a lead."""
    leads = load_leads()
    
    lead = None
    for l in leads:
        if l.get('id') == lead_id:
            lead = l
            break
    
    if not lead:
        print(f"Error: Lead #{lead_id} not found.")
        return False
    
    # Calculate follow-up date
    follow_up_date = datetime.utcnow() + timedelta(days=days)
    
    lead['follow_up_date'] = follow_up_date.isoformat() + 'Z'
    lead['follow_up_note'] = note or f"Follow up with {lead['name']}"
    lead['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    
    save_leads(leads)
    
    print(f"✓ Reminder set for Lead #{lead_id}")
    print(f"  Name: {lead['name']}")
    print(f"  Follow-up date: {follow_up_date.strftime('%Y-%m-%d %H:%M')}")
    if note:
        print(f"  Note: {note}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Set follow-up reminder')
    parser.add_argument('--lead-id', type=int, required=True, help='Lead ID')
    parser.add_argument('--days', type=int, default=3, help='Days until follow-up')
    parser.add_argument('--note', default='', help='Reminder note')
    
    args = parser.parse_args()
    set_reminder(args.lead_id, args.days, args.note)

if __name__ == '__main__':
    main()
