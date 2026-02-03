#!/bin/bash
# monitor_queries.sh - List or kill active queries

ACTION=$1
DURATION=${2:-"5 minutes"} # Default threshold for 'kill' check

if [ -z "$ACTION" ]; then
    echo "Usage: $0 [list|kill] [duration_threshold]"
    exit 1
fi

if [ "$ACTION" == "list" ]; then
    psql -c "SELECT pid, now() - query_start AS duration, usename, query FROM pg_stat_activity WHERE state != 'idle' ORDER BY duration DESC;"
elif [ "$ACTION" == "kill" ]; then
    echo "Killing queries running longer than $DURATION..."
    psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state != 'idle' AND now() - query_start > interval '$DURATION' AND pid <> pg_backend_pid();"
else
    echo "Invalid action. Use 'list' or 'kill'."
    exit 1
fi
