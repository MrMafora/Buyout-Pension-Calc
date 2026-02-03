# Email Campaigns Examples

This directory contains example files to help you get started.

## Files

### leads-sample.csv
Sample CSV file showing the expected format for importing leads.

**Columns:**
- `email` (required) - Lead's email address
- `firstName` (optional) - Lead's first name
- `lastName` (optional) - Lead's last name
- `source` (optional) - Lead source for tracking

**Usage:**
```bash
node scripts/add-to-sequence.js --campaign "my-campaign" --file examples/leads-sample.csv
```

### welcome-example.json
Example campaign configuration for a welcome sequence.

**Structure:**
- Campaign metadata (name, type, status)
- Email sequence configuration
- Send settings (from, reply-to, tracking)
- Statistics tracking

**Usage:**
```bash
# Copy as template
cp examples/welcome-example.json campaigns/my-campaign.json

# Edit with your settings
nano campaigns/my-campaign.json
```

## Creating Your First Campaign

1. Create a campaign:
   ```bash
   node scripts/create-campaign.js --name "my-first-campaign" --type welcome
   ```

2. Add some test leads:
   ```bash
   node scripts/add-to-sequence.js --campaign "my-first-campaign" --email "test@example.com" --firstName "Test"
   ```

3. Test send (dry run):
   ```bash
   node scripts/send-emails.js --campaign "my-first-campaign" --dry-run
   ```

4. Review output, then send for real:
   ```bash
   node scripts/send-emails.js --campaign "my-first-campaign"
   ```

## Lead Database Structure

The `leads.json` file stores all lead information:

```json
{
  "lead@example.com": {
    "email": "lead@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "joinedAt": "2024-01-15T09:00:00Z",
    "source": "website",
    "status": "active",
    "campaigns": {
      "my-campaign": {
        "status": "active",
        "currentStep": 1,
        "joinedAt": "2024-01-15T09:00:00Z",
        "lastEmailSent": "2024-01-15T09:05:00Z",
        "emailsSent": [1],
        "emailsOpened": [],
        "linksClicked": [],
        "unsubscribed": false
      }
    }
  }
}
```

## Campaign Workflow

```
Create Campaign → Add Leads → Test (Dry Run) → Send → Track → Report
```

## Best Practices

1. Always test with `--dry-run` first
2. Start with a small test list
3. Monitor metrics after each send
4. Use A/B testing for optimization
5. Keep list clean (remove bounces)
6. Honor unsubscribe requests immediately
