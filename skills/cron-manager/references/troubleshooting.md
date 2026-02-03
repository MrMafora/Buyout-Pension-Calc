# Troubleshooting Guide

Common issues and solutions for cron-manager.

## Jobs Not Running

### Check if Job is Enabled

```bash
python3 skills/cron-manager/scripts/list_jobs.py --name "my-job" --verbose
```

Look for `Status: enabled`. If disabled:

```bash
python3 skills/cron-manager/scripts/enable_job.py --name "my-job"
```

### Test Job Manually

```bash
python3 skills/cron-manager/scripts/test_job.py --name "my-job" --verbose
```

This runs the job immediately and shows output.

### Validate Cron Expression

```bash
python3 skills/cron-manager/scripts/cron_helper.py --validate "0 2 * * *"
```

### Check System Cron

List system crontab entries:

```bash
crontab -l
```

Check if the cron service is running:

```bash
# On Ubuntu/Debian
sudo systemctl status cron

# On RHEL/CentOS
sudo systemctl status crond
```

## Permission Denied

### Script Permissions

Make scripts executable:

```bash
chmod +x skills/cron-manager/scripts/*.py
```

### File Permissions

Ensure the cron-manager directory is writable:

```bash
mkdir -p ~/.openclaw/cron-manager
chmod 755 ~/.openclaw/cron-manager
```

## Path Issues

### Use Absolute Paths

Cron jobs run with a minimal PATH. Always use absolute paths:

```bash
# Bad
python3 script.py

# Good
/usr/bin/python3 /home/user/project/script.py
```

### Set PATH in Cron

Add at the top of crontab:

```
PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin
```

## Environment Variables

### Variables Not Available

Cron doesn't load shell profiles. Set variables explicitly:

```bash
# In the command
DB_HOST=localhost DB_USER=admin python3 script.py
```

### Python Environment

If using virtualenv, activate it:

```bash
# In crontab
* * * * * cd /path/to/project && source venv/bin/activate && python script.py
```

## Timezone Issues

### Check System Timezone

```bash
date
timedatectl
```

### Set Cron Timezone

Add to crontab:

```
TZ=America/New_York
```

Or use UTC consistently:

```
TZ=UTC
```

## Job Runs But No Output

### Redirect Output

Always capture output for debugging:

```bash
# Capture to file
python3 script.py >> /var/log/myjob.log 2>&1

# Or use the logging wrapper
python3 skills/cron-manager/scripts/run_with_logging.py --job my-job --command "python3 script.py"
```

### Check History

```bash
python3 skills/cron-manager/scripts/history.py --job "my-job" --verbose
```

## Debugging Steps

### Step 1: Verify Job Exists

```bash
python3 skills/cron-manager/scripts/list_jobs.py --name "my-job"
```

### Step 2: Test Command Manually

Run the exact command from the job:

```bash
bash -c "your-command-here"
```

### Step 3: Check Exit Code

```bash
your-command-here
echo "Exit code: $?"
```

### Step 4: Review History

```bash
python3 skills/cron-manager/scripts/history.py --job "my-job" --since "24h"
```

### Step 5: Run Diagnostics

```bash
python3 skills/cron-manager/scripts/diagnostics.py
```

## Common Error Messages

### "Job not found"

- Check spelling of job name
- Use `list_jobs.py` to see available jobs
- Job names are case-sensitive

### "Invalid schedule expression"

- Verify cron syntax with `cron_helper.py --validate`
- Check number of fields (must be 5)
- Try natural language format instead

### "Could not parse time"

For reminders, use supported formats:
- Absolute: `2026-02-03 14:30`
- Relative: `+30m`, `+2h`, `+1d`
- Time only: `14:30`

### "Timeout"

Job took too long. Increase timeout:

```bash
python3 skills/cron-manager/scripts/test_job.py --name "my-job" --timeout 600
```

## Performance Issues

### Too Many Jobs Running

Check for overlapping schedules:

```bash
python3 skills/cron-manager/scripts/list_jobs.py
```

Stagger start times:

```bash
# Instead of:
0 * * * * job1
0 * * * * job2
0 * * * * job3

# Use:
0 * * * * job1
5 * * * * job2
10 * * * * job3
```

### History Growing Too Large

History is automatically trimmed to 1000 entries. To clear manually:

```bash
rm ~/.openclaw/cron-manager/history.json
```

## Getting Help

### List All Commands

```bash
python3 skills/cron-manager/scripts/list_jobs.py --help
python3 skills/cron-manager/scripts/add_job.py --help
```

### Show Examples

```bash
python3 skills/cron-manager/scripts/cron_helper.py --examples
```

### Check Examples Reference

See [examples.md](examples.md) for common patterns.

## Advanced Debugging

### Enable Verbose Logging

Add to your scripts:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Run with Strace

```bash
strace -f -e trace=file python3 script.py 2>&1 | less
```

### Monitor Cron Logs

```bash
# Ubuntu/Debian
tail -f /var/log/syslog | grep CRON

# RHEL/CentOS
tail -f /var/log/cron
```
