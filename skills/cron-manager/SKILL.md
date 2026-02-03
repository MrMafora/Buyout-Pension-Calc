---
name: cron-manager
description: Manage OpenClaw scheduled jobs, cron tasks, and reminders. Use when creating, updating, listing, or removing scheduled tasks, setting one-time reminders, managing heartbeat tasks, checking job history, or understanding cron syntax. Provides comprehensive tools for task scheduling and automation management within OpenClaw.
---

# Cron Manager for OpenClaw

A comprehensive skill for managing scheduled jobs, cron tasks, reminders, and automation within the OpenClaw environment.

## Quick Start

### List All Cron Jobs

```bash
python3 skills/cron-manager/scripts/list_jobs.py
```

### Add a New Scheduled Task

```bash
python3 skills/cron-manager/scripts/add_job.py \
  --name "daily-backup" \
  --schedule "0 2 * * *" \
  --command "python3 backup.py" \
  --description "Daily database backup at 2 AM"
```

### Set a One-Time Reminder

```bash
python3 skills/cron-manager/scripts/add_reminder.py \
  --message "Team meeting in 15 minutes" \
  --time "2026-02-03 14:20" \
  --channel whatsapp
```

### Check Job History

```bash
python3 skills/cron-manager/scripts/history.py --job "daily-backup"
```

## Core Features

### 1. Cron Job Management

#### List All Jobs

View all scheduled cron jobs with details:

```bash
# List all jobs (table format)
python3 skills/cron-manager/scripts/list_jobs.py

# List with full details
python3 skills/cron-manager/scripts/list_jobs.py --verbose

# List only OpenClaw-managed jobs
python3 skills/cron-manager/scripts/list_jobs.py --openclaw-only

# Export to JSON
python3 skills/cron-manager/scripts/list_jobs.py --format json
```

#### Add New Jobs

Create scheduled tasks with flexible options:

```bash
# Basic cron job
python3 skills/cron-manager/scripts/add_job.py \
  --name "hourly-sync" \
  --schedule "0 * * * *" \
  --command "python3 sync.py"

# With description and tags
python3 skills/cron-manager/scripts/add_job.py \
  --name "weekly-report" \
  --schedule "0 9 * * 1" \
  --command "python3 reports/weekly.py" \
  --description "Generate weekly analytics report" \
  --tags "analytics,reports" \
  --enabled

# Using natural language schedule
python3 skills/cron-manager/scripts/add_job.py \
  --name "daily-cleanup" \
  --schedule "every day at 3am" \
  --command "python3 cleanup.py"
```

**Supported Schedule Formats:**
- Standard cron: `0 2 * * *` (minute hour day month weekday)
- Natural language: `every hour`, `daily at 9am`, `mondays at 10am`
- Special keywords: `@reboot`, `@yearly`, `@monthly`, `@weekly`, `@daily`, `@hourly`

#### Update Existing Jobs

Modify scheduled tasks:

```bash
# Update schedule
python3 skills/cron-manager/scripts/update_job.py \
  --name "daily-backup" \
  --schedule "0 3 * * *"

# Update command
python3 skills/cron-manager/scripts/update_job.py \
  --name "daily-backup" \
  --command "python3 backup.py --full"

# Enable/disable job
python3 skills/cron-manager/scripts/update_job.py \
  --name "daily-backup" \
  --enabled false

# Add tags
python3 skills/cron-manager/scripts/update_job.py \
  --name "daily-backup" \
  --add-tags "critical,production"
```

#### Remove/Disable Jobs

```bash
# Disable (keep but don't run)
python3 skills/cron-manager/scripts/disable_job.py --name "daily-backup"

# Enable a disabled job
python3 skills/cron-manager/scripts/enable_job.py --name "daily-backup"

# Remove completely
python3 skills/cron-manager/scripts/remove_job.py --name "daily-backup"

# Remove with confirmation prompt
python3 skills/cron-manager/scripts/remove_job.py --name "daily-backup" --confirm
```

### 2. One-Time Reminders

Set reminders that trigger once at a specific time:

