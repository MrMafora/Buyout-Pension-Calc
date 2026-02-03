#!/usr/bin/env python3
"""List and filter leads."""

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

def format_lead(lead):
    """Format a lead for display."""
    status_emoji = {
        'new': '🔵',
        'contacted': '🟡',
        'qualified': '🟢',
        'converted': '✅',
        'lost': '❌'
    }.get(lead.get('status', 'new'), '⚪')
    
    return (
        f"{status_emoji} #{lead['id']} | {lead['name']} | {lead.get('email', 'N/A')} | "
        f"Score: {lead.get('score', 0)}/100 | Status: {lead.get('status', 'new')}"
    )

def list_leads(status=None, min_score=None, source=None, limit=None):
    """List leads with optional filtering."""
    leads = load_leads()
    
    # Apply filters
    if status:
        leads = [l for l in leads if l.get('status') == status]
    if min_score:
        leads = [l for l in leads if l.get('score', 0) >= min_score]
    if source:
        leads = [l for l in leads if l.get('source') == source]
    
    # Sort by created date (newest first)
    leads = sorted(leads, key=lambda x: x.get('created_at', ''), reverse=True)
    
    if limit:
        leads = leads[:limit]
    
    if not leads:
        print("No leads found matching criteria.")
        return
    
    print(f"\n{'='*80}")
    print(f"Found {len(leads)} lead(s)")
    print(f"{'='*80}\n")
    
    for lead in leads:
        print(format_lead(lead))
    
    print(f"\n{'='*80}")
    
    # Print summary
    total = len(load_leads())
    print(f"Total leads in system: {total}")
    print(f"Status: new 🔵 | contacted 🟡 | qualified 🟢 | converted ✅ | lost ❌")

def main():
    parser = argparse.ArgumentParser(description='List leads')
    parser.add_argument('--status', choices=['new', 'contacted', 'qualified', 'converted', 'lost'],
                        help='Filter by status')
    parser.add_argument('--min-score', type=int, help='Minimum lead score')
    parser.add_argument('--source', help='Filter by source')
    parser.add_argument('--limit', type=int, help='Limit results')
    
    args = parser.parse_args()
    list_leads(args.status, args.min_score, args.source, args.limit)

if __name__ == '__main__':
    main()
