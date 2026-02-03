#!/usr/bin/env python3
"""Generate conversion and activity reports."""

import argparse
import json
from datetime import datetime, timedelta
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
LEADS_FILE = DATA_DIR / "leads.json"

def load_leads():
    """Load all leads from file."""
    if not LEADS_FILE.exists():
        return []
    with open(LEADS_FILE, 'r') as f:
        return json.load(f)

def parse_date(date_str):
    """Parse ISO date string."""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
    except:
        return None

def generate_report(period='all'):
    """Generate conversion report."""
    leads = load_leads()
    
    if not leads:
        print("No leads in database.")
        return
    
    # Filter by period
    now = datetime.utcnow()
    if period == 'weekly':
        cutoff = now - timedelta(days=7)
    elif period == 'monthly':
        cutoff = now - timedelta(days=30)
    elif period == 'quarterly':
        cutoff = now - timedelta(days=90)
    else:
        cutoff = None
    
    if cutoff:
        leads = [l for l in leads if parse_date(l.get('created_at')) and parse_date(l.get('created_at')) >= cutoff]
    
    # Calculate metrics
    total = len(leads)
    status_counts = Counter(l.get('status', 'new') for l in leads)
    
    converted = status_counts.get('converted', 0)
    lost = status_counts.get('lost', 0)
    
    closed = converted + lost
    conversion_rate = (converted / closed * 100) if closed > 0 else 0
    
    avg_score = sum(l.get('score', 0) for l in leads) / total if total > 0 else 0
    
    # Source breakdown
    source_counts = Counter(l.get('source', 'unknown') for l in leads)
    
    # Print report
    period_label = period.capitalize() if period != 'all' else 'All Time'
    
    print(f"\n{'='*80}")
    print(f"  Lead Conversion Report - {period_label}")
    print(f"{'='*80}\n")
    
    print(f"Total Leads: {total}")
    print(f"\nStatus Breakdown:")
    for status in ['new', 'contacted', 'qualified', 'converted', 'lost']:
        count = status_counts.get(status, 0)
        pct = (count / total * 100) if total > 0 else 0
        emoji = {'new': '🔵', 'contacted': '🟡', 'qualified': '🟢', 'converted': '✅', 'lost': '❌'}.get(status, '⚪')
        print(f"  {emoji} {status.capitalize():12} {count:4} ({pct:5.1f}%)")
    
    print(f"\nConversion Metrics:")
    print(f"  Conversion Rate: {conversion_rate:.1f}%")
    print(f"  Won: {converted} | Lost: {lost}")
    
    print(f"\nAverage Lead Score: {avg_score:.1f}/100")
    
    print(f"\nLead Sources:")
    for source, count in source_counts.most_common():
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {source}: {count} ({pct:.1f}%)")
    
    # High-value leads
    high_value = [l for l in leads if l.get('score', 0) >= 70 and l.get('status') not in ['converted', 'lost']]
    if high_value:
        print(f"\nHigh-Value Leads (Score ≥70, Active):")
        for l in sorted(high_value, key=lambda x: x.get('score', 0), reverse=True)[:5]:
            print(f"  #{l['id']} {l['name']} (Score: {l['score']}, Status: {l.get('status', 'new')})")
    
    print(f"\n{'='*80}\n")

def main():
    parser = argparse.ArgumentParser(description='Generate conversion report')
    parser.add_argument('--period', choices=['all', 'weekly', 'monthly', 'quarterly'],
                        default='all', help='Report period')
    
    args = parser.parse_args()
    generate_report(args.period)

if __name__ == '__main__':
    main()
