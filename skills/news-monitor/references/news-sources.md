# News Sources

Monitored RSS feeds and news sources for federal buyout news.

## Primary Sources

### FedSmith
- **URL**: https://www.fedsmith.com/feed/
- **Type**: RSS 2.0
- **Focus**: Federal employee news, benefits, retirement
- **Update frequency**: Daily
- **Priority**: High

### Government Executive (GovExec)
- **URL**: https://www.govexec.com/rss/all-news.xml
- **Type**: RSS 2.0
- **Focus**: Federal management, workforce, policy
- **Update frequency**: Multiple times daily
- **Priority**: High

### Federal News Network
- **URL**: https://federalnewsnetwork.com/feed/
- **Type**: RSS 2.0
- **Focus**: Federal news, workforce, technology
- **Update frequency**: Hourly
- **Priority**: High

### Federal Times
- **URL**: https://www.federaltimes.com/arc/outboundfeeds/rss/?outputType=xml
- **Type**: RSS 2.0
- **Focus**: Federal employee news, pay, benefits
- **Update frequency**: Daily
- **Priority**: High

### Federal Soup
- **URL**: https://www.federalsoup.com/rss/news
- **Type**: RSS 2.0
- **Focus**: Federal employee community news
- **Update frequency**: Daily
- **Priority**: Medium

## Secondary Sources

### Washington Post - Federal
- **URL**: https://feeds.washingtonpost.com/rss/rss_election-2012
- **Type**: RSS 2.0
- **Focus**: Federal government news
- **Update frequency**: Daily
- **Priority**: Medium

### Politico - Labor & Employment
- **URL**: https://www.politico.com/rss/labor-and-employment.xml
- **Type**: RSS 2.0
- **Focus**: Labor policy, federal workforce
- **Update frequency**: Daily
- **Priority**: Medium

### Federal Register
- **URL**: https://www.federalregister.gov/documents/search.rss
- **Type**: RSS 2.0
- **Focus**: Official federal notices, regulations
- **Update frequency**: Real-time
- **Priority**: Medium

### USA Today - Government News
- **URL**: https://rssfeeds.usatoday.com/usatodaycomwashington-topstories
- **Type**: RSS 2.0
- **Focus**: Government news
- **Update frequency**: Daily
- **Priority**: Low

## Government Agency Sources

### OPM (Office of Personnel Management)
- **URL**: https://www.opm.gov/news/releases/rss/releases.xml
- **Type**: RSS 2.0
- **Focus**: Personnel policy, retirement, benefits
- **Update frequency**: As needed
- **Priority**: High

### OMB (Office of Management and Budget)
- **URL**: https://www.whitehouse.gov/omb/news/feed/
- **Type**: RSS 2.0
- **Focus**: Budget, workforce management
- **Update frequency**: Weekly
- **Priority**: Medium

## News Aggregators

### Google News - Federal Buyout
- **Search**: "federal buyout" OR "VSIP" OR "voluntary separation"
- **Type**: Aggregated
- **Priority**: Medium

## Feed Reliability Notes

| Source | Uptime | Notes |
|--------|--------|-------|
| FedSmith | 99% | Very reliable |
| GovExec | 98% | Occasionally rate limits |
| Federal News Network | 99% | Reliable, good metadata |
| Federal Times | 95% | Sometimes slow to update |
| OPM | 90% | Government site, can be slow |

## Adding New Feeds

When adding new sources:

1. Verify feed is valid RSS/Atom
2. Test with `curl <feed-url>`
3. Add to fetch_news.py FEEDS dictionary
4. Update this file with source details
5. Set appropriate priority level
