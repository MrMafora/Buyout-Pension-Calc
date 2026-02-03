# Email Campaign Scripts

This directory contains automation scripts for managing email campaigns.

## Prerequisites

- Node.js 18+ installed
- Resend API key (set as `RESEND_API_KEY` environment variable)
- CSV parse dependency installed: `npm install`

## Quick Start

### 1. Create a Campaign

```bash
node scripts/create-campaign.js --name "welcome-new-leads" --type welcome
```

### 2. Add Leads

Single lead:
```bash
node scripts/add-to-sequence.js --campaign "welcome-new-leads" --email "john@example.com" --firstName "John"
```

From CSV file:
```bash
node scripts/add-to-sequence.js --campaign "welcome-new-leads" --file leads.csv
```

CSV format:
```csv
email,firstName,lastName
john@example.com,John,Doe
jane@example.com,Jane,Smith
```

### 3. Test Send (Dry Run)

```bash
node scripts/send-emails.js --campaign "welcome-new-leads" --dry-run
```

### 4. Send Actual Emails

```bash
node scripts/send-emails.js --campaign "welcome-new-leads"
```

## A/B Testing

Create test:
```bash
node scripts/ab-test.js --campaign "welcome-new-leads" --create --variants 2
```

View stats:
```bash
node scripts/ab-test.js --campaign "welcome-new-leads" --stats
```

Declare winner:
```bash
node scripts/ab-test.js --campaign "welcome-new-leads" --winner A
```

## Tracking

Generate report:
```bash
node scripts/track-opens.js --campaign "welcome-new-leads" --report
```

## Environment Variables

Create a `.env` file:

```
RESEND_API_KEY=your_resend_api_key_here
```

Or export directly:

```bash
export RESEND_API_KEY=re_xxxxxxxxxxxxxxxxx
```

## File Structure

```
campaigns/
├── welcome-new-leads.json    # Campaign config
└── ...

leads.json                     # Lead database
```

## Troubleshooting

**Error: Campaign not found**
- Check campaign name spelling
- Verify campaign exists in campaigns/ directory

**Error: Resend API key required**
- Set RESEND_API_KEY environment variable
- Or use --resend-key flag

**Error: Template not found**
- Check template name in campaign config
- Verify template exists in assets/templates/

## Campaign Types

- `welcome` - 3-email welcome sequence
- `drip` - 5-email educational series
- `reengagement` - 3-email win-back sequence
