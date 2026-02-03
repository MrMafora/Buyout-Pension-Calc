---
name: analytics-dashboard
description: Generate traffic reports from Google Analytics 4 for FedBuyOut business. Use when creating daily traffic summaries, weekly performance reports, monthly deep-dive analysis, traffic source breakdowns, conversion funnel tracking, goal completion reports, or mobile vs desktop stats. Property ID G-07WYT2HRDW.
---

# Analytics Dashboard for FedBuyOut

Generate comprehensive traffic reports from Google Analytics 4 (GA4) for the FedBuyOut business website.

## Property Details

- **Property ID**: G-07WYT2HRDW
- **Business**: FedBuyOut (federal employee buyout services)
- **Email Account**: fedbuyout@gmail.com

## Report Types

### 1. Daily Traffic Summary
Quick snapshot of daily performance:
- Total sessions and users
- Page views and bounce rate
- Top pages visited
- Traffic sources overview

**Script**: `scripts/daily_report.py`

### 2. Weekly Performance Report
Week-over-week comparison:
- Sessions, users, and pageviews
- Engagement metrics (avg session duration, bounce rate)
- Top traffic sources
- Most visited pages
- Conversion metrics

**Script**: `scripts/weekly_report.py`

### 3. Monthly Deep-Dive Analysis
Comprehensive monthly insights:
- Month-over-month trends
- User behavior patterns
- Content performance analysis
- Geographic distribution
- Device and browser breakdown
- Goal completions and conversion rates

**Script**: `scripts/monthly_report.py`

### 4. Traffic Source Breakdown
Detailed channel analysis:
- Organic search performance
- Direct traffic
- Referral sources
- Social media channels
- Campaign performance (if tagged)

**Script**: `scripts/source_report.py`

### 5. Conversion Funnel Tracking
Goal and conversion analysis:
- Goal completion rates
- Funnel drop-off points
- Conversion by traffic source
- Time to conversion

**Script**: `scripts/conversion_report.py`

### 6. Goal Completion Reports
Specific goal tracking:
- Form submissions
- Phone calls
- Downloads
- Newsletter signups
- Contact page visits

**Script**: `scripts/goals_report.py`

### 7. Mobile vs Desktop Stats
Device and platform analysis:
- Sessions by device category
- Engagement by device
- Conversion rates by device
- Browser breakdown
- Screen resolution insights

**Script**: `scripts/device_report.py`

## Authentication

The GA4 API requires authentication via OAuth 2.0 or service account credentials.

**Setup**:
1. Use Google Cloud Console with fedbuyout@gmail.com
2. Enable Google Analytics Data API (GA4)
3. Create service account credentials
4. Store credentials in `~/.config/fedbuyout-analytics/credentials.json`

**Reference**: See [references/authentication.md](references/authentication.md)

## Metrics Reference

For detailed definitions of all metrics and dimensions used in reports, see:
[references/metrics.md](references/metrics.md)

## Report Templates

For report output templates and formatting guidelines:
[references/report_templates.md](references/report_templates.md)

## Quick Start

### Generate a Daily Report

```bash
python scripts/daily_report.py --property G-07WYT2HRDW --days 1
```

### Generate a Weekly Report

```bash
python scripts/weekly_report.py --property G-07WYT2HRDW --weeks 1
```

### Generate a Monthly Report

```bash
python scripts/monthly_report.py --property G-07WYT2HRDW --month 2026-01
```

### Generate a Traffic Source Report

```bash
python scripts/source_report.py --property G-07WYT2HRDW --days 7
```

### Generate a Device Report

```bash
python scripts/device_report.py --property G-07WYT2HRDW --days 30
```

## Output Formats

Reports can be generated in multiple formats:
- **Console**: Text output to terminal (default)
- **JSON**: Structured data for further processing
- **Markdown**: Formatted document suitable for sharing
- **HTML**: Web-ready formatted report
- **CSV**: Spreadsheet-compatible data export

Use `--format` flag to specify output format.

## Scheduling Reports

To schedule automated reports:
- Daily: Run at 9:00 AM for previous day
- Weekly: Run on Mondays at 9:00 AM for previous week
- Monthly: Run on 1st of month at 9:00 AM for previous month
