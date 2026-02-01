# Google Analytics Setup for FedBuyOut

## Why Google Analytics?

- Track website visitors
- See traffic sources (Reddit, Google, direct)
- Monitor user behavior
- Calculate conversion rates
- Measure marketing ROI
- Free and essential

## Setup Steps

### 1. Create Google Analytics Account

1. Go to https://analytics.google.com/
2. Sign in with Google account (use support@fedbuyout.com)
3. Click "Start measuring"
4. Account name: "FedBuyOut"
5. Property name: "FedBuyOut.com"
6. Time zone: Eastern Time (US)
7. Currency: USD
8. Click "Next"

### 2. Create Data Stream

1. Choose "Web" platform
2. Website URL: https://fedbuyout.com
3. Stream name: "FedBuyOut Website"
4. Click "Create stream"
5. Copy the Measurement ID (looks like G-XXXXXXXXXX)

### 3. Add Tracking Code to Website

**Option A: Google Tag Manager (Recommended)**
1. Create GTM account: https://tagmanager.google.com/
2. Install GTM container code in website head
3. Add GA4 tag through GTM

**Option B: Direct GA4 Installation**

Add this code to index.html `<head>` section:

```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

Replace G-XXXXXXXXXX with your actual Measurement ID.

### 4. Verify Installation

1. Visit https://fedbuyout.com
2. Check Real-time reports in GA
3. Should see 1 active user (you)

### 5. Set Up Key Events (Conversions)

**Track these important actions:**

**Event: calculator_used**
- Trigger: User clicks "Calculate" button
- Importance: Core engagement metric

**Event: newsletter_signup**
- Trigger: Email submitted
- Importance: Lead generation

**Event: lead_captured**
- Trigger: Contact info saved
- Importance: High-value conversion

**Event: contact_form**
- Trigger: Contact form submitted
- Importance: User engagement

## How to Track Conversions

### Method 1: Google Tag Manager (Advanced)

Set up triggers for each event and send to GA4.

### Method 2: Direct gtag.js Calls (Simple)

Add JavaScript to each action:

```javascript
// When calculator is used
gtag('event', 'calculator_used', {
  'event_category': 'engagement',
  'event_label': 'buyout_calculation'
});

// When email is captured
gtag('event', 'newsletter_signup', {
  'event_category': 'lead_gen',
  'event_label': 'email_subscribed'
});

// When lead is saved
gtag('event', 'lead_captured', {
  'event_category': 'conversion',
  'event_label': 'full_lead'
});
```

## Key Metrics to Monitor

### Daily
- **Users:** Total visitors
- **Sessions:** Visits (one user can have multiple)
- **Pageviews:** Total page loads
- **Bounce Rate:** % who leave without interaction
- **Avg Session Duration:** Time on site

### Weekly
- **Traffic Sources:** Where visitors come from
- **Top Pages:** Most viewed content
- **Calculator Usage:** How many use the tool
- **Conversion Rate:** % who subscribe/submit lead

### Monthly
- **Organic Traffic:** From Google search
- **Social Traffic:** From Reddit, Twitter, LinkedIn
- **Referral Traffic:** From other websites
- **Goal Completions:** Total conversions
- **Revenue:** If you track lead sales

## Reports to Set Up

### 1. Traffic Acquisition Report
**What it shows:** Where users come from
**Why it matters:** See which marketing works

### 2. Engagement Report
**What it shows:** How users interact
**Why it matters:** Optimize user experience

### 3. Conversion Report
**What it shows:** How many complete goals
**Why it matters:** Measure business success

### 4. Real-time Report
**What it shows:** Current active users
**Why it matters:** Monitor campaigns live

## Goals to Set

**Goal 1: Newsletter Signup**
- Type: Event
- Event name: newsletter_signup
- Target: 50/month

**Goal 2: Lead Capture**
- Type: Event  
- Event name: lead_captured
- Target: 20/month

**Goal 3: Calculator Usage**
- Type: Event
- Event name: calculator_used
- Target: 200/month

## Dashboard Creation

**Create custom dashboard with:**
1. Users (last 7 days)
2. Conversion rate
3. Top traffic sources
4. Calculator usage
5. Revenue (manual entry)

## Alerts to Set

**Traffic Drop Alert:**
- Trigger: Users drop 50% vs previous day
- Action: Check if site is down

**Goal Completion Alert:**
- Trigger: Lead captured
- Action: Notify you immediately

## Privacy Compliance

**Add to Privacy Policy:**
"We use Google Analytics to understand website usage. You can opt out at https://tools.google.com/dlpage/gaoptout"

**Add Cookie Banner:**
"This site uses cookies to analyze traffic. [Accept] [Learn More]"

## Alternative: Plausible Analytics

If you prefer privacy-focused:
- https://plausible.io/
- No cookies needed
- GDPR compliant
- $9/month for 10k pageviews
- Easier setup

## Quick Setup Summary

1. ✅ Create GA account (5 min)
2. ✅ Get Measurement ID (1 min)
3. ⚠️ Add code to website (I need to do this)
4. ✅ Verify tracking (2 min)
5. ✅ Set up goals (10 min)
6. ✅ Create dashboard (5 min)

**Total time:** ~30 minutes

---

**Action Required:** 
1. Create GA4 account at https://analytics.google.com/
2. Send me the Measurement ID (G-XXXXXXXXXX)
3. I'll add the tracking code to the website
4. Start tracking traffic!

**Without GA, we're flying blind. This is critical for measuring marketing success.**
