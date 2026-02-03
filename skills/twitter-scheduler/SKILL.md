---
name: twitter-scheduler
description: Schedule tweets, create tweet threads, and manage Twitter content for FedBuyOut marketing. Use when creating or scheduling Twitter content, building tweet threads, planning social media campaigns, generating hashtag suggestions, or managing the content calendar for FedBuyOut's Twitter presence.
---

# Twitter Scheduler for FedBuyOut

A comprehensive tool for managing FedBuyOut's Twitter marketing presence.

## Quick Start

### Schedule a Single Tweet

```bash
python3 scripts/schedule_tweet.py --content "Your tweet text here" --time "2026-02-05 09:00"
```

### Create a Tweet Thread

```bash
python3 scripts/thread_builder.py --file thread_content.txt --time "2026-02-05 10:00"
```

### Generate Hashtag Suggestions

```bash
python3 scripts/hashtag_suggester.py --topic "government contracts"
```

### View Content Calendar

```bash
python3 scripts/calendar_view.py --week
```

## Core Workflows

### 1. Scheduling Tweets for Optimal Times

FedBuyOut's optimal posting times (US Eastern):
- **Tuesday-Thursday**: 9:00 AM - 11:00 AM, 1:00 PM - 3:00 PM
- **Friday**: 9:00 AM - 11:00 AM
- **Avoid**: Late evenings, weekends (unless specific campaign)

Use the schedule_tweet.py script to queue tweets:

```bash
# Schedule with optimal time auto-suggestion
python3 scripts/schedule_tweet.py --content "FedBuyOut makes gov contracts simple" --auto-time

# Schedule for specific time
python3 scripts/schedule_tweet.py --content "Your message" --time "2026-02-05 09:30" --timezone "America/New_York"
```

### 2. Building Tweet Threads

For complex topics requiring multiple tweets:

1. Create a text file with thread content (use `---` as separator):
```
Did you know small businesses can win federal contracts? 🧵
---
Step 1: Get your SAM registration done. This is mandatory for all federal contractors.
---
Step 2: Understand your NAICS codes. These classify what your business does.
---
Step 3: Start small with set-asides. 8(a), WOSB, HUBZone have less competition.
---
Ready to get started? Visit fedbuyout.com 🚀
```

2. Run the thread builder:
```bash
python3 scripts/thread_builder.py --file thread.txt --time "2026-02-06 10:00"
```

The script validates:
- Character limits per tweet (280 chars)
- Thread coherence
- Proper numbering

### 3. Hashtag Strategy

Use the hashtag suggester for research:

```bash
# Get suggestions for a topic
python3 scripts/hashtag_suggester.py --topic "government contracting"

# Analyze hashtag performance
python3 scripts/hashtag_suggester.py --analyze "#GovCon #SmallBusiness #FederalContracts"
```

**FedBuyOut Core Hashtags:**
- #GovCon (Government Contracting)
- #SmallBusiness
- #FederalContracts
- #8a #WOSB #HUBZone (set-asides)
- #SAMRegistration
- #ContractingMadeSimple

**Trending/Seasonal Hashtags:**
- #NAICSCodeHelp
- #ContractingTips
- #GovernmentSales
- #B2GGrowth

### 4. Content Calendar Management

View and manage scheduled content:

```bash
# View today's scheduled tweets
python3 scripts/calendar_view.py --today

# View this week
python3 scripts/calendar_view.py --week

# View by campaign
python3 scripts/calendar_view.py --campaign "feb-webinar"

# Export calendar to CSV
python3 scripts/calendar_view.py --export --format csv
```

**Content Pillars for FedBuyOut:**
1. **Educational** - How-to guides, explanations (40%)
2. **Success Stories** - Client wins, testimonials (20%)
3. **Industry News** - GovCon updates, policy changes (20%)
4. **Engagement** - Polls, questions, tips (20%)

### 5. Analytics Tracking

Track tweet performance:

```bash
# View scheduled tweet analytics
python3 scripts/analytics.py --scheduled

# Track campaign performance
python3 scripts/analytics.py --campaign "q1-2026"

# Generate weekly report
python3 scripts/analytics.py --weekly --export

# Compare hashtag performance
python3 scripts/analytics.py --hashtags "#GovCon,#SmallBusiness"
```

## Content Templates

See [references/templates.md](references/templates.md) for ready-to-use tweet templates:

- Educational threads
- Product announcements
- Client success stories
- Industry commentary
- Engagement posts
- Promotional content

## Best Practices

See [references/best-practices.md](references/best-practices.md) for:

- Twitter algorithm optimization
- Engagement tactics
- Tone and voice guidelines
- Image/video guidelines
- Compliance considerations for government contracting content

## File Structure

```
twitter-scheduler/
├── scripts/
│   ├── schedule_tweet.py      # Schedule individual tweets
│   ├── thread_builder.py      # Create and schedule threads
│   ├── hashtag_suggester.py   # Hashtag research and suggestions
│   ├── calendar_view.py       # View and manage content calendar
│   └── analytics.py           # Track performance metrics
└── references/
    ├── templates.md           # Tweet templates
    └── best-practices.md      # Twitter marketing best practices
```

## Automation Integration

The scripts output JSON files to `.openclaw/twitter-scheduler/`:
- `scheduled.json` - Upcoming tweets
- `threads.json` - Thread definitions
- `analytics.json` - Performance data
- `calendar.json` - Content calendar

These can be integrated with external scheduling tools or CI/CD pipelines.
