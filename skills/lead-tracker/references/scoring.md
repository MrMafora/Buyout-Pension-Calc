# Lead Scoring Guide

Lead scoring methodology for FedBuyOut lead qualification.

## Scoring Criteria

Leads are scored 0-100 based on four key dimensions:

### 1. Contact Completeness (30 points)

Points awarded based on information provided:

| Fields Provided | Points |
|-----------------|--------|
| Name only | 10 |
| Name + Email | 20 |
| Name + Email + Phone | 30 |
| Name + Email + Company | 30 |
| All fields | 30 |

**Rationale:** Complete contact information indicates higher intent and makes follow-up easier.

### 2. Timeline Urgency (25 points)

Points awarded for urgency indicators in notes:

**25 points** if any urgency keyword found:
- "urgent", "asap", "immediately"
- "this week", "this month"
- "soon", "quickly", "fast"
- "deadline", "time-sensitive"

**0 points** if no urgency indicated

**Rationale:** Urgent timelines suggest qualified prospects ready to engage.

### 3. Contract Value Indicators (25 points)

Points awarded for value indicators in notes:

**25 points** if any value keyword found:
- "million", "million dollar"
- "large contract", "substantial"
- "significant", "major"
- "high value", "big project"

**0 points** if no value indicators

**Rationale:** Value indicators suggest prospects with viable contracts for buyout.

### 4. Decision Authority (20 points)

Points awarded for authority indicators in notes:

**20 points** if any authority keyword found:
- "decision maker", "decision authority"
- "owner", "ceo", "director"
- "manager" (with decision context)
- "authorize", "approval"
- "I control", "I manage"

**0 points** if no authority indicators

**Rationale:** Speaking with decision-makers shortens sales cycle and improves close rates.

## Score Interpretation

| Score Range | Classification | Action |
|-------------|----------------|--------|
| 80-100 | Hot Lead | Immediate follow-up within 24 hours |
| 60-79 | Warm Lead | Follow-up within 48 hours |
| 40-59 | Qualified | Standard follow-up within 1 week |
| 20-39 | Nurture | Add to email nurture sequence |
| 0-19 | Low Priority | Minimal effort, periodic check-in |

## Recalculating Scores

Scores should be recalculated when:
- New information is added to notes
- Contact details are updated
- During periodic lead reviews

Use the `score_lead.py` script:

```bash
# Recalculate single lead
./scripts/score_lead.py --id 1

# Recalculate all leads
./scripts/score_lead.py --all
```

## Score Override

In some cases, manual scoring adjustments may be necessary. Update the `score` field directly in the JSON data file.

## Examples

### Example 1: High-Quality Lead (90 points)
- Name: John Smith
- Email: john@acmecorp.com
- Phone: 555-123-4567
- Company: Acme Corp
- Notes: "CEO looking to sell $5M contract ASAP"

Score: 30 (contact) + 25 (urgent) + 25 (value) + 20 (authority) = 100 (capped at 100)

### Example 2: Medium Lead (50 points)
- Name: Jane Doe
- Email: jane@example.com
- Phone: (none)
- Company: Example Inc
- Notes: "Interested in learning more"

Score: 20 (contact) + 0 + 0 + 0 = 20 → Re-evaluated with engagement = 50

### Example 3: Low Lead (20 points)
- Name: Bob Johnson
- Email: bob@mail.com
- Phone: (none)
- Company: (none)
- Notes: "Just browsing"

Score: 20 (contact) + 0 + 0 + 0 = 20
