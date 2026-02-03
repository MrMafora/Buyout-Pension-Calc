---
name: news-monitor
description: Monitor federal buyout news and alert when relevant articles are published. Use for tracking VSIP (Voluntary Separation Incentive Payments), federal employee buyouts, early retirement offers, and related federal workforce news. Supports RSS feed monitoring, keyword tracking, article summarization, social media sharing, and weekly digest generation.
---

# News Monitor

Monitor federal buyout news from key sources and alert on relevant articles.

## Quick Start

### Check for new articles manually
```bash
python3 scripts/fetch_news.py --check
```

### Generate weekly digest
```bash
python3 scripts/weekly_digest.py
```

### Share article to social media
```bash
python3 scripts/share.py --article "<url>" --platforms twitter,linkedin
```

## Supported News Sources

See [references/news-sources.md](references/news-sources.md) for complete list of monitored RSS feeds.

Primary sources:
- FedSmith (fedsmith.com)
- GovExec (govexec.com)
- Federal News Network (federalnewsnetwork.com)
- Federal Times (federaltimes.com)
- Government Executive (governmentexecutive.com)

## Keyword Tracking

See [references/keywords.md](references/keywords.md) for tracked terms and relevance scoring.

High-priority keywords:
- VSIP (Voluntary Separation Incentive Payment)
- Buyout / Voluntary buyout
- Early retirement / VER (Voluntary Early Retirement)
- Federal employee reduction
- RIF (Reduction in Force)
- Federal workforce restructuring

## Alert System

When relevant articles are found:

1. **Immediate alerts** - High-relevance articles trigger instant notifications
2. **Daily summary** - Digest of all articles from past 24 hours
3. **Weekly digest** - Comprehensive summary with trend analysis

### Alert threshold
- Score >= 70: Immediate alert
- Score >= 40: Include in daily summary
- All tracked articles: Include in weekly digest

## Article Relevance Scoring

Articles are scored 0-100 based on:
- Keyword matches (title weighted 3x, content 1x)
- Source reliability (established outlets score higher)
- Recency (newer articles get small boost)
- Context (mentions of specific agencies, numbers, deadlines)

## Scripts Reference

### fetch_news.py
Fetch and analyze articles from RSS feeds.

```bash
# Check for new articles
python3 scripts/fetch_news.py --check

# Fetch with full analysis
python3 scripts/fetch_news.py --full

# Fetch from specific source
python3 scripts/fetch_news.py --source fedsmith

# Output JSON for processing
python3 scripts/fetch_news.py --json
```

### summarize.py
Summarize article content.

```bash
python3 scripts/summarize.py --url "<article-url>"
python3 scripts/summarize.py --file article.html
```

### share.py
Share articles to social media platforms.

```bash
# Share to all configured platforms
python3 scripts/share.py --article "<url>"

# Share to specific platforms
python3 scripts/share.py --article "<url>" --platforms twitter,linkedin

# Share with custom message
python3 scripts/share.py --article "<url>" --message "Breaking:"
```

### weekly_digest.py
Generate weekly digest of federal buyout news.

```bash
# Generate and save digest
python3 scripts/weekly_digest.py --output digest.md

# Generate and email digest
python3 scripts/weekly_digest.py --email clark@fedbuyout.com

# Preview without saving
python3 scripts/weekly_digest.py --preview
```

### alert.py
Send alerts for high-relevance articles.

```bash
# Send alert for article
python3 scripts/alert.py --article "<url>" --score 85

# Test alert system
python3 scripts/alert.py --test
```

## Data Storage

Article data is stored in:
- `data/articles.json` - All tracked articles with metadata
- `data/alerts.json` - Alert history
- `data/digests/` - Generated weekly digests

## Configuration

Create `.env` file in skill directory for API keys:

```bash
# Social Media APIs
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
LINKEDIN_ACCESS_TOKEN=your_token

# Email (for digest delivery)
RESEND_API_KEY=your_resend_key
ALERT_EMAIL=clark@fedbuyout.com

# NewsAPI (optional, for additional sources)
NEWSAPI_KEY=your_key
```

## Automation

For continuous monitoring, set up cron job:

```bash
# Check for news every 2 hours
0 */2 * * * cd /root/.openclaw/workspace/skills/news-monitor && python3 scripts/fetch_news.py --check

# Weekly digest every Monday at 8 AM
0 8 * * 1 cd /root/.openclaw/workspace/skills/news-monitor && python3 scripts/weekly_digest.py
```

## Adding New Sources

To add a new RSS feed:

1. Add feed URL to `references/news-sources.md`
2. Update `scripts/fetch_news.py` feed list
3. Test: `python3 scripts/fetch_news.py --source <new-source>`

## Troubleshooting

### No articles found
- Check RSS feed URLs in `references/news-sources.md`
- Verify network connectivity
- Check feed is still active with `curl <feed-url>`

### Alerts not sending
- Verify `.env` file has correct API keys
- Check `data/alerts.json` for error logs
- Test with `python3 scripts/alert.py --test`

### Rate limiting
- RSS feeds: Add delays between requests (default: 2s)
- Social APIs: Respect rate limits in `scripts/share.py`
