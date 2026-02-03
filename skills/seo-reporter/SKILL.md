---
name: seo-reporter
description: SEO rank tracking and insights for FedBuyOut. Use when tracking search engine rankings for keywords, monitoring competitor positions, generating SEO reports, conducting SEO audits, analyzing keyword opportunities, or tracking backlink growth. Covers Google rank tracking, competitor analysis, keyword research, on-page SEO audits, and automated weekly/monthly reporting.
---

# SEO Reporter for FedBuyOut

Track search rankings, monitor competitors, and generate SEO insights for FedBuyOut.

## Quick Start

### Track Current Rankings
```bash
# Check all target keywords
node scripts/track-rankings.js

# Check specific keyword
node scripts/track-rankings.js --keyword "VSIP calculator"
```

### Generate Report
```bash
# Weekly report
node scripts/generate-report.js --type weekly

# Monthly report
node scripts/generate-report.js --type monthly
```

### SEO Audit
```bash
# Run full audit on fedbuyout.com
node scripts/seo-audit.js --url https://fedbuyout.com

# Check specific page
node scripts/seo-audit.js --url https://fedbuyout.com/calculator
```

## Features

### 1. Rank Tracking
- Track FedBuyOut rankings for target keywords
- Daily/weekly automated tracking
- Historical data storage
- Position change alerts

### 2. Competitor Monitoring
- Track competitor rankings for same keywords
- Identify competitor content gaps
- Monitor new competitor pages

### 3. Keyword Opportunities
- Suggest long-tail keyword variants
- Identify low-competition opportunities
- Track search volume trends

### 4. SEO Audit
- On-page SEO analysis
- Technical SEO checks
- Meta tag validation
- Page speed insights

### 5. Backlink Tracking
- Monitor new/lost backlinks
- Track referring domains
- Anchor text analysis

### 6. Reporting
- Weekly summary reports
- Monthly detailed reports
- Competitor comparison charts
- Export to CSV/JSON

## Target Keywords

See [references/target-keywords.json](references/target-keywords.json) for the full list.

Primary keywords:
- federal buyout calculator
- VSIP calculator
- FERS buyout
- federal employee buyout
- early retirement calculator

## Competitors

See [references/competitors.json](references/competitors.json) for competitor domains and tracking settings.

## Data Storage

All data is stored in:
- `data/rankings/` - Historical ranking data
- `data/reports/` - Generated reports
- `data/backlinks/` - Backlink tracking data
- `data/audits/` - SEO audit results

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `track-rankings.js` | Check keyword rankings | `node track-rankings.js [--keyword "..."]` |
| `competitor-tracker.js` | Monitor competitors | `node competitor-tracker.js [--domain "..."]` |
| `keyword-opportunities.js` | Find keyword gaps | `node keyword-opportunities.js` |
| `seo-audit.js` | Run SEO audits | `node seo-audit.js --url <url>` |
| `backlink-tracker.js` | Track backlinks | `node backlink-tracker.js` |
| `generate-report.js` | Create reports | `node generate-report.js --type <weekly|monthly>` |

## API Keys Required

Set these environment variables:
- `SERPAPI_KEY` - For rank tracking (serpapi.com)
- `PAGESPEED_API_KEY` - For PageSpeed insights
- `AHREFS_API_KEY` - For backlink data (optional)

## Reports

Reports are generated in:
- Markdown format for human reading
- JSON format for data processing
- CSV format for spreadsheets

Location: `data/reports/<YYYY-MM-DD>-<type>.<ext>`
