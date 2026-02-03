---
name: log-sentinel
description: Real-time log monitoring with regex pattern matching and message alerts.
tools:
  - name: log_monitor_start
    description: Start a background monitor for a log file.
    parameters:
      log_file: Path to the log file
      pattern: Regex pattern to match
      target: Alert recipient (phone/handle)
    command: /root/.openclaw/workspace/skills/log-sentinel/scripts/manager.sh start "${log_file}" "${pattern}" "${target}"
  - name: log_monitor_stop
    description: Stop monitoring a log file.
    parameters:
      log_file: Path to the log file
    command: /root/.openclaw/workspace/skills/log-sentinel/scripts/manager.sh stop "${log_file}"
  - name: log_monitor_list
    description: List active log monitors.
    command: /root/.openclaw/workspace/skills/log-sentinel/scripts/manager.sh status
  - name: log_rotate
    description: Rotate a log file (compress and keep backups).
    parameters:
      log_file: Path to the log file
      keep: Number of backups to keep (default 5)
    command: /root/.openclaw/workspace/skills/log-sentinel/scripts/rotate.sh "${log_file}" "${keep}"
---

# Log Sentinel

Monitor logs in real-time and get alerts via OpenClaw messages.

## Features
- **Real-time Tailing**: Uses `tail -F` to handle log rotation.
- **Regex Matching**: Supports full grep regex for error patterns.
- **Instant Alerts**: Sends messages via `openclaw message send` immediately upon match.
- **Log Rotation**: Utility to safely rotate and compress logs.

## Setup
Ensure the scripts are executable:
`chmod +x /root/.openclaw/workspace/skills/log-sentinel/scripts/*.sh`

## Examples

### Start Monitoring
Monitor `/var/log/syslog` for "error" and alert me:
`log_monitor_start --log_file "/var/log/syslog" --pattern "error|fail" --target "+15551234567"`

### Stop Monitoring
`log_monitor_stop --log_file "/var/log/syslog"`

### List Monitors
`log_monitor_list`

### Rotate Logs
Rotate the app log:
`log_rotate --log_file "/app/logs/server.log"`
