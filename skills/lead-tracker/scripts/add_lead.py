#!/usr/bin/env python3
"""Add a new lead from website form submission."""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Data directory and file path
DATA_DIR = Path(__file__).parent.parent / "data"
LEADS_FILE = DATA_DIR / "leads.json"

def ensure_data_dir():
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not LEADS_FILE.exists():
        with open(LEADS_FILE, 'w') as f:
            json.dump([], f)

def load_leads():
    """Load all leads from file."""
    with open(LEADS_FILE, 'r') as f:
        return json.load(f)

def save_leads(leads):
    """Save leads to file."""
    with open(LEADS_FILE, 'w') as f:
        json.dump(leads, f, indent=2)

def calculate_score(lead_data):
    """Calculate lead score based on criteria."""
    score = 0
    
    # Contact completeness (30 pts)
    contact_fields = [lead_data.get('email'), lead_data.get('phone'), lead_data.get('company')]
    contact_complete = sum(1 for f in contact_fields if f)
    score += (contact_complete / 3) * 30
    
    # Timeline urgency (25 pts) - check notes for urgency keywords
    urgency_keywords = ['urgent', 'asap', 'immediately', 'this week', 'this month', 'soon']
    notes_lower = lead_data.get('notes', '').lower()
    if any(kw in notes_lower for kw in urgency_keywords):
        score += 25
    
    # Contract value indicators (25 pts)
    value_keywords = ['million', 'large', 'substantial', 'significant', 'major', 'big']
    if any(kw in notes_lower for kw in value_keywords):
        score += 25
    
    # Decision authority (20 pts)
    authority_keywords = ['decision', 'owner', 'ceo', 'director', 'manager', 'authorize']
    if any(kw in notes_lower for kw in authority_keywords):
        score += 20
    
    return int(score)

def add_lead(name, email, phone=None, company=None, source="website", notes=""):
    """Add a new lead to the database."""
    ensure_data_dir()
    leads = load_leads()
    
    # Generate new ID
    new_id = max([l.get('id', 0) for l in leads], default=0) + 1
    
    now = datetime.utcnow().isoformat() + 'Z'
    
    lead_data = {
        'id': new_id,
        'name': name,
        'email': email,
        'phone': phone or '',
        'company': company or '',
        'source': source,
        'status': 'new',
        'score': 0,
        'notes': notes,
        'created_at': now,
        'updated_at': now,
        'follow_up_date': None,
        'follow_up_note': ''
    }
    
    # Calculate score
    lead_data['score'] = calculate_score(lead_data)
    
    leads.append(lead_data)
    save_leads(leads)
    
    print(f"✓ Lead added successfully!")
    print(f"  ID: {new_id}")
    print(f"  Name: {name}")
    print(f"  Email: {email}")
    print(f"  Score: {lead_data['score']}/100")
    print(f"  Status: new")
    
    return new_id

def main():
    parser = argparse.ArgumentParser(description='Add a new lead')
    parser.add_argument('--name', required=True, help='Lead name')
    parser.add_argument('--email', required=True, help='Email address')
    parser.add_argument('--phone', help='Phone number')
    parser.add_argument('--company', help='Company name')
    parser.add_argument('--source', default='website', help='Lead source')
    parser.add_argument('--notes', default='', help='Additional notes')
    
    args = parser.parse_args()
    add_lead(args.name, args.email, args.phone, args.company, args.source, args.notes)

if __name__ == '__main__':
    main()
