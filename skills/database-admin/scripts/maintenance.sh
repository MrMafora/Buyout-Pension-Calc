#!/bin/bash
# maintenance.sh - Vacuum and Analyze tables

DB_NAME=$1
MODE=${2:-analyze}

if [ -z "$DB_NAME" ]; then
    echo "Usage: $0 [database_name] [full|analyze]"
    exit 1
fi

if [ "$MODE" == "full" ]; then
    echo "Running VACUUM FULL on $DB_NAME..."
    psql "$DB_NAME" -c "VACUUM FULL;"
elif [ "$MODE" == "analyze" ]; then
    echo "Running VACUUM ANALYZE on $DB_NAME..."
    psql "$DB_NAME" -c "VACUUM ANALYZE;"
else
    echo "Invalid mode. Use 'full' or 'analyze'."
    exit 1
fi
