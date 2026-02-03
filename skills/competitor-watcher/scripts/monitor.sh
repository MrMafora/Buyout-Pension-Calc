#!/bin/bash
#
# monitor.sh - Monitor competitor websites for changes
# Usage: ./monitor.sh [competitor-id|--all|--force]
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
REFS_DIR="$SKILL_DIR/references"
SNAPSHOTS_DIR="$REFS_DIR/tracking-snapshots"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ensure snapshots directory exists
mkdir -p "$SNAPSHOTS_DIR"

# Load competitor list
COMPETITOR_FILE="$REFS_DIR/competitor-list.json"
if [[ ! -f "$COMPETITOR_FILE" ]]; then
    echo -e "${RED}Error: Competitor list not found at $COMPETITOR_FILE${NC}"
    exit 1
fi

FORCE=false
TARGET=""

# Parse arguments
for arg in "$@"; do
    case $arg in
        --force)
            FORCE=true
            ;;
        --all|"")
            TARGET="all"
            ;;
        *)
            TARGET="$arg"
            ;;
    esac
done

# Function to calculate checksum
calculate_checksum() {
    local url="$1"
    local content=$(curl -s -L --max-time 30 "$url" 2>/dev/null)
    if [[ -n "$content" ]]; then
        echo "$content" | md5sum | awk '{print $1}'
    else
        echo ""
    fi
}

# Function to save snapshot
save_snapshot() {
    local id="$1"
    local url="$2"
    local content="$3"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local snapshot_file="$SNAPSHOTS_DIR/${id}_${timestamp}.html"
    
    echo "$content" > "$snapshot_file"
    echo "$snapshot_file"
}

# Function to get last known checksum
get_last_checksum() {
    local id="$1"
    local state_file="$SNAPSHOTS_DIR/${id}_state.json"
    
    if [[ -f "$state_file" ]]; then
        jq -r '.checksum // empty' "$state_file" 2>/dev/null
    else
        echo ""
    fi
}

# Function to save state
save_state() {
    local id="$1"
    local checksum="$2"
    local timestamp=$(date -Iseconds)
    local state_file="$SNAPSHOTS_DIR/${id}_state.json"
    
    jq -n \
        --arg checksum "$checksum" \
        --arg timestamp "$timestamp" \
        '{checksum: $checksum, last_checked: $timestamp}' > "$state_file"
}

# Function to check single competitor
check_competitor() {
    local id="$1"
    local name=$(jq -r ".competitors[] | select(.id == \"$id\") | .name" "$COMPETITOR_FILE")
    local url=$(jq -r ".competitors[] | select(.id == \"$id\") | .url" "$COMPETITOR_FILE")
    local priority=$(jq -r ".competitors[] | select(.id == \"$id\") | .priority" "$COMPETITOR_FILE")
    
    if [[ -z "$name" || "$name" == "null" ]]; then
        echo -e "${RED}Unknown competitor: $id${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Checking $name ($url)...${NC}"
    
    # Fetch current content and calculate checksum
    local content=$(curl -s -L --max-time 30 "$url" 2>/dev/null)
    if [[ -z "$content" ]]; then
        echo -e "${RED}  ✗ Failed to fetch $url${NC}"
        return 1
    fi
    
    local current_checksum=$(echo "$content" | md5sum | awk '{print $1}')
    local last_checksum=$(get_last_checksum "$id")
    
    # Check for changes
    if [[ "$FORCE" == true || -z "$last_checksum" ]]; then
        # First check or forced refresh
        save_state "$id" "$current_checksum"
        local snapshot=$(save_snapshot "$id" "$url" "$content")
        echo -e "${GREEN}  ✓ Snapshot saved: $snapshot${NC}"
        
        if [[ -n "$last_checksum" && "$FORCE" == true ]]; then
            echo -e "${YELLOW}  ⚠ Forced refresh - checksum updated${NC}"
        fi
    elif [[ "$current_checksum" != "$last_checksum" ]]; then
        # Change detected!
        echo -e "${RED}  ⚠ CHANGE DETECTED!${NC}"
        save_state "$id" "$current_checksum"
        local snapshot=$(save_snapshot "$id" "$url" "$content")
        echo -e "${GREEN}  ✓ New snapshot saved${NC}"
        
        # Log change
        echo "$(date -Iseconds) | CHANGE | $id | $name | $url" >> "$SNAPSHOTS_DIR/changes.log"
        
        # Alert based on priority
        if [[ "$priority" == "high" ]]; then
            echo -e "${RED}  🚨 HIGH PRIORITY COMPETITOR CHANGED!${NC}"
        fi
    else
        echo -e "${GREEN}  ✓ No changes${NC}"
    fi
    
    save_state "$id" "$current_checksum"
}

# Main execution
echo "=========================================="
echo "  Competitor Monitor - $(date)"
echo "=========================================="

if [[ "$TARGET" == "all" || -z "$TARGET" ]]; then
    # Check all competitors
    competitors=$(jq -r '.competitors[].id' "$COMPETITOR_FILE")
    for id in $competitors; do
        check_competitor "$id"
        echo ""
    done
else
    # Check specific competitor
    check_competitor "$TARGET"
fi

echo ""
echo "=========================================="
echo "  Monitoring complete"
echo "=========================================="
