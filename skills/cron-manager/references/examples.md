# Cron-Manager Examples

Common job patterns and real-world examples for the cron-manager skill.

## Basic Examples

### Daily Backup

```bash
python3 skills/cron-manager/scripts/add_job.py \
  --name "daily-backup" \
  --schedule "0 2 * * *" \
  --command "python3 scripts/backup.py --full" \
  --description "Full database backup at 2 AM" \
  --tags "backup,critical"
```

### Hourly Status Check

```bash
python3 skills/cron-manager/scripts/add_job.py \
  --name "status-check" \
  --schedule "0 * * * *" \
  --command "curl -s https://api.example.com/health" \
  --tags "monitoring"
```

### Weekly Report

```bash
python3 skills/cron-manager/scripts/add_job.py \
  --name "weekly-report" \
  --schedule "0 9 * * 1" \
  --command "python3 reports/weekly.py --email" \
  --description "Generate and email weekly report" \
  --category "reports"
```

## Using Natural Language

```bash
# Every 15 minutes
python3 skills/cron-manager/scripts/add_job.py \
  --name "sync-data" \
  --schedule "every 15 minutes" \
  --command "python3 sync.py"

# Daily at 9 AM
python3 skills/cron-manager/scripts/add_job.py \
  --name "morning-task" \
  --schedule "daily at 9am" \
  --command "python3 morning.py"

# Every Monday
python3 skills/cron-manager/scripts/add_job.py \
  --name "weekly-cleanup" \
  --schedule "every monday" \
  --command "python3 cleanup.py"
```

## Reminder Examples

### One-Time Reminder

```bash
python3 skills/cron-manager/scripts/add_reminder.py \
  --message "Team meeting starts in 5 minutes!" \
  --time "2026-02-03 14:25" \
  --channel whatsapp
```

### Relative Time Reminder

```bash
# In 30 minutes
python3 skills/cron-manager/scripts/add_reminder.py \
  --message "Check the oven!" \
  --time "+30m"

# In 2 hours
python3 skills/cron-manager/scripts/add_reminder.py \
  --message "Follow up with client" \
  --time "+2h"

# Tomorrow same time
python3 skills/cron-manager/scripts/add_reminder.py \
  --message "Project deadline reminder" \
  --time "+1d"
```

### Recurring Reminder

```bash
# Every hour
python3 skills/cron-manager/scripts/add_reminder.py \
  --message "Take a break and stretch" \
  --time "every hour" \
  --channel whatsapp
```

## Workflow Examples

### Update and Check Status

```bash
# Update a job schedule
python3 skills/cron-manager/scripts/update_job.py \
  --name "daily-backup" \
  --schedule "0 3 * * *"

# Check the update
python3 skills/cron-manager/scripts/list_jobs.py --name "daily-backup" --verbose

# Test the job
python3 skills/cron-manager/scripts/test_job.py --name "daily-backup"
```

### Disable Jobs for Maintenance

```bash
# Disable all production jobs
python3 skills/cron-manager/scripts/list_jobs.py --tag "production" --format json | \
  jq -r '.[].name' | \
  while read job; do
    python3 skills/cron-manager/scripts/disable_job.py --name "$job"
  done

# Re-enable after maintenance
python3 skills/cron-manager/scripts/enable_job.py --name "daily-backup"
```

### Health Check and Report

```bash
# Check all jobs
python3 skills/cron-manager/scripts/health_check.py

# Check only critical issues
python3 skills/cron-manager/scripts/health_check.py --critical-only

# View recent history
python3 skills/cron-manager/scripts/history.py --since "24h" --limit 20
```

## Integration Examples

### Skill-to-Skill Integration

From another skill, schedule a follow-up:

```bash
# In lead-tracker skill, schedule a reminder
python3 skills/cron-manager/scripts/add_reminder.py \
  --message "Follow up with lead #123" \
  --time "+2 days" \
  --related-to "lead-tracker:123"
```

### Logging Wrapper

Use `run_with_logging.py` for better job tracking:

```bash
python3 skills/cron-manager/scripts/run_with_logging.py \
  --job "data-import" \
  --command "python3 import.py --source production" \
  --timeout 600
```

## Complete Setup Example

```bash
#!/bin/bash
# setup-monitoring.sh

# Add system health check
cron-manager add-job \
  --name "health-check" \
  --schedule "*/15 * * * *" \
  --command "python3 skills/cron-manager/scripts/run_with_logging.py --job health-check --command 'curl -s http://localhost/health'" \
  --tags "monitoring,health"

# Add daily summary
cron-manager add-job \
  --name "daily-summary" \
  --schedule "0 8 * * *" \
  --command "python3 skills/cron-manager/scripts/digest.py --daily" \
  --tags "reporting"

# Set up reminder for weekly review
cron-manager add-reminder \
  --message "Time for weekly review!" \
  --time "fridays at 4pm" \
  --channel whatsapp

echo "Monitoring setup complete!"
```

## Best Practice Patterns

### Pattern 1: Staggered Jobs

Instead of scheduling all daily jobs at midnight:

```bash
# Database backup at 2 AM
0 2 * * * backup.py

# Log rotation at 3 AM
0 3 * * * rotate-logs.py

# Report generation at 4 AM
0 4 * * * reports.py
```

### Pattern 2: Error Handling

Always include error handling:

```bash
# Good
python3 script.py >> /var/log/job.log 2>&1 || echo "FAILED $(date)" >> /var/log/errors.log

# Better with cron-manager
python3 skills/cron-manager/scripts/run_with_logging.py --job my-job --command "python3 script.py"
```

### Pattern 3: Job Categories

Organize jobs with categories and tags:

```bash
# Production jobs
--tags "production,critical" --category "maintenance"

# Development jobs
--tags "development,test" --category "testing"

# Reporting jobs
--tags "reporting" --category "analytics"
```
