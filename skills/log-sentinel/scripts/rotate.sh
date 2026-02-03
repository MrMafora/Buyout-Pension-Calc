#!/bin/bash
# rotate.sh: Rotate a log file
# Usage: ./rotate.sh <log_file> [keep_count]

LOG_FILE="$1"
KEEP="${2:-5}"

if [ -z "$LOG_FILE" ]; then
    echo "Usage: $0 <log_file> [keep_count]"
    exit 1
fi

if [ ! -f "$LOG_FILE" ]; then
    echo "Log file $LOG_FILE does not exist, nothing to rotate."
    exit 0
fi

# Rotate existing backups
for i in $(seq $((KEEP - 1)) -1 1); do
    if [ -f "${LOG_FILE}.$i.gz" ]; then
        mv "${LOG_FILE}.$i.gz" "${LOG_FILE}.$((i+1)).gz"
    fi
done

# Move current log and create new one
if [ -f "$LOG_FILE" ]; then
    mv "$LOG_FILE" "${LOG_FILE}.1"
    touch "$LOG_FILE"
    # Compress the rotated file
    gzip "${LOG_FILE}.1"
fi

echo "Rotated $LOG_FILE"
