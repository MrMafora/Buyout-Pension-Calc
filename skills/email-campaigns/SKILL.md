---
name: email-campaigns
description: Manage automated email sequences for FedBuyOut leads. Use when creating, editing, or managing email campaigns, drip sequences, welcome series, re-engagement campaigns, or email templates for the FedBuyOut business. Includes lead nurturing workflows, educational content sequences, A/B testing guidance, and deliverability best practices.
---

# Email Campaigns for FedBuyOut

This skill manages automated email sequences for lead nurturing, education, and re-engagement for the FedBuyOut business (federal pension buyout services).

## Key Features

- **Welcome Email Sequence** - Onboard new leads
- **Educational Drip Campaign** - 5-email series about buyouts
- **Re-engagement Campaigns** - Win back cold leads
- **Email Templates** - HTML and text formats
- **Subject Line Formulas** - Tested formulas for opens
- **A/B Testing Guidance** - Optimize campaigns
- **Deliverability Best Practices** - Stay out of spam

## Email Configuration

- **From Email**: `support@fedbuyout.com`
- **Transactional API**: Resend API
- **Contact Email**: fedbuyout@gmail.com (Google services)
- **Operations Email**: clark@fedbuyout.com

## Quick Start

### 1. Create a New Campaign

```bash
node scripts/create-campaign.js --name "campaign-name" --type welcome|drip|reengagement
```

### 2. Add Leads to a Sequence

```bash
node scripts/add-to-sequence.js --campaign "campaign-name" --email "lead@example.com"
```

### 3. Send Campaign Emails

```bash
node scripts/send-emails.js --campaign "campaign-name" --dry-run
```

## Campaign Types

### Welcome Sequence (welcome)

3-email sequence for new leads:
1. Welcome & What to Expect (immediate)
2. Value Proposition (Day 2)
3. Social Proof & CTA (Day 5)

See [references/sequences.md](references/sequences.md) for full sequence details.

### Educational Drip Campaign (drip)

5-email educational series about pension buyouts:
1. Understanding Your Pension Options
2. The True Cost of Waiting
3. Buyout vs. Monthly Payments
4. Tax Implications Explained
5. Next Steps & Consultation Offer

See [references/educational-drip.md](references/educational-drip.md) for email content.

### Re-engagement Campaign (reengagement)

3-email sequence for cold leads:
1. We Miss You (gentle)
2. What's Changed? (value-focused)
3. Final Chance (last call)

See [references/reengagement.md](references/reengagement.md) for sequence details.

## Email Templates

### HTML Templates

Located in `assets/templates/`:
- `welcome.html` - Welcome email template
- `educational.html` - Educational content template
- `reengagement.html` - Re-engagement template
- `newsletter.html` - Newsletter format

### Text Templates

Located in `assets/templates/text/`:
- `welcome.txt`
- `educational.txt`
- `reengagement.txt`
- `newsletter.txt`

### Using Templates

Load templates and customize variables:

```javascript
const template = require('./scripts/load-template.js');
const html = template.load('welcome', {
  firstName: 'John',
  companyName: 'FedBuyOut',
  unsubscribeUrl: '...'
});
```

## Subject Line Formulas

See [references/subject-lines.md](references/subject-lines.md) for tested formulas:

- Curiosity gaps
- Personalization patterns
- Urgency/Scarcity formulas
- Question-based subjects
- How-to promises

## A/B Testing

See [references/ab-testing.md](references/ab-testing.md) for guidance on:

- What to test (subject lines, CTAs, send times)
- Sample size requirements
- Statistical significance
- Test duration recommendations

## Deliverability Best Practices

See [references/deliverability.md](references/deliverability.md) for:

- Domain authentication (SPF, DKIM, DMARC)
- List hygiene practices
- Engagement monitoring
- Spam trigger words to avoid
- Inbox placement tips

## Scripts Reference

### create-campaign.js
Creates a new campaign with configuration file.

```bash
node scripts/create-campaign.js --name "summer-promo" --type drip
```

### add-to-sequence.js
Adds leads to an email sequence.

```bash
node scripts/add-to-sequence.js --campaign "summer-promo" --file leads.csv
node scripts/add-to-sequence.js --campaign "summer-promo" --email "test@example.com"
```

### send-emails.js
Sends pending emails in a campaign.

```bash
node scripts/send-emails.js --campaign "summer-promo" --dry-run
node scripts/send-emails.js --campaign "summer-promo"
```

### load-template.js
Loads and renders email templates.

```javascript
const template = require('./scripts/load-template.js');
const html = template.load('welcome', variables);
```

### track-opens.js
Tracks email opens (pixel-based).

```bash
node scripts/track-opens.js --campaign "summer-promo" --report
```

### ab-test.js
Manages A/B test campaigns.

```bash
node scripts/ab-test.js --campaign "summer-promo" --variants 2
```

## Campaign Configuration

Each campaign has a JSON config file:

```json
{
  "name": "welcome-sequence",
  "type": "welcome",
  "status": "active",
  "emails": [
    {
      "id": 1,
      "subject": "Welcome to FedBuyOut",
      "template": "welcome",
      "delayDays": 0,
      "sendTime": "09:00"
    }
  ],
  "settings": {
    "fromName": "FedBuyOut Team",
    "replyTo": "support@fedbuyout.com",
    "trackOpens": true,
    "trackClicks": true
  }
}
```

## Lead Management

Leads are stored with campaign state:

```json
{
  "email": "lead@example.com",
  "firstName": "John",
  "joinedAt": "2024-01-15T09:00:00Z",
  "campaigns": {
    "welcome-sequence": {
      "status": "active",
      "currentStep": 1,
      "lastEmailSent": "2024-01-15T09:05:00Z",
      "emailsSent": [1],
      "emailsOpened": [1],
      "linksClicked": []
    }
  }
}
```

## Best Practices

1. **Always test** campaigns with `--dry-run` first
2. **Segment audiences** based on lead source and interest level
3. **Resend unopened** emails after 48 hours with new subject
4. **Monitor metrics** - aim for >20% open rate, >2% click rate
5. **Clean lists** - remove hard bounces and non-engagers after 90 days
6. **Personalize** - use first name, reference their situation
7. **Mobile-first** - 60%+ of emails are opened on mobile

## Metrics to Track

- **Open Rate** - Target: 25%+
- **Click Rate** - Target: 3%+
- **Unsubscribe Rate** - Keep under 0.5%
- **Bounce Rate** - Keep under 2%
- **Conversion Rate** - Consultation bookings
- **Revenue per Email** - Track campaign ROI

## Legal Compliance

- Include unsubscribe link in every email
- Honor unsubscribe requests within 24 hours
- Include physical mailing address
- Comply with CAN-SPAM Act
- Maintain records of consent

## Resources

- [references/sequences.md](references/sequences.md) - Email sequence definitions
- [references/educational-drip.md](references/educational-drip.md) - 5-email drip content
- [references/reengagement.md](references/reengagement.md) - Re-engagement sequences
- [references/subject-lines.md](references/subject-lines.md) - Subject line formulas
- [references/ab-testing.md](references/ab-testing.md) - A/B testing guide
- [references/deliverability.md](references/deliverability.md) - Deliverability guide
