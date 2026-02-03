#!/bin/bash
# manager.sh: Manage log-sentinel processes

ACTION="$1"
shift

BASE_DIR=$(dirname "$(realpath "$0")")
PID_DIR="/root/.openclaw/workspace/skills/log-sentinel/pids"
mkdir -p "$PID_DIR"

case "$ACTION" in
  start)
    LOG="$1"
    PATTERN="$2"
    TARGET="$3"
    if [ -z "$TARGET" ]; then 
        echo "Usage: manager.sh start <log_file> <pattern> <target_channel>"
        echo "Example: manager.sh start /var/log/syslog 'error|fail' +15550001234"
        exit 1
    fi
    
    # ID based on log path hash to handle multiple monitors
    ID=$(echo -n "$LOG" | md5sum | awk '{print $1}')
    
    if [ -f "$PID_DIR/$ID.pid" ]; then
        OLD_PID=$(cat "$PID_DIR/$ID.pid")
        if ps -p "$OLD_PID" > /dev/null; then
            echo "Monitor already running for $LOG (PID $OLD_PID)"
            exit 0
        fi
    fi

    # Run monitor in background
    nohup "$BASE_DIR/monitor.sh" "$LOG" "$PATTERN" "$TARGET" > /dev/null 2>&1 &
    PID=$!
    
    echo "$PID" > "$PID_DIR/$ID.pid"
    echo "$LOG" > "$PID_DIR/$ID.log"
    echo "$PATTERN" > "$PID_DIR/$ID.pattern"
    echo "Started monitor for $LOG (PID $PID)"
    ;;
  stop)
    LOG="$1"
    if [ -z "$LOG" ]; then echo "Usage: manager.sh stop <log_file>"; exit 1; fi
    
    ID=$(echo -n "$LOG" | md5sum | awk '{print $1}')
    
    if [ -f "$PID_DIR/$ID.pid" ]; then
        PID=$(cat "$PID_DIR/$ID.pid")
        # Kill the monitor process and its children (monitor spawns tail/grep pipe)
        # Using pkill -P might be safer if we knew the PGID, but simple kill usually works for shell scripts
        kill "$PID" 2>/dev/null
        rm -f "$PID_DIR/$ID.pid" "$PID_DIR/$ID.log" "$PID_DIR/$ID.pattern"
        echo "Stopped monitor for $LOG (PID $PID)"
    else
        echo "No monitor found for $LOG"
    fi
    ;;
  status)
    echo "Active Monitors:"
    count=0
    for f in "$PID_DIR"/*.pid; do
        if [ -e "$f" ]; then
            ID=$(basename "$f" .pid)
            PID=$(cat "$f")
            LOG=$(cat "$PID_DIR/$ID.log" 2>/dev/null)
            PATTERN=$(cat "$PID_DIR/$ID.pattern" 2>/dev/null)
            
            if ps -p "$PID" > /dev/null; then
                echo "  • [$PID] $LOG (Pattern: '$PATTERN')"
                count=$((count+1))
            else
                echo "  • [$PID] $LOG (Dead/Stale - Cleaning up)"
                rm -f "$PID_DIR/$ID.pid" "$PID_DIR/$ID.log" "$PID_DIR/$ID.pattern"
            fi
        fi
    done
    if [ "$count" -eq 0 ]; then
        echo "  (No active monitors)"
    fi
    ;;
  *)
    echo "Usage: $0 {start|stop|status} ..."
    exit 1
    ;;
esac