```bash
# Basic reminder (console notification)
python3 skills/cron-manager/scripts/add_reminder.py \
  --message "Call John about the proposal" \
  --time "2026-02-03 15:00"

# Send to specific channel
python3 skills/cron-manager/scripts/add_reminder.py \
  --message "Meeting starts in 10 minutes!" \
  --time "2026-02-03 14:50" \
  --channel whatsapp \
  --target "+1234567890"

# Recurring reminder
python3 skills/cron-manager/scripts/add_reminder.py \
  --message "Take a break and stretch" \
  --time "every 2 hours"

# List active reminders
python3 skills/cron-manager/scripts/list_reminders.py

# Cancel a reminder
python3 skills/cron-manager/scripts/cancel_reminder.py --id "reminder-123"
```

### 3. Job Run History

Track and review job execution:

```bash
# View all history
python3 skills/cron-manager/scripts/history.py

# History for specific job
python3 skills/cron-manager/scripts/history.py --job "daily-backup"

# History for last 24 hours
python3 skills/cron-manager/scripts/history.py --since "24h"

# Failed jobs only
python3 skills/cron-manager/scripts/history.py --status failed

# Export history
python3 skills/cron-manager/scripts/history.py --export --format csv
```

### 4. Heartbeat Task Management

Manage OpenClaw heartbeat-driven tasks:

```bash
# List all heartbeat tasks defined in HEARTBEAT.md
python3 skills/cron-manager/scripts/heartbeat_tasks.py --list

# Check heartbeat status
python3 skills/cron-manager/scripts/heartbeat_tasks.py --status

# Add heartbeat task
python3 skills/cron-manager/scripts/heartbeat_tasks.py \
  --add "check-emails" \
  --description "Check for urgent emails" \
  --frequency "30m"

# Disable heartbeat task temporarily
python3 skills/cron-manager/scripts/heartbeat_tasks.py \
  --disable "check-emails"
```

### 5. Schedule Syntax Helper

Understand and validate cron expressions:

```bash
# Explain a cron expression
python3 skills/cron-manager/scripts/cron_helper.py --explain "0 2 * * *"

# Validate syntax
python3 skills/cron-manager/scripts/cron_helper.py --validate "0 2 * * *"

# Get next run times
python3 skills/cron-manager/scripts/cron_helper.py \
  --schedule "0 9 * * 1" \
  --next 5

# Convert natural language to cron
python3 skills/cron-manager/scripts/cron_helper.py \
  --parse "every Monday at 9am"

# Show common patterns
python3 skills/cron-manager/scripts/cron_helper.py --examples
```

**Common Cron Patterns:**

| Pattern | Description |
|---------|-------------|
| `* * * * *` | Every minute |
| `0 * * * *` | Every hour |
| `0 0 * * *` | Daily at midnight |
| `0 9 * * 1` | Every Monday at 9 AM |
| `0 0 1 * *` | First day of every month |
| `*/15 * * * *` | Every 15 minutes |
| `0 9-17 * * 1-5` | Every hour 9-5 on weekdays |

### 6. Job Categories & Organization

Organize jobs with tags and categories:

```bash
# List jobs by tag
python3 skills/cron-manager/scripts/list_jobs.py --tag "production"

# List jobs by category
python3 skills/cron-manager/scripts/list_jobs.py --category "maintenance"

# Bulk update tags
python3 skills/cron-manager/scripts/update_job.py \
  --tag "production" \
  --add-tags "critical"
```

## Configuration

### Job Storage

Jobs are stored in JSON format:

```bash
~/.openclaw/cron-manager/
├── jobs.json           # All scheduled jobs
├── reminders.json      # Active reminders
├── history.json        # Execution history
└── config.json         # Skill configuration
```

### Environment Variables

```bash
# Default notification channel
export OPENCLAW_CRON_CHANNEL="whatsapp"

# Default notification target
export OPENCLAW_CRON_TARGET="default"

# History retention (days)
export OPENCLAW_CRON_HISTORY_DAYS="30"

# Timezone for schedules
export OPENCLAW_CRON_TZ="UTC"
```

## Best Practices

### 1. Naming Conventions

Use descriptive, consistent names:
- `env-task-frequency` format: `prod-backup-daily`, `dev-cleanup-hourly`
- Include purpose: `email-sync`, `report-weekly`
- Use kebab-case (lowercase with hyphens)

