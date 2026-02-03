#!/bin/bash
# backup.sh - Backup PostgreSQL database with rotation

set -e

DB_NAME=$1
RETENTION_DAYS=${2:-7}
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

if [ -z "$DB_NAME" ]; then
    echo "Usage: $0 [database_name] [retention_days]"
    exit 1
fi

mkdir -p "$BACKUP_DIR"

FILENAME="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

echo "Starting backup for $DB_NAME..."
pg_dump "$DB_NAME" | gzip > "$FILENAME"

if [ $? -eq 0 ]; then
    echo "Backup created successfully: $FILENAME"
else
    echo "Backup failed!"
    rm -f "$FILENAME"
    exit 1
fi

# Cleanup old backups
echo "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "Cleanup complete."
