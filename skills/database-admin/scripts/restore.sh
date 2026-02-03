#!/bin/bash
# restore.sh - Restore PostgreSQL database from backup

set -e

DB_NAME=$1
BACKUP_FILE=$2

if [ -z "$DB_NAME" ] || [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 [database_name] [backup_file]"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "WARNING: This will overwrite the database '$DB_NAME'."
read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled."
    exit 1
fi

echo "Restoring $DB_NAME from $BACKUP_FILE..."

if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | psql "$DB_NAME"
else
    psql "$DB_NAME" < "$BACKUP_FILE"
fi

if [ $? -eq 0 ]; then
    echo "Restore complete."
else
    echo "Restore failed."
    exit 1
fi
