#!/usr/bin/env python3
"""Export leads to various formats for CRM import."""

import argparse
import json
import csv
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

def export_csv(leads, output_path):
    """Export leads to CSV format."""
    if not leads:
        print("No leads to export.")
        return
    
    fieldnames = ['id', 'name', 'email', 'phone', 'company', 'source', 
                  'status', 'score', 'notes', 'created_at', 'updated_at']
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for lead in leads:
            row = {k: lead.get(k, '') for k in fieldnames}
            writer.writerow(row)
    
    print(f"✓ Exported {len(leads)} leads to {output_path}")

def export_json(leads, output_path):
    """Export leads to JSON format."""
    with open(output_path, 'w') as f:
        json.dump(leads, f, indent=2)
    
    print(f"✓ Exported {len(leads)} leads to {output_path}")

def export_salesforce(leads, output_path):
    """Export in Salesforce-compatible format."""
    field_mapping = {
        'FirstName': lambda l: l['name'].split()[0] if l.get('name') else '',
        'LastName': lambda l: ' '.join(l['name'].split()[1:]) if l.get('name') and len(l['name'].split()) > 1 else l.get('name', ''),
        'Email': lambda l: l.get('email', ''),
        'Phone': lambda l: l.get('phone', ''),
        'Company': lambda l: l.get('company', ''),
        'LeadSource': lambda l: l.get('source', ''),
        'Status': lambda l: l.get('status', '').capitalize(),
        'Description': lambda l: l.get('notes', ''),
        'CreatedDate': lambda l: l.get('created_at', '')
    }
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=field_mapping.keys())
        writer.writeheader()
        for lead in leads:
            row = {k: v(lead) for k, v in field_mapping.items()}
            writer.writerow(row)
    
    print(f"✓ Exported {len(leads)} leads to {output_path} (Salesforce format)")

def main():
    parser = argparse.ArgumentParser(description='Export leads')
    parser.add_argument('--format', choices=['csv', 'json', 'salesforce'],
                        default='csv', help='Export format')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--status', choices=['new', 'contacted', 'qualified', 'converted', 'lost'],
                        help='Filter by status')
    
    args = parser.parse_args()
    
    leads = load_leads()
    
    if args.status:
        leads = [l for l in leads if l.get('status') == args.status]
    
    if args.format == 'csv':
        export_csv(leads, args.output)
    elif args.format == 'json':
        export_json(leads, args.output)
    elif args.format == 'salesforce':
        export_salesforce(leads, args.output)

if __name__ == '__main__':
    main()
