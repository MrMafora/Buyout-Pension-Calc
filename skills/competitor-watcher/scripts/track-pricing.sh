#!/bin/bash
#
# track-pricing.sh - Track competitor pricing changes
# Usage: ./track-pricing.sh [--compare|--export]
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
REFS_DIR="$SKILL_DIR/references"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

COMPETITOR_FILE="$REFS_DIR/competitor-list.json"
PRICING_FILE="$REFS_DIR/pricing-history.json"
COMPARE_MODE=false
EXPORT_MODE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --compare)
            COMPARE_MODE=true
            ;;
        --export)
            EXPORT_MODE=true
            ;;
    esac
done

# Initialize pricing history if doesn't exist
if [[ ! -f "$PRICING_FILE" ]]; then
    echo "{}" > "$PRICING_FILE"
fi

# Function to extract pricing from URL (basic implementation)
extract_pricing() {
    local url="$1"
    local pricing_url="$2"
    
    if [[ -n "$pricing_url" && "$pricing_url" != "null" ]]; then
        url="$pricing_url"
    fi
    
    # Fetch pricing page
    local content=$(curl -s -L --max-time 30 "$url" 2>/dev/null)
    
    # Extract pricing patterns (this is a basic implementation)
    # Looks for common pricing patterns like $XX, $XXX, etc.
    echo "$content" | grep -oE '\$[0-9]+(\.[0-9]{2})?' | sort -u | head -10
}

# Function to update pricing history
update_pricing() {
    local id="$1"
    local name="$2"
    local url="$3"
    local pricing_url="$4"
    
    echo -e "${YELLOW}Checking pricing for $name...${NC}"
    
    local prices=$(extract_pricing "$url" "$pricing_url")
    local timestamp=$(date -Iseconds)
    
    if [[ -n "$prices" ]]; then
        # Update pricing history
        local pricing_entry=$(jq -n \
            --arg timestamp "$timestamp" \
            --arg prices "$prices" \
            '{timestamp: $timestamp, prices: ($prices | split("\n"))}')
        
        jq --arg id "$id" \
           --argjson entry "$pricing_entry" \
           '.[$id].history += [$entry]' "$PRICING_FILE" > "$PRICING_FILE.tmp" && \
           mv "$PRICING_FILE.tmp" "$PRICING_FILE"
        
        echo -e "${GREEN}  ✓ Pricing updated${NC}"
        echo -e "${BLUE}  Found: $(echo "$prices" | tr '\n' ', ')${NC}"
    else
        echo -e "${RED}  ✗ No pricing data found${NC}"
    fi
}

# Function to compare current vs last pricing
compare_pricing() {
    local id="$1"
    local name="$2"
    
    local history=$(jq -r ".[$id].history // []" "$PRICING_FILE")
    local count=$(echo "$history" | jq 'length')
    
    if [[ "$count" -lt 2 ]]; then
        echo -e "${YELLOW}  Not enough history for comparison${NC}"
        return
    fi
    
    local current=$(echo "$history" | jq -r '.[-1].prices | join(", ")')
    local previous=$(echo "$history" | jq -r '.[-2].prices | join(", ")')
    
    echo -e "${BLUE}  Current:  $current${NC}"
    echo -e "${BLUE}  Previous: $previous${NC}"
    
    if [[ "$current" != "$previous" ]]; then
        echo -e "${RED}  ⚠ PRICING CHANGE DETECTED!${NC}"
    fi
}

# Function to export pricing report
export_pricing() {
    local output_file="$REFS_DIR/pricing-report-$(date +%Y%m%d).csv"
    
    echo "Competitor,Date,Prices" > "$output_file"
    
    jq -r 'to_entries[] | select(.value.history | length > 0) | 
           .key as $id | .value.history[-1] | 
           [$id, .timestamp, (.prices | join("; "))] | 
           @csv' "$PRICING_FILE" >> "$output_file"
    
    echo -e "${GREEN}Pricing report exported to: $output_file${NC}"
}

# Main
echo "=========================================="
echo "  Pricing Tracker - $(date)"
echo "=========================================="

# Get competitors with pricing URLs
competitors=$(jq -r '.competitors[] | select(.track_pricing == true) | "\(.id)|\(.name)|\(.url)|\(.pricing_url // \"\")"' "$COMPETITOR_FILE")

if [[ -z "$competitors" ]]; then
    echo -e "${YELLOW}No competitors configured for pricing tracking${NC}"
    echo "Add 'track_pricing: true' and 'pricing_url' to competitors in competitor-list.json"
    exit 0
fi

while IFS='|' read -r id name url pricing_url; do
    if [[ "$COMPARE_MODE" == true ]]; then
        compare_pricing "$id" "$name"
    else
        update_pricing "$id" "$name" "$url" "$pricing_url"
    fi
    echo ""
done <<< "$competitors"

if [[ "$EXPORT_MODE" == true ]]; then
    export_pricing
fi

echo "=========================================="
echo "  Pricing tracking complete"
echo "=========================================="
