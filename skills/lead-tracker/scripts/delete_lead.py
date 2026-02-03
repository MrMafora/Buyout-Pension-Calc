#!/usr/bin/env python3
"""Delete a lead from the database."""

import argparse
import json
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

def delete_lead(lead_id, force=False):
    """Delete a lead by ID."""
    leads = load_leads()
    
    lead = None
    for l in leads:
        if l.get('id') == lead_id:
            lead = l
            break
    
    if not lead:
        print(f"Error: Lead #{lead_id} not found.")
        return False
    
    if not force:
        print(f"\nYou are about to delete:")
        print(f"  ID: {lead['id']}")
        print(f"  Name: {lead['name']}")
        print(f"  Email: {lead.get('email', 'N/A')}")
        print(f"\nThis action cannot be undone.")
        confirm = input("Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print("Deletion cancelled.")
            return False
    
    leads = [l for l in leads if l.get('id') != lead_id]
    save_leads(leads)
    
    print(f"✓ Lead #{lead_id} deleted successfully!")
    return True

def main():
    parser = argparse.ArgumentParser(description='Delete a lead')
    parser.add_argument('--id', type=int, required=True, help='Lead ID to delete')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    delete_lead(args.id, args.force)

if __name__ == '__main__':
    main()
