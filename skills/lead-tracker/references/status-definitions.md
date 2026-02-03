# Lead Status Definitions

Detailed definitions and guidelines for lead status management.

## Status Definitions

### 🔵 New

**Definition:** Lead has been received from website form or other source but has not yet been contacted.

**Entry Criteria:**
- Form submission received
- Contact information captured
- Initial score calculated

**Exit Criteria:**
- First contact attempt made (phone, email, or SMS)

**Actions Required:**
1. Review lead details within 24 hours
2. Calculate/verify lead score
3. Send initial email response
4. Schedule follow-up reminders
5. Log first contact attempt

**SLA:** Initial contact within 24 business hours

---

### 🟡 Contacted

**Definition:** First contact has been made but lead has not yet been qualified or disqualified.

**Entry Criteria:**
- Initial email/call/SMS sent
- Waiting for response
- Interest level unknown

**Exit Criteria:**
- Response received and evaluated, OR
- 3 follow-up attempts made without response (move to Lost)

**Actions Required:**
1. Track response time
2. Send follow-up communications per schedule
3. Update notes with any interactions
4. Attempt phone contact if no email response
5. Adjust score based on engagement

**SLA:** Follow up every 3-5 days for up to 3 attempts

---

### 🟢 Qualified

**Definition:** Lead has expressed genuine interest, has decision-making authority, and meets basic qualification criteria.

**Entry Criteria:**
- Confirmed interest in selling
- Has valid government contract
- Is decision-maker or has access to one
- Timeline is realistic (not 2+ years out)
- Contract value meets minimum threshold

**Exit Criteria:**
- Deal closed (move to Converted), OR
- Decision made not to sell (move to Lost), OR
- Unresponsive after extended follow-up

**Actions Required:**
1. Conduct discovery call
2. Gather contract documentation
3. Prepare valuation/proposal
4. Present offer
5. Negotiate terms
6. Schedule closing

**SLA:** Proposal within 5 business days of qualification

---

### ✅ Converted

**Definition:** Deal closed successfully - contract purchased, payment received.

**Entry Criteria:**
- Purchase agreement signed
- Funds transferred
- Contract ownership transferred
- Deal fully executed

**Actions Required:**
1. Complete deal paperwork
2. Process payment
3. Transfer contract ownership
4. Send thank you / testimonial request
5. Archive deal file
6. Update conversion metrics

**Outcome:** Revenue recorded, lead archived

---

### ❌ Lost

**Definition:** Lead is no longer viable - either disqualified or unresponsive.

**Entry Criteria (Disqualified):**
- Not interested in selling
- No valid government contract
- Timeline doesn't align
- Unrealistic price expectations
- Not decision-maker with no path to one

**Entry Criteria (Unresponsive):**
- No response after 4+ follow-up attempts
- Multiple no-shows for scheduled calls
- Email bounces, phone disconnected

**Actions Required:**
1. Document reason for loss
2. Set "revisit" reminder if appropriate (6-12 months)
3. Move to nurture campaign if might be future opportunity
4. Close out follow-up reminders

**Reactivation:** Lost leads can be moved back to "New" if they re-engage

## Status Transitions

```
                    ┌─────────────┐
                    │     NEW     │
                    └──────┬──────┘
                           │ contact
                           ▼
                    ┌─────────────┐
                    │  CONTACTED  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌─────────┐  ┌──────────┐  ┌────────┐
        │ QUALIFIED│  │   LOST   │  │  LOST  │
        └────┬────┘  │(unresponsive)│(disqualified)│
             │       └──────────┘  └────────┘
             │
       ┌─────┴─────┐
       ▼           ▼
┌──────────┐ ┌──────────┐
│ CONVERTED│ │   LOST   │
└──────────┘ └──────────┘
```

## Allowed Transitions

| From | To | Conditions |
|------|-----|------------|
| New | Contacted | First contact made |
| New | Lost | Invalid email/phone after verification |
| Contacted | Qualified | Interest confirmed + criteria met |
| Contacted | Lost | Unresponsive after 3+ attempts |
| Qualified | Converted | Deal closed |
| Qualified | Lost | Decided not to sell |
| Lost | New | Re-engages after 90+ days |
| Converted | - | Terminal state |

## Status Change Logging

When updating status, always log:
- Previous status
- New status
- Date/time of change
- Reason for change
- Notes about decision

Use the update script:

```bash
./scripts/update_lead.py --id 1 --status qualified
```

## Pipeline Health Metrics

Track the following for pipeline management:

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| New leads > 24h old | < 10% | > 20% |
| Contacted > 7 days | < 15% | > 30% |
| Qualified > 30 days | < 20% | > 40% |
| Conversion rate | > 15% | < 10% |

## Reporting Status Distribution

Run weekly to monitor pipeline health:

```bash
./scripts/report.py --period weekly
```

A healthy pipeline should have:
- 30-40% New leads
- 25-35% Contacted
- 15-25% Qualified
- 5-10% Converted (cumulative)
- 10-15% Lost (cumulative)
