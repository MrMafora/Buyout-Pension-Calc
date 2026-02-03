#!/usr/bin/env python3
"""Update lead status and details."""

import argparse
import json
from datetime import datetime
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

def update_lead(lead_id, status=None, notes=None, phone=None, company=None):
    """Update a lead's information."""
    leads = load_leads()
    
    lead = None
    for l in leads:
        if l.get('id') == lead_id:
            lead = l
            break
    
    if not lead:
        print(f"Error: Lead #{lead_id} not found.")
        return False
    
    # Update fields
    if status:
        valid_statuses = ['new', 'contacted', 'qualified', 'converted', 'lost']
        if status not in valid_statuses:
            print(f"Error: Invalid status. Use: {', '.join(valid_statuses)}")
            return False
        lead['status'] = status
        print(f"Status updated to: {status}")
    
    if notes:
        # Append to existing notes
        if lead.get('notes'):
            lead['notes'] += f"\n[{datetime.utcnow().strftime('%Y-%m-%d')}] {notes}"
        else:
            lead['notes'] = notes
        print(f"Notes updated")
    
    if phone:
        lead['phone'] = phone
        print(f"Phone updated: {phone}")
    
    if company:
        lead['company'] = company
        print(f"Company updated: {company}")
    
    lead['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    
    save_leads(leads)
    print(f"\n✓ Lead #{lead_id} updated successfully!")
    return True

def main():
    parser = argparse.ArgumentParser(description='Update a lead')
    parser.add_argument('--id', type=int, required=True, help='Lead ID')
    parser.add_argument('--status', choices=['new', 'contacted', 'qualified', 'converted', 'lost'],
                        help='New status')
    parser.add_argument('--notes', help='Add note (appends to existing)')
    parser.add_argument('--phone', help='Update phone number')
    parser.add_argument('--company', help='Update company name')
    
    args = parser.parse_args()
    update_lead(args.id, args.status, args.notes, args.phone, args.company)

if __name__ == '__main__':
    main()
