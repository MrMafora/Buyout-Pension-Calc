#!/bin/bash
# monitor.sh: Monitor a log file for patterns and alert via OpenClaw
# Usage: ./monitor.sh <log_file> <pattern> <alert_target>

LOG_FILE="$1"
PATTERN="$2"
TARGET="$3"

if [ -z "$LOG_FILE" ] || [ -z "$PATTERN" ] || [ -z "$TARGET" ]; then
    echo "Usage: $0 <log_file> <pattern> <alert_target>"
    exit 1
fi

if [ ! -f "$LOG_FILE" ]; then
    # Create file if it doesn't exist so tail doesn't fail immediately,
    # though tail -F handles missing files, it's safer to ensure dir exists.
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
fi

# Store PID for management (naively using the log filename to name the pid file)
PID_FILE="/tmp/log-sentinel-$(basename "$LOG_FILE").pid"
echo $$ > "$PID_FILE"

echo "Starting monitor on $LOG_FILE for pattern '$PATTERN' notifying $TARGET"

# Use stdbuf to unbuffer the pipe if needed, but grep --line-buffered should suffice.
tail -F -n 0 "$LOG_FILE" | grep --line-buffered -E "$PATTERN" | while read -r line ; do
    # Notify
    openclaw message send --target "$TARGET" --message "🚨 **Log Sentinel Alert** 🚨

**File:** $LOG_FILE
**Pattern:** $PATTERN
**Match:** $line" >> /tmp/log-sentinel.log 2>&1
done
