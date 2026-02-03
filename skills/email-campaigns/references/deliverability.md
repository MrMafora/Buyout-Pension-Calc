# Email Deliverability Best Practices

How to ensure FedBuyOut emails reach the inbox, not the spam folder.

---

## Domain Authentication

### What Is It?

Domain authentication proves to email providers (Gmail, Yahoo, etc.) that you are who you say you are and authorized to send email from your domain.

### The Three Pillars

#### 1. SPF (Sender Policy Framework)

**Purpose:** Authorizes which servers can send email for your domain

**Setup:**
```
DNS Record Type: TXT
Host: @ (or your domain)
Value: v=spf1 include:resend.com ~all
```

**Verification:**
```bash
dig TXT fedbuyout.com | grep spf
```

**Common Mistakes:**
- Multiple SPF records (merge them)
- Syntax errors
- Using -all instead of ~all (too strict)

#### 2. DKIM (DomainKeys Identified Mail)

**Purpose:** Cryptographically signs emails to verify they weren't altered

**Setup (Resend):**
1. Get DKIM keys from Resend dashboard
2. Add provided TXT record to DNS
3. Wait for propagation (up to 48 hours)

**Verification:**
```bash
dig TXT default._domainkey.fedbuyout.com
```

#### 3. DMARC (Domain-based Message Authentication)

**Purpose:** Tells receivers what to do with failed authentication

**Setup (Progressive):**

**Phase 1: Monitor Only**
```
DNS Record Type: TXT
Host: _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc@fedbuyout.com; pct=100
```

**Phase 2: Quarantine (After 2 weeks of monitoring)**
```
Value: v=DMARC1; p=quarantine; rua=mailto:dmarc@fedbuyout.com; pct=100
```

**Phase 3: Reject (After 30 days of no issues)**
```
Value: v=DMARC1; p=reject; rua=mailto:dmarc@fedbuyout.com; pct=100
```

**Monitoring:**
- Set up DMARC reporting mailbox
- Review weekly reports
- Fix any authentication failures

### Authentication Checklist

- [ ] SPF record configured
- [ ] DKIM keys added to DNS
- [ ] DMARC policy in place (start with p=none)
- [ ] All records propagated (wait 24-48 hours)
- [ ] Test with authentication checker

---

## List Hygiene

### Regular Maintenance

**Weekly:**
- Review bounce reports
- Remove hard bounces immediately
- Investigate soft bounces (3+ = remove)

**Monthly:**
- Run re-engagement campaign
- Remove non-engagers (no opens in 90 days)
- Update suppressed addresses
- Check for role account bounces (admin@, info@, etc.)

**Quarterly:**
- Full list audit
- Segment inactive subscribers
- Review acquisition sources
- Clean duplicates

### Bounce Types

**Hard Bounces (Remove Immediately):**
- Invalid email address
- Domain doesn't exist
- Email account disabled
- Mailbox full (permanent)

**Soft Bounces (Monitor, Remove After 3):**
- Mailbox temporarily full
- Server temporarily unavailable
- Message too large
- Rate limiting

### Suppression List Management

**Never Send To:**
- Unsubscribed addresses
- Hard bounces
- Spam complaints
- Role accounts (noreply@, postmaster@)
- Typo domains (gmial.com, yahooo.com)

**Script for List Cleaning:**

```bash
node scripts/clean-list.js --list leads.json --output cleaned-leads.json
```

---

## Engagement Monitoring

### Key Metrics

| Metric | Target | Action if Below |
|--------|--------|-----------------|
| Open Rate | 20%+ | Review subject lines, list quality |
| Click Rate | 2%+ | Review content relevance |
| Unsubscribe Rate | <0.5% | Review frequency, content |
| Complaint Rate | <0.1% | Immediate investigation |
| Bounce Rate | <2% | Clean list immediately |

### Engagement-Based Segmentation

**Hot (Opened last 3 emails):**
- Highest frequency OK
- Sales-ready content
- Priority for new campaigns

**Warm (Opened in last 30 days):**
- Standard frequency
- Nurture content
- Target for reactivation

**Cold (No opens in 30-60 days):**
- Reduce frequency
- Re-engagement campaign
- Sunset if no response

**Frozen (No opens in 60+ days):**
- Final re-engagement attempt
- Remove if no response
- Move to suppression

### List Warming

**New Domain/Account:**
1. Start with small volume (50/day)
2. Target most engaged subscribers first
3. Gradually increase (double weekly)
4. Target: 1000+ sends/day after 30 days

**Volume Ramp Schedule:**

| Week | Daily Volume | Target Segment |
|------|--------------|----------------|
| 1 | 50 | Hot leads only |
| 2 | 100 | Hot + Warm |
| 3 | 250 | All engaged |
| 4 | 500 | Full list (minus cold) |
| 5+ | 1000+ | Full list |

---

## Content Best Practices

### Spam Trigger Avoidance

**Words to Avoid (see subject-lines.md for full list):**
- Free
- Act now
- Guaranteed
- No obligation
- Cash bonus
- Order now
- Limited time

**Safe Alternatives:**
- "Complimentary" instead of "Free"
- "Get started" instead of "Act now"
- "100% satisfaction" instead of "Guaranteed"
- "Learn more" instead of "Order now"

### HTML Best Practices

