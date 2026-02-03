---
name: health-checker
description: Monitor OpenClaw system health including disk space, memory, services, and network connectivity
author: OpenClaw
version: 1.0.0
tags: [monitoring, health, system, maintenance]
---

# health-checker

Monitor OpenClaw system health including disk space, memory, services, logs, and network connectivity. Provides alerts when issues are detected.

## Overview

This skill provides comprehensive system health monitoring for OpenClaw installations. It checks:

- **Disk Space** - Monitor available storage and warn on low space
- **Memory Usage** - Check RAM utilization
- **Service Status** - Verify gateway, WhatsApp, and other services are running
- **Log Files** - Monitor log sizes to prevent disk bloat
- **Temp Files** - Clean up temporary files
- **Network** - Test connectivity to essential services
- **System Report** - Generate overall health status

## Configuration

Set thresholds in `config/health-checker.json`:

```json
{
  "disk": {
    "warning_percent": 80,
    "critical_percent": 90
  },
  "memory": {
    "warning_percent": 85,
    "critical_percent": 95
  },
  "logs": {
    "max_size_mb": 100,
    "max_age_days": 7
  },
  "temp": {
    "max_age_hours": 24,
    "cleanup_enabled": true
  },
  "services": ["openclaw-gateway", "openclaw-whatsapp"],
  "network": {
    "ping_targets": ["8.8.8.8", "1.1.1.1"],
    "timeout_seconds": 5
  }
}
```

## Tools

### health-checker/check

Run a comprehensive health check and report issues.

**Usage:**
```bash
# Check everything
openclaw skills health-checker check

# Check specific component
openclaw skills health-checker check --component disk
openclaw skills health-checker check --component memory
openclaw skills health-checker check --component services
openclaw skills health-checker check --component logs
openclaw skills health-checker check --component network

# Auto-fix issues where possible
openclaw skills health-checker check --fix
```

### health-checker/cleanup

Clean temporary files and old logs.

**Usage:**
```bash
# Dry run (show what would be cleaned)
openclaw skills health-checker cleanup --dry-run

# Clean temporary files
openclaw skills health-checker cleanup --temp

# Clean old logs
openclaw skills health-checker cleanup --logs

# Clean everything
openclaw skills health-checker cleanup --all
```

### health-checker/report

Generate a system health report.

**Usage:**
```bash
# Generate report
openclaw skills health-checker report

# Save report to file
openclaw skills health-checker report --output health-report.json

# Include detailed metrics
openclaw skills health-checker report --verbose
```

### health-checker/watch

Continuous monitoring with alerts.

**Usage:**
```bash
# Watch mode (check every 5 minutes)
openclaw skills health-checker watch

# Custom interval (minutes)
openclaw skills health-checker watch --interval 10

# Alert on issues only
openclaw skills health-checker watch --alert-only
```

## Script Usage

Direct script execution for automation:

```bash
# Run all checks
./skills/health-checker/scripts/check.sh

# Check disk only
./skills/health-checker/scripts/check.sh --disk

# Check with auto-cleanup
./skills/health-checker/scripts/check.sh --fix

# Generate report
./skills/health-checker/scripts/report.sh

# Cleanup temp files
./skills/health-checker/scripts/cleanup.sh --temp
```

## Health Status Levels

- **OK** - All systems normal
- **WARNING** - Attention needed soon
- **CRITICAL** - Immediate action required

## Integration

Use in heartbeat or cron for automated monitoring:

```bash
# Add to crontab for hourly checks
0 * * * * /root/.openclaw/workspace/skills/health-checker/scripts/check.sh --quiet || notify-send "OpenClaw Health Alert"
```

## Alerts

The skill will output alerts when:

- Disk usage exceeds warning/critical thresholds
- Memory usage is high
- Services are not running
- Log files are too large
- Network connectivity fails

## Files

- `scripts/check.sh` - Main health check script
- `scripts/cleanup.sh` - Cleanup utility
- `scripts/report.sh` - Report generator
- `scripts/watch.sh` - Continuous monitoring
- `config/health-checker.json` - Configuration (user-created)

## Requirements

- bash
- df, free, ps, ping (standard Unix utilities)
- bc (for calculations)

## License

MIT - Part of OpenClaw
