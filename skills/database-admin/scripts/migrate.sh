#!/bin/bash
# migrate.sh - Run SQL migrations safely

set -e

DB_NAME=$1
MIGRATION_FILE=$2

if [ -z "$DB_NAME" ] || [ -z "$MIGRATION_FILE" ]; then
    echo "Usage: $0 [database_name] [migration_file]"
    exit 1
fi

if [ ! -f "$MIGRATION_FILE" ]; then
    echo "Error: Migration file not found: $MIGRATION_FILE"
    exit 1
fi

echo "Running migration $MIGRATION_FILE on $DB_NAME..."

# Wrap in a transaction
psql "$DB_NAME" <<EOF
BEGIN;
\i $MIGRATION_FILE
COMMIT;
EOF

if [ $? -eq 0 ]; then
    echo "Migration successful."
else
    echo "Migration failed (rolled back)."
    exit 1
fi
