---
name: session-manager
version: 1.0.0
description: Manage OpenClaw sessions and sub-agents - track, monitor, and control active sessions
author: OpenClaw
entry_point: scripts/session-manager.sh
---

# Session Manager

A comprehensive tool for managing OpenClaw sessions and sub-agents.

## Features

- **List Active Sessions**: View all currently running sessions
- **Check Sub-Agent Status**: Monitor progress and health of sub-agents
- **View Session History**: Access historical session data
- **Spawn Sub-Agents**: Create new sub-agents with proper labels and context
- **Cleanup Completed Sessions**: Remove finished sessions and free resources
- **Monitor Long-Running Tasks**: Track tasks that run for extended periods
- **Resource Usage Tracking**: Monitor CPU, memory, and other resources per session

## Usage

### List Active Sessions
```bash
session-manager list                    # List all active sessions
session-manager list --json            # Output as JSON
session-manager list --subagents       # List only sub-agents
```

### Check Sub-Agent Status
```bash
session-manager status <session-id>     # Check specific session status
session-manager status --all           # Check all sub-agents
session-manager status --watch         # Continuous monitoring
```

### View Session History
```bash
session-manager history                 # Show recent session history
session-manager history --limit 50     # Show last 50 sessions
session-manager history --since 1d     # Show sessions from last day
```

### Spawn Sub-Agents
```bash
session-manager spawn "task description"                    # Spawn basic sub-agent
session-manager spawn "task" --label "cleanup-task"        # With custom label
session-manager spawn "task" --parent <session-id>         # With parent session
session-manager spawn "task" --timeout 3600               # With timeout
```

### Cleanup Sessions
```bash
session-manager cleanup                 # Remove completed sessions
session-manager cleanup --force        # Force cleanup of stuck sessions
session-manager cleanup --older 7d     # Remove sessions older than 7 days
```

### Monitor Resources
```bash
session-manager resources               # Show resource usage
session-manager resources --session <id> # Specific session resources
session-manager top                    # Real-time resource monitor
```

### Monitor Long-Running Tasks
```bash
session-manager watch                   # Watch all long-running tasks
session-manager watch --alert 3600     # Alert on tasks > 1 hour
```

## Configuration

Create `~/.config/session-manager/config.json`:

```json
{
  "cleanup_policy": {
    "auto_cleanup": true,
    "keep_completed_for": "24h",
    "max_sessions": 100
  },
  "monitoring": {
    "enabled": true,
    "interval_seconds": 30,
    "alert_threshold_minutes": 60
  },
  "resources": {
    "track_cpu": true,
    "track_memory": true,
    "track_disk": false
  }
}
```

## Data Storage

Session data is stored in:
- Active sessions: `/tmp/openclaw/sessions/`
- Session logs: `~/.local/share/openclaw/session-logs/`
- History database: `~/.local/share/openclaw/session-history.db`

## Integration

This skill integrates with OpenClaw's process management and can be used within
other skills to spawn and manage sub-agents programmatically.
