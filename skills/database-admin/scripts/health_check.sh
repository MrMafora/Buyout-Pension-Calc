#!/bin/bash
# health_check.sh - Check DB connection

DB_NAME=$1

if [ -z "$DB_NAME" ]; then
    echo "Usage: $0 [database_name]"
    exit 1
fi

if psql "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    echo "Connection to $DB_NAME successful."
    psql "$DB_NAME" -c "SELECT version();"
    psql "$DB_NAME" -c "SELECT count(*) as active_connections FROM pg_stat_activity;"
else
    echo "Connection to $DB_NAME failed."
    exit 1
fi
