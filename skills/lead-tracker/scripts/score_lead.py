#!/usr/bin/env python3
"""Recalculate lead score based on current data."""

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

def calculate_score(lead):
    """Calculate lead score based on criteria."""
    score = 0
    
    # Contact completeness (30 pts)
    contact_fields = [lead.get('email'), lead.get('phone'), lead.get('company')]
    contact_complete = sum(1 for f in contact_fields if f)
    score += (contact_complete / 3) * 30
    
    # Timeline urgency (25 pts)
    urgency_keywords = ['urgent', 'asap', 'immediately', 'this week', 'this month', 'soon']
    notes_lower = lead.get('notes', '').lower()
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

def score_lead(lead_id=None, all_leads=False):
    """Recalculate lead score."""
    leads = load_leads()
    
    if all_leads:
        updated = 0
        for lead in leads:
            old_score = lead.get('score', 0)
            new_score = calculate_score(lead)
            if old_score != new_score:
                lead['score'] = new_score
                lead['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                updated += 1
        
        save_leads(leads)
        print(f"✓ Scores updated for {updated} lead(s)")
        return
    
    if lead_id:
        for lead in leads:
            if lead.get('id') == lead_id:
                old_score = lead.get('score', 0)
                new_score = calculate_score(lead)
                lead['score'] = new_score
                lead['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                save_leads(leads)
                print(f"✓ Lead #{lead_id} score: {old_score} → {new_score}")
                return
        
        print(f"Error: Lead #{lead_id} not found.")

def main():
    parser = argparse.ArgumentParser(description='Calculate lead scores')
    parser.add_argument('--id', type=int, help='Lead ID to score')
    parser.add_argument('--all', action='store_true', help='Score all leads')
    
    args = parser.parse_args()
    
    if not args.id and not args.all:
        parser.error('Must specify --id or --all')
    
    score_lead(args.id, args.all)

if __name__ == '__main__':
    main()
