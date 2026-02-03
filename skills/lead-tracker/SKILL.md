---
name: lead-tracker
description: Lead management and tracking system for FedBuyOut. Use when tracking website form submissions, managing lead status, scoring leads, setting follow-up reminders, generating conversion reports, or exporting leads for CRM import. Handles lead lifecycle from initial contact through conversion or closure.
---

# Lead Tracker

Lead management system for FedBuyOut business operations.

## Overview

This skill manages leads from website form submissions through the entire sales pipeline. It provides tools for:

- Logging new leads from contact forms
- Tracking lead status progression
- Scoring leads based on qualification criteria
- Managing follow-up schedules
- Reporting conversion metrics
- Exporting data for external CRM systems

## Quick Start

### Log a New Lead

```bash
./scripts/add_lead.py --name "John Smith" --email "john@example.com" --phone "555-123-4567" --source "website" --notes "Interested in government contract buyout"
```

### View All Leads

```bash
./scripts/list_leads.py
```

### Update Lead Status

```bash
./scripts/update_lead.py --id 1 --status qualified
```

### Generate Conversion Report

```bash
./scripts/report.py --period monthly
```

## Lead Status Workflow

Leads progress through these states:

1. **new** - Initial submission, not yet contacted
2. **contacted** - First contact made, awaiting response
3. **qualified** - Interest confirmed, evaluating fit
4. **converted** - Deal closed, contract signed
5. **lost** - Opportunity closed without conversion

## Lead Scoring

Leads are automatically scored (0-100) based on:

- **Contact completeness** (30 pts) - Full contact info provided
- **Timeline urgency** (25 pts) - Immediate need expressed
- **Contract value indicators** (25 pts) - Size/value mentioned
- **Decision authority** (20 pts) - Authority to proceed indicated

For detailed scoring criteria, see [references/scoring.md](references/scoring.md).

## Follow-Up Management

Set follow-up reminders:

```bash
./scripts/set_reminder.py --lead-id 1 --days 3 --note "Send proposal"
```

Check pending follow-ups:

```bash
./scripts/reminders.py --due
```

## Data Storage

Leads are stored in JSON format at `data/leads.json` with the following structure:

```json
{
  "id": 1,
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "555-123-4567",
  "company": "Acme Corp",
  "source": "website",
  "status": "new",
  "score": 75,
  "notes": "Interested in contract buyout",
  "created_at": "2026-02-03T10:00:00Z",
  "updated_at": "2026-02-03T10:00:00Z",
  "follow_up_date": "2026-02-06T10:00:00Z"
}
```

## Export Options

Export leads for CRM import:

```bash
# CSV format for Salesforce/HubSpot
./scripts/export.py --format csv --output leads.csv

# JSON format for API import
./scripts/export.py --format json --output leads.json
```

## Available Scripts

| Script | Purpose |
|--------|---------|
| `add_lead.py` | Add new lead from form submission |
| `list_leads.py` | Display leads with filtering options |
| `update_lead.py` | Update lead status and details |
| `delete_lead.py` | Remove lead record |
| `score_lead.py` | Recalculate lead score |
| `set_reminder.py` | Schedule follow-up reminder |
| `reminders.py` | List due and upcoming follow-ups |
| `report.py` | Generate conversion and activity reports |
| `export.py` | Export leads in various formats |
| `import_lead.py` | Bulk import from external source |

## Reference Materials

- **[references/scoring.md](references/scoring.md)** - Lead scoring criteria and methodology
- **[references/followup-templates.md](references/followup-templates.md)** - Email/SMS templates for follow-up communications
- **[references/status-definitions.md](references/status-definitions.md)** - Detailed status definitions and transition guidelines
