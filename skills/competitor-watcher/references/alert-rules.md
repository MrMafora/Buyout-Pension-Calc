# Alert Rules for Competitor Watcher

This document defines when and how alerts should be triggered for competitor activity.

## Alert Severity Levels

### Critical (Immediate Notification)

Trigger immediately via email/WhatsApp:

- **Pricing Changes** - Any competitor lowers price by >10% or introduces new pricing tier
- **Feature Launch** - Direct competitor launches major feature matching FedBuyOut's core offering
- **Site Redesign** - Complete website overhaul indicating strategic shift
- **New Competitor Entry** - Well-funded competitor enters market
- **Acquisition/Merger** - Competitor acquired by major player

### High (Daily Digest)

Include in daily summary:

- **Content Updates** - Significant changes to product/service descriptions
- **New Pages Added** - Expansion into new service areas
- **Testimonials/Case Studies** - New social proof added
- **Blog Posts** - New content on federal retirement topics
- **Pricing Page Changes** - Any modification to pricing presentation

### Medium (Weekly Summary)

Include in weekly report:

- **Minor Content Updates** - Text changes, typo fixes
- **SEO Changes** - Meta description, title tag updates
- **Navigation Changes** - Menu restructuring
- **Visual Updates** - Image changes, minor design tweaks

### Low (Monthly Review)

Review during monthly analysis:

- **Footer Changes** - Copyright updates, link changes
- **Minor Text Changes** - Single word changes
- **Asset Updates** - CSS/JS file updates

## Alert Triggers

### Pricing Alert Rules

```yaml
price_drop_threshold: 5%      # Alert if price drops >5%
price_increase_threshold: 10% # Alert if price increases >10%
new_pricing_tier: critical    # New tier/training = critical
free_tier_introduced: critical # New free tier = critical
```

### Feature Alert Rules

```yaml
new_calculator_type: high     # New FERS/CSRS/TSP calculator
ai_features: critical         # AI-powered analysis
mobile_app: high             # Mobile app launch
api_access: medium           # API availability
integration: medium          # New integrations (Zapier, etc.)
```

### Market Alert Rules

```yaml
new_competitor: high         # New entrant discovered
competitor_acquired: critical # M&A activity
funding_announced: high      # Competitor raises funding
key_hire: medium            # Industry expert joins competitor
```

## Alert Channels

### Critical Alerts

- Email: clark@fedbuyout.com (immediate)
- WhatsApp notification
- Dashboard alert

### High Alerts

- Daily email digest
- Dashboard notification

### Medium/Low Alerts

- Weekly summary email
- Monthly report inclusion

## Alert Templates

### Critical: Pricing Change

```
🚨 CRITICAL: Competitor Pricing Change Detected

Competitor: {name}
Change Type: Price {increase/decrease}
Old Price: {old_price}
New Price: {new_price}
Change: {percent}%

URL: {pricing_url}
Detected: {timestamp}

Action Required: Review FedBuyOut pricing strategy
```

### Critical: Feature Launch

```
🚨 CRITICAL: Competitor Feature Launch

Competitor: {name}
Feature: {feature_name}
Description: {feature_description}
Impact: {high/medium/low}

URL: {url}
Detected: {timestamp}

Action Required: Assess competitive threat
```

### High: Content Update

```
⚠️ HIGH: Competitor Content Update

Competitor: {name}
Page: {page_name}
Change Type: {added/modified/removed}
Summary: {brief_description}

URL: {url}
Detected: {timestamp}
```

## Escalation Process

1. **Detection** - Automated monitoring detects change
2. **Classification** - System categorizes by severity
3. **Notification** - Alert sent via appropriate channel
4. **Response** - Team reviews and takes action
5. **Documentation** - Change logged in competitor tracking

## Alert Fatigue Prevention

To prevent alert overload:

- **Batching** - Group similar alerts into digests
- **Thresholds** - Only alert on meaningful changes (>5% or new features)
- **Quiet Hours** - No non-critical alerts 10 PM - 7 AM
- **Deduplication** - Don't alert on same change within 24 hours
- **Mute Options** - Ability to mute specific competitors or alert types

## Configuration

Edit `references/alerts.conf`:

```bash
# Severity thresholds
CRITICAL_PRICE_CHANGE_PCT=10
HIGH_PRICE_CHANGE_PCT=5

# Channels
CRITICAL_CHANNEL=email,sms
dHIGH_CHANNEL=email
MEDIUM_CHANNEL=dashboard

# Quiet hours
QUIET_HOURS_START=22:00
QUIET_HOURS_END=07:00

# Batching
DAILY_DIGEST_TIME=09:00
WEEKLY_DIGEST_DAY=Monday
WEEKLY_DIGEST_TIME=09:00
```
