---
name: competitor-watcher
description: Track and analyze competitors for FedBuyOut business. Monitor competitor websites for changes, pricing updates, feature comparisons, and new competitor discovery. Use when: (1) Conducting competitive analysis, (2) Monitoring competitor pricing changes, (3) Tracking feature developments in the federal retirement/financial planning space, (4) Generating quarterly competitive reports, (5) Discovering new competitors, (6) Alerting on significant market changes.
---

# Competitor Watcher

Track competitors in the federal retirement and financial planning space for FedBuyOut.

## Overview

This skill provides tools and workflows for systematic competitive intelligence gathering. It monitors known competitors, discovers new entrants, tracks pricing changes, and generates analysis reports.

## Competitor Categories

**Primary Competitors:**
- Federal retirement calculators (FedCalc, etc.)
- Financial advisor sites targeting federal employees
- OPM resources and tools
- Federal benefits analysis platforms

**Secondary Competitors:**
- Generic retirement calculators
- Financial planning software
- Benefits consulting services

## Quick Start

1. **Monitor competitors:** Run `scripts/monitor.sh` to check all tracked competitors
2. **Add new competitor:** Update `references/competitor-list.json` and run `scripts/discover.sh`
3. **Generate report:** Run `scripts/generate-report.sh quarterly` for Q1, Q2, Q3, or Q4
4. **Check pricing:** Run `scripts/track-pricing.sh` to detect pricing changes

## Core Workflows

### Website Change Detection

Track competitor website changes using checksums:

```bash
# Check all competitors
./scripts/monitor.sh

# Check specific competitor
./scripts/monitor.sh fedcalc

# Force refresh (ignore cache)
./scripts/monitor.sh --force
```

See [references/monitoring-guide.md](references/monitoring-guide.md) for advanced configuration.

### Pricing Tracking

Monitor pricing page changes:

```bash
# Track all pricing pages
./scripts/track-pricing.sh

# Compare current vs last known prices
./scripts/track-pricing.sh --compare
```

### Feature Comparison

Update feature tracking matrix:

```bash
# Open feature comparison sheet
./scripts/compare-features.sh

# Generate feature gap analysis
./scripts/compare-features.sh --gap-analysis
```

### New Competitor Discovery

Search for new competitors:

```bash
# Run discovery scan
./scripts/discover.sh

# Review and approve candidates
./scripts/discover.sh --review
```

### Quarterly Report Generation

Generate comprehensive competitive analysis:

```bash
# Generate Q1 report (Jan-Mar)
./scripts/generate-report.sh q1

# Generate full year report
./scripts/generate-report.sh annual
```

## Alert Configuration

Configure alerts in `references/alerts.conf`:

- **High priority:** Pricing changes, new features, major site redesigns
- **Medium priority:** Content updates, blog posts, minor changes
- **Low priority:** Typos, small text changes

## Data Storage

All tracking data stored in:
- `references/competitor-list.json` - Master competitor registry
- `references/tracking-snapshots/` - Website snapshots over time
- `references/pricing-history.json` - Historical pricing data
- `references/feature-matrix.csv` - Feature comparison matrix

## Reference Files

Read these files for detailed information:

- **[competitor-list.json](references/competitor-list.json)** - All tracked competitors with URLs and metadata
- **[tracking-guide.md](references/tracking-guide.md)** - How monitoring works and configuration options
- **[report-templates/](references/report-templates/)** - Templates for quarterly reports
- **[alert-rules.md](references/alert-rules.md)** - When and how to alert on changes
