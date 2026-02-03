#!/bin/bash
#
# Common utilities for session-manager
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Data directories
SESSION_DIR="${SESSION_DIR:-/tmp/openclaw/sessions}"
LOG_DIR="${LOG_DIR:-$HOME/.local/share/openclaw/session-logs}"
HISTORY_DB="${HISTORY_DB:-$HOME/.local/share/openclaw/session-history.db}"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.config/session-manager/config.json}"

# Initialize directories
init_dirs() {
    mkdir -p "$SESSION_DIR" "$LOG_DIR" "$(dirname "$HISTORY_DB")" "$(dirname "$CONFIG_FILE")" 2>/dev/null || true
}

# Help text
show_help() {
    cat << 'EOF'
Session Manager - Manage OpenClaw sessions and sub-agents

USAGE:
    session-manager <command> [options]

COMMANDS:
    list, ls              List active sessions
    status, st            Check session/sub-agent status
    history, hist         View session history
    spawn, new            Spawn a new sub-agent
    cleanup, clean        Remove completed/stale sessions
    resources, res, top   Show resource usage
    watch, monitor        Monitor long-running tasks
    kill, stop            Terminate a session
    info, details         Show detailed session info
    help                  Show this help message

EXAMPLES:
    session-manager list
    session-manager status <session-id>
    session-manager spawn "Analyze this data"
    session-manager cleanup --older 7d
    session-manager resources --watch

For more details on each command, use:
    session-manager <command> --help
EOF
}

# Log message with timestamp
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_DIR/session-manager.log" 2>/dev/null || true
}

# Print error and exit
error_exit() {
    echo -e "${RED}Error: $1${NC}" >&2
    log "ERROR" "$1"
    exit 1
}

# Print warning
warn() {
    echo -e "${YELLOW}Warning: $1${NC}" >&2
    log "WARN" "$1"
}

# Print info
info() {
    echo -e "${BLUE}$1${NC}"
}

# Print success
success() {
    echo -e "${GREEN}$1${NC}"
}

# Print debug (only if DEBUG is set)
debug() {
    [[ -n "${DEBUG:-}" ]] && echo -e "${GRAY}[DEBUG] $1${NC}" >&2
}

# Get session age in seconds
get_session_age() {
    local session_file="$1"
    if [[ -f "$session_file" ]]; then
        local mtime=$(stat -c %Y "$session_file" 2>/dev/null || stat -f %m "$session_file" 2>/dev/null)
        local now=$(date +%s)
        echo $((now - mtime))
    else
        echo "0"
    fi
}

# Format duration from seconds
format_duration() {
    local seconds="$1"
    if [[ $seconds -lt 60 ]]; then
        echo "${seconds}s"
    elif [[ $seconds -lt 3600 ]]; then
        echo "$((seconds / 60))m $((seconds % 60))s"
    else
        echo "$((seconds / 3600))h $(((seconds % 3600) / 60))m"
    fi
}

# Parse duration string (e.g., "1d", "2h", "30m") to seconds
parse_duration() {
    local duration="$1"
    local num=$(echo "$duration" | sed 's/[^0-9]//g')
    local unit=$(echo "$duration" | sed 's/[0-9]//g')
    
    case "$unit" in
        d|days) echo $((num * 86400)) ;;
        h|hours|hr) echo $((num * 3600)) ;;
        m|minutes|min) echo $((num * 60)) ;;
        s|seconds|sec) echo "$num" ;;
        *) echo "$num" ;; # Assume seconds if no unit
    esac
}

# Check if running in OpenClaw environment
is_openclaw_env() {
    [[ -n "${OPENCLAW_HOME:-}" ]] || [[ -d "$HOME/.openclaw" ]]
}

# Get current session ID (if any)
get_current_session() {
    echo "${OPENCLAW_SESSION_ID:-${SESSION_ID:-unknown}}"
}

# JSON escape string
json_escape() {
    local str="$1"
    printf '%s' "$str" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()), end="")' 2>/dev/null || \
    printf '%s' "$str" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\t/\\t/g; s/\n/\\n/g'
}

# Initialize on source
init_dirs
