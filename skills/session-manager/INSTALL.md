# Session Manager Installation

## Quick Setup

Add to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
# Session Manager
export PATH="/root/.openclaw/workspace/skills/session-manager/scripts:$PATH"
alias sm="session-manager.sh"
```

## Commands

- `session-manager.sh list` - List active sessions
- `session-manager.sh status <id>` - Check session status
- `session-manager.sh spawn "task"` - Create sub-agent
- `session-manager.sh cleanup` - Remove completed sessions
- `session-manager.sh resources` - Show resource usage
- `session-manager.sh watch` - Monitor long-running tasks
- `session-manager.sh kill <id>` - Terminate session
- `session-manager.sh info <id>` - Show detailed info
- `session-manager.sh history` - View session history

## Short Aliases

Once installed:
- `sm list` or `sm ls`
- `sm status` or `sm st`
- `sm spawn` or `sm new`
- `sm cleanup` or `sm clean`
- `sm resources` or `sm top`
- `sm watch` or `sm monitor`

## Configuration

Create config at `~/.config/session-manager/config.json`:

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
  }
}
```