**Do:**
- Use inline CSS (not external stylesheets)
- Include plain text version
- Keep image-to-text ratio balanced (more text than images)
- Use alt text for all images
- Test rendering in multiple clients
- Keep total size under 100KB

**Don't:**
- Use JavaScript
- Embed forms
- Include attachments
- Use URL shorteners
- Hide text (white on white)
- Use ALL CAPS excessively

### Email Structure

**Template Checklist:**
- [ ] Plain text version included
- [ ] Unsubscribe link in footer
- [ ] Physical mailing address in footer
- [ ] Company name clear
- [ ] No broken links
- [ ] Mobile-responsive
- [ ] Alt text on images
- [ ] Balanced text/image ratio

---

## Reputation Management

### IP Warming

**New Dedicated IP:**
1. Start with transactional emails (high engagement)
2. Gradually add marketing emails
3. Monitor reputation daily
4. Adjust volume based on feedback loops

**Reputation Tools:**
- Google Postmaster Tools
- Microsoft SNDS
- Barracuda Reputation
- Sender Score

### Feedback Loops

**Set Up With Major Providers:**
- Yahoo Complaint Feedback Loop
- Microsoft JMRP
- Cloudmark Sender Intelligence

**Process Complaints:**
1. Remove complainer immediately
2. Add to suppression list
3. Investigate cause
4. Adjust content/frequency if pattern

### Blacklist Monitoring

**Check Regularly:**
- MXToolbox Blacklist Check
- MultiRBL.valli.org
- Barracuda Reputation

**If Blacklisted:**
1. Identify reason
2. Clean list
3. Fix authentication
4. Submit delisting request
5. Wait before resuming sends

---

## Technical Setup

### DNS Records Summary

| Record | Type | Host | Value |
|--------|------|------|-------|
| SPF | TXT | @ | v=spf1 include:resend.com ~all |
| DKIM | TXT | default._domainkey | [From Resend] |
| DMARC | TXT | _dmarc | v=DMARC1; p=none; rua=mailto:dmarc@fedbuyout.com |
| MX | MX | @ | [Your email provider] |

### Testing Tools

**Authentication:**
- MXToolbox SPF/DKIM/DMARC checkers
- Google Admin Toolbox Check MX
- Mail-tester.com

**Deliverability:**
- GlockApps
- Litmus
- Email on Acid
- SendForensics

**Inbox Placement:**
- Seed list testing
- GlockApps Inbox Tests
- 250ok Informed

### Pre-Send Checklist

Before sending any campaign:

- [ ] Authentication records validated
- [ ] Mail-tester score 8+/10
- [ ] No spam trigger words in subject/content
- [ ] Unsubscribe link working
- [ ] All links functional
- [ ] Plain text version included
- [ ] Images have alt text
- [ ] From name matches domain
- [ ] Reply-to address valid
- [ ] List cleaned of bounces
- [ ] Tested in multiple clients
- [ ] Mobile rendering verified

---

## Troubleshooting

### Low Open Rates (<15%)

**Possible Causes:**
- Subject lines need work
- List quality poor
- Authentication issues
- Deliverability problems
- Sending to spam folder

**Investigation Steps:**
1. Check authentication (SPF/DKIM/DMARC)
2. Review subject lines for spam triggers
3. Check sender reputation
4. Test inbox placement
5. Segment by engagement

### High Bounce Rates (>5%)

**Immediate Actions:**
1. Pause campaign
2. Clean list
3. Remove all hard bounces
4. Investigate data source
5. Resume with clean list

### Spam Complaints (>0.3%)

**Investigation:**
1. Review content for misleading claims
2. Check subject line accuracy
3. Verify opt-in process
4. Review frequency
5. Audit list sources

### Blocked by Major Provider

**Google (Gmail):**
- Check Google Postmaster Tools
- Review spam complaint rate
- Check authentication
- Submit sender contact form

**Microsoft (Outlook/Hotmail):**
- Check SNDS
- Review JMRP data
- Submit support request
- Improve engagement

---

## Compliance

### CAN-SPAM Requirements

**Required Elements:**
1. Accurate header information
2. Non-deceptive subject lines
3. Clear identification as advertisement (if applicable)
4. Physical mailing address
5. Working unsubscribe mechanism
6. Honor unsubscribe within 10 business days
7. Monitor what others do on your behalf

**Penalties:**
- Up to $50,000 per violation
- Criminal penalties for intentional violations
- Liability for false/misleading claims

### GDPR (If Applicable)

**For EU Recipients:**
- Explicit consent required
- Right to access data
- Right to erasure
- Data processing records
- Breach notification within 72 hours

### CCPA (If Applicable)

**For California Recipients:**
- Privacy policy required
- Opt-out of sale mechanism
- Data access/deletion rights
- Notice at collection

---

## Weekly Deliverability Checklist

- [ ] Review bounce reports
- [ ] Check spam complaint rate
- [ ] Monitor sender reputation scores
- [ ] Check blacklist status
- [ ] Review DMARC reports
- [ ] Verify authentication records
- [ ] Check engagement metrics
- [ ] Update suppression list

## Monthly Deliverability Review

- [ ] Full list hygiene
- [ ] Authentication audit
- [ ] Template spam score testing
- [ ] Inbox placement testing
- [ ] Reputation score review
- [ ] Blacklist monitoring
- [ ] Feedback loop analysis
- [ ] Engagement segmentation review
