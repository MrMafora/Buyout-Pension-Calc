# A/B Testing Guide for Email Campaigns

How to run effective A/B tests to optimize FedBuyOut email performance.

---

## What to A/B Test

### Priority 1: High Impact, Easy to Test

**Subject Lines**
- Easiest test to run
- Directly impacts open rates
- Test different formulas (curiosity vs. benefit vs. question)

**Send Times**
- Morning vs. afternoon
- Day of week variations
- Time zone considerations

**From Names**
- "FedBuyOut Team" vs. "Clark from FedBuyOut"
- Personal vs. brand name
- "Support" vs. specific person

### Priority 2: Medium Impact, Moderate Effort

**Email Content**
- Long-form vs. short-form
- Different CTAs
- Story-driven vs. fact-driven
- Number of CTAs (1 vs. 2)

**CTA Buttons**
- Button color (brand-appropriate options)
- Button text ("Learn More" vs. "Get Started")
- Button placement (top vs. bottom)
- Button style (solid vs. outlined)

**Preview Text**
- Complement subject vs. standalone message
- Length variations
- Question vs. statement

### Priority 3: Lower Impact, Higher Effort

**Template Design**
- Single column vs. multi-column
- Image-heavy vs. text-only
- Different header styles
- Footer variations

**Personalization Level**
- First name only vs. additional data
- Dynamic content blocks
- Segmented messaging

**Email Length**
- Very short (under 100 words)
- Medium (200-300 words)
- Long (400+ words)

---

## Testing Framework

### The Scientific Method

1. **Hypothesis**
   - "Subject lines with personalization will outperform generic subjects"
   - "Sending at 9 AM will have higher opens than 3 PM"

2. **Variable Selection**
   - Test ONE thing at a time
   - Keep everything else identical

3. **Sample Size**
   - Minimum 100 per variant
   - 200+ for statistical confidence
   - 10% of list for test, 90% to winner (winner-take-all)

4. **Test Duration**
   - Minimum 4 hours
   - Maximum 24 hours
   - Account for time zones

5. **Winner Selection**
   - Define metric before testing
   - Consider secondary metrics
   - Document results

### Sample Size Calculator

Use this formula for minimum sample size:

```
Minimum per variant = (Z² × p × (1-p)) / E²

Where:
- Z = 1.96 (for 95% confidence)
- p = expected conversion rate (decimal)
- E = margin of error (decimal, usually 0.05)

Example for 20% open rate, 5% margin of error:
(1.96² × 0.20 × 0.80) / 0.05² = 246 per variant
```

**Quick Reference:**

| Expected Rate | Margin of Error | Sample Size per Variant |
|---------------|-----------------|------------------------|
| 20% | 5% | 246 |
| 25% | 5% | 288 |
| 30% | 5% | 323 |
| 20% | 3% | 683 |
| 25% | 3% | 801 |

---

## Testing Calendar

### Weekly Testing Schedule

| Day | Activity |
|-----|----------|
| Monday | Review last week's test results |
| Tuesday | Design new test, set up in system |
| Wednesday | Launch test (morning) |
| Thursday | Check early results, no changes |
| Friday | Declare winner, send to remaining list |
| Saturday | Document results, plan next test |

### Monthly Testing Themes

**Week 1: Subject Lines**
- Test curiosity vs. benefit vs. question formulas
- Test personalization vs. no personalization
- Test length (short vs. long)

**Week 2: Send Time**
- Test morning (9 AM) vs. afternoon (1 PM) vs. evening (5 PM)
- Test Tuesday vs. Thursday
- Test time zones

**Week 3: Content**
- Test CTA button text
- Test email length
- Test story vs. facts approach

**Week 4: Advanced**
- Test from name
- Test template design
- Test segmentation strategies

---

## Test Ideas by Campaign Type

### Welcome Sequence

**Test 1:** Subject Line Formula
- A: "Welcome to FedBuyOut - Here's What to Expect"
- B: "{{firstName}}, You're In! Here's What's Next"
- Metric: Open rate

**Test 2:** CTA Placement
- A: CTA at bottom of email
- B: CTA at top AND bottom
- Metric: Click rate

**Test 3:** Email Length
- A: Full welcome message (300 words)
- B: Brief welcome (100 words) + "More coming soon"
- Metric: Click rate, subsequent email opens

### Educational Drip

**Test 1:** Subject Approach
- A: "Understanding Your Pension Options" (direct)
- B: "The 3 Pension Options Most Feds Don't Know About" (curiosity)
- Metric: Open rate

**Test 2:** Content Depth
- A: Detailed explanation with examples
- B: Summary with link to full article
- Metric: Time on page (if tracked), next email engagement

**Test 3:** Consultation CTA
- A: Soft CTA ("Questions? Reply to this email")
- B: Hard CTA ("Schedule Your Free Consultation")
- Metric: Consultation bookings

### Re-engagement

**Test 1:** Tone
- A: "We miss you" (emotional)
- B: "Is this still relevant?" (practical)
- Metric: Re-engagement rate

**Test 2:** CTA Type
- A: "Click to stay subscribed" (active opt-in)
- B: "Reply YES to stay" (email reply)
- Metric: Retention rate

---

## Statistical Significance

### When Is a Result Valid?

**Confidence Level:** 95% (industry standard)
**This means:** 95% chance the result isn't due to random chance

### Calculating Significance