### 2. Schedule Design

- **Stagger jobs**: Don't start all jobs at :00, spread across the hour
- **Avoid peak times**: Schedule heavy tasks during low-usage periods
- **Consider dependencies**: Ensure Job A completes before Job B starts
- **Use appropriate frequency**: Don't run every minute if hourly suffices

### 3. Error Handling

Always include error handling in job commands:

```bash
# Good: Logs errors and exits cleanly
python3 script.py >> /var/log/script.log 2>&1 || echo "Failed at $(date)" >> /var/log/errors.log

# Better: Use the wrapper
python3 skills/cron-manager/scripts/run_with_logging.py \
  --job "my-task" \
  --command "python3 script.py"
```

### 4. Monitoring

Set up monitoring for critical jobs:

```bash
# Check job health
python3 skills/cron-manager/scripts/health_check.py --critical-only

# Get daily digest
python3 skills/cron-manager/scripts/digest.py --daily

# Alert on failures
python3 skills/cron-manager/scripts/alert_config.py \
  --on-failure "daily-backup" \
  --channel whatsapp \
  --target "admin"
```

## Integration with OpenClaw

### Using with Skills

Reference cron-manager from other skills:

```bash
# From another skill, schedule a follow-up
python3 skills/cron-manager/scripts/add_reminder.py \
  --message "Follow up on lead" \
  --time "+2 days" \
  --related-to "lead-tracker:123"
```

### HEARTBEAT.md Integration

For tasks that should run periodically but don't need exact timing:

1. Add task to `HEARTBEAT.md`:
```markdown
- [ ] Check email inbox (every 30m)
- [ ] Review calendar events (every 1h)
```

2. Use heartbeat_tasks.py to track:
```bash
python3 skills/cron-manager/scripts/heartbeat_tasks.py --sync
```

### Cron vs Heartbeat: When to Use Each

| Use Cron When | Use Heartbeat When |
|--------------|-------------------|
| Exact timing matters | Approximate timing is fine |
| Task runs independently | Task needs session context |
| Output goes to channel directly | Task benefits from recent chat history |
| Precise schedule (9:00 AM daily) | Flexible schedule (every ~30 min) |
| One-shot reminders | Continuous monitoring |

## Troubleshooting

### Jobs Not Running

```bash
# Check if job is enabled
python3 skills/cron-manager/scripts/list_jobs.py --name "my-job"

# Verify cron service status
python3 skills/cron-manager/scripts/diagnostics.py --check-cron

# Test job manually
python3 skills/cron-manager/scripts/test_job.py --name "my-job"
```

### Debug Job Output

```bash
# Run job with verbose output
python3 skills/cron-manager/scripts/test_job.py \
  --name "my-job" \
  --verbose \
  --capture-output
```

### Common Issues

1. **Permission denied**: Ensure scripts have execute permissions
2. **Path issues**: Use absolute paths or set PATH in cron
3. **Environment variables**: Cron doesn't load shell profiles
4. **Timezone issues**: Check system timezone matches expected schedule

## Scripts Reference

### Core Management
- `list_jobs.py` - List all scheduled jobs
- `add_job.py` - Add new scheduled job
- `update_job.py` - Update existing job
- `remove_job.py` - Remove a job
- `enable_job.py` / `disable_job.py` - Toggle job status

### Reminders
- `add_reminder.py` - Set one-time or recurring reminders
- `list_reminders.py` - View active reminders
- `cancel_reminder.py` - Cancel a reminder

### History & Monitoring
- `history.py` - View job execution history
- `health_check.py` - Check job health status
- `digest.py` - Generate summary reports
- `diagnostics.py` - Troubleshooting tool

### Utilities
- `cron_helper.py` - Cron syntax helper and validator
- `heartbeat_tasks.py` - Manage heartbeat-driven tasks
- `test_job.py` - Test jobs manually
- `run_with_logging.py` - Wrapper for better logging

## Resources

- [references/cron-cheatsheet.md](references/cron-cheatsheet.md) - Quick reference for cron syntax
- [references/examples.md](references/examples.md) - Common job patterns and examples
- [references/troubleshooting.md](references/troubleshooting.md) - Detailed troubleshooting guide
