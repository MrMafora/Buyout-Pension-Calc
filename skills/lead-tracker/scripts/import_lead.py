#!/usr/bin/env python3
"""Bulk import leads from external sources."""

import argparse
import json
import csv
from datetime import datetime
from pathlib import Path

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
    
    # Timeline urgency (25 pts)
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

def import_csv(file_path, source='import'):
    """Import leads from CSV file."""
    ensure_data_dir()
    leads = load_leads()
    
    # Get next ID
    next_id = max([l.get('id', 0) for l in leads], default=0) + 1
    
    imported = 0
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            now = datetime.utcnow().isoformat() + 'Z'
            
            lead = {
                'id': next_id,
                'name': row.get('name', ''),
                'email': row.get('email', ''),
                'phone': row.get('phone', ''),
                'company': row.get('company', ''),
                'source': row.get('source', source),
                'status': row.get('status', 'new'),
                'score': 0,
                'notes': row.get('notes', ''),
                'created_at': row.get('created_at', now),
                'updated_at': now,
                'follow_up_date': None,
                'follow_up_note': ''
            }
            
            lead['score'] = calculate_score(lead)
            leads.append(lead)
            next_id += 1
            imported += 1
    
    save_leads(leads)
    print(f"✓ Imported {imported} lead(s) from {file_path}")
    return imported

def import_json(file_path):
    """Import leads from JSON file."""
    ensure_data_dir()
    leads = load_leads()
    
    # Get next ID
    next_id = max([l.get('id', 0) for l in leads], default=0) + 1
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Handle both array and single object
    if isinstance(data, dict):
        data = [data]
    
    imported = 0
    now = datetime.utcnow().isoformat() + 'Z'
    
    for item in data:
        lead = {
            'id': next_id,
            'name': item.get('name', ''),
            'email': item.get('email', ''),
            'phone': item.get('phone', ''),
            'company': item.get('company', ''),
            'source': item.get('source', 'import'),
            'status': item.get('status', 'new'),
            'score': 0,
            'notes': item.get('notes', ''),
            'created_at': item.get('created_at', now),
            'updated_at': now,
            'follow_up_date': item.get('follow_up_date'),
            'follow_up_note': item.get('follow_up_note', '')
        }
        
        lead['score'] = calculate_score(lead)
        leads.append(lead)
        next_id += 1
        imported += 1
    
    save_leads(leads)
    print(f"✓ Imported {imported} lead(s) from {file_path}")
    return imported

def main():
    parser = argparse.ArgumentParser(description='Import leads')
    parser.add_argument('--file', required=True, help='Input file path')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv',
                        help='Input file format')
    parser.add_argument('--source', default='import', help='Lead source label')
    
    args = parser.parse_args()
    
    if args.format == 'csv':
        import_csv(args.file, args.source)
    elif args.format == 'json':
        import_json(args.file)

if __name__ == '__main__':
    main()
