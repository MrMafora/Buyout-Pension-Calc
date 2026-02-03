# Competitor Monitoring Guide

This guide explains how the competitor monitoring system works and how to configure it.

## How Monitoring Works

### Website Change Detection

The `monitor.sh` script uses MD5 checksums to detect changes:

1. Fetches the competitor's website HTML
2. Calculates an MD5 checksum of the content
3. Compares to the last known checksum
4. If different, saves a snapshot and logs the change

### Snapshot Storage

Snapshots are stored in `references/tracking-snapshots/` with naming:
- `{competitor-id}_{timestamp}.html` - Full HTML snapshot
- `{competitor-id}_state.json` - Current checksum and timestamp

### Change Logging

All changes are logged to `references/tracking-snapshots/changes.log`:
```
2026-02-03T12:00:00+00:00 | CHANGE | fedcalc-pro | FedCalc Pro | https://fedcalcpro.com
```

## Configuration

### Adding a New Competitor

Edit `competitor-list.json` and add an entry:

```json
{
  "id": "unique-id",
  "name": "Competitor Name",
  "url": "https://example.com",
  "priority": "high",
  "category": "calculator",
  "track_pricing": true,
  "pricing_url": "https://example.com/pricing",
  "date_added": "2026-02-03T00:00:00Z",
  "notes": "Brief description"
}
```

**Priority Levels:**
- `high` - Direct competitors, checked frequently
- `medium` - Related competitors, checked regularly
- `low` - Peripheral competitors, checked occasionally

**Categories:**
- `calculator` - Retirement/benefits calculators
- `advisor` - Financial advisory services
- `tool` - Planning tools and software
- `resource` - Educational/reference sites

### Configuring Alerts

Create `references/alerts.conf`:

```bash
# Alert configuration
HIGH_PRIORITY_ALERT_EMAIL=clark@fedbuyout.com
ALERT_ON_PRICING_CHANGE=true
ALERT_ON_FEATURE_LAUNCH=true
ALERT_ON_SITE_REDESIGN=true

# Thresholds
MIN_CHANGE_AGE_HOURS=24
PRICE_CHANGE_THRESHOLD_PERCENT=5
```

## Advanced Usage

### Diff Between Snapshots

To see what changed between two snapshots:

```bash
diff snapshots/fedcalc-pro_20260101_120000.html snapshots/fedcalc-pro_20260201_120000.html
```

### Manual Snapshot

To force a new snapshot without comparing:

```bash
./scripts/monitor.sh fedcalc-pro --force
```

### Bulk Operations

Check all high-priority competitors only:

```bash
jq -r '.competitors[] | select(.priority == "high") | .id' references/competitor-list.json | \
  xargs -I {} ./scripts/monitor.sh {}
```

## Automation

### Recommended Schedule

- **High priority:** Daily
- **Medium priority:** Weekly
- **Low priority:** Monthly
- **Pricing checks:** Weekly
- **Full reports:** Quarterly

### Cron Example

```bash
# Daily high-priority check at 9 AM
0 9 * * * cd /root/.openclaw/workspace/skills/competitor-watcher && \
  jq -r '.competitors[] | select(.priority == "high") | .id' references/competitor-list.json | \
  xargs -I {} ./scripts/monitor.sh {} >> logs/monitor.log 2>&1

# Weekly pricing check
0 10 * * 1 cd /root/.openclaw/workspace/skills/competitor-watcher && \
  ./scripts/track-pricing.sh >> logs/pricing.log 2>&1

# Quarterly report
0 9 1 1,4,7,10 * cd /root/.openclaw/workspace/skills/competitor-watcher && \
  ./scripts/generate-report.sh quarterly >> logs/reports.log 2>&1
```

## Troubleshooting

### Common Issues

**Script fails to fetch website:**
- Check URL is correct in competitor-list.json
- Verify website is accessible: `curl -I https://example.com`
- Some sites block automated requests - may need User-Agent header

**False positive changes:**
- Some sites have dynamic content (ads, timestamps)
- Consider using more specific selectors
- Use `--force` to reset baseline

**Permission denied:**
- Make scripts executable: `chmod +x scripts/*.sh`
- Check directory permissions

### Debug Mode

Run scripts with debug output:

```bash
bash -x ./scripts/monitor.sh fedcalc-pro
```

## Data Retention

Consider implementing a cleanup policy:

```bash
# Keep only last 30 days of snapshots
find references/tracking-snapshots/ -name "*.html" -mtime +30 -delete

# Archive old reports
tar -czf reports/archive-$(date +%Y%m).tar.gz reports/*.md --remove-files
```