Use an online calculator:
- Optimizely Sample Size Calculator
- Evan Miller's Sample Size Calculator
- VWO A/B Significance Calculator

Or use the `ab-test.js` script:

```bash
node scripts/ab-test.js --campaign "welcome" --stats
```

### Reading Results

| Variant | Sent | Opened | Open Rate |
|---------|------|--------|-----------|
| A | 200 | 50 | 25% |
| B | 200 | 60 | 30% |

**Result:** B wins by 20% relative improvement
**Significance:** ~80% (not quite significant, but trending)

**Action:** Either wait for more data or call B winner with note

### When to Call a Test

**Call Early (4-6 hours):**
- 95%+ confidence reached
- One variant clearly underperforming (half the rate)
- Time-sensitive send

**Wait Full 24 Hours:**
- Confidence between 80-95%
- Close results
- High-stakes test

**Extend Test:**
- Low confidence (<80%)
- Sample size below minimum
- Unexpected results

---

## Documenting Results

### Test Log Template

```markdown
## Test ID: WL-001
**Date:** 2024-01-15
**Campaign:** Welcome Sequence Email 1

### Hypothesis
Personalized subject lines will increase open rates by 10%+

### Variables
- **Test:** Subject line
- **Constant:** Send time, from name, content

### Variants
| Variant | Subject Line |
|---------|--------------|
| A | "Welcome to FedBuyOut - Here's What to Expect" |
| B | "{{firstName}}, You're In! Here's What's Next" |

### Results
| Metric | Variant A | Variant B | Winner | Improvement |
|--------|-----------|-----------|--------|-------------|
| Open Rate | 22% | 28% | B | +27% |
| Click Rate | 3.5% | 4.2% | B | +20% |
| Unsubscribe | 0.1% | 0.1% | Tie | - |

### Confidence
95% (statistically significant)

### Learnings
- Personalization had stronger effect than expected
- Click rate improved even though not tested
- Applying to future welcome emails

### Action Items
- [ ] Update subject line template
- [ ] Test personalization in Email 2
- [ ] Document in best practices
```

### What to Track

**Primary Metrics:**
- Open rate (for subject/from tests)
- Click rate (for content/CTA tests)
- Conversion rate (for bottom-funnel tests)

**Secondary Metrics:**
- Unsubscribe rate (watch for negative effects)
- Reply rate (engagement quality)
- Forward rate (viral potential)
- Complaint rate (deliverability impact)

---

## Common A/B Testing Mistakes

### 1. Testing Too Many Variables
❌ Testing subject line AND send time AND CTA color
✅ Test ONE variable per experiment

### 2. Sample Size Too Small
❌ 20 recipients per variant
✅ Minimum 100, ideally 200+

### 3. Ending Tests Too Early
❌ Checking after 1 hour, calling winner
✅ Wait minimum 4 hours, ideally 24

### 4. Not Documenting Results
❌ "I think we tested that before..."
✅ Maintain test log, reference past results

### 5. Ignoring Secondary Metrics
❌ High open rate but 3x unsubscribes
✅ Review all metrics before declaring winner

### 6. Testing Without Hypothesis
❌ "Let's try this and see what happens"
✅ "We believe X because Y, therefore Z"

### 7. Not Applying Learnings
❌ Run test, declare winner, never change templates
✅ Implement winner, document for future reference

### 8. Testing Inconsequential Things
❌ Spending weeks on button shade differences
✅ Focus on subject lines, send times, major content

---

## Advanced Testing

### Multivariate Testing

When you want to test multiple variables simultaneously:

**Example:**
- Subject: Generic vs. Personalized
- Send Time: 9 AM vs. 1 PM
- CTA: "Learn More" vs. "Get Started"

**Combinations:** 2 × 2 × 2 = 8 variants

**Requirements:**
- Large list (1000+ for 100 per variant)
- Testing platform with multivariate support
- Statistical expertise recommended

### Sequential Testing

Test A vs. B, winner vs. C, winner vs. D...

**Good for:** Finding the absolute best option
**Risk:** Accumulated error rate
**Mitigation:** Use higher confidence (99%)

### Segmented Testing

Run different tests for different audience segments:

- New leads vs. existing customers
- FERS vs. CSRS employees
- Age groups
- Geographic regions

**Benefit:** Find what works for each segment
**Cost:** Requires larger list sizes

---

## Testing Tools

### Built-in to Campaign Scripts

```bash
# Enable A/B testing for a campaign
node scripts/ab-test.js --campaign "welcome" --create --variants 2

# View test statistics
node scripts/ab-test.js --campaign "welcome" --stats

# Declare winner
node scripts/ab-test.js --campaign "welcome" --winner A
```

### Third-Party Options

- **Mailchimp:** Built-in A/B testing
- **ConvertKit:** Automated winner selection
- **ActiveCampaign:** Advanced split testing
- **Resend:** Manual implementation (use scripts)

---

## Quick Start Checklist

- [ ] Identify what to test (start with subject lines)
- [ ] Form clear hypothesis
- [ ] Define success metric upfront
- [ ] Calculate required sample size
- [ ] Ensure list is large enough
- [ ] Create test variants
- [ ] Set up tracking
- [ ] Launch test
- [ ] Wait appropriate duration
- [ ] Calculate statistical significance
- [ ] Declare winner
- [ ] Document results
- [ ] Implement winner
- [ ] Plan next test
